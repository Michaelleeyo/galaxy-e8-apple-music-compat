"""Hide only the native Equalizer settings row on the audited 7.0.0/1614 host."""
import argparse,hashlib,io,json,os,re,subprocess,zipfile
from pathlib import Path
from apk_common import compare_payloads
from build_car_ui import rewrite,sign,CERT
from repack import certificate
METHOD='.method private final getAudioCategory(Lpi/a;Lpi/a;Lpi/a;Ljava/lang/String;ZZ)Lcom/apple/android/music/settings2/model/b$a;'

def patch(text):
    if '# E8 hide Equalizer entry' in text:raise ValueError('Equalizer row patch already exists')
    if text.count(METHOD)!=1:raise ValueError('Unexpected settings model version')
    start=text.index(METHOD);end=text.index('.end method',start);body=text[start:end]
    anchors=['const v0, 0x7f1404ad','const v1, 0x7f1404ae','const/4 v10, 0x0','invoke-static {v1}, Lci/m;->D([Ljava/lang/Object;)Ljava/util/List;','    aput-object v14, v1, v2']
    if any(body.count(x)!=1 for x in anchors):raise ValueError('Audited Equalizer list structure changed')
    # v10 is the existing null used for optional rows. The existing list builder
    # filters nulls. Only the Equalizer slot changes; do not touch preferences/DSP.
    body=body.replace('    aput-object v14, v1, v2','    # E8 hide Equalizer entry; preserve all DSP state.\n    aput-object v10, v1, v2',1)
    return text[:start]+body+text[end:]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('baseline','work','output'):p.add_argument('--'+key,type=Path,required=True)
    for key in ('expected-input-sha','java','baksmali','smali','zipalign','apksigner','keystore','alias'):p.add_argument('--'+key,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError('Output already exists')
    if hashlib.sha256(a.baseline.read_bytes()).hexdigest()!=a.expected_input_sha.lower():raise ValueError('Baseline hash mismatch')
    if certificate(a.java,a.apksigner,a.baseline)!=CERT:raise ValueError('Certificate mismatch')
    if not os.environ.get('E8_SIGN_PASSWORD'):raise ValueError('Set E8_SIGN_PASSWORD')
    a.work.mkdir(parents=True,exist_ok=False);a.output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(a.baseline) as z:origin=z.read('assets/npatch/origin.apk')
    (a.work/'origin.apk').write_bytes(origin)
    with zipfile.ZipFile(io.BytesIO(origin)) as z:original_dex=z.read('classes3.dex')
    (a.work/'original-classes3.dex').write_bytes(original_dex)
    subprocess.run([a.java,'-Xmx2g','-jar',a.baksmali,'d',str(a.work/'original-classes3.dex'),'-o',str(a.work/'smali')],check=True)
    source=a.work/'smali/com/apple/android/music/settings2/model/SettingsViewModel.smali'
    source.write_text(patch(source.read_text(encoding='utf-8')),encoding='utf-8',newline='\n')
    dex=a.work/'classes3.dex'
    subprocess.run([a.java,'-Xmx2g','-jar',a.smali,'a',str(a.work/'smali'),'-o',str(dex)],check=True)
    rewrite(a.work/'origin.apk',a.work/'patched-origin.apk',{'classes3.dex':dex.read_bytes()})
    inner=compare_payloads(a.work/'origin.apk',a.work/'patched-origin.apk')
    if inner['missing'] or inner['added'] or inner['changed']!=['classes3.dex']:raise ValueError('Unexpected inner change')
    rewrite(a.baseline,a.work/'unsigned.apk',{'assets/npatch/origin.apk':(a.work/'patched-origin.apk').read_bytes()})
    signed=a.work/'signed.apk';sign(a.work/'unsigned.apk',signed,a)
    outer=compare_payloads(a.baseline,signed)
    if outer['missing'] or outer['added'] or outer['changed']!=['assets/npatch/origin.apk']:raise ValueError('Unexpected outer change')
    with a.output.open('xb') as dest:dest.write(signed.read_bytes())
    print(json.dumps({'sha256':hashlib.sha256(a.output.read_bytes()).hexdigest(),'bytes':a.output.stat().st_size,'certificateSha256':CERT,'hostChangedDex':['classes3.dex'],'moduleUnchanged':True,'nativeLibrariesUnchanged':True,'audioEffectStateModifiedByPatch':False},indent=2))
if __name__=='__main__':main()
