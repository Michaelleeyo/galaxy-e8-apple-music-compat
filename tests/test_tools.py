import sys,tempfile,unittest,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from apk_common import repack,compare_payloads,inventory
from patch_ui import patch,MARKER
from patch_early_compatibility import patch_root,patch_cellular
from scan_repository import findings
from update_adapter import replace_adapter

class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.a=self.root/'a.apk';self.b=self.root/'b.apk'
        with zipfile.ZipFile(self.a,'w') as z:
            z.writestr('classes.dex',b'synthetic-dex')
            z.writestr('resources.arsc',b'synthetic-resource')
            z.writestr('assets/npatch/origin.apk',b'synthetic-nested'*100)
            z.writestr('lib/arm64-v8a/libfixture.so',b'synthetic-native'*100)
            z.writestr('META-INF/CERT.RSA',b'synthetic-signature')
    def test_lossless_and_baseline_unchanged(self):
        before=self.a.read_bytes();result=repack(self.a,self.b,True)
        self.assertTrue(result['equal']);self.assertEqual(before,self.a.read_bytes())
        with zipfile.ZipFile(self.b) as z:
            self.assertEqual(z.getinfo('resources.arsc').compress_type,0)
            self.assertEqual(z.getinfo('lib/arm64-v8a/libfixture.so').compress_type,8)
            self.assertNotIn('META-INF/CERT.RSA',z.namelist())
    def test_requires_manifest_confirmation(self):
        with self.assertRaises(ValueError):repack(self.a,self.b)
        self.assertFalse(self.b.exists())
    def test_refuses_replace(self):
        self.b.write_bytes(b'preserve')
        with self.assertRaises(FileExistsError):repack(self.a,self.b,True)
        self.assertEqual(self.b.read_bytes(),b'preserve')
    def test_detects_changed_missing_added(self):
        with zipfile.ZipFile(self.b,'w') as z:z.writestr('classes.dex',b'changed');z.writestr('extra',b'new')
        result=compare_payloads(self.a,self.b)
        self.assertFalse(result['equal']);self.assertIn('classes.dex',result['changed']);self.assertTrue(result['missing']);self.assertEqual(result['added'],['extra'])
    def test_unsafe_path(self):
        with zipfile.ZipFile(self.b,'w') as z:z.writestr('../outside',b'x')
        with self.assertRaises(ValueError):inventory(self.b)
    def test_duplicate_rejected(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            with zipfile.ZipFile(self.b,'w') as z:z.writestr('same',b'a');z.writestr('same',b'b')
        with self.assertRaises(ValueError):inventory(self.b)

class PatchTests(unittest.TestCase):
    SOURCE='.method public final postMessage(ILjava/lang/String;)V\n    .locals 2\n    .line 1\n    return-void\n.end method\n'
    def test_one_hook_only(self):
        result=patch(self.SOURCE);self.assertEqual(result.count(MARKER),1)
        with self.assertRaises(ValueError):patch(result)
    def test_rejects_version_drift(self):
        for s in (self.SOURCE.replace('.locals 2','.locals 0'),self.SOURCE*2,self.SOURCE.replace('.line 1','.line 2'),self.SOURCE.replace('    .line 1','    const/4 v0, 0x0\n    .line 1')):
            with self.subTest(source=s),self.assertRaises(ValueError):patch(s)

class EarlyCompatibilityPatchTests(unittest.TestCase):
    ROOT='''.method public static i()Z
    .registers 2
    invoke-static {}, Lwg/h;->h()Z
    move-result v0
    new-instance v0, Ljava/io/File;
    const-string v1, "/system/bin/su"
    return v0
.end method
'''
    CELLULAR='''.method public getUseCellularData(Landroid/content/Context;)Z
    .registers 3
    invoke-interface {p1}, Lcom/apple/android/music/playback/connectivity/ConnectivityChecker;->isCellularAvailable()Z
    const-string p1, "key_use_cellular_data"
    return p0
.end method

.method public isCellularDataEnabled()Z
    .registers 3
    .annotation build Landroidx/annotation/Keep;
    .end annotation
    const-string v0, "cellular_data_enabled"
    return p0
.end method
'''
    def test_root_gate_is_narrow(self):
        result=patch_root(self.ROOT)
        self.assertIn('const/4 v0, 0x0',result)
        self.assertNotIn('/system/bin/su',result)
    def test_root_gate_rejects_drift(self):
        with self.assertRaises(ValueError):patch_root(self.ROOT.replace('Lwg/h;->h()Z','Lx/y;->z()Z'))
    def test_cellular_patches_both_entry_points(self):
        result=patch_cellular(self.CELLULAR)
        self.assertEqual(result.count('const/4 v0, 0x1'),2)
        self.assertIn('Landroidx/annotation/Keep;',result)
    def test_cellular_rejects_partial_match(self):
        with self.assertRaises(ValueError):patch_cellular(self.CELLULAR.replace('key_use_cellular_data','other_key'))

class ScannerTests(unittest.TestCase):
    def test_artifacts(self):self.assertIn('forbidden-artifact',findings(Path('sample.apk'),b'fixture'))
    def test_binary(self):self.assertIn('binary',findings(Path('x.txt'),b'\0'))
    def test_email_without_real_identity(self):
        value=('fixture'+'@'+'qq'+'.com').encode()
        self.assertIn('personal-email',findings(Path('x.md'),value))
    def test_token_assignment(self):
        value=('password'+'='+'"'+'synthetic-only'+'"').encode()
        self.assertIn('token-assignment',findings(Path('x.txt'),value))
    def test_safe_metadata(self):self.assertEqual(findings(Path('safe.json'),b'{"tokenPresent":true,"length":244}'),[])

class AdapterUpdateTests(unittest.TestCase):
    def test_only_adapter_replaced(self):
        import io
        with tempfile.TemporaryDirectory() as td:
            r=Path(td);inner=io.BytesIO()
            with zipfile.ZipFile(inner,'w') as z:
                z.writestr('classes.dex',b'original-host')
                z.writestr('classes6.dex',b'dex\nold-fixture')
            baseline=r/'base.apk'
            with zipfile.ZipFile(baseline,'w') as z:
                z.writestr('assets/npatch/origin.apk',inner.getvalue())
                z.writestr('assets/module-fixture',b'unchanged')
            dex=r/'adapter.dex';dex.write_bytes(b'dex\nnew-fixture')
            result=replace_adapter(baseline,dex,r/'candidate.apk')
            self.assertEqual(result['inner']['changed'],['classes6.dex'])
            self.assertEqual(result['outer']['changed'],['assets/npatch/origin.apk'])
    def test_non_dex_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td);d=r/'bad.dex';d.write_bytes(b'not-a-dex')
            with self.assertRaises(ValueError):replace_adapter(r/'unused.apk',d,r/'out.apk')

if __name__=='__main__':unittest.main()
