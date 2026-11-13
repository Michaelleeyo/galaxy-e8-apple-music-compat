"""Heuristic pre-publication scan. Reports paths/rules only, never matched values."""
import re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BANNED={'.apk','.apks','.apkm','.xapk','.so','.dex','.jar','.class','.keystore','.jks','.p12','.pfx','.pem','.key','.idsig','.log','.jsonl','.zip'}
ALLOWED_BINARY={
 'assets/icons/launcher-light.png',
 'assets/icons/launcher-dark.png',
}
RULES={
 'private-key':r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
 'personal-email':r'[A-Z0-9._%+-]+@(?:qq|163|126|gmail|icloud|outlook)\.[A-Z]{2,}',
 'token-assignment':r'(?i)(?:password|passwd|passwordEquivalentToken|musicUserToken|xToken|cookie)\s*[=:]\s*[\"\x27][^\"\x27\n]{8,}[\"\x27]',
 'github-token':r'gh[pousr]_[A-Za-z0-9]{24,}',
 'bearer-value':r'Bearer\s+[A-Za-z0-9_.-]{24,}',
 'private-local-path':r'C:[/\\]Users[/\\][^/\\\s]+',
}

def findings(path,data):
    result=[]
    if path.suffix.lower() in BANNED:result.append('forbidden-artifact')
    if len(data)>1024*1024:result.append('oversize')
    normalized=path.as_posix()
    allowed_binary=any(normalized.endswith('/'+name) or normalized==name for name in ALLOWED_BINARY)
    if b'\0' in data and not allowed_binary:result.append('binary')
    text=data.decode('utf-8',errors='replace')
    for name,pattern in RULES.items():
        if re.search(pattern,text,re.I):result.append(name)
    return result

def paths():
    p=subprocess.run(['git','-C',str(ROOT),'ls-files','-z','--cached','--others','--exclude-standard'],capture_output=True)
    if p.returncode==0:return [ROOT/x.decode('utf-8') for x in p.stdout.split(b'\0') if x]
    return [x for x in ROOT.rglob('*') if x.is_file() and not any(v in {'.git','__pycache__','build','.venv'} for v in x.relative_to(ROOT).parts)]

def main():
    failures=[];files=paths()
    for p in files:
        if p.is_file():failures.extend((p.relative_to(ROOT).as_posix(),rule) for rule in findings(p,p.read_bytes()))
    for path,rule in failures:print(path+': '+rule)
    print('Scanned '+str(len(files))+' files; findings='+str(len(failures)))
    return int(bool(failures))
if __name__=='__main__':raise SystemExit(main())
