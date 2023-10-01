import maya.cmds as mc
from . import rig_base


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
