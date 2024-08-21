from imp import reload
import maya.cmds as mc
import maya.OpenMaya as om
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
reload(rgb)


class IkFkArmRig(rig_base.Rigbase):
    def __init__(
        self,
        uparm_tmpjnt,
        elbow_tmpjnt,
        wrist_tmpjnt,
        side,
        desc="",
        double_jnt=False,
        ikroot_space=None,
        ik_space=None,
        fk_par=None,
        jnt_par=None,
        ctrl_par=None,
        still_par=None,
    ):
        super(IkFkArmRig, self).__init__("Arm", desc, side)
        self.meta = self.create_meta(ctrl_par)
        self.still = self.create_still(still_par)
        self.space = self.create_space(self.meta)

        uparm_tmpjnt = loc.Dag(uparm_tmpjnt)
        elbow_tmpjnt = loc.Dag(elbow_tmpjnt)
        wrist_tmpjnt = loc.Dag(wrist_tmpjnt)

        # Cast
        if double_jnt:
            compo_names = ["Up", "Double", "Fore", "Elbow", "Wrist"]
            up_vec, low_vec = utils.get_double_jnt_pos(
                uparm_tmpjnt, elbow_tmpjnt, wrist_tmpjnt, double_jnt
            )

            double_tmpjnt = self.init_dag(
                loc.Joint(), "Double", None, side, "TmpJnt"
            )
            double_tmpjnt.set_pos((up_vec.x, up_vec.y, up_vec.z))
            double_tmpjnt.snap_rot(uparm_tmpjnt)

            elbowdb_tmpjnt = self.init_dag(
                loc.Joint(), "ElbowDb", None, side, "TmpJnt"
            )

            elbowdb_tmpjnt.set_pos((low_vec.x, low_vec.y, low_vec.z))
            elbowdb_tmpjnt.snap_rot(elbow_tmpjnt)

            double_tmpjnt.set_parent(uparm_tmpjnt)
            elbowdb_tmpjnt.set_parent(elbow_tmpjnt)

            arm_tmpjnts = [
                uparm_tmpjnt,
                double_tmpjnt,
                elbow_tmpjnt,
                elbowdb_tmpjnt,
                wrist_tmpjnt,
            ]

        else:
            compo_names = ["Up", "Elbow", "Wrist"]
            arm_tmpjnts = [
                uparm_tmpjnt,
                elbow_tmpjnt,
                wrist_tmpjnt,
            ]

        jnt_grp = loc.Null(lnt.construct("ArmJnt", None, side, "Grp"))
        jnt_grp.set_parent(self.still)
        if ctrl_par:
            loc.parent_constraint(ctrl_par, jnt_grp)
            loc.scale_constraint(ctrl_par, jnt_grp)

        # Create Joint
        self.fk_jnts = []
        self.ik_jnts = []  # self.ik_jnts : list[loc.Joint]
        self.arm_jnts = []
        self.par_cons = []

        for name, tmpjnt in zip(compo_names, arm_tmpjnts):
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
                armjnt.set_parent(self.arm_jnts[-1])

            else:
                fkjnt.set_parent(jnt_grp)
                ikjnt.set_parent(jnt_grp)
                if jnt_par:
                    armjnt.set_parent(jnt_par)

            self.fk_jnts.append(fkjnt)
            self.ik_jnts.append(ikjnt)
            self.arm_jnts.append(armjnt)
            self.par_cons.append(con)

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
                ee=self.ik_jnts[-1],
                sol="ikRPsolver",
                n=lnt.construct("IkArm", None, self.side, "IkHandle"),
            )[0]
        )
        ik_handle.hide = True

        for jnt in self.ik_jnts:
            jnt.attr("rx").v = 0
            jnt.attr("ry").v = 0
            jnt.attr("rz").v = 0

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
            loc.Controller(loc.cp.cube), "IkWrist", None, self.side, "Ctrl"
        )
        self.ik_ctrl.lhattr("s", "v")

        self.ik_zr, self.ik_ofst = self._init_duo_grp(
            self.ik_ctrl,
            "IkWrist",
            None,
            self.side,
        )

        self.ik_zr.snap(self.ik_jnts[-1])
        ik_handle.set_parent(self.ik_ctrl)
        self.ik_zr.set_parent(self.meta)

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
            self.ik_jnts[0], elbow_tmpjnt, self.ik_jnts[-1]
        )
        self.ik_pole_zr.set_pos((pole_pos.x, pole_pos.y, pole_pos.z))
        self.ik_pole_ctrl.lhattr("r", "s")
        mc.poleVectorConstraint(self.ik_pole_ctrl, ik_handle)
        mc.orientConstraint(self.ik_ctrl, self.ik_jnts[-1])

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
            mc.renameAttr(self.ik_ctrl.attr("space"), "wristSpace")

        self.create_space_switch(
            {
                "World": loc.main_grp.worldspace_grp,
                "Wrist": "{}".format(self.ik_ctrl),
            },
            self.ik_pole_zr,
            self.ik_ctrl,
            self.space,
        )
        self.ik_ctrl.attr("space").v = 1
        mc.renameAttr(self.ik_ctrl.attr("space"), "ikPoleSpace")

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

        ikfk_zr.snap_pos(self.arm_jnts[-1])
        loc.parent_constraint(self.arm_jnts[-1], ikfk_zr)
        ikfk_zr.set_parent(self.meta)
        self.ikfk_ctrl.lhattr("t", "r", "s", "v")
        self.ikfk_ctrl.add(ln="ikFkSwitch", min=0, max=1, k=True)

        # reverse
        rev = self.init_node(
            loc.create_node("reverse"), "IkFk", None, self.side, "Rev"
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
        self.skin_jnts = self.arm_jnts
        utils.add_to_skin_set(self.skin_jnts)

        # Detail Vis
        utils.connect_visiblity()

        # Set Parent
        self.ctrl_parent = self.init_dag(
            loc.Null(), "", None, self.side, "CtrlParent"
        )
        self.ctrl_parent.set_parent(self.meta)
        loc.parent_constraint(self.arm_jnts[-1], self.ctrl_parent)
        loc.scale_constraint(self.arm_jnts[-1], self.ctrl_parent)

        self.joint_parent = self.arm_jnts[-1]
