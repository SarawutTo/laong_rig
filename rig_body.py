from imp import reload
from . import core as loc
from . import rig_base
from . import naming_tools as lont
import maya.cmds as mc


reload(loc)
reload(lont)
reload(rig_base)


class SimpleBodyRig(rig_base.Rigbase):
    def __init__(
        self,
        tmp_jnt,
        mod,
        desc="",
        ctrl_par=None,
        jnt_par=None,
    ):
        super(SimpleBodyRig, self).__init__(mod, desc)
        self.meta = self.create_meta(ctrl_par)

        # setup FKjoint
        spineFkJnt = mc.duplicate(rc=True)

        for i in range(0, 6):
            mc.parent(spineFkJnt[i + 1], w=True)
        mc.delete(spineFkJnt[1], spineFkJnt[3], spineFkJnt[5])

        # control joint
        rootCtrJnt = mc.duplicate(spineFkJnt[0], n="root_CtrJnt")
        neckCtrJnt = mc.duplicate(spineFkJnt[6], n="neck_CtrJnt")

        # parent FkJoint
        mc.parent(spineFkJnt[6], spineFkJnt[4])
        mc.parent(spineFkJnt[4], spineFkJnt[2])
        mc.parent(spineFkJnt[2], spineFkJnt[0])
        mc.select(spineFkJnt[0], hi=True)
        spineFkJnt = mc.ls(sl=True)

        # create ik
        ikspline = mc.ikHandle(
            sj=tmp_jnt[0],
            ee=tmp_jnt[6],
            solver="ikSplineSolver",
            n="spine_IKhandle",
        )
        splineCv = mc.rename(ikspline[2], "spline_Curve")

        # skin joint to curve
        mc.select(cl=True)
        mc.select(rootCtrJnt, neckCtrJnt, splineCv)
        mc.SmoothBindSkin()

        # create curve
        rootctr = mc.circle(n="root_Ctr", nr=[0, 1, 0], ch=False, r=2)
        rootOffsctr = mc.group(n="root_OffsCtr")
        neckctr = mc.circle(n="neck_Ctr", nr=[0, 1, 0], ch=False, r=2)
        neckOffsctr = mc.group(n="neck_OffsCtr")
        mc.parentConstraint(tmp_jnt[0], rootOffsctr)
        mc.parentConstraint(tmp_jnt[0], rootOffsctr, rm=True)
        mc.parentConstraint(tmp_jnt[6], neckOffsctr)
        mc.parentConstraint(tmp_jnt[6], neckOffsctr, rm=True)

        # parent
        mc.parent(rootCtrJnt, rootctr)
        mc.parent(neckCtrJnt, neckctr)
        # fkctr
        fkctrspineCtr = mc.circle(n="spinefk_Ctr", nr=[0, 1, 0], ch=False)
        fkctrspineOffs = mc.group(n="spinefk_OffsCtr")
        fkctrchestCtr = mc.circle(n="chestfk_Ctr", nr=[0, 1, 0], ch=False)
        fkctrchestOffs = mc.group(n="chest_OffsCtr")
        mc.parentConstraint(tmp_jnt[2], fkctrspineOffs)
        mc.parentConstraint(tmp_jnt[2], fkctrspineOffs, rm=True)
        mc.parentConstraint(tmp_jnt[4], fkctrchestOffs)
        mc.parentConstraint(tmp_jnt[4], fkctrchestOffs, rm=True)
        # mc.parentConstraint(spineJnt[2],fkctrspineOffs)
        mc.parentConstraint(fkctrspineCtr, spineFkJnt[1])
        mc.parentConstraint(fkctrchestCtr, spineFkJnt[2])

        # set twist
        mc.setAttr(ikspline[0] + ".dTwistControlEnable", 1)
        mc.setAttr(ikspline[0] + ".dWorldUpType", 4)
        mc.setAttr(ikspline[0] + ".dForwardAxis", 0)
        mc.setAttr(ikspline[0] + ".dWorldUpAxis", 4)
        mc.setAttr(ikspline[0] + ".dWorldUpVectorY", 0)
        mc.setAttr(ikspline[0] + ".dWorldUpVectorEndY", 0)
        mc.setAttr(ikspline[0] + ".dWorldUpVectorZ", 1)
        mc.setAttr(ikspline[0] + ".dWorldUpVectorEndZ", 1)
        mc.connectAttr(
            rootctr[0] + ".worldMatrix[0]", ikspline[0] + ".dWorldUpMatrix"
        )
        mc.connectAttr(
            neckctr[0] + ".worldMatrix[0]", ikspline[0] + ".dWorldUpMatrixEnd"
        )

        # parent
        mc.parent(neckOffsctr, fkctrchestCtr)
        mc.parent(fkctrchestOffs, fkctrspineCtr)
        mc.parent(fkctrspineOffs, rootctr)

        Skin_Grp = "Skin_Grp"
        SkinGrpCheck = mc.objExists(Skin_Grp)
        if SkinGrpCheck == False:
            mc.group(n=Skin_Grp, em=True)

        Joint_Grp = "Joint_Grp"
        JointGrpCheck = mc.objExists(Joint_Grp)
        if JointGrpCheck == False:
            mc.group(n=Joint_Grp, em=True)

        Controller_Grp = "Controller_Grp"
        ControllerGrpCheck = mc.objExists(Controller_Grp)
        if ControllerGrpCheck == False:
            mc.group(n=Controller_Grp, em=True)

        # cleanup
        mc.select(ikspline[0], splineCv)
        splineIKsolverGrp = mc.group(n="splineIKsolver_Grp")
        mc.parent(splineIKsolverGrp, Controller_Grp)
        mc.parent(spineFkJnt[0], Joint_Grp)

        mc.parent(tmp_jnt[0], Skin_Grp)

        for each in spineFkJnt:
            FKname = each.replace("Jnt1", "FKJnt")
            mc.rename(each, FKname)
