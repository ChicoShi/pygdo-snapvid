from gdo.base.GDO_Module import GDO_Module
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_String import GDT_String

class module_snapvid(GDO_Module):
    def gdo_module_config(self):
        return [GDT_Bool('snapvid_enabled').not_null().initial('0'),
                GDT_String('snapvid_display').initial(''),
                GDT_String('snapvid_output').initial('')]
