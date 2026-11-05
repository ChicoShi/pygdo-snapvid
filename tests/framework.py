"""Run with PYTHONPATH pointing at a PyGDO checkout; no DB or desktop access."""
import importlib.util,sys,asyncio
from pathlib import Path
from unittest.mock import patch
from gdo.base.Application import Application
from gdo.base.Render import Mode
Application.mode(Mode.render_txt)
p=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('gdo.snapvid',p/'__init__.py',submodule_search_locations=[str(p)])
m=importlib.util.module_from_spec(s);sys.modules['gdo.snapvid']=m;s.loader.exec_module(m)
from gdo.snapvid.method.snapvid import snapvid
cmd=snapvid()
assert cmd.gdo_trigger()=='snapvid';assert cmd.gdo_user_permission()=='staff'
assert cmd.gdo_parameters()[0].get_value()==5
class Config:
 enabled=False
 def get_config_value(self,k):return self.enabled
 def get_config_val(self,k):return ''
config=Config()
module_patch=patch.object(snapvid,"gdo_module",return_value=config);module_patch.start()
r=asyncio.run(cmd.gdo_execute());assert 'deaktiviert' in r.get_val()
config.enabled=True
with patch.object(snapvid,'param_value',return_value=5),patch('gdo.snapvid.method.snapvid.capture',return_value={'duration':5,'video':'/test/a.mp4','gif':'/test/a.gif'}) as recording:
 r=asyncio.run(cmd.gdo_execute());assert 'Nicht versendet' in r.get_val();recording.assert_called_once_with(5,None,None)
print('PyGDO import/trigger/staff/default/disabled and enabled async adapter passed (capture mocked)')
