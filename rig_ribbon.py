from imp import reload
from . import core as loc
from . import rig_base
from . import naming_tools as lnt
import maya.cmds as mc


reload(loc)
reload(lnt)
reload(rig_base)


class TailRig(rig_base.Rigbase):
    def __init__(
        self,
        start_loc,
        end_loc,
        ctrl_amount,
        jnt_amount,
        mod,
        desc="",
        side=None,
        jnt_par=None,
        ctrl_par=None,
        still_par=None,
    ):
        super(TailRig, self).__init__(mod, desc)
        self.meta = self.create_meta(ctrl_par)
        self.still = self.create_still(still_par)

        start_pos = mc.xform(start_loc, t=True, q=True, ws=True)
        end_pos = mc.xform(end_loc, t=True, q=True, ws=True)

        # Create Curve
        curve = loc.Curve(mc.curve(p=(start_pos, end_pos), d=1))
        mc.rebuildCurve(curve, s=ctrl_amount + 1, kr=0, ch=False)

        # Aim

        # Create Main Controller
        self.main_zrs = []
        self.main_ofsts = []
        self.main_ctrls = []
        self.main_jnts = []

        ctrl_dis = 1.00 / (ctrl_amount - 1)
        for ix in range(ctrl_amount):
            idx = ix + 1
            point = curve.get_point_at_param(ix * ctrl_dis)

            ctrl = self.init_dag(
                loc.Controller(loc.cp.n_circle), "Fk", idx, side, "Ctrl"
            )
            zr, ofst = self._init_duo_grp(ctrl, "Fk", idx, side)
            zr.set_pos((point.x, point.y, point.z))

            jnt = self.init_dag(loc.Joint(), "Fk", idx, side, "Jnt")

            loc.parent_constraint(ctrl, jnt)

            if self.main_ctrls:
                zr.set_parent(self.main_ctrls[-1])
                jnt.set_parent(self.main_jnts[-1])
            else:
                zr.set_parent(self.meta)
                jnt.set_parent(self.still)

            self.main_zrs.append(zr)
            self.main_ofsts.append(ofst)
            self.main_ctrls.append(ctrl)
            self.main_jnts.append(jnt)

        mc.skinCluster(
            self.main_jnts,
            curve,
            n=lnt.construct(
                "{}{}Crv".format(mod, desc), None, side, "SkinCluster"
            ),
        )

        # Create Dtl Ctrl
