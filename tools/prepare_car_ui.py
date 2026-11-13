"""Extract audited UI DEX from a self-supplied 35 APK, patch and reassemble."""
import argparse,hashlib,io,json,subprocess,zipfile
from pathlib import Path
from patch_car_ui import patch_knockout,patch_song_column

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--expected-input-sha',required=True)
    p.add_argument('--work',type=Path,required=True)
    for key in ('java','baksmali','smali'):p.add_argument('--'+key,required=True)
    a=p.parse_args()
    if hashlib.sha256(a.baseline.read_bytes()).hexdigest()!=a.expected_input_sha.lower():raise ValueError('Baseline hash mismatch')
    a.work.mkdir(parents=True,exist_ok=False)
    with zipfile.ZipFile(a.baseline) as z:
        origin=z.read('assets/npatch/origin.apk');module=z.read('assets/npatch/modules/dev.amenhancer.module.apk')
    for tag,data in [('host',origin),('module',module)]:
        with zipfile.ZipFile(io.BytesIO(data)) as z:raw=z.read('classes2.dex')
        (a.work/(tag+'-input.dex')).write_bytes(raw)
        subprocess.run([a.java,'-Xmx2g','-jar',a.baksmali,'d',str(a.work/(tag+'-input.dex')),'-o',str(a.work/(tag+'-smali'))],check=True)
    paths=[(a.work/'host-smali/com/apple/android/music/common/views/KnockoutButton.smali',patch_knockout),(a.work/'module-smali/dev/amenhancer/module/hook/tabletmedia/TabletSongColumnLayout.smali',patch_song_column)]
    # Validate both before mutating either disassembled tree.
    changes=[(path,patch(path.read_text(encoding='utf-8'))) for path,patch in paths]
    for path,text in changes:path.write_text(text,encoding='utf-8',newline='\n')
    report={}
    for tag in ('host','module'):
        out=a.work/(tag+'-classes2.dex')
        subprocess.run([a.java,'-Xmx2g','-jar',a.smali,'a',str(a.work/(tag+'-smali')),'-o',str(out)],check=True)
        report[tag+'DexSha256']=hashlib.sha256(out.read_bytes()).hexdigest()
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
