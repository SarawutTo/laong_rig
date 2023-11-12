from imp import reload
from . import core as loc
from . import rig_base
from . import naming_tools as lont

reload(loc)
reload(lont)
reload(rig_base)


class SimpleBodyRig(rig_base.Rigbase):
    pass
