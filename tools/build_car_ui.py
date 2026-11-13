"""Package audited UI DEX changes over an external 35 APK; authentication is preserved."""
import argparse,copy,hashlib,io,json,os,tempfile,zipfile
from pathlib import Path
from apk_common import compare_payloads,is_signature
from repack import certificate,run
ORIGIN='assets/npatch/origin.apk'
MODULE='assets/npatch/modules/dev.amenhancer.module.apk'
CERT='113307a4a4974d875fff074b6f79ef557abef81aac845c145b88bc529c62eed3'

def rewrite(source,output,changes):
    with zipfile.ZipFile(source) as src,zipfile.ZipFile(output,'x',allowZip64=True) as dst:
        missing=set(changes)-set(src.namelist())
        if missing:raise ValueError('Missing replacement entry')
        for info in src.infolist():
            if is_signature(info.filename):continue
            dst.writestr(copy.copy(info),changes.get(info.filename,src.read(info.filename)),compresslevel=9)

def sign(source,dest,args):
    aligned=source.with_suffix('.aligned.apk')
    run([args.zipalign,'-P','16','4',source,aligned])
    keyenv='E8_KEY_PASSWORD' if os.environ.get('E8_KEY_PASSWORD') else 'E8_SIGN_PASSWORD'
    run([args.java,'-jar',args.apksigner,'sign','--ks',args.keystore,'--ks-key-alias',args.alias,'--ks-pass','env:E8_SIGN_PASSWORD','--key-pass','env:'+keyenv,'--out',dest,aligned])
    if certificate(args.java,args.apksigner,dest)!=CERT:raise ValueError('Certificate mismatch')
    run([args.zipalign,'-c','-P','16','4',dest])

def build(args):
    if args.output.exists():raise ValueError('Output already exists')
    if hashlib.sha256(args.baseline.read_bytes()).hexdigest()!=args.expected_input_sha.lower():raise ValueError('Baseline hash mismatch')
    if certificate(args.java,args.apksigner,args.baseline)!=CERT:raise ValueError('Baseline certificate mismatch')
    if not os.environ.get('E8_SIGN_PASSWORD'):raise ValueError('Set E8_SIGN_PASSWORD')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='e8-ui-',dir=args.output.parent) as td:
        d=Path(td)
        with zipfile.ZipFile(args.baseline) as z:
            (d/'origin.apk').write_bytes(z.read(ORIGIN));(d/'module.apk').write_bytes(z.read(MODULE))
        rewrite(d/'origin.apk',d/'new-origin.apk',{'classes2.dex':args.host_dex.read_bytes()})
        rewrite(d/'module.apk',d/'new-module.apk',{'classes2.dex':args.module_dex.read_bytes()})
        sign(d/'new-module.apk',d/'signed-module.apk',args)
        inner=compare_payloads(d/'origin.apk',d/'new-origin.apk')
        module=compare_payloads(d/'module.apk',d/'signed-module.apk')
        for result in (inner,module):
            if result['missing'] or result['added'] or result['changed']!=['classes2.dex']:raise ValueError('Unexpected DEX scope')
        rewrite(args.baseline,d/'outer.apk',{ORIGIN:(d/'new-origin.apk').read_bytes(),MODULE:(d/'signed-module.apk').read_bytes()})
        sign(d/'outer.apk',d/'signed.apk',args)
        outer=compare_payloads(args.baseline,d/'signed.apk')
        if outer['missing'] or outer['added'] or set(outer['changed'])!={ORIGIN,MODULE}:raise ValueError('Unexpected outer scope')
        with args.output.open('xb') as dst:dst.write((d/'signed.apk').read_bytes())
    return {'sha256':hashlib.sha256(args.output.read_bytes()).hexdigest(),'bytes':args.output.stat().st_size,'certificateSha256':CERT,'hostChanges':inner['changed'],'moduleChanges':module['changed'],'outerChanges':outer['changed'],'authenticationDexUnchanged':True}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('baseline','host-dex','module-dex','output'):p.add_argument('--'+key,type=Path,required=True)
    for key in ('expected-input-sha','java','zipalign','apksigner','keystore','alias'):p.add_argument('--'+key,required=True)
    a=p.parse_args();print(json.dumps(build(a),indent=2))
if __name__=='__main__':main()
