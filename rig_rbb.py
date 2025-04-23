# System Modules
import math
from imp import reload

# Maya Modules
import maya.cmds as mc
import maya.OpenMaya as om

# pkrig Modules
from . import core as loc
from . import utils
from . import rig_base as prb
from . import naming_tools as prnt
from . import rig_global as rgb

reload(loc)
reload(prb)
reload(prnt)


class RubberLineRig(prb.Rigbase):
    def __init__(
        self,
        mod,
        desc,
        side,
        color,
        skin_parent,
        ctrl_grp_parent,
        still_grp_parent,
        crv,
        spans,
        joint_amount,
    ):
        # Casts args to pkrig object
        self.crv = loc.Dag(crv)
        self.crv_shp = self.crv.get_shape()
        self.crv_spans = self.crv_shp.attr("spans").v

        # Main Groups
        super(RubberLineRig, self).__init__(None, mod, desc, False)
        self.meta.name = prnt.compose(
            "{m}Rig{d}".format(m=self.mod_name, d=desc), None, side, "Grp"
        )
        if ctrl_grp_parent:
            self.meta.set_parent(ctrl_grp_parent)

        if skin_parent:
            loc.parent_constraint(skin_parent, self.meta.name)

        self.scale_grp = self.init_dag(loc.Null(), "Sca", None, side, "Grp")
        self.scale_grp.set_parent(self.meta)

        self.ctrl_grp = self.init_dag(loc.Null(), "Ctrl", None, side, "Grp")
        self.ctrl_grp.set_parent(self.scale_grp)

        self.still_grp = self.init_dag(loc.Null(), "Still", None, side, "Grp")
        if still_grp_parent:
            self.still_grp.set_parent(still_grp_parent)

        self.skin_jnt = self.init_dag(loc.Joint(), "Master", None, side, "Jnt")
        self.skin_jnt.attr("drawStyle").v = loc.DrawStyle.none
        if skin_parent:
            self.skin_jnt.set_parent(skin_parent)

        # Create NURBS surface
        mc.rebuildCurve(
            self.crv, ch=False, rpo=True, kt=False, kr=0, end=1, s=spans
        )
        a_crv = loc.Dag(
            mc.offsetCurve(
                self.crv, ch=False, rn=False, d=-1, ugn=False, cb=1
            )[0]
        )
        mc.rebuildCurve(
            a_crv, ch=False, rpo=True, kt=False, kr=0, end=1, s=spans
        )
        b_crv = loc.Dag(
            mc.offsetCurve(self.crv, ch=False, rn=False, d=1, ugn=False, cb=1)[
                0
            ]
        )
        mc.rebuildCurve(
            b_crv, ch=False, rpo=True, kt=False, kr=0, end=1, s=spans
        )

        self.nrb = self.init_dag(
            loc.Dag(mc.loft(b_crv, a_crv, ch=False)[0]),
            "Main",
            None,
            side,
            "Nrb",
        )
        mc.rebuildSurface(
            self.nrb,
            ch=False,
            rpo=True,
            kr=2,
            kc=False,
            su=1,
            end=1,
            sv=spans,
        )
        self.nrb.set_parent(self.still_grp)

        # Main Controller
        self.main_ctrl = self.init_dag(
            loc.Controller(loc.Cp.square), "Main", None, side, "Ctrl"
        )
        self.main_ctrl.lhattrs("v")
        self.main_ctrl.rotate_shape((90, 0, 0))
        self.main_ctrl.set_default_color(color, 0)

        self.main_ctrl_zr = self.init_dag(
            loc.group(self.main_ctrl), "MainCtrl", None, side, "Zr"
        )
        self.main_ctrl_zr.snap(self.crv)
        self.main_ctrl_zr.set_parent(self.ctrl_grp)

        self.sub_ctrls = []
        self.sub_ctrl_ofsts = []
        self.sub_rigjnts = []
        for ix in range(spans + 1):
            idx = ix + 1
            curr_ctrl = self.init_dag(
                loc.Controller(loc.Cp.sphere), "Sub", idx, side, "Ctrl"
            )
            curr_ctrl.scale_shape(4.5)
            curr_ctrl.set_default_color(color, 1)
            if idx == 1:
                curr_ctrl.scale_shape(1.2)
            curr_ctrl.lhattrs("s", "v")
            self.sub_ctrls.append(curr_ctrl)

            ctrl_ofst = self.init_dag(
                loc.group(curr_ctrl), "SubCtrl", idx, side, "Ofst"
            )
            self.sub_ctrl_ofsts.append(ctrl_ofst)

            ctrl_zr = self.init_dag(
                loc.group(ctrl_ofst), "SubCtrl", idx, side, "Zr"
            )
            ctrl_zr.set_parent(self.main_ctrl)

            # Positioning
            pos, norm, _, tv = loc.get_pnuv_at_surface_param(
                nrb=self.nrb, pu=0.5, pv=ix
            )

            obj_pos = om.MVector(0, 0, 0)
            up_pos = om.MVector(*norm)
            up_pos.normalize()
            aim_pos = om.MVector(*tv)
            aim_pos.normalize()

            # Get U-V-W Vector
            u_vec = aim_pos - obj_pos
            u_vec.normalize()
            v_vec = up_pos - obj_pos
            v_vec.normalize()
            w_vec = aim_pos ^ up_pos
            w_vec.normalize()
            mtx_list = [
                v_vec.x,
                v_vec.y,
                v_vec.z,
                0,
                u_vec.x,
                u_vec.y,
                u_vec.z,
                0,
                w_vec.x,
                w_vec.y,
                w_vec.z,
                0,
                0,
                0,
                0,
                1,
            ]
            matx = om.MMatrix()
            om.MScriptUtil.createMatrixFromList(mtx_list, matx)
            xform_mtx = om.MTransformationMatrix(matx)

            euler_rot = xform_mtx.eulerRotation()
            rot_value = [
                math.degrees(euler_rot.x),
                math.degrees(euler_rot.y),
                math.degrees(euler_rot.z),
            ]
            mc.xform(ctrl_zr, t=pos, ws=True)
            mc.xform(ctrl_zr, ro=rot_value, ws=True)

            # Control joints
            curr_jnt = self.init_dag(
                loc.create_joint_at(curr_ctrl), "Sub", idx, side, "RigJnt"
            )
            curr_jnt.attr("drawStyle").v = loc.DrawStyle.none
            curr_jnt.set_parent(curr_ctrl)
            self.sub_rigjnts.append(curr_jnt)

        # Binding Skin to Nurb Surface
        skc = mc.skinCluster(self.sub_rigjnts, self.nrb)[0]
        for ix in range(spans + 1):
            curr_idx = ix + 1
            if ix == 0:
                curr_idx = "0:1"
            elif ix == len(self.sub_rigjnts) - 1:
                curr_idx = "{s1}:{s2}".format(s1=spans + 1, s2=spans + 2)
            curr_cvs = "{r}.cv[0:3][{i}]".format(r=self.nrb, i=curr_idx)
            mc.skinPercent(skc, curr_cvs, tv=[(self.sub_rigjnts[ix], 1)])

        # Smooth skin
        start_id = "{r}.cv[0:3][1]".format(r=self.nrb)
        mc.skinPercent(skc, start_id, tv=[(self.sub_rigjnts[1], 0.35)])
        end_id = "{r}.cv[0:3][{s}]".format(r=self.nrb, s=spans + 1)
        mc.skinPercent(skc, end_id, tv=[(self.sub_rigjnts[-2], 0.35)])

        # Generating POSIs
        self.dtl_ctrl_grp = self.init_dag(
            loc.Null(), "DtlCtrl", None, side, "Grp"
        )
        self.dtl_ctrl_grp.set_parent(self.main_ctrl)

        self.dtl_ctrls = []
        for ix in range(joint_amount + 1):
            idx = ix + 1
            posi = self.init_node(
                loc.create("pointOnSurfaceInfo"), "Dtl", idx, side, "Posi"
            )
            posi.add(ln="offset", dv=0, k=True)

            self.nrb.attr("worldSpace[0]") >> posi.attr("is")
            posi.attr("parameterU").v = 0.5
            div = float(joint_amount + 1)
            mult = float(ix)
            posi.attr("parameterV").v = (spans / (div - 1)) * mult

            w_vec_norm = self.init_node(
                loc.create("vectorProduct"), "WVecNorm", idx, side, "Vecprod"
            )
            w_vec_norm.attr("op").v = loc.Operator.cross
            w_vec_norm.attr("normalizeOutput").v = 1
            posi.attr("normalizedNormal") >> w_vec_norm.attr("i1")
            posi.attr("normalizedTangentV") >> w_vec_norm.attr("i2")

            fbf_mtx = self.init_node(
                loc.create("fourByFourMatrix"), "Dtl", idx, side, "Fbf"
            )
            de_mtx = self.init_node(
                loc.create("decomposeMatrix"), "Dtl", idx, side, "Decomp"
            )
            mult_mtx = self.init_node(
                loc.create("multMatrix"), "Dtl", idx, side, "MultMat"
            )

            # Plug in 4b4 Matrix
            # 0-x 1-y 2-z 3-translate
            posi.attr("normalizedNormalX") >> fbf_mtx.attr("in00")
            posi.attr("normalizedNormalY") >> fbf_mtx.attr("in01")
            posi.attr("normalizedNormalZ") >> fbf_mtx.attr("in02")

            posi.attr("normalizedTangentVX") >> fbf_mtx.attr("in10")
            posi.attr("normalizedTangentVY") >> fbf_mtx.attr("in11")
            posi.attr("normalizedTangentVZ") >> fbf_mtx.attr("in12")

            w_vec_norm.attr("outputX") >> fbf_mtx.attr("in20")
            w_vec_norm.attr("outputY") >> fbf_mtx.attr("in21")
            w_vec_norm.attr("outputZ") >> fbf_mtx.attr("in22")

            posi.attr("px") >> fbf_mtx.attr("in30")
            posi.attr("py") >> fbf_mtx.attr("in31")
            posi.attr("pz") >> fbf_mtx.attr("in32")

            # Add Detail Controller
            ctrl = self.init_dag(
                loc.Controller(loc.Cp.cube), "Dtl", idx, side, "Ctrl"
            )
            ctrl.lhattrs("v")
            ctrl.scale_shape(color, 2)
            self.dtl_ctrls.append(ctrl)
            ctrl.set_default_color(2)

            ctrl_ofst = self.init_dag(
                loc.group(ctrl), "DtlCtrl", idx, side, "Ofst"
            )

            ctrl_zr = self.init_dag(
                loc.group(ctrl_ofst), "DtlCtrl", idx, side, "Zr"
            )
            ctrl_zr.set_parent(self.dtl_ctrl_grp)

            fbf_mtx.attr("o") >> mult_mtx.attr("matrixIn[0]")
            ctrl_zr.attr("pim") >> mult_mtx.attr("matrixIn[1]")
            mult_mtx.attr("matrixSum") >> de_mtx.attr("inputMatrix")

            de_mtx.attr("ot") >> ctrl_zr.attr("t")
            de_mtx.attr("or") >> ctrl_zr.attr("r")

            # Adding Offset along V axis
            ctrl_shp = ctrl.get_shape()
            ctrl_shp.add(ln="offsetV", k=True)

            ofst_u_mdv = self.init_node(
                loc.create("multiplyDivide"), "OfstU", idx, side, "Mdv"
            )
            ofst_u_mdv.attr("i2x").v = 0.1
            ctrl_shp.attr("offsetV") >> ofst_u_mdv.attr("i1x")

            ofst_u_pma = self.init_node(
                loc.create("plusMinusAverage"), "OfstU", idx, side, "Pma"
            )
            ofst_u_pma.add(ln="default", k=True)
            ofst_u_pma.attr("default").v = posi.attr("parameterV").v
            ofst_u_pma.attr("default") >> ofst_u_pma.attr("input1D").last()

            ofst_u_mdv.attr("ox") >> ofst_u_pma.attr("input1D").last()
            ofst_u_pma.attr("output1D") >> posi.attr("parameterV")

        self.skin_jnts = []
        for ix in range(joint_amount + 1):
            idx = ix + 1
            jnt = self.init_dag(
                loc.create_joint_at(self.dtl_ctrls[ix]),
                "Skin",
                idx,
                side,
                "Jnt",
            )

            jnt.set_parent(self.skin_jnt)
            loc.parent_constraint(self.dtl_ctrls[ix], jnt)
            loc.scale_constraint(self.dtl_ctrls[ix], jnt)
            self.skin_jnts.append(jnt)

        # Cleanup
        mc.select(cl=True)
        mc.delete(self.crv)
        mc.delete(a_crv)
        mc.delete(b_crv)

        # Vis Attrs
        self.detail_vis = self.meta.add(
            ln="detailVis", min=0, max=1, at="short"
        )
        loc.connect_shape_vises(self.detail_vis, self.dtl_ctrls)
        self.detail_vis.v = 1


class RubberBandRig(prb.Rigbase):
    def __init__(
        self,
        crv,
        mod,
        ctrl_amount,
        dtl_amount,
        side,
        desc="",
        jnt_par=None,
        ctrl_par=None,
        still_par=None,
    ):
        # Casts args to pkrig object
        self.crv = loc.Curve(crv)
        # mc.xform(self.crv, cp=True)
        self.crv_shp = self.crv.get_shape()

        # Main Groups
        super(RubberBandRig, self).__init__(mod, desc, False)
        self.meta = self.create_meta(ctrl_par)

        if jnt_par:
            loc.parent_constraint(jnt_par, self.meta.name)

        self.scale_grp = self.init_dag(loc.Null(), "Sca", None, side, "Grp")
        self.scale_grp.set_parent(self.meta)

        self.ctrl_grp = self.init_dag(loc.Null(), "Ctrl", None, side, "Grp")
        self.ctrl_grp.set_parent(self.scale_grp)

        self.still_grp = self.init_dag(loc.Null(), "Still", None, side, "Grp")
        if still_par:
            self.still_grp.set_parent(still_par)

        self.skin_jnt = self.init_dag(
            loc.Joint(style=2), "Root", None, side, "Jnt"
        )
        if jnt_par:
            self.skin_jnt.snap(jnt_par)
            self.skin_jnt.set_parent(jnt_par)

        # Createting NURBS Surface
        a_crv = loc.Curve(mc.duplicate(self.crv, rr=True)[0])
        a_crv.scale_shape(1.1)

        b_crv = loc.Curve(mc.duplicate(self.crv, rr=True)[0])
        b_crv.scale_shape(0.9)

        self.nrb = self.init_dag(
            loc.Surface(mc.loft(b_crv, a_crv, ch=False)[0]),
            "Main",
            None,
            side,
            "Nrb",
        )
        mc.rebuildSurface(
            self.nrb,
            ch=False,
            rpo=True,
            kr=2,
            kc=False,
            su=1,
            end=1,
            sv=ctrl_amount,
        )

        self.nrb.set_parent(self.still_grp)

        # Main Controller
        self.main_ctrl = self.init_dag(
            loc.Controller(rgb.Cp.square), "Main", None, side, "Ctrl"
        )
        self.main_ctrl.lhattr("v")
        self.main_ctrl.rotate_shape(90, 0, 0)
        self.main_ctrl.set_color(None, 0)

        self.main_zr = self.init_dag(
            loc.Group(self.main_ctrl), "Main", None, side, "Zr"
        )
        self.main_zr.snap(self.crv)
        self.main_zr.set_parent(self.ctrl_grp)

        self.ctrls = []
        self.ofsts = []
        self.jnts = []

        for ix in range(ctrl_amount):
            idx = ix + 1
            ctrl = self.init_dag(
                loc.Controller(rgb.Cp.cube), "", idx, side, "Ctrl"
            )
            ctrl.scale_shape(4.5)
            ctrl.set_color(None, 1)
            ctrl.lhattr("s", "v")
            self.ctrls.append(ctrl)

            ofst, zr = self._init_duo_grp(ctrl, "", idx, side)
            self.ofsts.append(ofst)
            # zr.set_parent(self.main_ctrl)

            # Positioning
            pos, norm, _, tv = self.nrb.get_pnuv_on_sfc(
                param_u=0.5, param_v=ix, space=rgb.MSpace.world
            )

            obj_pos = om.MVector(0, 0, 0)
            up_pos: om.MVector = norm
            up_pos.normalize()
            aim_pos: om.MVector = tv
            aim_pos.normalize()

            # Get U-V-W Vector
            u_vec: om.MVector = aim_pos - obj_pos
            u_vec.normalize()
            v_vec: om.MVector = up_pos - obj_pos
            v_vec.normalize()
            w_vec: om.MVector = aim_pos ^ up_pos
            w_vec.normalize()
            mtx_list = [
                u_vec.x,
                u_vec.y,
                u_vec.z,
                0,
                v_vec.x,
                v_vec.y,
                v_vec.z,
                0,
                w_vec.x,
                w_vec.y,
                w_vec.z,
                0,
                0,
                0,
                0,
                1,
            ]
            matx = om.MMatrix()
            om.MScriptUtil.createMatrixFromList(mtx_list, matx)
            xform_mtx = om.MTransformationMatrix(matx)

            euler_rot = xform_mtx.eulerRotation()
            rot_value = [
                math.degrees(euler_rot.x),
                math.degrees(euler_rot.y),
                math.degrees(euler_rot.z),
            ]
            mc.xform(zr, t=(pos.x, pos.y, pos.z), ws=True)
            mc.xform(zr, ro=rot_value, ws=True)

            # Control joints
            curr_jnt = self.init_dag(
                loc.Joint(at=ctrl, style=2), "Sub", idx, side, "RigJnt"
            )
            curr_jnt.set_parent(ctrl)
            self.jnts.append(curr_jnt)

        # Binding Skin to Nurb Surface
        skc = mc.skinCluster(self.jnts, self.nrb)[0]
        for ix in range(ctrl_amount):
            if ix == 0:
                iflu_id = -1
            else:
                iflu_id = ix - 1

            curr_cvs = "{r}.cv[0:3][{i}]".format(r=self.nrb, i=ix)
            mc.skinPercent(skc, curr_cvs, tv=[(self.jnts[iflu_id], 1)])

        # Generating POSIs
        self.dtl_grp = self.init_dag(loc.Null(), "Dtl", None, side, "Grp")
        self.dtl_grp.set_parent(self.main_ctrl)

        self.meta.attr("detailVis") >> self.dtl_grp.attr("v")

        self.dtl_ctrls = []
        for ix in range(dtl_amount):
            idx = ix + 1
            # Point on surface
            posi = self.init_node(
                loc.create_node("pointOnSurfaceInfo"), "Dtl", idx, side, "Posi"
            )
            posi.add(ln="offset", dv=0, k=True)

            self.nrb.attr("worldSpace[0]") >> posi.attr("is")
            posi.attr("parameterU").v = 0.5
            div = float(dtl_amount + 1)
            mult = float(ix)
            posi.attr("parameterV").v = (ctrl_amount / (div - 1)) * mult

            w_vec_norm = self.init_node(
                loc.create_node("vectorProduct"),
                "WVecNorm",
                idx,
                side,
                "Vecprod",
            )
            w_vec_norm.attr("op").v = 2
            w_vec_norm.attr("normalizeOutput").v = 1
            posi.attr("normalizedNormal") >> w_vec_norm.attr("i1")
            posi.attr("normalizedTangentV") >> w_vec_norm.attr("i2")

            fbf_mtx = self.init_node(
                loc.create_node("fourByFourMatrix"), "Dtl", idx, side, "Fbf"
            )
            de_mtx = self.init_node(
                loc.create_node("decomposeMatrix"), "Dtl", idx, side, "Decomp"
            )
            mult_mtx = self.init_node(
                loc.create_node("multMatrix"), "Dtl", idx, side, "MultMat"
            )

            # Plug in 4b4 Matrix
            # 0-x 1-y 2-z 3-translate
            posi.attr("normalizedNormalX") >> fbf_mtx.attr("in00")
            posi.attr("normalizedNormalY") >> fbf_mtx.attr("in01")
            posi.attr("normalizedNormalZ") >> fbf_mtx.attr("in02")

            posi.attr("normalizedTangentVX") >> fbf_mtx.attr("in10")
            posi.attr("normalizedTangentVY") >> fbf_mtx.attr("in11")
            posi.attr("normalizedTangentVZ") >> fbf_mtx.attr("in12")

            w_vec_norm.attr("outputX") >> fbf_mtx.attr("in20")
            w_vec_norm.attr("outputY") >> fbf_mtx.attr("in21")
            w_vec_norm.attr("outputZ") >> fbf_mtx.attr("in22")

            posi.attr("px") >> fbf_mtx.attr("in30")
            posi.attr("py") >> fbf_mtx.attr("in31")
            posi.attr("pz") >> fbf_mtx.attr("in32")

            # Add Detail Controller
            dtl_ctrl = self.init_dag(
                loc.Controller(rgb.Cp.cube), "Dtl", idx, side, "Ctrl"
            )
            dtl_ctrl.lhattr("v")
            dtl_ctrl.scale_shape(2)
            self.dtl_ctrls.append(dtl_ctrl)
            dtl_ctrl.set_color(None, 2)

            dtl_zr, dtl_ofst = self._init_duo_grp(dtl_ctrl, "Dtl", idx, side)
            dtl_zr.set_parent(self.dtl_grp)

            fbf_mtx.attr("o") >> mult_mtx.attr("matrixIn[0]")
            dtl_zr.attr("pim") >> mult_mtx.attr("matrixIn[1]")
            mult_mtx.attr("matrixSum") >> de_mtx.attr("inputMatrix")

            de_mtx.attr("ot") >> dtl_zr.attr("t")
            de_mtx.attr("or") >> dtl_zr.attr("r")

            # Adding Offset along V axis
            ctrl_shp = dtl_ctrl.get_shape()
            ctrl_shp.add(ln="offsetV", k=True)

            offu_mdv = self.init_node(
                loc.create_node("multiplyDivide"), "DtlOfstU", idx, side, "Mdv"
            )
            offu_mdv.attr("i2x").v = 0.1
            ctrl_shp.attr("offsetV") >> offu_mdv.attr("i1x")

            offu_pma = self.init_node(
                loc.create_node("plusMinusAverage"),
                "DtlOfstU",
                idx,
                side,
                "Pma",
            )
            offu_pma.add(ln="default", k=True)
            offu_pma.attr("default").v = posi.attr("parameterV").v
            offu_pma.attr("default") >> offu_pma.attr("input1D").last()

            offu_mdv.attr("ox") >> offu_pma.attr("input1D").last()
            offu_pma.attr("output1D") >> posi.attr("parameterV")

        for ix in range(dtl_amount):
            idx = ix + 1
            skin_jnt = self.init_dag(
                loc.Joint(at=self.dtl_ctrls[ix]),
                "Skin",
                idx,
                side,
                "Jnt",
            )

            skin_jnt.set_parent(self.skin_jnt)
            loc.parent_constraint(self.dtl_ctrls[ix], skin_jnt)
            loc.scale_constraint(self.dtl_ctrls[ix], skin_jnt)

        # Cleanup
        mc.delete(self.crv)
        mc.delete(a_crv)
        mc.delete(b_crv)
