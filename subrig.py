from imp import reload
from . import core as loc
from . import rig_base
from . import naming_tools as lont

reload(loc)
reload(lont)
reload(rig_base)


class PointRig(rig_base.Rigbase):
    def __init__(
        self,
        tmp_jnt,
        mod,
        desc="",
        idx="",
        side="",
        shape=loc.cp.n_circle,
        ctrl_par=None,
        jnt_par=None,
    ):
        super(PointRig, self).__init__(mod, desc, side)
        self.meta = self.create_meta(ctrl_par)

        # Cast
        tmp_jnt = loc.Dag(tmp_jnt)

        self.ctrl = self._init_dag(
            loc.Controller(shape), "", idx, side, "Ctrl"
        )
        self.jnt = self._init_dag(loc.Joint(), "", idx, side, "Jnt")
        self.zr, self.ofst = self._init_duo_grp(self.ctrl, "", idx, side)
        loc.parent_constraint(self.ctrl, self.jnt)
        self.zr.snap(tmp_jnt)
        self.zr.set_parent(self.meta)

        if jnt_par:
            self.jnt.set_parent(jnt_par)


class FkRig(rig_base.Rigbase):
    def __init__(
        self,
        tmp_jnts,
        jnt_name,
        mod,
        desc="",
        ctrl_par=None,
        jnt_par=None,
    ):
        super(FkRig, self).__init__(mod, desc)
        self.meta = self.create_meta(ctrl_par)

        # Cast
        tmp_jnts = loc.cast_dags(tmp_jnts)

        self.zrs = []
        self.ofsts = []
        self.ctrls = []
        self.jnts = []

        for tmp_jnt, name in zip(tmp_jnts, jnt_name):
            # Fix This use enumeate
            _, idx, side, _ = lont.deconstruct(tmp_jnt.name)
            ctrl = self._init_dag(
                loc.Controller(loc.cp.n_circle), name, idx, side, "Ctrl"
            )
            jnt = self._init_dag(loc.Joint(), name, idx, side, "Jnt")
            zr, ofst = self._init_duo_grp(ctrl, name, idx, side)
            loc.parent_constraint(ctrl, jnt)
            zr.snap(tmp_jnt)

            if self.ctrls:
                zr.set_parent(self.ctrls[-1])
                jnt.set_parent(self.jnts[-1])
            else:
                zr.set_parent(self.meta)
                if jnt_par:
                    jnt.set_parent(jnt_par)

            self.zrs.append(zr)
            self.ofsts.append(ofst)
            self.jnts.append(jnt)
            self.ctrls.append(ctrl)
