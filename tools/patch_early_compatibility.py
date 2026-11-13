"""Patch the audited Apple Music 7.0.0/1614 Root and cellular gates.

The input is a user-extracted classes2 smali directory. Every target is tied to
the verified 7.0.0/1614 structure and fails closed when its anchors drift.
"""
import argparse
import hashlib
import re
from pathlib import Path

ROOT_FILE = Path("com/apple/android/music/AppleMusicApplication.smali")
CELLULAR_FILE = Path(
    "com/apple/android/music/playback/preferences/MediaPlaybackPreferences.smali"
)
ROOT_METHOD = ".method public static i()Z"
CELLULAR_METHODS = (
    "getUseCellularData(Landroid/content/Context;)Z",
    "isCellularDataEnabled()Z",
)


def method(text: str, declaration: str) -> tuple[int, int, str]:
    pattern = rf"(?ms)^{re.escape(declaration)}\n.*?^\.end method$"
    matches = list(re.finditer(pattern, text))
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one {declaration}; found {len(matches)}")
    match = matches[0]
    return match.start(), match.end(), match.group(0)


def patch_root(text: str) -> str:
    start, end, body = method(text, ROOT_METHOD)
    required = ("/system/bin/su", "Lwg/h;->h()Z")
    missing = [anchor for anchor in required if anchor not in body]
    if missing:
        raise ValueError(f"Unexpected 7.0 Root gate; missing anchors: {missing}")
    replacement = """.method public static i()Z
    .registers 1

    # E8 7.0.0/1614 compatibility: the authorized car environment is rooted,
    # so this app-specific startup gate must not block launch.
    const/4 v0, 0x0
    return v0
.end method"""
    return text[:start] + replacement + text[end:]


def patch_cellular(text: str) -> str:
    anchors = {
        CELLULAR_METHODS[0]: ("isCellularAvailable()Z", "key_use_cellular_data"),
        CELLULAR_METHODS[1]: ("cellular_data_enabled", "Landroidx/annotation/Keep;"),
    }
    for name in CELLULAR_METHODS:
        declaration = f".method public {name}"
        start, end, body = method(text, declaration)
        missing = [anchor for anchor in anchors[name] if anchor not in body]
        if missing:
            raise ValueError(f"Unexpected 7.0 cellular gate {name}; missing: {missing}")
        annotation = ""
        if "Landroidx/annotation/Keep;" in body:
            annotation = """    .annotation build Landroidx/annotation/Keep;
    .end annotation
"""
        replacement = f"""{declaration}
    .registers 2
{annotation}
    # E8 compatibility: permit app playback on the car's Android network.
    # This does not alter SIM, ConnectivityManager, TLS, accounts, or DRM.
    const/4 v0, 0x1
    return v0
.end method"""
        text = text[:start] + replacement + text[end:]
    return text


def apply(smali_root: Path, root_gate: bool, cellular_policy: bool, dry_run: bool):
    if not root_gate and not cellular_policy:
        raise ValueError("Select --root-gate and/or --cellular-policy")
    targets = []
    if root_gate:
        targets.append((smali_root / ROOT_FILE, patch_root))
    if cellular_policy:
        targets.append((smali_root / CELLULAR_FILE, patch_cellular))
    changes = []
    for path, transform in targets:
        original = path.read_text(encoding="utf-8")
        patched = transform(original)
        if patched == original:
            raise ValueError(f"No change produced for {path}")
        changes.append((path, original, patched))
    if not dry_run:
        for path, original, patched in changes:
            backup = path.with_suffix(path.suffix + ".bak")
            with backup.open("xb") as stream:
                stream.write(original.encode("utf-8"))
            path.write_text(patched, encoding="utf-8")
    return [
        {
            "file": str(path.relative_to(smali_root)),
            "before": hashlib.sha256(original.encode()).hexdigest(),
            "after": hashlib.sha256(patched.encode()).hexdigest(),
        }
        for path, original, patched in changes
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("smali_root", type=Path)
    parser.add_argument("--root-gate", action="store_true")
    parser.add_argument("--cellular-policy", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    for result in apply(
        args.smali_root, args.root_gate, args.cellular_policy, args.dry_run
    ):
        print(result)
    print("Validated; no files written" if args.dry_run else "Patch applied; originals preserved as .bak")


if __name__ == "__main__":
    main()
