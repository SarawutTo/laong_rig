from . import core as loc
from . import rig_base
from . import subrig
import maya.cmds as mc


class EyeRig(rig_base.Rigbase):
    def __init__(
        self,
        eye_tmpjnt,
        pupil_tmpjnt,
        target_loc,
        side,
        desc="",
        target_par=None,
        jnt_par=None,
        ctrl_par=None,
    ):
        super(EyeRig, self).__init__("Eye", desc, side)
        self.meta = self.create_meta(ctrl_par)

        eye_tmpjnt = loc.Dag(eye_tmpjnt)
        pupil_tmpjnt = loc.Dag(pupil_tmpjnt)
        target_loc = loc.Dag(target_loc)

        eye_jnt = self.init_dag(
            loc.Joint(at=eye_tmpjnt), "", None, side, "Jnt"
        )
        pupil_jnt = self.init_dag(
            loc.Joint(at=pupil_tmpjnt), "Pupil", None, side, "Jnt"
        )
        eye_jnt.set_parent(jnt_par)
        pupil_jnt.set_parent(eye_jnt)

        # Eye
        self.eye_ctrl = self.init_dag(
            loc.Controller(loc.cp.aim), "", None, side, "Ctrl"
        )
        self.eye_zr, self.eye_aim = self._init_duo_grp(
            self.eye_ctrl, "", None, side
        )
        self.eye_ctrl.set_color(None, 0)
        self.eye_ctrl.lhattr("v")
        loc.parent_constraint(self.eye_ctrl, eye_jnt)
        loc.scale_constraint(self.eye_ctrl, eye_jnt)
        self.init_dag(self.eye_aim, "", None, side, "Aim")
        self.eye_zr.snap(eye_tmpjnt)
        self.eye_zr.set_parent(self.meta)

        self.pupil_ctrl = self.init_dag(
            loc.Controller(loc.cp.n_circle), "Iris", None, side, "Ctrl"
        )
        self.pupil_ctrl.set_color(None, 1)
        self.pupil_ctrl.lhattr("r", "v")
        self.pupil_zr, self.pupil_ofst = self._init_duo_grp(
            self.pupil_ctrl, "Iris", None, side
        )
        loc.parent_constraint(self.pupil_ctrl, pupil_jnt)
        loc.scale_constraint(self.pupil_ctrl, pupil_jnt)
        self.pupil_zr.snap(pupil_tmpjnt)
        self.pupil_zr.set_parent(self.eye_ctrl)

        # Target Position
        self.target_ctrl = self.init_dag(
            loc.Controller(loc.cp.locator), "Target", None, side, "Ctrl"
        )
        self.target_ctrl.lhattr("r", "s", "v")
        self.target_ctrl.set_color(None, 0)
        self.target_zr, self.target_ofst = self._init_duo_grp(
            self.target_ctrl, "Target", None, side
        )

        self.target_zr.attr("tx").v = pupil_jnt.world_vec.x
        self.target_zr.attr("ty").v = target_loc.world_vec.y
        self.target_zr.attr("tz").v = target_loc.world_vec.z

        mc.aimConstraint(
            self.target_ctrl,
            self.eye_aim,
            aimVector=(0, 0, 1),
            upVector=(0, 1, 0),
            worldUpType="objectrotation",
            worldUpVector=(0, 1, 0),
            worldUpObject=self.eye_zr,
            mo=True,
        )

        if target_par:
            self.target_zr.set_parent(target_par)


class TwoEyeRig(rig_base.Rigbase):
    def __init__(
        self,
        l_eye_tmpjnt,
        l_pupil_tmpjnt,
        r_eye_tmpjnt,
        r_pupil_tmpjnt,
        target_loc,
        target_space,
        desc="",
        jnt_par=None,
        ctrl_par=None,
    ):
        super(TwoEyeRig, self).__init__("Eye", desc, None)
        self.meta = self.create_meta(ctrl_par)
        self.space = self.create_space(self.meta)

        self.target_ctrl = self.init_dag(
            loc.Controller(loc.cp.n_circle), "Target", None, None, "Ctrl"
        )
        self.target_ctrl.lhattr("s", "v")
        self.maintarget_zr, self.maintarget_ofst = self._init_duo_grp(
            self.target_ctrl,
            "",
            None,
            None,
        )
        self.target_ctrl.set_color(None, 0)
        self.target_ctrl.rotate_shape(0, 90, 0)
        self.maintarget_zr.snap(target_loc)
        self.maintarget_zr.set_parent(self.meta)
        if target_space:
            self.create_space_switch(
                target_space,
                self.maintarget_zr,
                self.target_ctrl,
                self.space,
            )
            self.target_ctrl.attr("space").v = 1

        self.l_eyerig = EyeRig(
            eye_tmpjnt=l_eye_tmpjnt,
            pupil_tmpjnt=l_pupil_tmpjnt,
            target_loc=target_loc,
            side="L",
            desc="",
            target_par=self.target_ctrl,
            jnt_par=jnt_par,
            ctrl_par=self.meta,
        )
        self.r_eyerig = EyeRig(
            eye_tmpjnt=r_eye_tmpjnt,
            pupil_tmpjnt=r_pupil_tmpjnt,
            target_loc=target_loc,
            side="R",
            desc="",
            target_par=self.target_ctrl,
            jnt_par=jnt_par,
            ctrl_par=self.meta,
        )


class EyeLidBlendShape(rig_base.Rigbase):
    def __init__(
        self,
        up_lid,
        low_lid,
        side,
        desc="",
        ctrl_scale=1,
        ctrl_par=None,
    ):
        super(EyeLidBlendShape, self).__init__("EyeLid", desc, side)
        self.meta = self.create_meta(ctrl_par)
        self.driver = self.create_driver(self.meta)

        up_lid = loc.Dag(up_lid)
        low_lid = loc.Dag(low_lid)

        def create_ctrl(compo, tmp):
            lid_ctrl = self.init_dag(
                loc.Controller(loc.cp.n_circle), compo, None, side, "Ctrl"
            )
            lid_ctrl.set_color(None, 0)
            lid_ctrl.lhattr("tx", "tz", "r", "s", "v")
            if compo == "Up":
                lid_ctrl.add(ln="blink", k=True, min=0, max=1, dv=0)
                lid_ctrl.add(ln="blinkHeight", k=True, min=0, max=1, dv=0.15)

            lid_zr, lid_ofst = self._init_duo_grp(lid_ctrl, compo, None, side)
            lid_zr.snap(tmp)
            lid_zr.attr("sx").v = ctrl_scale
            lid_zr.attr("sy").v = ctrl_scale
            lid_zr.attr("sz").v = ctrl_scale
            lid_zr.set_parent(self.meta)

            return lid_zr, lid_ofst, lid_ctrl

        self.uplid_zr, self.uplid_ofst, self.uplid_ctrl = create_ctrl(
            "Up", up_lid
        )
        self.lowlid_zr, self.lowlid_ofst, self.lowlid_ctrl = create_ctrl(
            "Low", low_lid
        )

        # Clamp Value
        up_pos, up_neg = self.split_to_pos_neg(
            self.uplid_ctrl, self.uplid_ctrl.shape, "Uplid", "ty", -1, 1
        )
        low_pos, low_neg = self.split_to_pos_neg(
            self.lowlid_ctrl, self.lowlid_ctrl.shape, "Lowlid", "ty", -1, 1
        )

        # Blink Attribute
        self.driver.add(ln="uplidClose", k=True)
        self.driver.add(ln="lowlidClose", k=True)
        self.driver.add(ln="uplidOpen", k=True)
        self.driver.add(ln="lowlidOpen", k=True)

        blink_pma = self.init_node(
            loc.create_node("plusMinusAverage"),
            "BlinkHeight",
            None,
            side,
            "Pma",
        )
        blink_pma.attr("op").v = 2
        blink_pma.add(ln="default", dv=1)
        blink_blend = self.init_node(
            loc.create_node("blendColors"),
            "BlinkHeight",
            None,
            side,
            "Blend",
        )

        blink_pma.attr("default") >> blink_pma.attr("input1D[0]")
        self.uplid_ctrl.attr("blinkHeight") >> blink_pma.attr("input1D[1]")
        self.uplid_ctrl.attr("blink") >> blink_blend.attr("blender")

        blink_pma.attr("output1D") >> blink_blend.attr("color1R")
        self.uplid_ctrl.attr("blinkHeight") >> blink_blend.attr("color1G")

        blink_blend.attr("outputR") >> self.driver.attr("uplidClose")
        blink_blend.attr("outputG") >> self.driver.attr("lowlidClose")

        up_pos >> blink_blend.attr("color2R")
        low_pos >> blink_blend.attr("color2G")
        up_neg >> self.driver.attr("uplidOpen")
        low_neg >> self.driver.attr("lowlidOpen")
