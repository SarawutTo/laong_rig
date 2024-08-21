# System Modules
from imp import reload

# Maya modules
import maya.cmds as mc

#  modules
from . import rig_global as rgb
from . import core as loc
from . import utils as lu
from . import rig_base
from . import naming_tools as lnt


class HeadRig(rig_base.Rigbase):
    def __init__(
        self,
        head_jnt,
        desc="",
        shape=loc.cp.cube,
        ctrl_par=None,
        jnt_par=None,
        still_par=None,
    ):
        super(HeadRig, self).__init__("Head", desc, None)
        self.meta = self.create_meta(ctrl_par)
        self.space = self.create_space(self.meta)
        self.still = self.create_still(still_par)

        # Cast
        head_jnt = loc.Dag(head_jnt)

        self.ctrl = self.init_dag(
            loc.Controller(shape), "", None, None, "Ctrl"
        )
        self.ctrl.lhattr("v")
        self.ctrl.set_color(None, 0)

        self.jnt = self.init_dag(loc.Joint(), "", None, None, "Jnt")
        self.zr, self.ofst = self._init_duo_grp(self.ctrl, "", None, None)
        loc.parent_constraint(self.ctrl, self.jnt)
        loc.scale_constraint(self.ctrl, self.jnt)
        self.zr.snap(head_jnt)
        self.zr.set_parent(self.meta)

        if jnt_par:
            self.jnt.set_parent(jnt_par)

        head_piv = self.init_dag(loc.Null(), "HeadSpace", None, None, "Piv")
        head_piv.snap(head_jnt)
        head_piv.set_parent(self.space)

        world_piv = self.init_dag(loc.Null(), "HeadWorld", None, None, "Piv")
        world_piv.set_parent(self.still)

        # Parent to root
        loc.point_constraint(head_piv, world_piv)
        con = loc.parent_constraint(head_piv, world_piv, self.zr)

        lu.add_divide_attr(self.ctrl, "spaceControl")
        space_attr = self.ctrl.add(ln="space", min=0, max=1, k=True, dv=1)

        # reverse
        rev = self.init_node(
            loc.create_node("reverse"), "Space", None, self.side, "Rev"
        )
        space_attr >> rev.attr("inputX")
        # Set Constraint weight
        space_attr >> con.attr("w0")
        rev.attr("outputX") >> con.attr("w1")


class HeadSqRig(rig_base.Rigbase):
    def __init__(
        self,
        head_tmpjnt,
        mid_tmpjnt,
        upbase_tmpjnt,
        uptip_tmpjnt,
        lowbase_tmpjnt,
        lowtip_tmpjnt,
        desc,
        ctrl_par,
        jnt_par,
    ):
        """
        Args:
            head_tmpjnt (str):
            mid_tmpjnt (str):
            upbase_tmpjnt (str):
            uptip_tmpjnt (str):
            lowbase_tmpjnt (str):
            lowtip_tmpjnt (str):
            desc (str):
            ctrl_par (loc.Dag):
            jnt_par (loc.Dag):
        """

        # Casts
        head_loc = loc.Dag(head_tmpjnt)
        mid_loc = loc.Dag(mid_tmpjnt)
        upbase_loc = loc.Dag(upbase_tmpjnt)
        uptip_loc = loc.Dag(uptip_tmpjnt)
        lowbase_loc = loc.Dag(lowbase_tmpjnt)
        lowtip_loc = loc.Dag(lowtip_tmpjnt)

        # Main Groups
        super(HeadSqRig, self).__init__("Hd", desc, None)
        self.meta = self.create_meta(ctrl_par)
        if not jnt_par:
            self.still_grp = self.init_dag(
                loc.Null(), "Still", None, None, "Grp"
            )
        else:
            self.still_grp = jnt_par

        def _add_rig_skin_joints(
            name, idx, tarjnt, rigpar, skinpar, connect, space_jnt
        ):
            """Create rigjnt and skinjnt at tarjnt and parent to jntpar

            Args:
                name (str):
                index (int):
                target (loc.Dag):
                rigpar (loc.Dag):
                skinpar (loc.Dag):
                connect (bol): Is connect t r s.
                space_jnt (bol): Create Spc Jnt

            Return:
                loc.Dag: skinjnt.
                loc.Dag: rigjnt.
            """

            skinjnt = self.init_dag(
                loc.Joint(at=tarjnt), name, idx, None, "Jnt"
            )
            rigjnt = self.init_dag(
                loc.Joint(at=tarjnt, style=2), name, idx, None, "RigJnt"
            )

            if space_jnt:
                spc_rigjnt = self.init_dag(
                    loc.Joint(at=tarjnt, style=2),
                    "Spc{}".format(name),
                    idx,
                    None,
                    "RigJnt",
                )

                spc_skinjnt = self.init_dag(
                    loc.Joint(at=tarjnt, style=2),
                    "Spc{}".format(name),
                    idx,
                    None,
                    "Jnt",
                )

                lu.connect_trs(spc_rigjnt, spc_skinjnt)

            skinjnt.ssc = False
            rigjnt.ssc = False

            if connect:
                lu.connect_trs(rigjnt, skinjnt)

            if space_jnt:
                rigjnt.set_parent(spc_rigjnt)
                skinjnt.set_parent(spc_skinjnt)
                spc_rigjnt.set_parent(rigpar)
                spc_skinjnt.set_parent(skinpar)

                return rigjnt, skinjnt, spc_rigjnt, spc_skinjnt
            else:
                rigjnt.set_parent(rigpar)
                skinjnt.set_parent(skinpar)

                return rigjnt, skinjnt

        self.head_rigjnt, self.head_jnt = _add_rig_skin_joints(
            "Head", None, head_loc, self.meta, self.still_grp, False, False
        )
        self.mid_rigjnt, self.mid_jnt = _add_rig_skin_joints(
            "Mid", None, mid_loc, self.head_rigjnt, self.head_jnt, True, False
        )

        # Up
        self.upbase_rigjnt, self.upbase_jnt = _add_rig_skin_joints(
            "Up", 1, upbase_loc, self.head_rigjnt, self.head_jnt, True, False
        )
        (
            self.up_rigjnt,
            self.up_jnt,
            spcup_rigjnt,
            spcup_jnt,
        ) = _add_rig_skin_joints(
            "Up", 2, uptip_loc, self.head_rigjnt, self.head_jnt, True, True
        )
        self.uptip_rigjnt, self.uptip_jnt = _add_rig_skin_joints(
            "Up", 3, uptip_loc, self.head_rigjnt, self.head_jnt, True, False
        )

        # Low
        self.lowbase_rigjnt, self.lowbase_jnt = _add_rig_skin_joints(
            "Low", 1, lowbase_loc, self.head_rigjnt, self.head_jnt, True, False
        )
        (
            self.low_rigjnt,
            self.low_jnt,
            spclow_rigjnt,
            spclow_jnt,
        ) = _add_rig_skin_joints(
            "Low", 2, lowtip_loc, self.head_rigjnt, self.head_jnt, True, True
        )
        self.lowtip_rigjnt, self.lowtip_jnt = _add_rig_skin_joints(
            "Low", 3, lowtip_loc, self.head_rigjnt, self.head_jnt, True, False
        )

        # Add Constraint
        # Up Constraint
        mc.pointConstraint(self.mid_rigjnt, self.upbase_rigjnt, mo=True)
        mc.pointConstraint(self.upbase_rigjnt, self.uptip_rigjnt, spcup_rigjnt)
        mc.aimConstraint(
            self.uptip_rigjnt,
            spcup_rigjnt,
            aim=[0, 1, 0],
            u=[0, 1, 0],
            wut="object",
            wuo=self.meta,
        )

        # Low Constraint
        mc.pointConstraint(self.mid_rigjnt, self.lowbase_rigjnt, mo=True)
        mc.pointConstraint(
            self.lowbase_rigjnt, self.lowtip_rigjnt, spclow_rigjnt
        )
        mc.aimConstraint(
            self.lowtip_rigjnt,
            spclow_rigjnt,
            aim=[0, -1, 0],
            u=[0, 1, 0],
            wut="object",
            wuo=self.meta,
        )

        # Controllers
        def _create_controller(loca, compo):
            """
            Args:
                loc (loc.Dag):
                compo (str)

            Returns:
                loc.Dag: A controller.
                loc.Dag: A zero group.
            """
            ctrl = self.init_dag(
                loc.Controller(loc.cp.cube), compo, None, None, "Ctrl"
            )
            ctrl.lhattr("r", "s", "v")
            ctrl.set_color(None, 0)
            zr = self.init_dag(loc.Group(ctrl), compo, None, None, "Zr")
            zr.snap(loca)
            zr.set_parent(self.meta)

            return ctrl, zr

        (self.lower_ctrl, self.lower_ctrl_zr) = _create_controller(
            lowtip_loc, "Low"
        )
        (self.middle_ctrl, self.middle_ctrl_zr) = _create_controller(
            mid_loc, "Mid"
        )
        (self.upper_ctrl, self.upper_ctrl_zr) = _create_controller(
            uptip_loc, "Up"
        )

        mc.parentConstraint(self.lower_ctrl, self.lowtip_rigjnt)
        mc.parentConstraint(self.upper_ctrl, self.uptip_rigjnt)
        mc.parentConstraint(self.middle_ctrl, self.mid_rigjnt)

        # Attributes
        for ctrl, jnt in zip(
            (self.lower_ctrl, self.upper_ctrl),
            (self.low_rigjnt, self.up_rigjnt),
        ):
            lu.add_divide_attr(ctrl, "hdAttr")
            ctrl.add(ln="slide", k=True)
            ctrl.add(ln="squash", k=True, dv=0)
            ctrl.add(ln="autoSquash", k=True, dv=0, min=0, max=1)
            ctrl.attr("slide") >> jnt.attr("tx")

        def add_local_xform(name, zr, ctrl):
            # Add a compound attribute for the vector
            loct = zr.add(ln="localTranslate", at="double3")

            # Add child attributes for X, Y, and Z components of the vector
            zr.add(ln="localTranslateX", parent="localTranslate")
            zr.add(ln="localTranslateY", parent="localTranslate")
            zr.add(ln="localTranslateZ", parent="localTranslate")
            mulmat = self.init_dag(
                loc.create_node("multMatrix"), name, None, None, "MulMat"
            )
            decom = self.init_dag(
                loc.create_node("decomposeMatrix"), name, None, None, "Decomp"
            )
            zr.attr("matrix") >> mulmat.attr("matrixIn[0]")
            ctrl.attr("matrix") >> mulmat.attr("matrixIn[1]")

            mulmat.attr("o") >> decom.attr("inputMatrix")
            decom.attr("ot") >> loct

        add_local_xform("Mid", self.middle_ctrl_zr, self.middle_ctrl)

        def _add_squash(compo_zr, compo_ctrl, jnt, component):
            compo_ctrl = loc.Dag(compo_ctrl)
            compo_zr = loc.Dag(compo_zr)
            compo = "{}Squash".format(component)
            compo_shape = compo_ctrl.get_shape()

            # Get Ctrl Distance
            dist = self.init_node(
                loc.create_node("distanceBetween"), compo, None, None, "Dist"
            )
            add_local_xform(compo, compo_zr, compo_ctrl)
            compo_zr.attr("localTranslate") >> dist.attr("p1")
            self.middle_ctrl_zr.attr("localTranslate") >> dist.attr("p2")

            # Get Original Distance
            orivec = self.middle_ctrl.world_vec - compo_ctrl.world_vec
            ori_len = compo_shape.add(ln="oriLen", k=True, dv=orivec.length())
            ori_len.lock = True

            # Scale
            div = self.init_node(
                loc.create_node("multiplyDivide"), compo, None, None, "Div"
            )
            div.attr("op").v = rgb.Operation.MultDivide.divide

            dist.attr("distance") >> div.attr("i1x")
            ori_len >> div.attr("i2x")

            pow = self.init_node(
                loc.create_node("multiplyDivide"), compo, None, None, "Pow"
            )
            pow.attr("op").v = rgb.Operation.MultDivide.power

            div.attr("ox") >> pow.attr("i1x")
            pow.attr("i2x").v = -1

            autosq_sum = self.init_node(
                loc.create_node("addDoubleLinear"),
                "{}AutoSum".format(compo),
                None,
                None,
                "Add",
            )
            autosq_sum.add(ln="default", k=True, dv=-1)

            autosq_sum.attr("default") >> autosq_sum.attr("i1")
            pow.attr("ox") >> autosq_sum.attr("i2")

            amper = self.init_node(
                loc.create_node("multDoubleLinear"), compo, None, None, "Amp"
            )
            compo_ctrl.attr("autoSquash") >> amper.attr("i1")
            autosq_sum.attr("o") >> amper.attr("i2")

            sq_sum = self.init_node(
                loc.create_node("addDoubleLinear"),
                "{}Sum".format(compo),
                None,
                None,
                "Pma",
            )
            amper.attr("o") >> sq_sum.attr("i1")
            compo_ctrl.attr("squash") >> sq_sum.attr("i2")

            sq_norm = self.init_node(
                loc.create_node("addDoubleLinear"), compo, None, None, "Add"
            )
            sq_norm.add(ln="default", dv=1, min=0, max=1)
            sq_norm.attr("default") >> sq_norm.attr("i1")
            sq_sum.attr("o") >> sq_norm.attr("i2")

            sq_norm.attr("o") >> jnt.attr("sx")
            sq_norm.attr("o") >> jnt.attr("sz")

        _add_squash(
            self.lower_ctrl_zr, self.lower_ctrl, self.low_rigjnt, "Low"
        )
        _add_squash(self.upper_ctrl_zr, self.upper_ctrl, self.up_rigjnt, "Up")

        # # Skin Jnt
        # mc.sets(self.head_jnt, self.up_jnt, self.low_jnt, n="Hd_SkinJnts")
