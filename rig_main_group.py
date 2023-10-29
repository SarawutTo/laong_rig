from imp import reload
from . import rig_base
from . import core as loc
from . import naming_tools as lont

reload(loc)
reload(lont)
reload(rig_base)


class MainGroup(object):
    def __init__(self, asset_name="Asset"):
        """Create Main Group for rig
        Args:
            asset_name(str):
        """
        # Create Transform
        self.main_grp = loc.Null(n="{}_Rig".format(asset_name))
        self.still_grp = loc.Null(n="Still_Grp")
        self.rig_grp = loc.Null(n="Rig_Grp")
        self.ctrl_grp = loc.Null(n="Control_Grp")
        self.jnt_grp = loc.Null(n="Joint_Grp")
        self.world_ctrl = loc.Controller(loc.cp.square, n="Global_Ctrl")
        self.offset_ctrl = loc.Controller(loc.cp.four_arrow, n="Offset_Ctrl")

        # Parent
        self.rig_grp.set_parent(self.main_grp)
        self.ctrl_grp.set_parent(self.offset_ctrl)
        self.jnt_grp.set_parent(self.main_grp)
        self.still_grp.set_parent(self.main_grp)
        self.world_ctrl.set_parent(self.rig_grp)
        self.offset_ctrl.set_parent(self.world_ctrl)
