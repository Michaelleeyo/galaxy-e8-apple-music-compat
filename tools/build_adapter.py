"""Compile original adapter only. Host compile stubs are not packaged."""
import argparse,os,subprocess,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('jdk','android-jar','d8','out'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();suffix='.exe' if os.name=='nt' else ''
    a.out.mkdir(parents=True,exist_ok=True)
    target=a.out/'classes.dex'
    if target.exists():raise ValueError('Refusing to replace existing classes.dex')
    def run(args):subprocess.run([str(v) for v in args],check=True)
    with tempfile.TemporaryDirectory(prefix='adapter-') as td:
        b=Path(td);stubs=b/'stubs';classes=b/'classes';dex=b/'dex'
        for q in (stubs,classes,dex):q.mkdir()
        javac=a.jdk/'bin'/('javac'+suffix);java=a.jdk/'bin'/('java'+suffix)
        run([javac,'-source','8','-target','8','-d',stubs,*sorted((ROOT/'stubs').rglob('*.java'))])
        run([javac,'-source','8','-target','8','-cp',str(a.android_jar)+os.pathsep+str(stubs),'-d',classes,*sorted((ROOT/'src').rglob('*.java'))])
        jar=b/'adapter.jar'
        with zipfile.ZipFile(jar,'w') as z:
            for q in classes.rglob('*.class'):z.write(q,q.relative_to(classes).as_posix())
        run([java,'-cp',a.d8,'com.android.tools.r8.D8','--min-api','26','--lib',a.android_jar,'--classpath',stubs,'--output',dex,jar])
        with target.open('xb') as f:f.write((dex/'classes.dex').read_bytes())
    print('Compiled adapter DEX; compile stubs excluded')
if __name__=='__main__':main()
