"""Build compat-39 from an audited user-supplied compat-38 APK."""
import argparse
import copy
import hashlib
import io
import json
import os
import subprocess
import zipfile
from pathlib import Path

from apk_common import compare_payloads, is_signature
from repack import certificate

BASE_SHA256 = "73d1028ded0ed2749f5ff08be67f1c4405534c3051579c365283e7d753ea6d99"
MODULE = "assets/npatch/modules/dev.amenhancer.module.apk"
DEX = "classes2.dex"


def run(*args):
    subprocess.run([str(value) for value in args], check=True)


def rewrite(source: Path, output: Path, changes: dict[str, bytes]):
    with zipfile.ZipFile(source) as src, zipfile.ZipFile(output, "x", allowZip64=True) as dst:
        missing = set(changes) - set(src.namelist())
        if missing:
            raise ValueError(f"Missing replacement entries: {sorted(missing)}")
        for info in src.infolist():
            if is_signature(info.filename):
                continue
            dst.writestr(copy.copy(info), changes.get(info.filename, src.read(info.filename)), compresslevel=9)


def sign(source: Path, output: Path, args) -> str:
    aligned = source.with_suffix(".aligned.apk")
    run(args.zipalign, "-P", "16", "4", source, aligned)
    key_env = "E8_KEY_PASSWORD" if os.environ.get("E8_KEY_PASSWORD") else "E8_SIGN_PASSWORD"
    run(
        args.java, "-jar", args.apksigner, "sign",
        "--ks", args.keystore, "--ks-key-alias", args.alias,
        "--ks-pass", "env:E8_SIGN_PASSWORD", "--key-pass", f"env:{key_env}",
        "--out", output, aligned,
    )
    run(args.java, "-jar", args.apksigner, "verify", "--verbose", output)
    run(args.zipalign, "-c", "-P", "16", "4", output)
    return certificate(args.java, args.apksigner, output)


def patch_module(smali: Path):
    policy = smali / "dev/amenhancer/module/hook/TabletArtworkLayoutPolicy.smali"
    text = policy.read_text(encoding="utf-8")
    marker = "# E8 UI39: enlarge shared song and queue geometry by ten percent."
    if marker in text:
        raise ValueError("UI39 patch already exists; refusing double application")
    anchor = "    invoke-direct/range {v37 .. v67}, Ldev/amenhancer/module/hook/TabletArtworkLayoutPolicy$SongColumn;-><init>(IIIIIIIIIIIFIIIIIFIIIIIIIIIIII)V"
    if text.count(anchor) != 1:
        raise ValueError("Expected one audited AM++ 1.6.8 SongColumn constructor")
    code = f"""    {marker}
    move/from16 v3, v42
    move/from16 v1, v44
    div-int/lit8 v1, v1, 0x2
    sub-int/2addr v3, v1
    move/from16 v4, v39
    const v6, 0x3f8ccccd    # 1.1f
"""
    # v43/v44 are the floating collapse handle width/height. Keep both at the
    # compat-38 size; only its center position follows the enlarged geometry.
    for register in (39, 41, 48, 50, 52, 53, 54, 57, 58, 59, 60, 61):
        code += f"""    move/from16 v1, v{register}
    int-to-float v1, v1
    mul-float/2addr v1, v6
    invoke-static {{v1}}, Ljava/lang/Math;->round(F)I
    move-result v1
    move/16 v{register}, v1
"""
    for register in (49, 55):
        code += f"""    move/from16 v1, v{register}
    mul-float/2addr v1, v6
    move/16 v{register}, v1
"""
    code += """    move/from16 v1, v39
    sub-int/2addr v4, v1
    div-int/lit8 v4, v4, 0x2
    move/from16 v1, v38
    add-int/2addr v1, v4
    move/16 v38, v1
"""
    for register, gap in ((40, 0), (42, 0), (45, 5), (46, 20), (47, 5), (51, 12), (56, 20)):
        code += f"""    move/from16 v1, v{register}
    sub-int/2addr v1, v3
    int-to-float v1, v1
    mul-float/2addr v1, v6
    invoke-static {{v1}}, Ljava/lang/Math;->round(F)I
    move-result v1
    add-int/2addr v1, v3
"""
        if gap:
            code += f"    add-int/lit8 v1, v1, {gap}\n"
        code += f"    move/16 v{register}, v1\n"
    policy.write_text(text.replace(anchor, code + anchor), encoding="utf-8")


def build(args):
    if args.output.exists():
        raise FileExistsError(args.output)
    actual_sha = hashlib.sha256(args.baseline.read_bytes()).hexdigest()
    if actual_sha != args.expected_input_sha.lower():
        raise ValueError(f"Baseline SHA256 mismatch: {actual_sha}")
    if not os.environ.get("E8_SIGN_PASSWORD"):
        raise ValueError("Set E8_SIGN_PASSWORD; optionally set E8_KEY_PASSWORD")
    args.work.mkdir(parents=True)
    with zipfile.ZipFile(args.baseline) as outer:
        module_bytes = outer.read(MODULE)
    original_module = args.work / "module-original.apk"
    original_module.write_bytes(module_bytes)
    with zipfile.ZipFile(io.BytesIO(module_bytes)) as module:
        input_dex = module.read(DEX)
    input_path = args.work / "module-classes2-original.dex"
    output_path = args.work / "module-classes2-ui39.dex"
    smali = args.work / "module-smali"
    input_path.write_bytes(input_dex)
    run(args.java, "-jar", args.baksmali, "d", input_path, "-o", smali)
    patch_module(smali)
    run(args.java, "-jar", args.smali, "a", smali, "-o", output_path)

    unsigned_module = args.work / "module-unsigned.apk"
    signed_module = args.work / "module-signed.apk"
    rewrite(original_module, unsigned_module, {DEX: output_path.read_bytes()})
    output_cert = sign(unsigned_module, signed_module, args)
    module_diff = compare_payloads(original_module, signed_module)
    if module_diff["missing"] or module_diff["added"] or module_diff["changed"] != [DEX]:
        raise ValueError(f"Unexpected module changes: {module_diff}")

    unsigned_outer = args.work / "compat39-unsigned.apk"
    rewrite(args.baseline, unsigned_outer, {MODULE: signed_module.read_bytes()})
    final_cert = sign(unsigned_outer, args.output, args)
    if final_cert != output_cert:
        raise ValueError("Nested module and outer APK certificates differ")
    if args.expected_output_cert and final_cert != args.expected_output_cert.lower():
        raise ValueError("Output certificate mismatch")
    outer_diff = compare_payloads(args.baseline, args.output)
    if outer_diff["missing"] or outer_diff["added"] or outer_diff["changed"] != [MODULE]:
        raise ValueError(f"Unexpected outer changes: {outer_diff}")
    return {
        "file": str(args.output),
        "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "bytes": args.output.stat().st_size,
        "baselineSha256": actual_sha,
        "baselineCertificateSha256": certificate(args.java, args.apksigner, args.baseline),
        "outputCertificateSha256": final_cert,
        "moduleChanges": module_diff["changed"],
        "outerChanges": outer_diff["changed"],
        "originUnchanged": True,
        "authenticationDexUnchanged": True,
        "queueAdapterModified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--expected-input-sha", default=BASE_SHA256)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--java", required=True)
    parser.add_argument("--baksmali", required=True)
    parser.add_argument("--smali", required=True)
    parser.add_argument("--zipalign", required=True)
    parser.add_argument("--apksigner", required=True)
    parser.add_argument("--keystore", required=True)
    parser.add_argument("--alias", required=True)
    parser.add_argument("--expected-output-cert")
    args = parser.parse_args()
    print(json.dumps(build(args), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
