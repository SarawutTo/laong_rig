from imp import reload
from . import rig_base
from . import core as loc
from . import naming_tools as lont
from . import rig_global as rgb

import maya.cmds as mc

reload(rgb)
reload(loc)
reload(lont)
reload(rig_base)


class MainGroup(object):
    def __init__(self, asset_name: str = "Asset"):
        """Create Main Group for rig
        Args:
            asset_name(str):
        """
        # Create Transform
        self.main_grp = loc.Null(n="{}_Rig".format(asset_name))
        self.still_grp = loc.Null(n=rgb.MainGroup.still_grp)
        self.rig_grp = loc.Null(n=rgb.MainGroup.rig_grp)
        self.ctrl_grp = loc.Null(n=rgb.MainGroup.ctrl_grp)
        self.worldspace_grp = loc.Null(n=rgb.MainGroup.worldspace_grp)
        self.jnt_grp = loc.Null(n=rgb.MainGroup.joint_grp)
        self.world_ctrl = loc.Controller(
            loc.cp.square, n=rgb.MainGroup.global_ctrl
        )
        self.offset_ctrl = loc.Controller(
            loc.cp.offset_ctrl, n=rgb.MainGroup.offset_grp
        )

        self.world_ctrl.set_ctrl_color(rgb.Color.black)
        self.offset_ctrl.set_ctrl_color(rgb.Color.grey)

        # Parent
        self.rig_grp.set_parent(self.main_grp)
        self.ctrl_grp.set_parent(self.offset_ctrl)
        self.jnt_grp.set_parent(self.main_grp)
        self.still_grp.set_parent(self.main_grp)
        self.world_ctrl.set_parent(self.rig_grp)
        self.offset_ctrl.set_parent(self.world_ctrl)
        self.worldspace_grp.set_parent(self.offset_ctrl)

        # Default set
        self.skin_set = mc.sets(n=rgb.MainGroup.skin_set, em=True)
