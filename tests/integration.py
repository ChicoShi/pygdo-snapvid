import sys,tempfile,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import capture as c
with tempfile.TemporaryDirectory() as td:
 result=c._record(Path(td),5,['-f','lavfi','-i','testsrc2=size=640x360:rate=10'])
 assert Path(result['video']).stat().st_mode&0o777==0o600
 assert Path(result['gif']).stat().st_mode&0o777==0o600
 for key in ['video','gif']:
  c.run(['ffmpeg','-v','error','-i',result[key],'-f','null','-'],10)
 print(json.dumps({'synthetic':True,'desktop_captured':False,'duration':5,'video_seconds':c.probe(Path(result['video'])),'gif_seconds':c.probe(Path(result['gif'])),'decoded':True}))
