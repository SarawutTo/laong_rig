from imp import reload
import maya.cmds as mc
from . import core as loc
from . import rig_base
from . import rig_math
from . import naming_tools as lnt
from . import rig_global as rgb
from . import utils as lu

reload(loc)
reload(rgb)
reload(lnt)
reload(rig_base)
reload(rig_math)


class PointRig(rig_base.Rigbase):
    def __init__(
        self,
        tmp_jnt,
        mod,
        desc="",
        idx="",
        side="",
        shape=loc.cp.n_circle,
        color_tone=0,
        space=None,
        ctrl_par=None,
        jnt_par=None,
    ):
        super(PointRig, self).__init__(mod, desc, side)
        self.meta = self.create_meta(ctrl_par)

        # Cast
        tmp_jnt = loc.Dag(tmp_jnt)

        self.ctrl = self.init_dag(loc.Controller(shape), "", idx, side, "Ctrl")
        self.ctrl.lhattr("v")
        self.ctrl.set_color(None, color_tone)
        self.jnt = self.init_dag(loc.Joint(), "", idx, side, "Jnt")
        self.zr, self.ofst = self._init_duo_grp(self.ctrl, "", idx, side)
        loc.parent_constraint(self.ctrl, self.jnt)
        loc.scale_constraint(self.ctrl, self.jnt)
        self.zr.snap(tmp_jnt)
        self.zr.set_parent(self.meta)

        if jnt_par:
            self.jnt.set_parent(jnt_par)

        if space:
            self.space = self.create_space(self.meta)
            self.create_space_switch(space, self.zr, self.ctrl, self.space)


class FkRig(rig_base.Rigbase):
    def __init__(
        self,
        tmp_jnts,
        mod,
        desc="",
        shape=loc.cp.n_circle,
        side=None,
        dtl_ctrl=False,
        ctrl_par=None,
        jnt_par=None,
    ):
        super(FkRig, self).__init__(mod, desc, side)
        self.meta = self.create_meta(ctrl_par)

        # Cast
        tmp_jnts = loc.to_dags(tmp_jnts)

        self.zrs = []
        self.ofsts = []
        self.ctrls = []
        self.dtls = []
        self.jnts = []

        for ix, tmp_jnt in enumerate(tmp_jnts):
            idx = ix + 1
            ctrl = self.init_dag(loc.Controller(shape), "", idx, side, "Ctrl")
            ctrl.set_color(None, 0)
            zr, ofst = self._init_duo_grp(ctrl, "", idx, side)
            jnt = self.init_dag(loc.Joint(at=tmp_jnt), "", idx, side, "Jnt")

            if dtl_ctrl:
                dtl = self.init_dag(
                    loc.Controller(shape),
                    "{}Dtl".format(""),
                    idx,
                    side,
                    "Ctrl",
                )
                dtl.scale_shape(0.8)
                dtl.set_parent(ctrl)
                dtl.set_color(None, 1)
                loc.parent_constraint(dtl, jnt)
            else:
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


class SplineIK(rig_base.Rigbase):
    def __init__(
        self,
        start_tmploc,
        end_tmploc,
        mod,
        ctrl_amount,
        jnt_amount,
        desc="",
        side=None,
        ctrl_par=None,
        jnt_par=None,
    ):
        super(SplineIK, self).__init__(mod, desc, side)
        self.meta = self.create_meta(ctrl_par)

        start_loc = loc.Dag(start_tmploc)
        end_loc = loc.Dag(end_tmploc)

        self.spline_crv = loc.create_curve(
            p=[start_loc.world_pos, end_loc.world_pos], d=1
        )
        self.spline_crv.rebuild(s=jnt_amount + 1, d=3, ch=False)


class SplineFk(rig_base.Rigbase):
    def __init__(
        self,
        start_tmploc,
        end_tmploc,
        mod,
        ctrl_amount,
        jnt_amount,
        desc="",
        side=None,
        ctrl_par=None,
        jnt_par=None,
    ):
        super(SplineFk, self).__init__(mod, desc, side)
        self.meta = self.create_meta(ctrl_par)
        self.still = self.create_still(rgb.MainGroup.still_grp)

        start_loc = loc.Dag(start_tmploc)
        end_loc = loc.Dag(end_tmploc)

        self.meta.snap(start_loc)
        self.crv = self.init_dag(
            loc.create_curve(
                p=[start_loc.world_pos, end_loc.world_pos],
                d=1,
            ),
            "Main",
            None,
            side,
            "Crv",
        )
        self.crv.rebuild(s=ctrl_amount - 1, d=3, ch=False)
        self.crv.set_parent(self.still)

        self.fk_ctrls = []
        self.fk_ofsts = []
        self.fk_zrs = []
        self.ik_ctrls = []
        self.ik_ofsts = []
        self.ik_zrs = []
        self.crv_jnt = []

        ctrl_dis = rig_math.get_linear_base_distance(ctrl_amount)
        ctrl_param = [ix * ctrl_dis for ix in range(ctrl_amount)]

        for ix in range(ctrl_amount):
            param = ix * ctrl_dis
            idx = ix + 1

            fk_ctrl = self.init_dag(
                loc.Controller(loc.cp.n_circle), "Fk", idx, side, "Ctrl"
            )
            fk_ctrl.set_color(None, 0)
            fk_ctrl.lhattr("s", "v")
            fk_zr, fk_ofst = self._init_duo_grp(fk_ctrl, "Fk", idx, side)

            ik_ctrl = self.init_dag(
                loc.Controller(loc.cp.n_circle), "Ik", idx, side, "Ctrl"
            )
            ik_ctrl.set_color(None, 1)
            ik_ctrl.scale_shape(0.8)
            ik_ctrl.lhattr("s", "r", "v")
            ik_zr, ik_ofst = self._init_duo_grp(ik_ctrl, "Ik", idx, side)
            ik_zr.set_parent(fk_ctrl)

            jnt = self.init_dag(
                loc.Joint(style=2), "IkSpline", idx, side, "RigJnt"
            )
            jnt.set_parent(ik_ctrl)

            pos = self.crv.get_point_at_param(param)
            fk_zr.set_pos((pos.x, pos.y, pos.z))

            if self.fk_ctrls:
                fk_zr.set_parent(self.fk_ctrls[-1])
            else:
                fk_zr.set_parent(self.meta)

            self.fk_ctrls.append(fk_ctrl)
            self.fk_ofsts.append(fk_ofst)
            self.fk_zrs.append(fk_zr)
            self.ik_ctrls.append(ik_ctrl)
            self.ik_ofsts.append(ik_ofst)
            self.ik_zrs.append(ik_zr)
            self.crv_jnt.append(jnt)

        mc.skinCluster(self.crv_jnt, self.crv, mi=1)

        self.dtl_ctrls = []
        self.dtl_grp = self.init_dag(loc.Null(), "DtlCtrl", None, side, "Grp")
        self.dtl_grp.set_parent(self.meta)

        dtl_dis = rig_math.get_linear_base_distance(jnt_amount)
        for ix in range(jnt_amount):
            param = ix * dtl_dis
            idx = ix + 1

            dtl_ctrl = self.init_dag(
                loc.Controller(loc.cp.cube), "Dtl", idx, side, "Ctrl"
            )
            dtl_ctrl.lhattr("s", "v")
            dtl_ctrl.set_color(None, 2)
            dtl_zr, dtl_ofst = self._init_duo_grp(dtl_ctrl, "Dtl", idx, side)
            dtl_zr.set_parent(self.dtl_grp)
            dtl_zr.attr("inheritsTransform").v = False

            dtl_ctrl.scale_shape(0.6)
            dtl_jnt = self.init_dag(
                loc.Joint(style=0), "Dtl", idx, side, "Jnt"
            )

            loc.parent_constraint(dtl_ctrl, dtl_jnt)

            mop = self.init_node(
                loc.create_node("motionPath"), "Dtl", idx, side, "Mop"
            )
            # Up Vector
            up_vec = self.init_node(
                loc.create_node("vectorProduct"),
                "DtlUpVec",
                idx,
                side,
                "VecProd",
            )
            up_vec.attr("operation").v = 3
            up_vec.attr("i1z").v = 1
            ctrl_id = rig_math.get_closest_section(param, ctrl_param)
            self.fk_ctrls[ctrl_id].attr("worldMatrix") >> up_vec.attr("matrix")

            self.crv.attr("worldSpace") >> mop.attr("geometryPath")
            mop.attr("uValue").v = param
            up_vec.attr("output") >> mop.attr("worldUpVector")

            mop.attr("ac") >> dtl_zr.attr("t")
            mop.attr("r") >> dtl_zr.attr("r")

            if self.dtl_ctrls:
                dtl_jnt.set_parent(self.skin_jnts[-1])
            else:
                dtl_jnt.set_parent(jnt_par)

            self.dtl_ctrls.append(dtl_ctrl)
            self.skin_jnts.append(dtl_jnt)

        self.control_parent = self.fk_ctrls[-1]
        self.joint_parent = self.skin_jnts[-1]

        # Vis Attr
        lu.add_divide_attr(self.fk_ctrls[0], "detail")
        dtl_vis = self.fk_ctrls[0].add(
            ln="detailVis", min=0, max=1, dv=0, at="short"
        )
        dtl_vis >> self.dtl_grp.attr("v")
