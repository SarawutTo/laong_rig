from imp import reload
import maya.cmds as mc
from . import utils
from . import vector
from . import rig_base
from . import core as loc
from . import rig_global as rgb
from . import naming_tools as lnt


reload(loc)
reload(lnt)
reload(utils)
reload(vector)
reload(rig_base)

EE_INDEX = 2


class IkFkLegRig(rig_base.Rigbase):
    def __init__(
        self,
        upleg_tmpjnt,
        lowleg_tmpjnt,
        ankle_tmpjnt,
        ball_tmpjnt,
        toe_tmpjnt,
        heel_tmpjnt,
        in_tmpjnt,
        out_tmpjnt,
        side,
        desc="",
        double_jnt=False,
        ik_polevector_amp=1,
        ikroot_space=None,
        ik_space=None,
        fk_par=None,
        jnt_par=None,
        ctrl_par=None,
        still_par=None,
    ):
        super(IkFkLegRig, self).__init__("Leg", desc, side)
        self.meta = self.create_meta(ctrl_par)
        self.still = self.create_still(still_par)
        self.space = self.create_space(self.meta)

        upleg_tmpjnt = loc.Dag(upleg_tmpjnt)
        lowleg_tmpjnt = loc.Dag(lowleg_tmpjnt)
        ankle_tmpjnt = loc.Dag(ankle_tmpjnt)
        ball_tmpjnt = loc.Dag(ball_tmpjnt)
        heel_tmpjnt = loc.Dag(heel_tmpjnt)
        in_tmpjnt = loc.Dag(in_tmpjnt)
        out_tmpjnt = loc.Dag(out_tmpjnt)

        # Cast
        if double_jnt:
            compo_names = [
                "Up",
                "Double",
                "Knee",
                "Low",
                "Ankle",
                "Ball",
                "Toe",
            ]
            up_vec, low_vec = utils.get_double_jnt_pos(
                upleg_tmpjnt, lowleg_tmpjnt, ankle_tmpjnt, double_jnt
            )

            double_tmpjnt = self.init_dag(
                loc.Joint(), "Double", None, side, "TmpJnt"
            )
            double_tmpjnt.set_pos((up_vec.x, up_vec.y, up_vec.z))
            double_tmpjnt.snap_rot(upleg_tmpjnt)

            kneedb_tmpjnt = self.init_dag(
                loc.Joint(), "KneeDb", None, side, "TmpJnt"
            )

            kneedb_tmpjnt.set_pos((low_vec.x, low_vec.y, low_vec.z))
            kneedb_tmpjnt.snap_rot(lowleg_tmpjnt)

            double_tmpjnt.set_parent(upleg_tmpjnt)
            kneedb_tmpjnt.set_parent(lowleg_tmpjnt)

            leg_tmpjnts = [
                upleg_tmpjnt,
                double_tmpjnt,
                lowleg_tmpjnt,
                kneedb_tmpjnt,
                ankle_tmpjnt,
                ball_tmpjnt,
                toe_tmpjnt,
            ]

        else:
            compo_names = [
                "Up",
                "Low",
                "Ankle",
                "Ball",
                "Toe",
            ]
            leg_tmpjnts = [
                upleg_tmpjnt,
                lowleg_tmpjnt,
                ankle_tmpjnt,
                ball_tmpjnt,
                toe_tmpjnt,
            ]

        jnt_grp = loc.Null(lnt.construct("LegJnt", None, side, "Grp"))
        jnt_grp.set_parent(self.still)
        if ctrl_par:
            loc.parent_constraint(ctrl_par, jnt_grp)
            loc.scale_constraint(ctrl_par, jnt_grp)

        # Create Joint
        self.fk_jnts = []
        self.ik_jnts = []  # self.ik_jnts: list[loc.Joint] = []
        self.leg_jnts = []
        self.par_cons = []

        for name, tmpjnt in zip(compo_names, leg_tmpjnts):
            fkjnt = self.init_dag(
                loc.Joint(tmpjnt, 2),
                "Fk{}".format(name),
                None,
                side,
                "RigJnt",
            )
            ikjnt = self.init_dag(
                loc.Joint(tmpjnt, 2),
                "Ik{}".format(name),
                None,
                side,
                "RigJnt",
            )
            armjnt = self.init_dag(loc.Joint(tmpjnt), name, None, side, "Jnt")

            con = loc.parent_constraint(ikjnt, fkjnt, armjnt)

            if self.fk_jnts:
                fkjnt.set_parent(self.fk_jnts[-1])
                ikjnt.set_parent(self.ik_jnts[-1])
                armjnt.set_parent(self.leg_jnts[-1])

            else:
                fkjnt.set_parent(jnt_grp)
                ikjnt.set_parent(jnt_grp)
                if jnt_par:
                    armjnt.set_parent(jnt_par)

            self.fk_jnts.append(fkjnt)
            self.ik_jnts.append(ikjnt)
            self.leg_jnts.append(armjnt)
            self.par_cons.append(con)

        pref_angle = 90 if self.side == rgb.Side.right else -90

        if double_jnt:
            self.ik_jnts[-2].attr("preferredAngleY").v = pref_angle / 3
            self.ik_jnts[-3].attr("preferredAngleY").v = pref_angle / 3
            self.ik_jnts[-4].attr("preferredAngleY").v = pref_angle / 3
        else:
            self.ik_jnts[-2].attr("preferredAngleY").v = pref_angle

        self.fk_zrs = []
        self.fk_ofsts = []
        self.fk_ctrls = []

        # Fk
        for ix, (name, jnt) in enumerate(zip(compo_names, self.fk_jnts)):
            shape = loc.cp.n_circle
            if ix == 0:
                shape = loc.cp.half_cy
            ctrl = self.init_dag(
                loc.Controller(shape), name, None, side, "Ctrl"
            )
            ctrl.lhattr("s", "v")
            zr, ofst = self._init_duo_grp(ctrl, name, None, side)
            zr.snap(jnt)
            loc.parent_constraint(ctrl, jnt)

            if self.fk_ctrls:
                zr.set_parent(self.fk_ctrls[-1])
            else:
                zr.set_parent(self.meta)

            self.fk_zrs.append(zr)
            self.fk_ofsts.append(ofst)
            self.fk_ctrls.append(ctrl)

        # Fk Space
        if fk_par:
            # Create Grp
            fk_spacegrp = self.init_dag(
                loc.Null(), "FkSpace", None, self.side, "Spc"
            )
            fk_spacepiv = self.init_dag(
                loc.Group(fk_spacegrp), "FkSpace", None, self.side, "Piv"
            )
            fk_spacepiv.snap(self.fk_jnts[0])
            fk_spacepiv.set_parent(self.space)

            loc.parent_constraint(fk_par, fk_spacepiv, mo=True)
            # Parent to root
            loc.point_constraint(fk_spacegrp, self.fk_zrs[0])
            fkori_con = loc.orient_constraint(fk_spacegrp, self.fk_zrs[0])

            name, _, _, _ = lnt.deconstruct(fk_par)
            utils.add_divide_attr(self.fk_ctrls[0], "spaceControl")
            spacefk_attr = self.fk_ctrls[0].add(
                ln="space",
                en="World Orient:{}".format(name),
                at="enum",
                k=True,
                dv=1,
            )

            # Set Constraint weight
            spacefk_attr >> fkori_con.attr("w0")

        # Ik
        ik_handle = loc.Dag(
            mc.ikHandle(
                sj=self.ik_jnts[0],
                ee=self.ik_jnts[EE_INDEX],
                sol="ikRPsolver",
                n=lnt.construct("Ik", None, self.side, "IkHandle"),
            )[0]
        )
        ik_handle.hide = True

        ball_handle = loc.Dag(
            mc.ikHandle(
                sj=self.ik_jnts[EE_INDEX],
                ee=self.ik_jnts[EE_INDEX + 1],
                sol="ikSCsolver",
                n=lnt.construct("BallIk", None, self.side, "IkHandle"),
            )[0]
        )
        ball_handle.hide = True

        toe_handle = loc.Dag(
            mc.ikHandle(
                sj=self.ik_jnts[EE_INDEX + 1],
                ee=self.ik_jnts[EE_INDEX + 2],
                sol="ikSCsolver",
                n=lnt.construct("ToeIk", None, self.side, "IkHandle"),
            )[0]
        )
        toe_handle.hide = True

        # Ik Root Ctrl
        self.ik_root_ctrl = self.init_dag(
            loc.Controller(loc.cp.cube),
            "IkUp",
            None,
            self.side,
            "Ctrl",
        )
        self.ik_root_ctrl.lhattr("r", "s", "v")
        self.ik_root_zr, self.ik_root_ofst = self._init_duo_grp(
            self.ik_root_ctrl,
            "IkUp",
            None,
            self.side,
        )
        self.ik_root_zr.snap(self.ik_jnts[0])
        loc.point_constraint(self.ik_root_ctrl, self.ik_jnts[0])
        self.ik_root_zr.set_parent(self.meta)

        # Ik Ctrl
        self.ik_ctrl = self.init_dag(
            loc.Controller(loc.cp.cube), "Ik", None, self.side, "Ctrl"
        )
        self.ik_ctrl.lhattr("s", "v")

        self.ik_zr, self.ik_ofst = self._init_duo_grp(
            self.ik_ctrl,
            "Ik",
            None,
            self.side,
        )
        self.ik_zr.snap(self.ik_jnts[EE_INDEX])
        self.ik_zr.set_parent(self.meta)

        # Roll
        self.ankle_roll = self.init_dag(
            loc.Null(), "AnkleRoll", None, self.side, "Grp"
        )
        self.ball_roll = self.init_dag(
            loc.Group(self.ankle_roll), "BallRoll", None, self.side, "Grp"
        )
        self.ball_roll_zr = self.init_dag(
            loc.Group(self.ball_roll), "BallRoll", None, self.side, "Zr"
        )
        self.ankle_rot = self.init_dag(
            loc.Group(self.ball_roll_zr), "AnkleRot", None, self.side, "Grp"
        )
        self.ankle_rot_zr = self.init_dag(
            loc.Group(self.ankle_rot), "AnkleRot", None, self.side, "Zr"
        )
        self.toe_roll = self.init_dag(
            loc.Group(self.ankle_rot_zr), "ToeRoll", None, self.side, "Grp"
        )
        self.toe_tap = self.init_dag(
            loc.Null(), "ToeTap", None, self.side, "Grp"
        )
        self.toe_lift_zr = self.init_dag(
            loc.Group(self.toe_tap), "ToeTap", None, self.side, "Zr"
        )
        self.toe_roll_zr = self.init_dag(
            loc.Group(self.toe_roll), "ToeRoll", None, self.side, "Zr"
        )
        self.heel_roll = self.init_dag(
            loc.Group(self.toe_roll_zr), "HeelRoll", None, self.side, "Grp"
        )
        self.heel_lift = self.init_dag(
            loc.Group(self.heel_roll), "HeelLift", None, self.side, "Grp"
        )
        self.heel_roll_zr = self.init_dag(
            loc.Group(self.heel_lift), "HeelRoll", None, self.side, "Zr"
        )
        self.foot_roll = self.init_dag(
            loc.Group(self.heel_roll_zr), "FootRoll", None, self.side, "Grp"
        )
        self.foot_roll_zr = self.init_dag(
            loc.Group(self.foot_roll), "FootRoll", None, self.side, "Zr"
        )
        self.out_roll = self.init_dag(
            loc.Group(self.foot_roll_zr), "OutRoll", None, self.side, "Grp"
        )
        self.in_roll = self.init_dag(
            loc.Group(self.out_roll), "InRoll", None, self.side, "Grp"
        )
        self.roll_zr = self.init_dag(
            loc.Group(self.in_roll), "Roll", None, self.side, "Zr"
        )

        # Snap
        self.roll_zr.snap(in_tmpjnt)
        self.in_roll.snap(in_tmpjnt)
        self.out_roll.snap(out_tmpjnt)
        self.foot_roll_zr.snap(ball_tmpjnt)
        self.heel_roll_zr.snap(heel_tmpjnt)
        self.toe_roll_zr.snap(toe_tmpjnt)
        self.toe_lift_zr.snap(ball_tmpjnt)
        self.ankle_rot_zr.snap(ankle_tmpjnt)
        self.ball_roll_zr.snap(ball_tmpjnt)
        self.ankle_roll.snap(ankle_tmpjnt)

        # Set-Parent
        self.roll_zr.set_parent(self.ik_ctrl)
        self.toe_lift_zr.set_parent(self.ankle_rot)

        # Set-Parent Ik Handle
        ik_handle.set_parent(self.ankle_roll)
        ball_handle.set_parent(self.ball_roll)
        toe_handle.set_parent(self.toe_tap)

        self.ik_pole_ctrl = self.init_dag(
            loc.Controller(loc.cp.locator),
            "IkPoleVector",
            None,
            self.side,
            "Ctrl",
        )
        self.ik_pole_zr, self.ik_pole_ofst = self._init_duo_grp(
            self.ik_pole_ctrl,
            "IkPoleVector",
            None,
            self.side,
        )
        pole_pos = vector.get_ik_pole_vector(
            root=self.ik_jnts[0],
            mid=lowleg_tmpjnt,
            end=self.ik_jnts[EE_INDEX],
            amp=ik_polevector_amp,
        )
        self.ik_pole_zr.set_pos((pole_pos.x, pole_pos.y, pole_pos.z))
        self.ik_pole_ctrl.lhattr("r", "s")
        mc.poleVectorConstraint(self.ik_pole_ctrl, ik_handle)
        mc.orientConstraint(self.ik_ctrl, self.ik_jnts[EE_INDEX])

        self.ik_pole_zr.set_parent(self.meta)

        # Stretch Rig - Auto Stretch
        utils.add_divide_attr(self.ik_ctrl, "stretch")
        self.ik_ctrl.add(ln="autoStretch", k=True, min=0, max=1, dv=1)

        def create_position_grp(target="", compo="A"):
            post_grp = self.init_dag(
                loc.Null(), "IkStretch{}".format(compo), None, side, "Pos"
            )

            post_grp.set_parent(self.space)
            mc.pointConstraint(target, post_grp)

            return post_grp

        self.root_pos = create_position_grp(self.ik_root_ctrl, "A")
        self.end_pos = create_position_grp(self.ik_ctrl, "B")

        self.stch_dist = self.init_node(
            loc.create_node("distanceBetween"), "IkStretch", None, side, "Dist"
        )

        self.root_pos.attr("t") >> self.stch_dist.attr("p1")
        self.end_pos.attr("t") >> self.stch_dist.attr("p2")

        self.stch_mdv = self.init_node(
            loc.create_node("multiplyDivide"), "IkStretch", None, side, "Mdv"
        )

        self.stch_mdv.attr("op").v = 2
        self.stch_dist.attr("distance") >> self.stch_mdv.attr("i1x")
        self.stch_mdv.attr("i2x").v = self.stch_mdv.attr("i1x").v

        self.stch_blend = self.init_node(
            loc.create_node("blendTwoAttr"), "IkStretch", None, side, "Blend"
        )
        self.stch_clamp = self.init_node(
            loc.create_node("clamp"), "IkStretch", None, side, "Clamp"
        )
        self.stch_clamp.attr("minR").v = 1
        self.stch_clamp.attr("maxR").v = 1000

        self.stch_blend.add(ln="default", k=True, min=1, max=1)
        self.ik_ctrl.attr("autoStretch") >> self.stch_blend.attr(
            "attributesBlender"
        )
        self.stch_blend.attr("default") >> self.stch_blend.attr("input[0]")
        self.stch_mdv.attr("ox") >> self.stch_clamp.attr("inputR")
        self.stch_clamp.attr("outputR") >> self.stch_blend.attr("input[1]")

        up_stch_mdl = self.init_node(
            loc.create_node("multDoubleLinear"),
            "UpIkStretch",
            None,
            side,
            "Mdl",
        )
        low_stch_mdl = self.init_node(
            loc.create_node("multDoubleLinear"),
            "LowIkStretch",
            None,
            side,
            "Mdl",
        )
        self.stch_blend.attr("output") >> up_stch_mdl.attr("input1")
        self.stch_blend.attr("output") >> low_stch_mdl.attr("input1")

        up_stch_mdl.attr("input2").v = self.ik_jnts[1].attr("tx").v
        low_stch_mdl.attr("input2").v = self.ik_jnts[2].attr("tx").v

        up_stch_mdl.attr("output") >> self.ik_jnts[1].attr("tx")
        low_stch_mdl.attr("output") >> self.ik_jnts[2].attr("tx")

        # Ik Space
        utils.add_divide_attr(self.ik_ctrl, "spaceControl")
        if ikroot_space:
            self.create_space_switch(
                ikroot_space, self.ik_root_zr, self.ik_root_ctrl, self.space
            )

        if ik_space:
            self.create_space_switch(
                ik_space, self.ik_zr, self.ik_ctrl, self.space
            )
            self.ik_ctrl.attr("space").v = 1
            mc.renameAttr(self.ik_ctrl.attr("space"), "ankleSpace")

        self.create_space_switch(
            {
                "World": loc.main_grp.worldspace_grp,
                "Ankle": "{}".format(self.ik_ctrl),
            },
            self.ik_pole_zr,
            self.ik_ctrl,
            self.space,
        )
        mc.renameAttr(self.ik_ctrl.attr("space"), "ikPoleSpace")

        # Roll Attr
        utils.add_divide_attr(self.ik_ctrl, "footRollAttr")
        footroll_attr = self.ik_ctrl.add(ln="roll", min=-10, dv=0, max=10)
        rollinout_attr = self.ik_ctrl.add(
            ln="rollInOut", k=True, min=-10, max=10
        )
        foottw_attr = self.ik_ctrl.add(ln="footTwist", k=True, min=-10, max=10)
        heeltw_attr = self.ik_ctrl.add(ln="heelTwist", k=True, min=-10, max=10)
        heellift_attr = self.ik_ctrl.add(
            ln="heelLift", k=True, min=-10, max=10
        )
        toetw_attr = self.ik_ctrl.add(ln="toeTwist", k=True, min=-10, max=10)
        toelift_attr = self.ik_ctrl.add(ln="toeLift", k=True, min=-10, max=10)

        rolla_remp = self.init_node(
            loc.create_remap(in_min=0, in_max=-10, out_min=0, out_max=45),
            "RollStepA",
            None,
            side,
            "Remp",
        )
        rollb_remp = self.init_node(
            loc.create_remap(in_min=0, in_max=10, out_min=0, out_max=-45),
            "RollStepB",
            None,
            side,
            "Remp",
        )
        rollc_remp = self.init_node(
            loc.create_remap(in_min=5, in_max=10, out_min=0, out_max=-45),
            "RollStepC",
            None,
            side,
            "Remp",
        )
        rollin_remp = self.init_node(
            loc.create_remap(in_min=0, in_max=-10, out_min=0, out_max=45),
            "RollIn",
            None,
            side,
            "Remp",
        )
        rollout_remp = self.init_node(
            loc.create_remap(in_min=0, in_max=10, out_min=0, out_max=-45),
            "RollOut",
            None,
            side,
            "Remp",
        )
        foottwist_remap = self.init_node(
            loc.create_remap(in_min=-10, in_max=10, out_min=-45, out_max=45),
            "FootTwist",
            None,
            side,
            "Remp",
        )
        heeltwist_remap = self.init_node(
            loc.create_remap(in_min=-10, in_max=10, out_min=-45, out_max=45),
            "HeelTwist",
            None,
            side,
            "Remp",
        )
        heellift_remap = self.init_node(
            loc.create_remap(in_min=-10, in_max=10, out_min=-45, out_max=45),
            "HeelLift",
            None,
            side,
            "Remp",
        )
        toetwist_remap = self.init_node(
            loc.create_remap(in_min=-10, in_max=10, out_min=-45, out_max=45),
            "ToeTwist",
            None,
            side,
            "Remp",
        )
        toelift_remap = self.init_node(
            loc.create_remap(in_min=-10, in_max=10, out_min=-45, out_max=45),
            "ToeLift",
            None,
            side,
            "Remp",
        )
        # Set Remap
        rollb_remp.attr("value[2].value_FloatValue").v = 1
        rollb_remp.attr("value[2].value_Position").v = 0.5
        rollb_remp.attr("value[2].value_Interp").v = 1
        rollb_remp.attr("value[1].value_FloatValue").v = 0

        # Connect Remap
        footroll_attr >> rolla_remp.attr("i")
        footroll_attr >> rollb_remp.attr("i")
        footroll_attr >> rollc_remp.attr("i")

        rollinout_attr >> rollin_remp.attr("i")
        rollinout_attr >> rollout_remp.attr("i")

        foottw_attr >> foottwist_remap.attr("i")
        heeltw_attr >> heeltwist_remap.attr("i")
        heellift_attr >> heellift_remap.attr("i")
        toetw_attr >> toetwist_remap.attr("i")
        toelift_attr >> toelift_remap.attr("i")

        # Connect to Roll Pivot Grp
        rolla_remp.attr("ov") >> self.heel_roll.attr("rz")
        rollb_remp.attr("ov") >> self.ball_roll.attr("rz")
        rollc_remp.attr("ov") >> self.toe_roll.attr("rz")
        rollin_remp.attr("ov") >> self.in_roll.attr("rx")
        rollout_remp.attr("ov") >> self.out_roll.attr("rx")
        foottwist_remap.attr("ov") >> self.foot_roll.attr("ry")
        heeltwist_remap.attr("ov") >> self.ankle_rot.attr("ry")
        heellift_remap.attr("ov") >> self.heel_lift.attr("rz")
        toetwist_remap.attr("ov") >> self.toe_roll.attr("ry")
        toelift_remap.attr("ov") >> self.toe_tap.attr("rz")

        # IkFk Switch
        self.ikfk_ctrl = self.init_dag(
            loc.Controller(loc.cp.plus),
            "AttrControl",
            None,
            self.side,
            "Ctrl",
        )
        ikfk_zr = self.init_dag(
            loc.Group(self.ikfk_ctrl), "AttrControl", None, self.side, "Zr"
        )

        ikfk_zr.snap_pos(self.leg_jnts[EE_INDEX])
        loc.parent_constraint(self.leg_jnts[EE_INDEX], ikfk_zr)
        ikfk_zr.set_parent(self.meta)
        self.ikfk_ctrl.lhattr("t", "r", "s", "v")
        self.ikfk_ctrl.add(ln="ikFkSwitch", min=0, max=1, k=True, dv=1)

        # reverse
        rev = self.init_node(
            loc.create_node("reverse"), "IkFk", None, side, "Rev"
        )
        self.ikfk_ctrl.attr("ikFkSwitch") >> rev.attr("inputX")
        rev.attr("outputX") >> self.fk_zrs[0].attr("v")

        for ctrl_grp in [self.ik_pole_zr, self.ik_root_zr, self.ik_zr]:
            self.ikfk_ctrl.attr("ikFkSwitch") >> ctrl_grp.attr("v")

        for con in self.par_cons:
            self.ikfk_ctrl.attr("ikFkSwitch") >> con.attr("w0")
            rev.attr("outputX") >> con.attr("w1")

        # Clean Up
        # Set Color
        self.main_ctrl += (
            self.fk_ctrls
            + [self.ik_ctrl]
            + [self.ik_root_ctrl]
            + [self.ik_pole_ctrl]
        )
        self.sub_ctrl += [self.ikfk_ctrl]
        utils.set_ctrls_color(
            None, self.main_ctrl, self.sub_ctrl, self.dtl_ctrl
        )

        # Joint skin set
        self.skin_jnts = self.leg_jnts
        utils.add_to_skin_set(self.skin_jnts)

        # Detail Vis
        utils.connect_visiblity()

        # Set Parent
        self.ctrl_parent = self.init_dag(
            loc.Null(), "", None, self.side, "CtrlParent"
        )
        self.ctrl_parent.set_parent(self.meta)
        loc.parent_constraint(self.leg_jnts[-1], self.ctrl_parent)
        loc.scale_constraint(self.leg_jnts[-1], self.ctrl_parent)

        self.joint_parent = self.leg_jnts[-1]
