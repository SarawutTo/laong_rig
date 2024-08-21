import maya.cmds as mc
from . import rig_base
from . import core as loc


class RibbonRig(rig_base.Rigbase):
    def __init__(
        self,
        start_loc,
        end_loc,
        ctrl_amount,
        joint_amount,
        mod,
        desc,
        meta_parent,
        still_parent,
    ):
        super(RibbonRig, self).__init__(mod, desc)

        self.meta = self.create_meta(meta_parent)
        self.still = self.create_still(still_parent)


def create_follicle(ctrl_amount, follicle_amount):
    nurb_length = 1.00 / ctrl_amount
    nurb_surface = mc.nurbsPlane(
        u=(ctrl_amount - 1), v=1, ax=(0, 0, 1), ch=True, w=5, lr=nurb_length
    )[0]
    nurb_shape = mc.listRelatives(nurb_surface, s=True)[0]
    dis_btw = 1.00 / (follicle_amount - 1)
    foll_grp = mc.createNode("transform")

    for ix in range(follicle_amount):
        u_param = ix * dis_btw
        v_param = 0.5

        foll_shape = mc.createNode("follicle")
        foll_trans = mc.listRelatives(foll_shape, p=True)[0]
        ctrl = mc.circle(nr=(1, 0, 0))[0]
        foll_jnt = mc.createNode("joint")
        mc.setAttr("{}.radius".format(foll_jnt), 0.2)

        mc.parent(foll_jnt, ctrl)
        mc.parent(ctrl, foll_trans)
        mc.parent(foll_trans, foll_grp)

        # Connect Surface
        mc.connectAttr(
            "{}.local".format(nurb_shape), "{}.inputSurface".format(foll_shape)
        )
        mc.connectAttr(
            "{}.worldMatrix".format(nurb_shape),
            "{}.inputWorldMatrix".format(foll_shape),
        )

        # Connect Foll Translate Rotate
        mc.connectAttr(
            "{}.outTranslate".format(foll_shape),
            "{}.translate".format(foll_trans),
        )
        mc.connectAttr(
            "{}.outRotate".format(foll_shape), "{}.rotate".format(foll_trans)
        )

        # Set Follicle Position Along Surface UV
        mc.setAttr("{}.parameterU".format(foll_shape), u_param)
        mc.setAttr("{}.parameterV".format(foll_shape), v_param)


foll_shp = prc.Dag(prc.create("follicle"))
foll_shp.hide = True
foll = prc.Dag(foll_shp.get_parent())
foll.name = prnt.compose(name, None, side, "Foll")

foll.set_parent(foll_grp)
foll_grp.set_parent(self.foll_grp)


def ribbon(sub, locA, locB, locC, part, side):
    # create nurb controller
    nsurface = loc.create_nsurface(sub)

    # create nHair Follicle
    for i in range(0, sub + 1):
        # crete follicle
        fol_disper = 1.0 / (sub - 1)
        fol_dis = (i - 1) * fol_disper
        fol_name = "Rbn_{}_Fol".format(i + 1)
        fol, folshp = loc.create_follicle(u=fol_dis, v=0.5)

        # create controller
        ctrl = mc.circle(
            c=(0, 0, 0),
            nr=(1, 0, 0),
            r=0.5,
            ch=0,
            name=fol.replace("Fol", "CTR"),
        )
        # create joint parent to CTR
        joint = mc.joint(name=fol.replace("Fol", "Jnt"))
        # make ctr offs
        grp_GRP = mc.group(ctrl, n=fol.replace("Fol", "GRP"))
        grp_Offs = mc.group(ctrl[0], n=fol.replace("Fol", "Offs"))
        # parent grp to fol
        mc.parent(grp_GRP, fol_name)

        nsurface.attr("local") >> folshp.attr("inputSurface")
        nsurface.attr("worldMatrix[0]") >> folshp.attr("inputWorldMatrix")

    # Grp follicle
    mc.select("Rbn_*_Fol")
    selfol = mc.ls(sl=True)
    startPoint = selfol[0]
    middlePoint = selfol[5]
    endPoint = selfol[-1]
    get_startPosi = mc.xform(startPoint, q=True, ws=True, t=True)
    get_middlePosi = mc.xform(middlePoint, q=True, ws=True, t=True)
    get_endPosi = mc.xform(endPoint, q=True, ws=True, t=True)
    folGrp = mc.group(selfol, n="Foliicle_GRP")

    PosA = mc.xform(locA, q=True, ws=True, t=True)
    PosB = mc.xform(locB, q=True, ws=True, t=True)

    # clear
    mc.select(cl=True)
    # start joint
    startJnt = mc.joint(n="start_Jnt", p=(get_startPosi[0], 0, 0))
    startJntOffs = mc.group(startJnt, name="start_JntOffs")
    # mid joint
    middleJnt = mc.joint(n="middle_Jnt", p=(0, 0, 0))
    middleJntOffs = mc.group(middleJnt, name="middle_JntOffs")
    # end joint
    endJnt = mc.joint(n="end_Jnt", p=(get_endPosi[0], 0, 0))
    endJntOffs = mc.group(endJnt, name="end_JntOffs")
    # inbetween upper
    upJnt = mc.joint(n="up_Jnt", p=(-2.5, 0, 0))
    upJntOffs = mc.group(upJnt, name="up_JntOffs")
    lowJnt = mc.joint(n="low_Jnt", p=(2.5, 0, 0))
    lowJntOffs = mc.group(lowJnt, name="low_JntOffs")

    # Group joint
    mc.parent(middleJntOffs, endJntOffs, w=True)
    jntGrp = mc.group(
        [middleJntOffs, startJntOffs, endJntOffs, upJntOffs, lowJntOffs],
        n="Control_Jnt_Offs",
    )

    # Create deformController and grp
    startCtr = mc.circle(
        c=(0, 0, 0), nr=(1, 0, 0), r=1.5, ch=0, name="start_Ctr"
    )
    SLEx = mc.group(name="start_ExtraOffs")
    SLGrp = mc.group(SLEx, name="start_CtrOffs")

    middleCtr = mc.circle(
        c=(0, 0, 0), nr=(1, 0, 0), r=1.5, ch=0, name="middle_Ctr"
    )
    MLEx = mc.group(middleCtr, name="middle_CtrExtra")
    MLExtra = mc.group(MLEx, name="middle_OffsExtra")
    MLGrp = mc.group(MLExtra, name="middle_CtrOffs")

    endCtr = mc.circle(c=(0, 0, 0), nr=(1, 0, 0), r=1.5, ch=0, name="end_Ctr")
    ELEx = mc.group(endCtr, name="end_ExtraOffs")
    ELGrp = mc.group(ELEx, name="end_CtrOffs")

    upCtr = mc.circle(c=(0, 0, 0), nr=(1, 0, 0), r=1, ch=0, name="up_Ctr")
    upEx = mc.group(upCtr, name="up_ExtraOffs")
    upGrp = mc.group(upEx, name="up_CtrOffs")

    lowCtr = mc.circle(c=(0, 0, 0), nr=(1, 0, 0), r=1, ch=0, name="low_Ctr")
    lowEx = mc.group(lowCtr, name="low_ExtraOffs")
    lowGrp = mc.group(lowEx, name="low_CtrOffs")

    # set pivot
    mc.parentConstraint(startPoint, SLGrp, mo=False)
    mc.parentConstraint(startPoint, SLGrp, e=True, rm=True)
    mc.parentConstraint(endPoint, ELGrp, mo=False)
    mc.parentConstraint(endPoint, ELGrp, e=True, rm=True)
    mc.parentConstraint(upJnt, upGrp, mo=False)
    mc.parentConstraint(upJnt, upGrp, e=True, rm=True)
    mc.parentConstraint(lowJnt, lowGrp, mo=False)
    mc.parentConstraint(lowJnt, lowGrp, e=True, rm=True)
    # parent ctr to joint
    mc.parentConstraint(startCtr, startJnt, mo=True)
    mc.parentConstraint(middleCtr, middleJnt, mo=True)
    mc.parentConstraint(endCtr, endJnt, mo=True)
    mc.parentConstraint(upCtr, upJnt, mo=True)
    mc.parentConstraint(lowCtr, lowJnt, mo=True)

    # pointCon uplow
    mc.pointConstraint(startJnt, middleJnt, upGrp)
    mc.pointConstraint(middleJnt, endJnt, lowGrp)

    # constrain point controller
    mc.pointConstraint(startCtr, endCtr, MLGrp)

    # aim Con
    mc.aimConstraint(
        endCtr[0],
        lowGrp,
        aim=(0, 1, 0),
        upVector=(0, 0, 1),
        mo=True,
        wut="object",
        wuo=endCtr[0],
    )
    mc.aimConstraint(
        middleCtr[0],
        upGrp,
        aim=(0, 1, 0),
        upVector=(0, 0, 1),
        mo=True,
        wut="object",
        wuo=middleCtr[0],
    )

    ##### twist ######
    rbnTwist = mc.duplicate(rbnMain, n="Ribbon_twist")
    mc.select(rbnTwist)
    twistDef = mc.nonLinear(type="twist")
    mc.setAttr(twistDef[1] + ".rz", -90)
    twist = mc.rename(twistDef[1], "Twist_Deformer")

    ##### sine ######
    mc.duplicate(rbnMain, n="Ribbon_sine")
    mc.select("Ribbon_sine")
    sineDef = mc.nonLinear(type="sine")
    mc.setAttr(sineDef[1] + ".rz", -90)
    mc.setAttr(sineDef[0] + ".dropoff", 1)
    sine = mc.rename(sineDef[1], "Sine_Deformer")

    #### blendshape ####
    rbnSubBS = mc.blendShape("Ribbon_twist", "Ribbon_sine", rbnMain)
    mc.setAttr(rbnSubBS[0] + ".Ribbon_twist", 1)
    mc.setAttr(rbnSubBS[0] + ".Ribbon_sine", 1)

    # bindskin
    mc.select(cl=True)
    mc.select(endJnt, middleJnt, startJnt, upJnt, lowJnt, rbnMain)
    mc.SmoothBindSkin()

    # addatrr function
    def create_twist_attr(Control):
        mc.addAttr(Control, ln="TWIST", at="enum", en="---------")
        mc.setAttr(Control + ".TWIST", l=True, k=True)
        mc.addAttr(Control, ln="twist", at="float")
        mc.setAttr(Control + ".twist", k=True)
        ctrTwist = Control + ".twist"
        return ctrTwist

    create_twist_attr(endCtr[0])
    create_twist_attr(middleCtr[0])
    create_twist_attr(startCtr[0])

    # add sine attr to middle CTR
    mc.addAttr(middleCtr[0], ln="SINE", at="enum", en="---------", k=True)
    mc.setAttr(middleCtr[0] + ".SINE", l=True)
    mc.addAttr(middleCtr[0], ln="Sine_Amp", at="float", k=True)
    mc.addAttr(middleCtr[0], ln="Sine_Offs", at="float", k=True)
    mc.addAttr(middleCtr[0], ln="Sine_Length", at="float", k=True, min=2)
    mc.addAttr(middleCtr[0], ln="Sine_Twist", at="float", k=True)

    # connect twist deformer node
    Spma = mc.shadingNode(
        "plusMinusAverage",
        asUtility=1,
        name=part + "_" + side + "_start_twist_pma",
    )
    Epma = mc.shadingNode(
        "plusMinusAverage",
        asUtility=1,
        name=part + "_" + side + "_end_twist_pma",
    )

    mc.connectAttr(
        (startCtr[0] + ".twist"),
        (part + "_" + side + "_start_twist_pma.input 1D[0]"),
    )
    mc.connectAttr(
        (middleCtr[0] + ".twist"),
        (part + "_" + side + "_start_twist_pma.input 1D[1]"),
    )
    mc.connectAttr(
        (part + "_" + side + "_start_twist_pma.output 1D"),
        (twistDef[0] + ".startAngle"),
    )

    mc.connectAttr(
        (endCtr[0] + ".twist"),
        (part + "_" + side + "_end_twist_pma.input 1D[0]"),
    )
    mc.connectAttr(
        (middleCtr[0] + ".twist"),
        (part + "_" + side + "_end_twist_pma.input 1D[1]"),
    )
    mc.connectAttr(
        (part + "_" + side + "_end_twist_pma.output 1D"),
        (twistDef[0] + ".endAngle"),
    )

    # connect sine deformer node
    mc.connectAttr((middleCtr[0] + ".Sine_Amp"), (sineDef[0] + ".amplitude"))
    mc.connectAttr((middleCtr[0] + ".Sine_Offs"), (sineDef[0] + ".offset"))
    mc.connectAttr((middleCtr[0] + ".Sine_Twist"), (sine + ".rotateY"))
    mc.connectAttr(
        (middleCtr[0] + ".Sine_Length"), (sineDef[0] + ".wavelength")
    )

    # group and hide
    mc.select("Ribbon_twist", "Ribbon_sine", sine, twist, jntGrp, rbnMain)
    DefromGrp = mc.group(n="Still_GRP")
    mc.hide(DefromGrp)

    # group CTR
    mc.select(SLGrp, MLGrp, ELGrp, lowGrp, upGrp, "Foliicle_GRP")
    ctrGrp = mc.group(n="Controller_GRP")

    # snap to Position A&B
    mc.setAttr(SLGrp + ".translate", type="float3", *PosA)
    mc.setAttr(ELGrp + ".translate", type="float3", *PosB)

    mc.select(ctrGrp, DefromGrp, rbnMain)
    allGrp = mc.group(n="Rbn_GRP")

    mc.parentConstraint(locA, SLGrp)
    mc.parentConstraint(locC, MLExtra)
    mc.parentConstraint(locB, ELGrp)
    mc.hide("Ribbon_Main")

    mc.select(
        "Ribbon_Main",
        folGrp,
        DefromGrp,
        "Controller_GRP",
        allGrp,
        Spma,
        Epma,
        hi=True,
    )
    sels = mc.ls(sl=True, type="transform")
    for sel in sels:
        if side == "L" or side == "R":
            mc.rename(sel, part + "_" + side + "_" + sel)
        else:
            mc.rename(sel, part + "_" + sel)
