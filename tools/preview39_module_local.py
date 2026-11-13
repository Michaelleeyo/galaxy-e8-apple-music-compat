from pathlib import Path
import zipfile,io,subprocess,hashlib
import argparse
parser=argparse.ArgumentParser(description='Build the 39 preview module DEX from the local 38 APK')
parser.add_argument('--baseline',type=Path,required=True)
parser.add_argument('--work',type=Path,required=True)
parser.add_argument('--toolchain',type=Path,required=True)
args=parser.parse_args()
base=args.baseline;work=args.work;work.mkdir(exist_ok=True)
t=args.toolchain;java=t/'jdk/jdk-21.0.13+9/bin/java.exe'

with zipfile.ZipFile(base) as z:mod=z.read('assets/npatch/modules/dev.amenhancer.module.apk')
with zipfile.ZipFile(io.BytesIO(mod)) as z:dex=z.read('classes2.dex')
(work/'module.dex').write_bytes(dex)
subprocess.run([str(java),'-jar',str(t/'baksmali.jar'),'d',str(work/'module.dex'),'-o',str(work/'smali')],check=True)
p=work/'smali/dev/amenhancer/module/hook/TabletArtworkLayoutPolicy.smali';s=p.read_text(encoding='utf-8')
anchor='    invoke-direct/range {v37 .. v67}, Ldev/amenhancer/module/hook/TabletArtworkLayoutPolicy$SongColumn;-><init>(IIIIIIIIIIIFIIIIIFIIIIIIIIIIII)V'
assert s.count(anchor)==1
code='''    # E8: enlarge the shared song/queue control geometry by ten percent.
    move/from16 v3, v42
    move/from16 v1, v44
    div-int/lit8 v1, v1, 0x2
    sub-int/2addr v3, v1
    move/from16 v4, v39
    const v6, 0x3f8ccccd    # 1.1f
'''
# Keep thumbWidth/thumbHeight (v43/v44) at their original size so the floating
# collapse bar does not become larger with the rest of the player. Its center
# position still follows the enlarged layout.
for reg in [39,41,48,50,52,53,54,57,58,59,60,61]:
 code+=f'    move/from16 v1, v{reg}\n    int-to-float v1, v1\n    mul-float/2addr v1, v6\n    invoke-static {{v1}}, Ljava/lang/Math;->round(F)I\n    move-result v1\n    move/16 v{reg}, v1\n'
for reg in [49,55]:code+=f'    move/from16 v1, v{reg}\n    mul-float/2addr v1, v6\n    move/16 v{reg}, v1\n'
code+='    move/from16 v1, v39\n    sub-int/2addr v4, v1\n    div-int/lit8 v4, v4, 0x2\n    move/from16 v1, v38\n    add-int/2addr v1, v4\n    move/16 v38, v1\n'
for reg,gap in [(40,0),(42,0),(45,5),(46,20),(47,5),(51,12),(56,20)]:
 code+=f'    move/from16 v1, v{reg}\n    sub-int/2addr v1, v3\n    int-to-float v1, v1\n    mul-float/2addr v1, v6\n    invoke-static {{v1}}, Ljava/lang/Math;->round(F)I\n    move-result v1\n    add-int/2addr v1, v3\n'
 if gap:code+=f'    add-int/lit8 v1, v1, {gap}\n'
 code+=f'    move/16 v{reg}, v1\n'
s=s.replace(anchor,code+anchor);p.write_text(s,encoding='utf-8')
subprocess.run([str(java),'-jar',str(t/'smali.jar'),'a',str(work/'smali'),'-o',str(work/'module-patched.dex')],check=True)
print('Patched module DEX:',hashlib.sha256((work/'module-patched.dex').read_bytes()).hexdigest())
