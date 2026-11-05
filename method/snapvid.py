import asyncio
from gdo.base.Method import Method
from gdo.core.GDT_Int import GDT_Int
from gdo.core.GDT_String import GDT_String
from gdo.snapvid.capture import capture, CaptureError

class snapvid(Method):
    @classmethod
    def gdo_trigger(cls): return 'snapvid'
    def gdo_user_permission(self): return 'staff'
    def gdo_transactional(self): return False
    def gdo_parameters(self):
        return [GDT_Int('duration').not_null().initial('5').min(1).max(15)]
    async def gdo_execute(self):
        module=self.gdo_module()
        if not module.get_config_value('snapvid_enabled'):
            return GDT_String('result').val('Snapvid ist deaktiviert.')
        try:
            result=await asyncio.to_thread(capture,self.param_value('duration'),
                module.get_config_val('snapvid_output') or None,
                module.get_config_val('snapvid_display') or None)
        except CaptureError as exc:
            return GDT_String('result').val('Snapvid: '+str(exc))
        return GDT_String('result').val(f"Lokal erstellt ({result['duration']} s): MP4 {result['video']} | GIF {result['gif']}. Nicht versendet.")
