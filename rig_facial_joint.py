# Maya Modules.
import maya.cmds as mc
from imp import reload

# pkrig Modules
from . import rig_base
from . import core as loc
from . import utils as pru
from . import naming_tools as prnt
from . import rig_global as rgb

reload(loc)
# from . import blend_shape_tools as bst


class ExtraBaseRig(rig_base.Rigbase):
    def __init__(self, mod, desc, write_side):
        super(ExtraBaseRig, self).__init__(mod, desc, write_side)
        self.meta = self.create_meta()

    def add_rig_at_joint(
        self, name, idx, side, cp, tmpjnt, jnt_par, ctrl_par, inv
    ):
        jnt = self.init_dag(loc.Joint(tmpjnt), name, idx, side, "Jnt")
        ctrl = self.init_dag(loc.Controller(cp), name, idx, side, "Ctrl")
        zr, ex, ofst = self._init_tri_grp(ctrl, name, idx, side)
        ctrl.lhattr("v")

        jnt.ssc = False

        zr.snap(tmpjnt)
        if inv:
            zr.attr("sz").v = -1

        loc.parent_constraint(ctrl, jnt, mo=True)
        loc.scale_constraint(ctrl, jnt)

        zr.set_parent(ctrl_par)
        jnt.set_parent(jnt_par)

        return jnt, ctrl, ofst, ex, zr

    def add_fk_rig(self, name, side, cp, tmpjnts, jnt_par, ctrl_par):
        dtl_jnts = []
        dtl_ctrls = []
        dtl_ofsts = []
        dtl_exs = []
        dtl_zrs = []

        # Casts args to pkrig objects.
        jnts = loc.to_dags(tmpjnts)
        for ix, jnt in enumerate(jnts):
            if not dtl_jnts:
                (
                    dtl_jnt,
                    dtl_ctrl,
                    dtl_ofst,
                    dtl_con,
                    dtl_zr,
                ) = self.add_rig_at_joint(
                    name=name,
                    idx=ix + 1,
                    side=side,
                    cp=cp,
                    tmpjnt=jnt,
                    jnt_par=jnt_par,
                    ctrl_par=ctrl_par,
                    inv=False,
                )
            else:
                (
                    dtl_jnt,
                    dtl_ctrl,
                    dtl_ofst,
                    dtl_con,
                    dtl_zr,
                ) = self.add_rig_at_joint(
                    name=name,
                    idx=ix + 1,
                    side=side,
                    cp=cp,
                    tmpjnt=jnt,
                    jnt_par=dtl_jnts[-1],
                    ctrl_par=dtl_ctrls[-1],
                    inv=False,
                )

            dtl_jnts.append(dtl_jnt)
            dtl_ctrls.append(dtl_ctrl)
            dtl_ofsts.append(dtl_ofst)
            dtl_exs.append(dtl_con)
            dtl_zrs.append(dtl_zr)

        return dtl_jnts, dtl_ctrls, dtl_ofsts, dtl_exs, dtl_zrs


class MouthRigEx(ExtraBaseRig):
    """Create Mouth Rig For Charater Extra.

    Example:
    mouth_rig = rig_facial_joint.MouthRigEx(
        jaw_tmpjnt="Jaw_TmpJnt",
        miduplip_tmpjnt="UpLip_TmpJnt",
        midlowlip_tmpjnt="LowLip_TmpJnt",
        corner_l_tmpjnt="Corner_L_TmpJnt",
        corner_r_tmpjnt="Corner_R_TmpJnt",
        uplipa_l_tmpjnt="UpLipA_L_TmpJnt",
        uplipb_l_tmpjnt="UpLipB_L_TmpJnt",
        lowlipa_l_tmpjnt="LowLipA_L_TmpJnt",
        lowlipb_l_tmpjnt="LowLipB_L_TmpJnt",
        uplipa_r_tmpjnt="UpLipA_R_TmpJnt",
        uplipb_r_tmpjnt="UpLipB_R_TmpJnt",
        lowlipa_r_tmpjnt="LowLipA_R_TmpJnt",
        lowlipb_r_tmpjnt="LowLipB_R_TmpJnt",
        desc="",
        jnt_par=head_rig.jnt,
        ctrl_par=None,
    )

    """

    def __init__(
        self,
        jaw_tmpjnt,
        miduplip_tmpjnt,
        midlowlip_tmpjnt,
        corner_l_tmpjnt,
        corner_r_tmpjnt,
        uplipa_l_tmpjnt,
        uplipb_l_tmpjnt,
        lowlipa_l_tmpjnt,
        lowlipb_l_tmpjnt,
        uplipa_r_tmpjnt,
        uplipb_r_tmpjnt,
        lowlipa_r_tmpjnt,
        lowlipb_r_tmpjnt,
        desc,
        jnt_par,
        ctrl_par,
        upjaw_tmpjnt=None,
    ):
        jaw_jnt = loc.Dag(jaw_tmpjnt)
        uplip_jnt = loc.Dag(miduplip_tmpjnt)
        lowlip_jnt = loc.Dag(midlowlip_tmpjnt)
        corner_l_jnt = loc.Dag(corner_l_tmpjnt)
        corner_r_jnt = loc.Dag(corner_r_tmpjnt)
        uplipa_l_jnt = loc.Dag(uplipa_l_tmpjnt)
        uplipb_l_jnt = loc.Dag(uplipb_l_tmpjnt)
        uplipa_r_jnt = loc.Dag(uplipa_r_tmpjnt)
        uplipb_r_jnt = loc.Dag(uplipb_r_tmpjnt)
        lowlipa_l_jnt = loc.Dag(lowlipa_l_tmpjnt)
        lowlipb_l_jnt = loc.Dag(lowlipb_l_tmpjnt)
        lowlipa_r_jnt = loc.Dag(lowlipa_r_tmpjnt)
        lowlipb_r_jnt = loc.Dag(lowlipb_r_tmpjnt)

        # Main Groups
        super(MouthRigEx, self).__init__("Mth", desc, False)

        # Main Joints
        self.mouth_jnt = self.init_dag(loc.Joint(), "Main", None, None, "Jnt")
        self.mouth_jnt.ssc = False

        if jnt_par:
            self.meta.snap(jnt_par)
            self.mouth_jnt.snap(jnt_par)
            self.mouth_jnt.set_parent(jnt_par)

        if ctrl_par:
            self.meta.set_parent(ctrl_par)

        (
            self.jaw_jnt,
            self.jaw_ctrl,
            self.jaw_ofst,
            self.jaw_con,
            self.jaw_zr,
        ) = self.add_rig_at_joint(
            name="Jaw",
            idx=None,
            side=None,
            cp=rgb.Cp.n_circle,
            tmpjnt=jaw_jnt,
            jnt_par=self.mouth_jnt,
            ctrl_par=self.meta,
            inv=False,
        )
        up_ctrl_parent = self.meta
        if upjaw_tmpjnt:
            upjaw_tmpjnt = loc.Dag(upjaw_tmpjnt)

            (
                self.upjaw_jnt,
                self.upjaw_ctrl,
                self.upjaw_ofst,
                self.upjaw_con,
                self.upjaw_zr,
            ) = self.add_rig_at_joint(
                name="UpJaw",
                idx=None,
                side=None,
                cp=rgb.Cp.n_circle,
                tmpjnt=upjaw_tmpjnt,
                jnt_par=self.mouth_jnt,
                ctrl_par=self.meta,
                inv=False,
            )
            up_ctrl_parent = self.upjaw_ctrl

        openmax = self.jaw_ctrl.get_shape().add(
            ln="openMax", k=True, min=0, dv=27
        )
        mc.setAttr(openmax, cb=True, k=False)

        def open_amp(con, ctrl):
            for attr in ("tx", "ty", "tz"):
                amp_attr: loc.Attribute = ctrl.get_shape().add(
                    ln="open{}Amp".format(prnt.upfirst(attr)), k=True
                )
                mc.setAttr(amp_attr, cb=True, k=False)
                amp_attr >> con.attr(attr)
                name, _, side, _ = prnt.deconstruct(ctrl)
                remap = self.init_node(
                    loc.create_node("remapValue"),
                    "{}{}".format(name, attr),
                    None,
                    side,
                    "Remap",
                )
                self.jaw_ctrl.attr("rx") >> remap.attr("i")
                openmax >> remap.attr("imx")
                amp_attr >> remap.attr("omx")
                remap.attr("ov") >> con.attr(attr)

        (
            self.uplip_jnt,
            self.uplip_ctrl,
            self.uplip_ofst,
            self.uplip_con,
            self.uplip_zr,
        ) = self.add_rig_at_joint(
            name="UpLip",
            idx=None,
            side=None,
            cp=rgb.Cp.n_circle,
            tmpjnt=uplip_jnt,
            jnt_par=self.jaw_jnt,
            ctrl_par=up_ctrl_parent,
            inv=False,
        )

        (
            self.lowlip_jnt,
            self.lowlip_ctrl,
            self.lowlip_ofst,
            self.lowlip_con,
            self.lowlip_zr,
        ) = self.add_rig_at_joint(
            name="LowLip",
            idx=None,
            side=None,
            cp=rgb.Cp.n_circle,
            tmpjnt=lowlip_jnt,
            jnt_par=self.jaw_jnt,
            ctrl_par=up_ctrl_parent,
            inv=False,
        )

        # Corner
        (
            self.coner_l_jnt,
            self.coner_l_ctrl,
            self.coner_l_ofst,
            self.coner_l_con,
            self.coner_l_zr,
        ) = self.add_rig_at_joint(
            name="Corner",
            idx=None,
            side=rgb.Side.left,
            cp=rgb.Cp.n_circle,
            tmpjnt=corner_l_jnt,
            jnt_par=self.jaw_jnt,
            ctrl_par=up_ctrl_parent,
            inv=False,
        )
        (
            self.coner_r_jnt,
            self.coner_r_ctrl,
            self.coner_r_ofst,
            self.coner_r_con,
            self.coner_r_zr,
        ) = self.add_rig_at_joint(
            name="Corner",
            idx=None,
            side=rgb.Side.right,
            cp=rgb.Cp.n_circle,
            tmpjnt=corner_r_jnt,
            jnt_par=self.jaw_jnt,
            ctrl_par=up_ctrl_parent,
            inv=True,
        )

        # Up Lip
        (
            self.uplipa_l_jnt,
            self.uplipa_l_ctrl,
            self.uplipa_l_ofst,
            self.uplipa_l_con,
            self.uplipa_l_zr,
        ) = self.add_rig_at_joint(
            name="UpLipA",
            idx=None,
            side=rgb.Side.left,
            cp=rgb.Cp.n_circle,
            tmpjnt=uplipa_l_jnt,
            jnt_par=self.jaw_jnt,
            ctrl_par=up_ctrl_parent,
            inv=False,
        )

        (
            self.uplipb_l_jnt,
            self.uplipb_l_ctrl,
            self.uplipb_l_ofst,
            self.uplipb_l_con,
            self.uplipb_l_zr,
        ) = self.add_rig_at_joint(
            name="UpLipB",
            idx=None,
            side=rgb.Side.left,
            cp=rgb.Cp.n_circle,
            tmpjnt=uplipb_l_jnt,
            jnt_par=self.jaw_jnt,
            ctrl_par=self.coner_l_ctrl,
            inv=False,
        )

        (
            self.uplipa_r_jnt,
            self.uplipa_r_ctrl,
            self.uplipa_r_ofst,
            self.uplipa_r_con,
            self.uplipa_r_zr,
        ) = self.add_rig_at_joint(
            name="UpLipA",
            idx=None,
            side=rgb.Side.right,
            cp=rgb.Cp.n_circle,
            tmpjnt=uplipa_r_jnt,
            jnt_par=self.jaw_jnt,
            ctrl_par=up_ctrl_parent,
            inv=True,
        )

        (
            self.uplipb_r_jnt,
            self.uplipb_r_ctrl,
            self.uplipb_r_ofst,
            self.uplipb_r_con,
            self.uplipb_r_zr,
        ) = self.add_rig_at_joint(
            name="UpLipB",
            idx=None,
            side=rgb.Side.right,
            cp=rgb.Cp.n_circle,
            tmpjnt=uplipb_r_jnt,
            jnt_par=self.jaw_jnt,
            ctrl_par=self.coner_r_ctrl,
            inv=True,
        )

        # Low Lip
        (
            self.lowlipa_l_jnt,
            self.lowlipa_l_ctrl,
            self.lowlipa_l_ofst,
            self.lowlipa_l_con,
            self.lowlipa_l_zr,
        ) = self.add_rig_at_joint(
            name="LowLipA",
            idx=None,
            side=rgb.Side.left,
            cp=rgb.Cp.n_circle,
            tmpjnt=lowlipa_l_jnt,
            jnt_par=self.jaw_jnt,
            ctrl_par=self.meta,
            inv=False,
        )

        (
            self.lowlipb_l_jnt,
            self.lowlipb_l_ctrl,
            self.lowlipb_l_ofst,
            self.lowlipb_l_con,
            self.lowlipb_l_zr,
        ) = self.add_rig_at_joint(
            name="LowLipB",
            idx=None,
            side=rgb.Side.left,
            cp=rgb.Cp.n_circle,
            tmpjnt=lowlipb_l_jnt,
            jnt_par=self.jaw_jnt,
            ctrl_par=self.coner_l_ctrl,
            inv=False,
        )

        (
            self.lowlipa_r_jnt,
            self.lowlipa_r_ctrl,
            self.lowlipa_r_ofst,
            self.lowlipa_r_con,
            self.lowlipa_r_zr,
        ) = self.add_rig_at_joint(
            name="LowLipA",
            idx=None,
            side=rgb.Side.right,
            cp=rgb.Cp.n_circle,
            tmpjnt=lowlipa_r_jnt,
            jnt_par=self.jaw_jnt,
            ctrl_par=self.meta,
            inv=True,
        )

        (
            self.lowlipb_r_jnt,
            self.lowlipb_r_ctrl,
            self.lowlipb_r_ofst,
            self.lowlipb_r_con,
            self.lowlipb_r_zr,
        ) = self.add_rig_at_joint(
            name="LowLipB",
            idx=None,
            side=rgb.Side.right,
            cp=rgb.Cp.n_circle,
            tmpjnt=lowlipb_r_jnt,
            jnt_par=self.jaw_jnt,
            ctrl_par=self.coner_r_ctrl,
            inv=True,
        )

        open_amp(self.lowlipb_l_con, self.lowlipb_l_ctrl)
        open_amp(self.lowlipb_r_con, self.lowlipb_r_ctrl)
        open_amp(self.uplipb_l_con, self.uplipb_l_ctrl)
        open_amp(self.uplipb_r_con, self.uplipb_r_ctrl)

        self.space_grp = self.init_dag(loc.Null(), "Space", None, None, "Grp")
        self.space_grp.set_parent(self.meta)

        def add_blend_constaint(
            name, side, driver_a, driver_b, driven, ctrl, dv
        ):
            driver_a_piv = self.init_dag(
                loc.Null(), "{}A".format(name), None, side, "Piv"
            )
            driver_a_spc = self.init_dag(
                loc.Group(driver_a_piv), "{}A".format(name), None, side, "Spc"
            )
            driver_b_piv = self.init_dag(
                loc.Null(), "{}B".format(name), None, side, "Piv"
            )
            driver_b_spc = self.init_dag(
                loc.Group(driver_b_piv), "{}B".format(name), None, side, "Spc"
            )

            driver_a_spc.snap(driven)
            driver_b_spc.snap(driven)
            driver_a_spc.set_parent(self.space_grp)
            driver_b_spc.set_parent(self.space_grp)
            loc.parent_constraint(driver_a, driver_a_spc, mo=True)
            loc.parent_constraint(driver_b, driver_b_spc, mo=True)
            con = loc.parent_constraint(
                driver_b_piv, driver_a_piv, driven, mo=True
            )

            space_attr = ctrl.add(ln="follow", min=0, max=1, dv=dv, k=True)
            rev = self.init_node(
                loc.create_node("reverse"),
                "{}Space".format(name),
                None,
                side,
                "Rev",
            )
            space_attr >> rev.attr("ix")
            space_attr >> con.attr("w0")
            rev.attr("ox") >> con.attr("w1")

        add_blend_constaint(
            "UpLip",
            None,
            up_ctrl_parent,
            self.jaw_ctrl,
            self.uplip_con,
            self.uplip_ctrl,
            0,
        )

        add_blend_constaint(
            "LowLip",
            None,
            up_ctrl_parent,
            self.jaw_ctrl,
            self.lowlip_con,
            self.lowlip_ctrl,
            1,
        )

        add_blend_constaint(
            "Corner",
            rgb.Side.left,
            up_ctrl_parent,
            self.jaw_ctrl,
            self.coner_l_con,
            self.coner_l_ctrl,
            0.5,
        )

        add_blend_constaint(
            "Corner",
            rgb.Side.right,
            up_ctrl_parent,
            self.jaw_ctrl,
            self.coner_r_con,
            self.coner_r_ctrl,
            0.5,
        )

        add_blend_constaint(
            "UplipA",
            rgb.Side.left,
            up_ctrl_parent,
            self.uplip_ctrl,
            self.uplipa_l_con,
            self.uplipa_l_ctrl,
            1,
        )

        add_blend_constaint(
            "UplipA",
            rgb.Side.right,
            up_ctrl_parent,
            self.uplip_ctrl,
            self.uplipa_r_con,
            self.uplipa_r_ctrl,
            1,
        )

        add_blend_constaint(
            "LowlipA",
            rgb.Side.left,
            self.jaw_ctrl,
            self.lowlip_ctrl,
            self.lowlipa_l_con,
            self.lowlipa_l_ctrl,
            1,
        )

        add_blend_constaint(
            "LowlipA",
            rgb.Side.right,
            self.jaw_ctrl,
            self.lowlip_ctrl,
            self.lowlipa_r_con,
            self.lowlipa_r_ctrl,
            1,
        )

        # Set Color
        self.all_ctrls: list[loc.Controller] = [
            self.jaw_ctrl,
            self.uplip_ctrl,
            self.lowlip_ctrl,
            self.uplipa_l_ctrl,
            self.uplipa_r_ctrl,
            self.uplipb_l_ctrl,
            self.uplipb_r_ctrl,
            self.lowlipa_l_ctrl,
            self.lowlipa_r_ctrl,
            self.lowlipb_l_ctrl,
            self.lowlipb_r_ctrl,
            self.coner_l_ctrl,
            self.coner_r_ctrl,
        ]
        for ctrl in self.all_ctrls:
            ctrl.set_color(None, 0)


class SingleEyeBrowRigEx(ExtraBaseRig):
    """Create Mouth Rig For Charater Extra.

    Example:
    rig_facial_extra

    """

    def __init__(
        self,
        main_tmpjnt,
        in_tmpjnt,
        mid_tmpjnt,
        out_tmpjnt,
        indtl_tmpjnt,
        outdtl_tmpjnt,
        side,
        dtl_enable,
        eb_line_rig,
        desc,
        jnt_par,
        ctrl_par,
    ):
        # Cast to Dag
        main_jnt = loc.Dag(main_tmpjnt)
        in_jnt = loc.Dag(in_tmpjnt)
        mid_jnt = loc.Dag(mid_tmpjnt)
        out_jnt = loc.Dag(out_tmpjnt)
        indtl_jnt = loc.Dag(indtl_tmpjnt)
        outdtl_jnt = loc.Dag(outdtl_tmpjnt)

        # Main Groups
        super(SingleEyeBrowRigEx, self).__init__("Eb", desc, side)
        self.meta.snap(main_jnt)

        if ctrl_par:
            self.meta.set_parent(ctrl_par)

        offset = 1
        if self.side == rgb.Side.right:
            offset = -1

        offset_value = ((in_jnt.world_vec - mid_jnt.world_vec).length()) / 20

        (
            self.main_jnt,
            self.main_ctrl,
            self.main_ofst,
            self.main_con,
            self.main_zr,
        ) = self.add_rig_at_joint(
            name="Main",
            idx=None,
            side=self.side,
            cp=rgb.Cp.n_circle,
            tmpjnt=main_jnt,
            jnt_par=jnt_par,
            ctrl_par=self.meta,
            inv=False,
        )
        self.main_ctrl.set_color(None, 0)

        (
            self.in_jnt,
            self.in_ctrl,
            self.in_ofst,
            self.in_con,
            self.in_zr,
        ) = self.add_rig_at_joint(
            name="In",
            idx=None,
            side=self.side,
            cp=rgb.Cp.n_circle,
            tmpjnt=in_jnt,
            jnt_par=self.main_jnt,
            ctrl_par=self.main_ctrl,
            inv=False,
        )

        (
            self.mid_jnt,
            self.mid_ctrl,
            self.mid_ofst,
            self.mid_con,
            self.mid_zr,
        ) = self.add_rig_at_joint(
            name="Mid",
            idx=None,
            side=self.side,
            cp=rgb.Cp.n_circle,
            tmpjnt=mid_jnt,
            jnt_par=self.main_jnt,
            ctrl_par=self.main_ctrl,
            inv=False,
        )

        (
            self.out_jnt,
            self.out_ctrl,
            self.out_ofst,
            self.out_con,
            self.out_zr,
        ) = self.add_rig_at_joint(
            name="Out",
            idx=None,
            side=self.side,
            cp=rgb.Cp.n_circle,
            tmpjnt=out_jnt,
            jnt_par=self.main_jnt,
            ctrl_par=self.main_ctrl,
            inv=False,
        )
        self.in_ctrl.set_color(None, 0)
        self.mid_ctrl.set_color(None, 0)
        self.out_ctrl.set_color(None, 0)
        unparent_grp = [self.in_zr, self.mid_zr, self.out_zr]

        if eb_line_rig:
            (
                self.ineb_jnt,
                self.ineb_ctrl,
                self.ineb_ofst,
                self.ineb_con,
                self.ineb_zr,
            ) = self.add_rig_at_joint(
                name="InEyebrow",
                idx=None,
                side=self.side,
                cp=rgb.Cp.n_circle,
                tmpjnt=in_jnt,
                jnt_par=self.in_jnt,
                ctrl_par=self.in_ctrl,
                inv=False,
            )

            (
                self.mideb_jnt,
                self.mideb_ctrl,
                self.mideb_ofst,
                self.mideb_con,
                self.mideb_zr,
            ) = self.add_rig_at_joint(
                name="MidEyebrow",
                idx=None,
                side=self.side,
                cp=rgb.Cp.n_circle,
                tmpjnt=mid_jnt,
                jnt_par=self.mid_jnt,
                ctrl_par=self.mid_ctrl,
                inv=False,
            )

            (
                self.outeb_jnt,
                self.outeb_ctrl,
                self.outeb_ofst,
                self.outeb_con,
                self.outeb_zr,
            ) = self.add_rig_at_joint(
                name="OutEyebrow",
                idx=None,
                side=self.side,
                cp=rgb.Cp.n_circle,
                tmpjnt=out_jnt,
                jnt_par=self.out_jnt,
                ctrl_par=self.out_ctrl,
                inv=False,
            )

            self.ineb_ctrl.set_color(None, 1)
            self.mideb_ctrl.set_color(None, 1)
            self.outeb_ctrl.set_color(None, 1)
            self.ineb_ctrl.scale_shape(0.8)
            self.mideb_ctrl.scale_shape(0.8)
            self.outeb_ctrl.scale_shape(0.8)

            self.ineb_zr.attr("tz").v = offset_value  # * offset
            self.mideb_zr.attr("tz").v = offset_value  # * offset
            self.outeb_zr.attr("tz").v = offset_value  # * offset

        if dtl_enable:
            (
                self.indtl_jnt,
                self.indtl_ctrl,
                self.indtl_ofst,
                self.indtl_con,
                self.indtl_zr,
            ) = self.add_rig_at_joint(
                name="InDtl",
                idx=None,
                side=self.side,
                cp=rgb.Cp.n_circle,
                tmpjnt=indtl_jnt,
                jnt_par=self.main_jnt,
                ctrl_par=self.main_ctrl,
                inv=False,
            )
            unparent_grp.append(self.indtl_zr)

            (
                self.outdtl_jnt,
                self.outdtl_ctrl,
                self.outdtl_ofst,
                self.outdtl_con,
                self.outdtl_zr,
            ) = self.add_rig_at_joint(
                name="OutDtl",
                idx=None,
                side=self.side,
                cp=rgb.Cp.n_circle,
                tmpjnt=outdtl_jnt,
                jnt_par=self.main_jnt,
                ctrl_par=self.main_ctrl,
                inv=False,
            )
            unparent_grp.append(self.outdtl_zr)
            self.indtl_ctrl.set_color(None, 1)
            self.outdtl_ctrl.set_color(None, 1)

            indtl_pos = self.init_dag(
                loc.Null(), "InDtlPos", None, side, "Grp"
            )
            midindtl_pos = self.init_dag(
                loc.Null(), "MidInDtlPos", None, side, "Grp"
            )
            outdtl_pos = self.init_dag(
                loc.Null(), "OutDtlPos", None, side, "Grp"
            )
            midoutdtl_pos = self.init_dag(
                loc.Null(), "MidOutDtlPos", None, side, "Grp"
            )

            indtl_pos.snap_pos(self.indtl_ctrl)
            indtl_pos.set_parent(self.in_ctrl)
            outdtl_pos.snap_pos(self.outdtl_ctrl)
            outdtl_pos.set_parent(self.out_ctrl)

            midindtl_pos.snap_pos(self.indtl_ctrl)
            midindtl_pos.set_parent(self.mid_ctrl)
            midoutdtl_pos.snap_pos(self.outdtl_ctrl)
            midoutdtl_pos.set_parent(self.mid_ctrl)

            in_con = loc.point_constraint(
                midindtl_pos, indtl_pos, self.indtl_con, mo=True
            )
            out_con = loc.point_constraint(
                midoutdtl_pos, outdtl_pos, self.outdtl_con, mo=True
            )

            for ctrl, name, con in zip(
                [self.indtl_ctrl, self.outdtl_ctrl],
                ["indtl", "outdtl"],
                [in_con, out_con],
            ):
                fol_attr = ctrl.add(
                    ln="midFollow", k=True, min=0, max=1, dv=0.5
                )
                reverse = self.init_node(
                    loc.create_node("reverse"), name, None, side, "Rev"
                )
                fol_attr >> reverse.attr("ix")
                fol_attr >> con.attr("w0")
                reverse.attr("ox") >> con.attr("w1")

            if eb_line_rig:
                (
                    self.indtleb_jnt,
                    self.indtleb_ctrl,
                    self.indtleb_ofst,
                    self.indtleb_con,
                    self.indtleb_zr,
                ) = self.add_rig_at_joint(
                    name="InDtlEyebrow",
                    idx=None,
                    side=self.side,
                    cp=rgb.Cp.n_circle,
                    tmpjnt=indtl_jnt,
                    jnt_par=self.indtl_jnt,
                    ctrl_par=self.indtl_ctrl,
                    inv=False,
                )

                (
                    self.outdtleb_jnt,
                    self.outdtleb_ctrl,
                    self.outdtleb_ofst,
                    self.outdtleb_con,
                    self.outdtleb_zr,
                ) = self.add_rig_at_joint(
                    name="OutDtlEyebrow",
                    idx=None,
                    side=self.side,
                    cp=rgb.Cp.n_circle,
                    tmpjnt=outdtl_jnt,
                    jnt_par=self.outdtl_jnt,
                    ctrl_par=self.outdtl_ctrl,
                    inv=False,
                )

                self.indtleb_ctrl.set_color(side, 1)
                self.outdtleb_ctrl.set_color(side, 1)
                self.indtleb_ctrl.scale_shape(0.8)
                self.outdtleb_ctrl.scale_shape(0.8)

                self.indtleb_zr.attr("tz").v = offset_value  # * offset
                self.outdtleb_zr.attr("tz").v = offset_value  # * offset

        # Fix Joint Transform node
        # if side == rgb.Side.right:
        #     for zr in unparent_grp:
        #         mc.parent(zr, w=True)
        #         zr.attr("sz").v = -1
        #     self.main_zr.attr("sz").v = -1

        #     for zr in unparent_grp:
        #         mc.parent(zr, self.main_ctrl)


class EyebrowRigEx(ExtraBaseRig):
    """ """

    def __init__(
        self,
        main_tmpjnt,
        mid_tmpjnt,
        main_l_tmpjnt,
        in_l_tmpjnt,
        mid_l_tmpjnt,
        out_l_tmpjnt,
        indtl_l_tmpjnt,
        outdtl_l_tmpjnt,
        main_r_tmpjnt,
        in_r_tmpjnt,
        mid_r_tmpjnt,
        out_r_tmpjnt,
        indtl_r_tmpjnt,
        outdtl_r_tmpjnt,
        dtl_enable,
        eb_line_rig,
        desc,
        jnt_par,
        ctrl_par,
    ):
        main_jnt = loc.Dag(main_tmpjnt)
        mid_jnt = loc.Dag(mid_tmpjnt)
        super(EyebrowRigEx, self).__init__("Eb", desc, False)

        # Main Joints
        self.main_jnt = self.init_dag(loc.Joint(), "Main", None, None, "Jnt")
        self.main_jnt.attr("ssc").v = False

        if jnt_par:
            self.meta.snap(jnt_par)
            self.main_jnt.snap(main_jnt)
            self.main_jnt.set_parent(jnt_par)

        if ctrl_par:
            self.meta.set_parent(ctrl_par)

        (
            self.mid_jnt,
            self.mid_ctrl,
            self.mid_ofst,
            self.mid_con,
            self.mid_zr,
        ) = self.add_rig_at_joint(
            name="Mid",
            idx=None,
            side=None,
            cp=rgb.Cp.n_circle,
            tmpjnt=mid_jnt,
            jnt_par=self.main_jnt,
            ctrl_par=self.meta,
            inv=False,
        )
        self.mid_ctrl.set_color(None, 0)

        self.l_eb_rig = SingleEyeBrowRigEx(
            main_tmpjnt=main_l_tmpjnt,
            in_tmpjnt=in_l_tmpjnt,
            mid_tmpjnt=mid_l_tmpjnt,
            out_tmpjnt=out_l_tmpjnt,
            indtl_tmpjnt=indtl_l_tmpjnt,
            outdtl_tmpjnt=outdtl_l_tmpjnt,
            side=rgb.Side.left,
            dtl_enable=dtl_enable,
            eb_line_rig=eb_line_rig,
            desc=desc,
            jnt_par=self.main_jnt,
            ctrl_par=self.meta,
        )

        self.r_eb_rig = SingleEyeBrowRigEx(
            main_tmpjnt=main_r_tmpjnt,
            in_tmpjnt=in_r_tmpjnt,
            mid_tmpjnt=mid_r_tmpjnt,
            out_tmpjnt=out_r_tmpjnt,
            indtl_tmpjnt=indtl_r_tmpjnt,
            outdtl_tmpjnt=outdtl_r_tmpjnt,
            side=rgb.Side.right,
            dtl_enable=dtl_enable,
            eb_line_rig=eb_line_rig,
            desc=desc,
            jnt_par=self.main_jnt,
            ctrl_par=self.meta,
        )


class DetailRigEx(ExtraBaseRig):
    def __init__(self, tmpjnts, desc, skin_parent, ctrl_grp_parent):
        super(DetailRigEx, self).__init__("Dtl", desc, False)

        # Main Joints
        if skin_parent:
            self.meta.snap(skin_parent)

        if ctrl_grp_parent:
            self.meta.set_parent(ctrl_grp_parent)

        self.jnts = []
        self.ctrls = []
        self.ofsts = []
        self.cons = []
        self.zrs = []

        # Casts args to pkrig objects.
        jnts = loc.to_dags(tmpjnts)
        for jnt in jnts:
            name, _, side, _ = prnt.deconstruct(jnt.name)

            inv = False
            if side == rgb.Side.right:
                inv = True

            (
                self.jnt,
                self.ctrl,
                self.ofst,
                self.con,
                self.zr,
            ) = self.add_rig_at_joint(
                name=name,
                idx=None,
                side=side,
                cp=rgb.Cp.cube,
                tmpjnt=jnt,
                jnt_par=skin_parent,
                ctrl_par=self.meta,
                inv=inv,
            )
            self.ctrl.set_color(None, 1)
            self.jnts.append(self.jnt)
            self.ctrls.append(self.ctrl)
            self.ofsts.append(self.ofst)
            self.cons.append(self.con)
            self.zrs.append(self.zr)


class NoseRigEx(ExtraBaseRig):
    def __init__(
        self,
        bridge_tmpjnt,
        nose_tmpjnt,
        nose_l_tmpjnt,
        nose_r_tmpjnt,
        nose_tip_tmpjnt,
        dtl_enable,
        desc,
        skin_parent,
        ctrl_grp_parent,
    ):
        # Casts args to pkrig objects.
        bridge_jnt = loc.Dag(bridge_tmpjnt)
        nose_jnt = loc.Dag(nose_tmpjnt)
        nose_l_jnt = loc.Dag(nose_l_tmpjnt)
        nose_r_jnt = loc.Dag(nose_r_tmpjnt)
        nosetip_jnt = loc.Dag(nose_tip_tmpjnt)

        super(NoseRigEx, self).__init__("Ns", desc, False)

        self.meta.name = prnt.compose(
            "{m}Rig{d}".format(m=self.mod_name, d=self.desc), None, None, "Grp"
        )

        if skin_parent:
            self.meta.snap(skin_parent)
            pru.dag_constraint(skin_parent, self.meta)

        if ctrl_grp_parent:
            self.meta.set_parent(ctrl_grp_parent)

        (
            self.bridge_jnt,
            self.bridge_ctrl,
            self.bridge_ofst,
            self.bridge_con,
            self.bridge_zr,
        ) = self.add_rig_at_joint(
            name="Bridge",
            idx=None,
            side=None,
            cp=rgb.Cp.n_circle,
            tmpjnt=bridge_jnt,
            jnt_par=skin_parent,
            ctrl_par=self.meta,
            inv=False,
        )

        (
            self.nose_jnt,
            self.nose_ctrl,
            self.nose_ofst,
            self.nose_con,
            self.nose_zr,
        ) = self.add_rig_at_joint(
            name="Nose",
            idx=None,
            side=None,
            cp=rgb.Cp.n_circle,
            tmpjnt=nose_jnt,
            jnt_par=self.bridge_jnt,
            ctrl_par=self.bridge_ctrl,
            inv=False,
        )

        if dtl_enable:
            (
                self.nosetip_jnt,
                self.nosetip_ctrl,
                self.nosetip_ofst,
                self.nosetip_con,
                self.nosetip_zr,
            ) = self.add_rig_at_joint(
                name="NoseTip",
                idx=None,
                side=None,
                cp=rgb.Cp.n_circle,
                tmpjnt=nosetip_jnt,
                jnt_par=self.nose_jnt,
                ctrl_par=self.nose_ctrl,
                inv=False,
            )

            (
                self.nose_l_jnt,
                self.nose_l_ctrl,
                self.nose_l_ofst,
                self.nose_l_con,
                self.nose_l_zr,
            ) = self.add_rig_at_joint(
                name="NoseTip",
                idx=None,
                side=rgb.Side.left,
                cp=rgb.Cp.n_circle,
                tmpjnt=nose_l_jnt,
                jnt_par=self.nose_jnt,
                ctrl_par=self.nose_ctrl,
                inv=False,
            )

            (
                self.nose_r_jnt,
                self.nose_r_ctrl,
                self.nose_r_ofst,
                self.nose_r_con,
                self.nose_r_zr,
            ) = self.add_rig_at_joint(
                name="NoseTip",
                idx=None,
                side=rgb.Side.right,
                cp=rgb.Cp.n_circle,
                tmpjnt=nose_r_jnt,
                jnt_par=self.nose_jnt,
                ctrl_par=self.nose_ctrl,
                inv=True,
            )


class SingleEarRigEx(ExtraBaseRig):
    def __init__(self, tmpjnts, side, desc, skin_parent, ctrl_grp_parent):
        super(SingleEarRigEx, self).__init__("Ear", desc, True)

        self.side = side

        self.meta.name = prnt.compose(
            "{m}Rig{d}".format(m=self.mod_name, d=self.desc),
            None,
            self.side,
            "Grp",
        )

        # Main Joints
        if ctrl_grp_parent:
            self.meta.set_parent(ctrl_grp_parent)

        (
            self.jnts,
            self.ctrls,
            self.ofsts,
            self.cons,
            self.zrs,
        ) = self.add_fk_rig(
            name="",
            side=self.side,
            cp=rgb.Cp.n_circle,
            tmpjnts=tmpjnts,
            jnt_par=skin_parent,
            ctrl_par=self.meta,
        )


class EarRigEx(ExtraBaseRig):
    def __init__(
        self, l_ear_tmpjnts, r_ear_tmpjnts, desc, skin_parent, ctrl_grp_parent
    ):
        super(EarRigEx, self).__init__("Ear", desc, False)

        self.meta.name = prnt.compose(
            "{m}Rig{d}".format(m=self.mod_name, d=self.desc), None, None, "Grp"
        )

        # Main Joints
        if skin_parent:
            self.meta.snap(skin_parent)
            pru.dag_constraint(skin_parent, self.meta)

        if ctrl_grp_parent:
            self.meta.set_parent(ctrl_grp_parent)

        self.l_ear_rig = SingleEarRigEx(
            tmpjnts=l_ear_tmpjnts,
            side=rgb.Side.left,
            desc=desc,
            skin_parent=skin_parent,
            ctrl_grp_parent=self.meta,
        )

        self.r_ear_rig = SingleEarRigEx(
            tmpjnts=r_ear_tmpjnts,
            side=rgb.Side.right,
            desc=desc,
            skin_parent=skin_parent,
            ctrl_grp_parent=self.meta,
        )


class TeethRigEx(ExtraBaseRig):
    def __init__(
        self,
        compo,
        main_tmpjnt,
        mid_tmpjnt,
        in_l_tmpjnts,
        out_l_tmpjnt,
        in_r_tmpjnt,
        out_r_tmpjnt,
        desc,
        jnt_par,
        ctrl_par,
    ):
        super(TeethRigEx, self).__init__("{}Teeth".format(compo), desc, False)

        self.meta = self.create_meta()

        # Casts args to pkrig objects.
        main_jnt = loc.Dag(main_tmpjnt)

        if ctrl_par:
            self.meta.set_parent(ctrl_par)

        (
            self.main_jnt,
            self.main_ctrl,
            self.main_ofst,
            self.main_con,
            self.main_zr,
        ) = self.add_rig_at_joint(
            name="Main",
            idx=None,
            side=None,
            cp=rgb.Cp.n_circle,
            tmpjnt=main_jnt,
            jnt_par=jnt_par,
            ctrl_par=self.meta,
            inv=False,
        )

        (
            self.mid_jnts,
            self.mid_ctrls,
            self.mid_ofsts,
            self.mid_cons,
            self.mid_zrs,
        ) = self.add_fk_rig(
            name="Mid",
            side=None,
            cp=rgb.Cp.cube,
            tmpjnts=mid_tmpjnt,
            jnt_par=self.main_jnt,
            ctrl_par=self.main_ctrl,
        )

        (
            self.in_l_jnts,
            self.in_l_ctrls,
            self.in_l_ofsts,
            self.in_l_cons,
            self.in_l_zrs,
        ) = self.add_fk_rig(
            name="In",
            side=rgb.Side.left,
            cp=rgb.Cp.cube,
            tmpjnts=in_l_tmpjnts,
            jnt_par=self.main_jnt,
            ctrl_par=self.main_ctrl,
        )

        (
            self.out_l_jnts,
            self.out_l_ctrls,
            self.out_l_ofsts,
            self.out_l_cons,
            self.out_l_zrs,
        ) = self.add_fk_rig(
            name="Out",
            side=rgb.Side.left,
            cp=rgb.Cp.cube,
            tmpjnts=out_l_tmpjnt,
            jnt_par=self.main_jnt,
            ctrl_par=self.main_ctrl,
        )

        (
            self.in_r_jnts,
            self.in_r_ctrls,
            self.in_r_ofsts,
            self.in_r_cons,
            self.in_r_zrs,
        ) = self.add_fk_rig(
            name="In",
            side=rgb.Side.right,
            cp=rgb.Cp.cube,
            tmpjnts=in_r_tmpjnt,
            jnt_par=self.main_jnt,
            ctrl_par=self.main_ctrl,
        )

        (
            self.out_r_jnts,
            self.out_r_ctrls,
            self.out_r_ofsts,
            self.out_r_cons,
            self.out_r_zrs,
        ) = self.add_fk_rig(
            name="Out",
            side=rgb.Side.right,
            cp=rgb.Cp.cube,
            tmpjnts=out_r_tmpjnt,
            jnt_par=self.main_jnt,
            ctrl_par=self.main_ctrl,
        )


class TongueRigEx(ExtraBaseRig):
    def __init__(self, tmpjnts, desc, skin_parent, ctrl_grp_parent):
        super(TongueRigEx, self).__init__("Tongue", desc, False)
        self.meta = self.create_meta()

        # Main Joints
        if skin_parent:
            self.meta.snap(skin_parent)
            if ctrl_grp_parent != skin_parent:
                pru.dag_constraint(skin_parent, self.meta)

        if ctrl_grp_parent:
            self.meta.set_parent(ctrl_grp_parent)

        (
            self.jnts,
            self.ctrls,
            self.ofsts,
            self.cons,
            self.zrs,
        ) = self.add_fk_rig(
            name="",
            side=None,
            cp=rgb.Cp.n_circle,
            tmpjnts=tmpjnts,
            jnt_par=skin_parent,
            ctrl_par=self.meta,
        )


class TeethTongueRigEx(ExtraBaseRig):
    def __init__(
        self,
        tongue_tmpjnts,
        up_main_tmpjnt,
        up_mid_tmpjnts,
        up_in_l_tmpjnts,
        up_out_l_tmpjnts,
        up_in_r_tmpjnts,
        up_out_r_tmpjnts,
        low_main_tmpjnt,
        low_mid_tmpjnts,
        low_in_l_tmpjnts,
        low_out_l_tmpjnts,
        low_in_r_tmpjnts,
        low_out_r_tmpjnts,
        desc,
        up_skin_parent,
        low_skin_parent,
        ctrl_grp_parent,
    ):
        super(TeethTongueRigEx, self).__init__("Tt", desc, False)

        self.meta.name = prnt.compose(
            "{m}UpRig{d}".format(m=self.mod_name, d=self.desc),
            None,
            None,
            "Grp",
        )
        self.up_grp = self.meta

        self.low_grp = loc.Null()
        self.low_grp.name = prnt.compose(
            "{m}LowRig{d}".format(m=self.mod_name, d=self.desc),
            None,
            None,
            "Grp",
        )

        # Main Joints
        if up_skin_parent:
            self.meta.snap(up_skin_parent)
            pru.dag_constraint(up_skin_parent, self.up_grp)

        if low_skin_parent:
            self.meta.snap(low_skin_parent)
            pru.dag_constraint(low_skin_parent, self.low_grp)

        if ctrl_grp_parent:
            self.meta.set_parent(ctrl_grp_parent)
            self.low_grp.set_parent(ctrl_grp_parent)

        self.tongue_rig = TongueRigEx(
            tmpjnts=tongue_tmpjnts,
            desc=desc,
            skin_parent=low_skin_parent,
            ctrl_grp_parent=self.low_grp,
        )

        self.upteeth_rig = TeethRigEx(
            compo="Up",
            main_tmpjnt=up_main_tmpjnt,
            mid_tmpjnt=up_mid_tmpjnts,
            in_l_tmpjnts=up_in_l_tmpjnts,
            out_l_tmpjnt=up_out_l_tmpjnts,
            in_r_tmpjnt=up_in_r_tmpjnts,
            out_r_tmpjnt=up_out_r_tmpjnts,
            desc=desc,
            jnt_par=up_skin_parent,
            ctrl_par=self.up_grp,
        )

        self.upteeth_rig = TeethRigEx(
            compo="Low",
            main_tmpjnt=low_main_tmpjnt,
            mid_tmpjnt=low_mid_tmpjnts,
            in_l_tmpjnts=low_in_l_tmpjnts,
            out_l_tmpjnt=low_out_l_tmpjnts,
            in_r_tmpjnt=low_in_r_tmpjnts,
            out_r_tmpjnt=low_out_r_tmpjnts,
            desc=desc,
            jnt_par=low_skin_parent,
            ctrl_par=self.low_grp,
        )


class PositionAimRig(ExtraBaseRig):
    def __init__(
        self,
        base_tmpjnt,
        tip_tmpjnt,
        side,
        mod,
        desc,
        z_ofst=0,
        inv=False,
        jnt_par=None,
        ctrl_par=None,
        still_par=None,
    ):
        base_tmpjnt = loc.Dag(base_tmpjnt)
        tip_tmpjnt = loc.Dag(tip_tmpjnt)

        super(PositionAimRig, self).__init__(mod, desc, side)
        self.meta.snap(base_tmpjnt)
        self.still_grp = self.create_still()

        if ctrl_par:
            self.meta.set_parent(ctrl_par)
        if still_par:
            self.still_grp.set_parent(still_par)

        self.base_jnt = self.init_dag(
            loc.Joint(base_tmpjnt), "Base", None, side, "Jnt"
        )
        self.tip_jnt = self.init_dag(
            loc.Joint(tip_tmpjnt), "Tip", None, side, "Jnt"
        )
        if jnt_par:
            self.base_jnt.set_parent(jnt_par)

        self.aim_loc = self.init_dag(
            loc.Locator(), "Tip", None, side, "Target"
        )
        self.aim_zr, self.aim_ex, self.aim_ofst = self._init_tri_grp(
            self.aim_loc, "Tip", None, side
        )
        self.aim_zr.hide = True

        aimat = loc.aim_constraint(
            self.tip_jnt,
            self.base_jnt,
            aim=(0, 0, 1),
            upVector=(0, 1, 0),
            wu=(0, 1, 0),
        )
        mc.delete(aimat)

        self.tip_jnt.set_parent(self.base_jnt)
        attrs = ["rx", "ry", "rz", "jox", "joy", "joz"]
        for attr in attrs:
            self.tip_jnt.attr(attr).v = 0

        self.aim_zr.snap(self.tip_jnt)
        self.aim_ofst.snap(tip_tmpjnt)

        self.ctrl = self.init_dag(
            loc.Controller(rgb.Cp.n_circle), "Aim", None, side, "Ctrl"
        )
        self.ctrl.lhattr("rx", "ry", "s", "v")
        self.zr, self.ofst = self._init_duo_grp(self.ctrl, "Aim", None, side)
        self.zr.snap(self.tip_jnt)
        self.ofst.snap(tip_tmpjnt)

        # Mul
        self.mult = self.init_node(
            loc.create_node("multiplyDivide"), "ZInv", None, side, "Mul"
        )
        if inv:
            self.mult.attr("i2x").v = -1
            self.mult.attr("i2y").v = -1
            self.mult.attr("i2z").v = -1

        self.pma = self.init_node(
            loc.create_node("plusMinusAverage"), "Zpos", None, side, "Pma"
        )
        self.pma.add(ln="default", dv=self.tip_jnt.attr("tz").v)
        self.pma.attr("default") >> self.pma.attr("input1D[0]")
        self.pma.attr("o1") >> self.tip_jnt.attr("tz")

        # connection
        self.ctrl.attr("tx") >> self.aim_loc.attr("tx")
        self.ctrl.attr("ty") >> self.aim_loc.attr("ty")
        self.ctrl.attr("rz") >> self.mult.attr("i1x")
        self.mult.attr("ox") >> self.tip_jnt.attr("rz")
        self.ctrl.attr("tz") >> self.mult.attr("i1y")
        self.mult.attr("oy") >> self.pma.attr("input1D[1]")

        self.ctrl.set_color(None, 1)
        if jnt_par:
            aim = loc.aim_constraint(
                self.aim_loc,
                self.base_jnt,
                aim=(0, 0, 1),
                upVector=(0, 1, 0),
                u=(0, 1, 0),
                wut="objectrotation",
                wuo=jnt_par,
            )

        else:
            aim = loc.aim_constraint(
                self.aim_loc,
                self.base_jnt,
                aim=(0, 0, 1),
                upVector=(0, 1, 0),
                wu=(0, 1, 0),
            )
        self.aim_ex.attr("tz").v = z_ofst

        self.zr.set_parent(self.meta)
        self.aim_zr.set_parent(self.still_grp)


def extra_facial_assembler(fullbody_geo, head_geo):
    fullbody_geo = loc.Dag(fullbody_geo)
    head_geo = loc.Dag(head_geo)

    wrap_geo = pru.dup_and_clean_unused_intermediate_shape(fullbody_geo)
    wrap_geo.name = fullbody_geo.name.replace("Geo", "Wrap")
    wrap_geo.set_parent("*:Still_Grp")

    # try create wrap node
    wrap_node = loc.Node(mc.deformer(wrap_geo, type="wrap")[0])
    wrap_node.name = "Fcl_wrap"
    fcl_basewrap = pru.dup_and_clean_unused_intermediate_shape(head_geo)

    if not wrap_geo.attr("dropoff").exists:
        wrap_geo.add(ln="dropoff", dv=4)
    if not wrap_geo.attr("inflType").exists:
        wrap_geo.add(ln="inflType", dv=2)
    if not wrap_geo.attr("smoothness").exists:
        wrap_geo.add(ln="smoothness", dv=0)

    wrap_geo.attr("dropoff") >> wrap_node.attr("dropoff[0]")
    wrap_geo.attr("inflType") >> wrap_node.attr("inflType[0]")
    wrap_geo.attr("smoothness") >> wrap_node.attr("smoothness[0]")

    name, _, _, _ = prnt.tokenize(head_geo.name)
    fcl_basewrap.name = head_geo.name.replace(name, "{}Base".format(name))
    fcl_basewrap.attr("intermediateObject").v = True
    fcl_basewrap.hide = True
    fcl_basewrap.set_parent("*:Still_Grp")

    fcl_basewrap.attr("worldMesh") >> wrap_node.attr("basePoints[0]")
    head_geo.attr("worldMesh") >> wrap_node.attr("driverPoints[0]")
    wrap_node.attr("maxDistance").v = 0.01

    if bst.get_connected_blend_shape(fullbody_geo):
        bsn = bst.get_connected_blend_shape(fullbody_geo)[0]
        blend_attrs = mc.aliasAttr(bsn.name, query=True)

        blend_index = 0
        if blend_attrs:
            blend_index = len(blend_attrs) / 2

        mc.blendShape(
            bsn.name,
            edit=True,
            target=(fullbody_geo.name, blend_index, wrap_geo.name, 1),
        )
        bst.set_blend_shape_weight_of_target(bsn, wrap_geo, 1)

    else:
        bsn = bst.create_front_of_chain_blend_shape(fullbody_geo, wrap_geo, 1)
        bsn.name = "FclWrap_Bsn"
