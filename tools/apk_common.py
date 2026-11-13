"""Archive integrity helpers. No account or application data parsing."""
import copy
import hashlib
import zipfile
from pathlib import PurePosixPath

def is_signature(name):
    u=name.upper()
    return u == 'META-INF/MANIFEST.MF' or (u.startswith('META-INF/') and u.endswith(('.SF','.RSA','.DSA','.EC')))

def inventory(path):
    result={}
    with zipfile.ZipFile(path) as z:
        for i in z.infolist():
            if i.filename in result:
                raise ValueError('Duplicate archive entry')
            p=PurePosixPath(i.filename)
            if p.is_absolute() or '..' in p.parts or '\\' in i.filename:
                raise ValueError('Unsafe archive path')
            with z.open(i) as f:
                h=hashlib.sha256()
                for chunk in iter(lambda:f.read(1024*1024),b''):
                    h.update(chunk)
            result[i.filename]={'bytes':i.file_size,'sha256':h.hexdigest(),'compression':i.compress_type}
    return result

def compare_payloads(a,b):
    aa={k:(v['bytes'],v['sha256']) for k,v in inventory(a).items() if not is_signature(k)}
    bb={k:(v['bytes'],v['sha256']) for k,v in inventory(b).items() if not is_signature(k)}
    missing=sorted(aa.keys()-bb.keys());added=sorted(bb.keys()-aa.keys())
    changed=sorted(k for k in aa.keys() & bb.keys() if aa[k]!=bb[k])
    return {'equal':not(missing or added or changed),'missing':missing,'added':added,'changed':changed,'entries':len(aa)}

def repack(source,dest,extract_native_libs_confirmed=False):
    if not extract_native_libs_confirmed:
        raise ValueError('Confirm original extractNativeLibs=true before compression')
    inventory(source) # CRC/hash and duplicate/path checks before writing
    with zipfile.ZipFile(source) as src,zipfile.ZipFile(dest,'x',allowZip64=True) as dst:
        for i in src.infolist():
            if is_signature(i.filename):continue
            # Reuse harmless metadata, change compression only.
            payload=src.read(i.filename)
            i=copy.copy(i)
            i.compress_type=zipfile.ZIP_STORED if i.filename.endswith('resources.arsc') or i.is_dir() else zipfile.ZIP_DEFLATED
            dst.writestr(i,payload,compresslevel=9)
    result=compare_payloads(source,dest)
    if not result['equal']:raise ValueError('Repack changed payload')
    return result
