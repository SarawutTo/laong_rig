from imp import reload
from . import core as loc
from . import rig_base
from . import naming_tools as lont

reload(loc)
reload(lont)
reload(rig_base)


class PointRig(rig_base.Rigbase):
    def __init__(self, tmp_jnts, mod, desc, meta_par, skin_par):
        super(PointRig, self).__init__(mod, desc)
        self.meta = self.create_meta(meta_par)

        # Cast
        tmp_jnts = loc.cast_dags(tmp_jnts)
        self.zrs = []
        self.exs = []
        self.ofsts = []
        self.ctrls = []
        self.jnts = []

        for tmp_jnt in tmp_jnts:
            name, idx, side, _ = lont.deconstruct(tmp_jnt.name)
            ctrl = self._init_dag(
                loc.Controller(loc.cp.n_circle), name, idx, side, "Ctrl"
            )
            jnt = self._init_dag(loc.Joint(), name, idx, side, "Jnt")
            zr, ex, ofst = self._init_quad_grp(ctrl, name, idx, side)
            loc.parent_constraint(ctrl, jnt)
            zr.snap(tmp_jnt)

            self.zrs.append(zr)
            self.exs.append(ex)
            self.ofsts.append(ofst)
            self.jnts.append(jnt)
            self.ctrls.append(ctrl)
