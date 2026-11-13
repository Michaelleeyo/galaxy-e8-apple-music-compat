"""Strict one-time final-action hook for a user-supplied 7.0 smali file."""
import argparse,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
METHOD='.method public final postMessage(ILjava/lang/String;)V'
MARKER='Lcom/e8/auth36/FinalAccount;->route'

def patch(text):
    if MARKER in text:raise ValueError('Hook already exists; refusing double application')
    if text.count(METHOD)!=1:raise ValueError('Expected exactly one target method')
    start=text.index(METHOD);end=text.find('.end method',start)
    if end<0:raise ValueError('Unterminated method')
    body=text[start:end]
    locals_=re.search(r'\.locals\s+(\d+)',body)
    registers=re.search(r'\.registers\s+(\d+)',body)
    if not ((locals_ and int(locals_[1])>=1) or (registers and int(registers[1])>=4)):
        raise ValueError('No verified v0 scratch register')
    # v0 must not alias p2; the original method uses a pre-existing local.
    anchor='    .line 1'
    anchors=list(re.finditer(r'(?m)^    \.line 1$',body))
    if len(anchors)!=1:raise ValueError('Expected unique entry anchor')
    pos=start+anchors[0].start()
    prefix=body[:anchors[0].start()]
    if re.search(r'^\s*(?:invoke-|move-|const|new-|if-|goto|return|throw)',prefix,re.M):
        raise ValueError('Executable code before entry anchor')
    hook=(ROOT/'patches/final-action-hook.smali').read_text(encoding='utf-8')+'\n'
    return text[:pos]+hook+text[pos:]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('file',type=Path);p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    text=a.file.read_text(encoding='utf-8');out=patch(text)
    if a.dry_run:print('Validated; no files written');return
    backup=a.file.with_suffix(a.file.suffix+'.bak')
    with backup.open('xb') as f:f.write(a.file.read_bytes())
    a.file.write_text(out,encoding='utf-8');print('Hook applied; original preserved in .bak')
if __name__=='__main__':main()
