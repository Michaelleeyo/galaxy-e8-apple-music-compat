"""Rebuild from a trusted 34/35 baseline, replacing only the final adapter DEX."""
import argparse,copy,hashlib,io,json,os,tempfile,zipfile
from pathlib import Path
from apk_common import compare_payloads,is_signature
from repack import certificate,run
ORIGIN='assets/npatch/origin.apk'

def replace_adapter(source,dex,output):
    payload=Path(dex).read_bytes()
    if not payload.startswith(b'dex\n'):raise ValueError('Expected compiled DEX')
    with zipfile.ZipFile(source) as outer:
        original=outer.read(ORIGIN)
        with zipfile.ZipFile(io.BytesIO(original)) as inner:
            if 'classes6.dex' not in inner.namelist():raise ValueError('Baseline lacks final adapter DEX')
            new=io.BytesIO()
            with zipfile.ZipFile(new,'w') as z:
                for info in inner.infolist():
                    if is_signature(info.filename):continue
                    z.writestr(copy.copy(info),payload if info.filename=='classes6.dex' else inner.read(info.filename))
        with zipfile.ZipFile(output,'x') as z:
            for info in outer.infolist():
                if is_signature(info.filename):continue
                z.writestr(copy.copy(info),new.getvalue() if info.filename==ORIGIN else outer.read(info.filename))
    # Guard both layers; compare contents rather than compressed bytes.
    changed=compare_payloads(source,output)
    if changed['missing'] or changed['added'] or set(changed['changed'])-{ORIGIN}:raise ValueError('Unexpected outer change')
    inner_changes=compare_payloads(io.BytesIO(original),io.BytesIO(new.getvalue()))
    if inner_changes['missing'] or inner_changes['added'] or set(inner_changes['changed'])-{'classes6.dex'}:raise ValueError('Unexpected inner change')
    return {'outer':changed,'inner':inner_changes}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('baseline','adapter','output'):p.add_argument(name,type=Path)
    for name in ('expected-input-sha','java','zipalign','apksigner','keystore','alias','expected-cert'):p.add_argument('--'+name,required=True)
    a=p.parse_args()
    if a.output.exists() or a.output.resolve()==a.baseline.resolve():raise ValueError('Output must be new')
    if hashlib.sha256(a.baseline.read_bytes()).hexdigest()!=a.expected_input_sha.lower():raise ValueError('Baseline SHA256 mismatch')
    if not os.environ.get('E8_SIGN_PASSWORD'):raise ValueError('Set E8_SIGN_PASSWORD in process environment')
    cert=a.expected_cert.replace(':','').lower()
    if certificate(a.java,a.apksigner,a.baseline)!=cert:raise ValueError('Input certificate mismatch')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='e8-update-',dir=a.output.parent) as td:
        root=Path(td);unsigned=root/'unsigned.apk';aligned=root/'aligned.apk';signed=root/'signed.apk'
        result=replace_adapter(a.baseline,a.adapter,unsigned)
        run([a.zipalign,'-P','16','4',unsigned,aligned])
        keyenv='E8_KEY_PASSWORD' if os.environ.get('E8_KEY_PASSWORD') else 'E8_SIGN_PASSWORD'
        run([a.java,'-jar',a.apksigner,'sign','--ks',a.keystore,'--ks-key-alias',a.alias,'--ks-pass','env:E8_SIGN_PASSWORD','--key-pass','env:'+keyenv,'--out',signed,aligned])
        if certificate(a.java,a.apksigner,signed)!=cert:raise ValueError('Output certificate mismatch')
        run([a.zipalign,'-c','-P','16','4',signed])
        if not compare_payloads(unsigned,signed)['equal']:raise ValueError('Signing changed content')
        with a.output.open('xb') as dst,signed.open('rb') as src:
            import shutil
            shutil.copyfileobj(src,dst)
    result.update(sha256=hashlib.sha256(a.output.read_bytes()).hexdigest(),bytes=a.output.stat().st_size,certificateSha256=cert)
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
