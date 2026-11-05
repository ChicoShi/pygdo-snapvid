import sys,unittest,tempfile,subprocess,os
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import capture as c
class Tests(unittest.TestCase):
 def test_default_and_bounds(self):
  self.assertEqual(c.duration_seconds(),5)
  for n in [1,15]:self.assertEqual(c.duration_seconds(n),n)
  for n in [0,16,-1,True,5.5,'15',None]:
   with self.assertRaises(c.CaptureError):c.duration_seconds(n)
 def test_remote_display_rejected(self):
  for display in ['host:0',';touch /tmp/bad',':0;echo bad','']:
   with self.assertRaises(c.CaptureError):c.screen(display)
 def test_screen_geometry(self):
  with patch.object(c,'run',return_value=b'dimensions: 1920x1080 pixels'):
   self.assertEqual(c.screen(':0.0'),'1920x1080')
 def test_large_screen(self):
  with patch.object(c,'run',return_value=b'dimensions: 9000x9000 pixels'):
   with self.assertRaises(c.CaptureError):c.screen(':0')
 def test_timeout_sanitized(self):
  with patch.object(c.subprocess,'run',side_effect=subprocess.TimeoutExpired('secret',1)):
   with self.assertRaises(c.CaptureError) as e:c.run(['ffmpeg'],1)
   self.assertNotIn('secret',str(e.exception))
 def test_no_shell(self):
  with patch.object(c.subprocess,'run',return_value=subprocess.CompletedProcess([],0,b'ok')) as mocked:
   c.run(['ffmpeg','a b'],1)
   self.assertNotIn('shell',mocked.call_args.kwargs)
 def test_lock_prevents_second_capture(self):
  with tempfile.TemporaryDirectory() as td,patch.object(c,'screen',return_value='640x480'):
   with open(Path(td)/'.capture.lock','w') as lock:
    c.fcntl.flock(lock,c.fcntl.LOCK_EX|c.fcntl.LOCK_NB)
    with self.assertRaisesRegex(c.CaptureError,'bereits'):c.capture(5,td,':0')
 def test_failure_cleans_only_own_attempt(self):
  with tempfile.TemporaryDirectory() as td,patch.object(c,'screen',return_value='640x480'),patch.object(c,'_record',side_effect=c.CaptureError('fail')):
   old=Path(td)/'keep';old.write_text('old')
   with self.assertRaises(c.CaptureError):c.capture(5,td,':0')
   self.assertEqual(old.read_text(),'old');self.assertEqual(list(Path(td).glob('snapvid-*')),[])
 def test_public_output_rejected(self):
  with tempfile.TemporaryDirectory() as td,patch.object(c,'screen',return_value='640x480'):
   os.chmod(td,0o755)
   with self.assertRaisesRegex(c.CaptureError,'privat'):c.capture(5,td,':0')
 def test_quota(self):
  with tempfile.TemporaryDirectory() as td,patch.object(c,'screen',return_value='640x480'),patch.object(c,'BUDGET',1):
   with self.assertRaisesRegex(c.CaptureError,'Speicherlimit'):c.capture(5,td,':0')
if __name__=='__main__':unittest.main()
