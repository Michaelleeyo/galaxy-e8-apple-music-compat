"""Lossless 34-to-35 packaging; uses external signing tools and environment secrets."""
import argparse,hashlib,json,os,re,subprocess,tempfile
from pathlib import Path
from apk_common import repack,compare_payloads

def run(args):
    # Do not echo subprocess arguments or tool output; failures cannot spill secrets.
    p=subprocess.run([str(x) for x in args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    if p.returncode:raise RuntimeError('External tool failed; exit code '+str(p.returncode))
    return p.stdout

def certificate(java,signer,apk):
    out=run([java,'-jar',signer,'verify','--verbose','--print-certs',apk])
    values=re.findall(r'Signer #\d+ certificate SHA-256 digest:\s*([0-9a-fA-F:]+)',out)
    values={v.replace(':','').lower() for v in values}
    if len(values)!=1:raise ValueError('Expected one signing certificate')
    return values.pop()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path);p.add_argument('output',type=Path)
    for n in ('java','zipalign','apksigner','keystore','alias','expected-cert'):p.add_argument('--'+n,required=True)
    p.add_argument('--extract-native-libs-confirmed',action='store_true');a=p.parse_args()
    if a.source.resolve()==a.output.resolve() or a.output.exists():raise ValueError('Output must be new and distinct')
    if not os.environ.get('E8_SIGN_PASSWORD'):raise ValueError('Set E8_SIGN_PASSWORD in the process environment')
    expected=a.expected_cert.replace(':','').lower()
    if not re.fullmatch('[a-f0-9]{64}',expected):raise ValueError('Invalid expected certificate digest')
    if certificate(a.java,a.apksigner,a.source)!=expected:raise ValueError('Input certificate mismatch')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='e8-repack-',dir=a.output.parent) as td:
        root=Path(td);unsigned=root/'unsigned.apk';aligned=root/'aligned.apk';signed=root/'signed.apk'
        repack(a.source,unsigned,a.extract_native_libs_confirmed)
        run([a.zipalign,'-P','16','4',unsigned,aligned])
        keyenv='E8_KEY_PASSWORD' if os.environ.get('E8_KEY_PASSWORD') else 'E8_SIGN_PASSWORD'
        run([a.java,'-jar',a.apksigner,'sign','--ks',a.keystore,'--ks-key-alias',a.alias,'--ks-pass','env:E8_SIGN_PASSWORD','--key-pass','env:'+keyenv,'--out',signed,aligned])
        if certificate(a.java,a.apksigner,signed)!=expected:raise ValueError('Output certificate mismatch')
        run([a.zipalign,'-c','-P','16','4',signed])
        result=compare_payloads(a.source,signed)
        if not result['equal']:raise ValueError('Signed payload mismatch')
        # Exclusive creation avoids replacing an output created concurrently.
        with signed.open('rb') as src,a.output.open('xb') as dst:
            import shutil
            shutil.copyfileobj(src,dst)
    result.update(bytes=a.output.stat().st_size,sha256=hashlib.sha256(a.output.read_bytes()).hexdigest(),certificateSha256=expected)
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
