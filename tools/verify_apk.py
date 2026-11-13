"""Compare uncompressed non-signature payloads, not just archive sizes."""
import argparse,json
from apk_common import compare_payloads,inventory

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('baseline');p.add_argument('candidate');a=p.parse_args()
    result=compare_payloads(a.baseline,a.candidate)
    entries=inventory(a.candidate)
    result['nativeAbis']=sorted({n.split('/')[1] for n in entries if n.startswith('lib/') and n.endswith('.so')})
    result['resourceTableStored']=all(v['compression']==0 for n,v in entries.items() if n.endswith('resources.arsc'))
    print(json.dumps(result,indent=2))
    return 0 if result['equal'] and result['resourceTableStored'] else 1
if __name__=='__main__':raise SystemExit(main())
