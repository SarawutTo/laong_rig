from . import core as amc
from . import rig_base
from . import naming_tools as alnt


class PointRig(rig_base.Rigbase):
    def __init__(self, tmp_jnts, mod, desc, meta_parent, still_parent):
        super(self, PointRig).__init__(mod, desc)

        self.meta = self.create_meta(meta_parent)
        self.still = self.create_still(still_parent)

        self.zrs = []
        self.ofsts = []
        self.ctrls = []
        self.jnts = []

        for tmp_jnt in tmp_jnts:
            name, idx, side, _ = alnt.deconstruct(tmp_jnt)
            ctrl = self._init_dag(
                amc.Controller(amc.cp.n_circle), name, idx, side, "Ctrl"
            )
            ofst = self._init_dag(amc.group(ctrl), name, idx, side, "Ofst")
            zr = self._init_dag(amc.group(ofst), name, idx, side, "Zr")
