from imp import reload
import maya.cmds as mc
from . import core as loc
from . import rig_base
from . import rig_math
from . import naming_tools as lnt
from . import rig_global as rgb
from . import subrig

reload(loc)
reload(rgb)
reload(lnt)
reload(rig_base)
reload(rig_math)
reload(subrig)


class TorsoRig(rig_base.Rigbase):
    def __init__(
        self,
        root_tmpjnt,
        hip_tmpjnt,
        spine_tmpjnt,
        chest_tmpjnt,
        desc="",
        ctrl_par=None,
        jnt_par=None,
    ):
        super(TorsoRig, self).__init__("", desc, None)
        self.meta = self.create_meta(ctrl_par)
        self.meta.name = "Body_Rig"
        self.still = self.create_still(rgb.MainGroup.still_grp)

        root_tmpjnt = loc.Dag(root_tmpjnt)
        hip_tmpjnt = loc.Dag(hip_tmpjnt)
        spine_tmpjnt = loc.Dag(spine_tmpjnt)
        chest_tmpjnt = loc.Dag(chest_tmpjnt)

        self.meta.snap(root_tmpjnt)

        def create_ctrl(compo, idx, tmp, cp, ctrl_par, jnt_par, rot_shape):
            ctrl = self.init_dag(loc.Controller(cp), compo, idx, None, "Ctrl")
            ctrl.set_color(None, 0)
            zr, ofst = self._init_duo_grp(ctrl, compo, idx, None)
            jnt = self.init_dag(loc.Joint(), compo, idx, None, "Jnt")
            loc.parent_constraint(ctrl, jnt)
            zr.snap(tmp)

            if rot_shape:
                ctrl.rotate_shape(0, 0, 90)

            zr.set_parent(ctrl_par)
            jnt.set_parent(jnt_par)

            return zr, ofst, ctrl, jnt

        (
            self.root_zr,
            self.root_ofst,
            self.root_ctrl,
            self.root_jnt,
        ) = create_ctrl(
            "Root",
            None,
            root_tmpjnt,
            loc.cp.square,
            self.meta,
            jnt_par,
            rot_shape=False,
        )
        self.root_ctrl.set_color(14)

        (
            self.hip_zr,
            self.hip_ofst,
            self.hip_ctrl,
            self.hip_jnt,
        ) = create_ctrl(
            "Hip",
            None,
            hip_tmpjnt,
            loc.cp.n_circle,
            self.root_ctrl,
            self.root_jnt,
            rot_shape=True,
        )

        # (
        #     self.spine_zr,
        #     self.spine_ofst,
        #     self.spine_ctrl,
        #     self.spine_jnt,
        # ) = create_ctrl(
        #     "Spine",
        #     None,
        #     spine_tmpjnt,
        #     loc.cp.n_circle,
        #     self.root_ctrl,
        #     self.root_jnt,
        #     rot_shape=True,
        # )

        # (
        #     self.spinemid_zr,
        #     self.spinemid_ofst,
        #     self.spinemid_ctrl,
        #     self.spinemid_jnt,
        # ) = create_ctrl(
        #     "SpineMid",
        #     None,
        #     spine_tmpjnt,
        #     loc.cp.n_circle,
        #     self.root_ctrl,
        #     self.root_jnt,
        #     rot_shape=True,
        # )

        # (
        #     self.chest_zr,
        #     self.chest_ofst,
        #     self.chest_ctrl,
        #     self.chest_jnt,
        # ) = create_ctrl(
        #     "Chest",
        #     None,
        #     chest_tmpjnt,
        #     loc.cp.n_circle,
        #     self.spine_ctrl,
        #     self.spine_jnt,
        #     rot_shape=True,
        # )

        # mc.parentConstraint(
        #     self.spine_ctrl, self.chest_ctrl, self.spinemid_zr, mo=False
        # )
        # mc.parentConstraint(
        #     self.spine_ctrl, self.chest_ctrl, self.spinemid_zr, e=True, rm=True
        # )

        self.torso_rig = subrig.SplineFk(
            start_tmploc="Spine_Tmpjnt",
            end_tmploc="Chest_Tmpjnt",
            mod="Spine",
            ctrl_amount=3,
            jnt_amount=5,
            ctrl_par=self.root_ctrl,
            jnt_par=self.root_jnt,
        )
        for ctrl in self.torso_rig.fk_ctrls + self.torso_rig.ik_ctrls:
            ctrl.rotate_shape(0, 0, 90)

        self.chest_ctrl = self.torso_rig.fk_ctrls[-1]
        self.chest_jnt = self.torso_rig.skin_jnts[-1]

        sq_attr = self.torso_rig.fk_ctrls[0].add(ln="squash", min=0, dv=1)
        sq_jnts = self.torso_rig.skin_jnts[:-1]
        for jnt in sq_jnts:
            sq_attr >> jnt.attr("sx")
            sq_attr >> jnt.attr("sz")

        # sub = 5
        # self.nurb = loc.create_nsurface(sub, "V")
        # folroot_grp = self.init_dag(loc.Null(), "Fol", None, None, "Grp")
        # folroot_grp.snap(spine_tmpjnt)
        # folroot_jnt = self.init_dag(
        #     loc.Joint(style=2), "Fol", None, None, "Jnt"
        # )
        # folroot_jnt.snap(spine_tmpjnt)
        # folroot_jnt.set_parent(self.spine_jnt)

        # self.dtl_zrs = []
        # self.dtl_ofsts = []
        # self.dtl_ctrls = []
        # self.dtl_jnts = []
        # rb_jnts = []

        # for ix in range(sub):
        #     idx = ix + 1
        #     dis = rig_math.get_linear_base_distance(sub)
        #     param = ix * dis
        #     fol, folshp = loc.create_follicle(
        #         u=0.5, v=param, surface=self.nurb
        #     )
        #     fol.set_parent(folroot_grp)
        #     self.init_dag(fol, "Spine", idx, None, "Fol")
        #     (
        #         zr,
        #         ofst,
        #         ctrl,
        #         jnt,
        #     ) = create_ctrl(
        #         "SpineDtl",
        #         idx,
        #         fol,
        #         loc.cp.n_circle,
        #         fol,
        #         folroot_jnt,
        #         rot_shape=True,
        #     )
        #     ctrl.set_color(None, 2)
        #     self.dtl_zrs.append(zr)
        #     self.dtl_ofsts.append(ofst)
        #     self.dtl_ctrls.append(ctrl)
        #     self.dtl_jnts.append(jnt)

        #     rb_jnt = self.init_dag(loc.Joint(style=2), "Rbb", idx, None, "Jnt")
        #     rb_jnt.snap(jnt)
        #     rb_jnts.append(rb_jnt)

        # # start_loc = self.nurb.get_point_on_sfc(param_u=0.5, param_v=0)
        # # mid_loc = self.nurb.get_point_on_sfc(param_u=0.5, param_v=0.5)
        # # end_loc = self.nurb.get_point_on_sfc(param_u=0.5, param_v=1)

        # # start_jnt.set_pos((start_loc.x, start_loc.y, start_loc.z))
        # # mid_jnt.set_pos((mid_loc.x, mid_loc.y, mid_loc.z))
        # # end_jnt.set_pos((end_loc.x, end_loc.y, end_loc.z))

        # # mc.skinCluster([start_jnt, mid_jnt, end_jnt], self.nurb, mi=1)

        # # clear
        # mc.select(cl=True)
        # # start joint
        # startJnt = mc.joint(n="start_Jnt", p=(0, 0, 0))
        # startJntOffs = mc.group(startJnt, name="start_JntOffs")
        # # mid joint
        # middleJnt = mc.joint(n="middle_Jnt", p=(0, 0, 0))
        # middleJntOffs = mc.group(middleJnt, name="middle_JntOffs")
        # # end joint
        # endJnt = mc.joint(n="end_Jnt", p=(0, 0, 0))
        # endJntOffs = mc.group(endJnt, name="end_JntOffs")
        # # inbetween upper
        # upJnt = mc.joint(n="up_Jnt", p=(0, 0, 0))
        # upJntOffs = mc.group(upJnt, name="up_JntOffs")
        # lowJnt = mc.joint(n="low_Jnt", p=(0, 0, 0))
        # lowJntOffs = mc.group(lowJnt, name="low_JntOffs")

        # # Group joint
        # mc.parent(middleJntOffs, endJntOffs, w=True)
        # jntGrp = mc.group(
        #     [middleJntOffs, startJntOffs, endJntOffs, upJntOffs, lowJntOffs],
        #     n="Control_Jnt_Offs",
        # )

        # # Create deformController and grp
        # startCtr = mc.circle(
        #     c=(0, 0, 0), nr=(0, 1, 0), r=1.5, ch=0, name="start_Ctr"
        # )
        # SLEx = mc.group(name="start_ExtraOffs")
        # SLGrp = mc.group(SLEx, name="start_CtrOffs")

        # middleCtr = mc.circle(
        #     c=(0, 0, 0), nr=(0, 1, 0), r=1.5, ch=0, name="middle_Ctr"
        # )
        # MLEx = mc.group(middleCtr, name="middle_CtrExtra")
        # MLExtra = mc.group(MLEx, name="middle_OffsExtra")
        # MLGrp = mc.group(MLExtra, name="middle_CtrOffs")

        # endCtr = mc.circle(
        #     c=(0, 0, 0), nr=(0, 1, 0), r=1.5, ch=0, name="end_Ctr"
        # )
        # ELEx = mc.group(endCtr, name="end_ExtraOffs")
        # ELGrp = mc.group(ELEx, name="end_CtrOffs")

        # upCtr = mc.circle(c=(0, 0, 0), nr=(0, 1, 0), r=1, ch=0, name="up_Ctr")
        # upEx = mc.group(upCtr, name="up_ExtraOffs")
        # upGrp = mc.group(upEx, name="up_CtrOffs")

        # lowCtr = mc.circle(
        #     c=(0, 0, 0), nr=(0, 1, 0), r=1, ch=0, name="low_Ctr"
        # )
        # lowEx = mc.group(lowCtr, name="low_ExtraOffs")
        # lowGrp = mc.group(lowEx, name="low_CtrOffs")

        # # set pivot
        # mc.xform(SLGrp, t=(start_loc.x, start_loc.y, start_loc.z))
        # mc.xform(ELGrp, t=(end_loc.x, end_loc.y, end_loc.z))
        # mc.parentConstraint(upJnt, upGrp, mo=False)
        # mc.parentConstraint(upJnt, upGrp, e=True, rm=True)
        # mc.parentConstraint(lowJnt, lowGrp, mo=False)
        # mc.parentConstraint(lowJnt, lowGrp, e=True, rm=True)
        # # parent ctr to joint
        # mc.parentConstraint(startCtr, startJnt)
        # mc.parentConstraint(middleCtr, middleJnt)
        # mc.parentConstraint(endCtr, endJnt)
        # mc.parentConstraint(upCtr, upJnt)
        # mc.parentConstraint(lowCtr, lowJnt)

        # # pointCon uplow
        # mc.pointConstraint(startJnt, middleJnt, upGrp)
        # mc.pointConstraint(middleJnt, endJnt, lowGrp)

        # # constrain point controller
        # mc.pointConstraint(startCtr, endCtr, MLGrp)

        # # aim Con
        # mc.aimConstraint(
        #     endCtr[0],
        #     lowGrp,
        #     aim=(0, 1, 0),
        #     upVector=(0, 0, 1),
        #     mo=True,
        #     wut="object",
        #     wuo=endCtr[0],
        # )
        # mc.aimConstraint(
        #     middleCtr[0],
        #     upGrp,
        #     aim=(0, 1, 0),
        #     upVector=(0, 0, 1),
        #     mo=True,
        #     wut="object",
        #     wuo=middleCtr[0],
        # )

        # # bindskin
        # mc.select(cl=True)
        # mc.select(endJnt, middleJnt, startJnt, upJnt, lowJnt, self.nurb)
        # mc.SmoothBindSkin()

        # mc.parentConstraint(self.spine_ctrl, SLGrp)
        # mc.parentConstraint(self.spinemid_ctrl, MLExtra)
        # mc.parentConstraint(self.chest_ctrl, ELGrp)

        # # self.crv = self._init_dag(
        # #     loc.create_curve(
        # #         p=[start_loc.world_pos, end_loc.world_pos],
        # #         d=1,
        # #     ),
        # #     "Main",
        # #     None,
        # #     side,
        # #     "Crv",
        # # )
        # # self.crv.rebuild(s=ctrl_amount - 1, d=3, ch=False)
        # # self.crv.set_parent(self.still)

        # # self.fk_ctrls = []
        # # self.fk_ofsts = []
        # # self.fk_zrs = []
        # # self.ik_ctrls = []
        # # self.ik_ofsts = []
        # # self.ik_zrs = []
        # # self.crv_jnt = []

        # # ctrl_dis = rig_math.get_linear_base_distance(ctrl_amount)
        # # ctrl_param = [ix * ctrl_dis for ix in range(ctrl_amount)]

        # # for ix in range(ctrl_amount):
        # #     param = ix * ctrl_dis
        # #     idx = ix + 1

        # #     fk_ctrl = self._init_dag(
        # #         loc.Controller(loc.cp.n_circle), "Fk", idx, side, "Ctrl"
        # #     )
        # #     fk_ctrl.set_color(None, 0)
        # #     fk_ctrl.lhattr("s", "v")
        # #     fk_zr, fk_ofst = self._init_duo_grp(fk_ctrl, "Fk", idx, side)

        # #     ik_ctrl = self._init_dag(
        # #         loc.Controller(loc.cp.n_circle), "Ik", idx, side, "Ctrl"
        # #     )
        # #     ik_ctrl.set_color(None, 1)
        # #     ik_ctrl.scale_shape(0.8)
        # #     ik_ctrl.lhattr("s", "v")
        # #     ik_zr, ik_ofst = self._init_duo_grp(ik_ctrl, "Ik", idx, side)
        # #     ik_zr.set_parent(fk_ctrl)

        # #     jnt = self._init_dag(
        # #         loc.Joint(style=2), "IkSpline", idx, side, "RigJnt"
        # #     )
        # #     jnt.set_parent(ik_ctrl)

        # #     pos = self.crv.get_point_at_param(param)
        # #     fk_zr.set_pos((pos.x, pos.y, pos.z))

        # #     if self.fk_ctrls:
        # #         fk_zr.set_parent(self.fk_ctrls[-1])
        # #     else:
        # #         fk_zr.set_parent(self.meta)

        # #     self.fk_ctrls.append(fk_ctrl)
        # #     self.fk_ofsts.append(fk_ofst)
        # #     self.fk_zrs.append(fk_zr)
        # #     self.ik_ctrls.append(ik_ctrl)
        # #     self.ik_ofsts.append(ik_ofst)
        # #     self.ik_zrs.append(ik_zr)
        # #     self.crv_jnt.append(jnt)

        # # mc.skinCluster(self.crv_jnt, self.crv, mi=1)

        # # self.dtl_ctrls = []
        # # self.dtl_grp = self._init_dag(loc.Null(), "DtlCtrl", None, side, "Grp")
        # # self.dtl_grp.set_parent(self.meta)

        # # dtl_dis = rig_math.get_linear_base_distance(5)
        # # for ix in range(jnt_amount):
        # #     param = ix * dtl_dis
        # #     idx = ix + 1

        # #     dtl_ctrl = self._init_dag(
        # #         loc.Controller(loc.cp.cube), "Dtl", idx, side, "Ctrl"
        # #     )
        # #     dtl_ctrl.lhattr("s", "v")
        # #     dtl_ctrl.set_color(None, 2)
        # #     dtl_zr, dtl_ofst = self._init_duo_grp(dtl_ctrl, "Dtl", idx, side)
        # #     dtl_zr.set_parent(self.dtl_grp)
        # #     dtl_zr.attr("inheritsTransform").v = False

        # #     dtl_ctrl.scale_shape(0.6)
        # #     dtl_jnt = self._init_dag(
        # #         loc.Joint(style=0), "Dtl", idx, side, "Jnt"
        # #     )

        # #     loc.parent_constraint(dtl_ctrl, dtl_jnt)

        # #     mop = self._init_node(
        # #         loc.create_node("motionPath"), "Dtl", idx, side, "Mop"
        # #     )
        # #     # Up Vector
        # #     up_vec = self._init_node(
        # #         loc.create_node("vectorProduct"),
        # #         "DtlUpVec",
        # #         idx,
        # #         side,
        # #         "VecProd",
        # #     )
        # #     up_vec.attr("operation").v = 3
        # #     up_vec.attr("i1z").v = 1
        # #     ctrl_id = rig_math.get_closest_section(param, ctrl_param)
        # #     self.fk_ctrls[ctrl_id].attr("worldMatrix") >> up_vec.attr("matrix")

        # #     self.crv.attr("worldSpace") >> mop.attr("geometryPath")
        # #     mop.attr("uValue").v = param
        # #     up_vec.attr("output") >> mop.attr("worldUpVector")

        # #     mop.attr("ac") >> dtl_zr.attr("t")
        # #     mop.attr("r") >> dtl_zr.attr("r")

        # #     if self.dtl_ctrls:
        # #         dtl_jnt.set_parent(self.skin_jnts[-1])
        # #     else:
        # #         dtl_jnt.set_parent(jnt_par)

        # #     self.dtl_ctrls.append(dtl_ctrl)
        # #     self.skin_jnts.append(dtl_jnt)

        # # self.control_parent = self.fk_ctrls[-1]
        # # self.joint_parent = self.skin_jnts[-1]
