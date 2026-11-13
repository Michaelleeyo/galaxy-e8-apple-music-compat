"""Build day/night launcher resources over the audited compat-37 APK."""
import argparse, copy, hashlib, io, json, os, shutil, struct, subprocess, zipfile
from pathlib import Path
from apk_common import compare_payloads, is_signature
from build_car_ui import sign, CERT
from repack import certificate
BASE_SHA = '747aaf7a48a2dc893408b36f5f5121b68745f46ccbce0b1b972e4c9e81ef9e92'
ORIGIN = 'assets/npatch/origin.apk'

def png(path):
    data = path.read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n' or data[12:16] != b'IHDR' or struct.unpack('>II', data[16:24]) != (182, 104):
        raise ValueError('Expected an original 182x104 PNG')
    return data

def rewrite(source, output, changes):
    with zipfile.ZipFile(source) as src, zipfile.ZipFile(output, 'x') as dst:
        names = set(src.namelist())
        for info in src.infolist():
            if not is_signature(info.filename):
                dst.writestr(copy.copy(info), changes.get(info.filename, src.read(info.filename)))
        for name, data in changes.items():
            if name not in names:
                dst.writestr(name, data, compress_type=zipfile.ZIP_DEFLATED)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ('baseline', 'light', 'dark', 'work', 'output'):
        p.add_argument('--' + key, type=Path, required=True)
    for key in ('java', 'apkeditor', 'zipalign', 'apksigner', 'keystore', 'alias'):
        p.add_argument('--' + key, required=True)
    a = p.parse_args()
    if a.output.exists() or a.work.exists():
        raise ValueError('Output and work paths must not exist')
    if hashlib.sha256(a.baseline.read_bytes()).hexdigest() != BASE_SHA:
        raise ValueError('Expected audited compat-37 baseline')
    if certificate(a.java, a.apksigner, a.baseline) != CERT:
        raise ValueError('Baseline certificate mismatch')
    if not os.environ.get('E8_SIGN_PASSWORD'):
        raise ValueError('Set E8_SIGN_PASSWORD in the process environment')
    images = {'': png(a.light), '-night': png(a.dark)}
    a.work.mkdir(parents=True)
    decoded = a.work / 'decoded'
    def editor(*args):
        subprocess.run([a.java, '-jar', a.apkeditor, *map(str, args)], check=True)
    editor('d', '-dex', '-i', a.baseline, '-o', decoded)
    res = decoded / 'resources/package_1/res'
    if not res.is_dir():
        raise ValueError('Unexpected resource package structure')
    # Remove adaptive/other-density launcher variants so they cannot outrank nodpi.
    for name in ('ic_launcher', 'ic_launcher_round'):
        for f in res.glob('mipmap*/' + name + '.*'):
            f.unlink()
    for suffix, data in images.items():
        folder = res / ('mipmap' + suffix + '-nodpi')
        folder.mkdir(exist_ok=True)
        for name in ('ic_launcher', 'ic_launcher_round'):
            (folder / (name + '.png')).write_bytes(data)
    rebuilt = a.work / 'rebuilt.apk'
    editor('b', '-i', decoded, '-o', rebuilt)
    with zipfile.ZipFile(rebuilt) as z:
        changes = {'resources.arsc': z.read('resources.arsc')}
        for suffix, data in images.items():
            for name in ('ic_launcher', 'ic_launcher_round'):
                path = 'res/mipmap' + suffix + '-nodpi/' + name + '.png'
                if z.read(path) != data:
                    raise ValueError('Rebuilt icon differs from supplied PNG')
                changes[path] = data
    # Use only the rebuilt resource table and four PNGs. Keep original code,
    # manifest and every unrelated resource byte intact in both containers.
    with zipfile.ZipFile(a.baseline) as z:
        origin = z.read(ORIGIN)
        with zipfile.ZipFile(io.BytesIO(origin)) as inner:
            if inner.read('resources.arsc') != z.read('resources.arsc'):
                raise ValueError('Inner/outer baseline resource tables differ')
    patched = a.work / 'origin.apk'
    rewrite(io.BytesIO(origin), patched, changes)
    with zipfile.ZipFile(io.BytesIO(origin)) as before, zipfile.ZipFile(patched) as after:
        old_names = {n for n in before.namelist() if not is_signature(n)}
        new_names = {n for n in after.namelist() if not is_signature(n)}
        if old_names - new_names or new_names - old_names != set(changes) - {'resources.arsc'}:
            raise ValueError('Unexpected inner entry changes')
        modified = {n for n in old_names if before.read(n) != after.read(n)}
        if modified != {'resources.arsc'}:
            raise ValueError('Unexpected inner payload changes')
    changes[ORIGIN] = patched.read_bytes()
    unsigned = a.work / 'unsigned.apk'
    rewrite(a.baseline, unsigned, changes)
    signed = a.work / 'signed.apk'
    sign(unsigned, signed, a)
    if not compare_payloads(unsigned, signed)['equal']:
        raise ValueError('Signing changed payload')
    diff = compare_payloads(a.baseline, signed)
    expected_added = sorted(set(changes) - {'resources.arsc', ORIGIN})
    if diff['missing'] or diff['added'] != expected_added or diff['changed'] != sorted([ORIGIN, 'resources.arsc']):
        raise ValueError('Unexpected outer changes')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with a.output.open('xb') as dest, signed.open('rb') as src:
        shutil.copyfileobj(src, dest)
    result = {'build': 38, 'sha256': hashlib.sha256(a.output.read_bytes()).hexdigest(),
              'certificateSha256': CERT, 'imageSize': [182, 104],
              'outerDifferences': diff, 'physicalCarRuntimeTested': False}
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
