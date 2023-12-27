from imp import reload
from . import core as loc
from . import rig_base
from . import naming_tools as lont
from . import vector
from . import rig_global as rgb
from typing import Union
import maya.cmds as mc

reload(loc)
reload(lont)
reload(rig_base)
reload(vector)


def get_ws_center(object):
    bbx = mc.xform(object, q=True, bb=True, ws=True)  # world space
    x = (bbx[0] + bbx[3]) / 2.0
    y = (bbx[1] + bbx[4]) / 2.0
    z = (bbx[2] + bbx[5]) / 2.0

    return (x, y, z)


def snap_to_pos(object, pos):
    mc.xform(object, t=pos, ws=True)


def get_rml_vtx(object):
    # Get the number of vertices in the mesh
    vtx_count = mc.polyEvaluate(object, vertex=True)

    # Loop through all the vertices in the mesh
    for vtx_id in range(vtx_count):
        # Get the X position of the vertex
        pos = mc.xform(vtx_id, t=True, q=True)
        x_pos = pos[0]

        # Check if the X position is less than zero
        if x_pos < 0:
            # If it is, select the vertex
            mc.select("{}.vtx[{}]".format(object, vtx_id), add=True)


def check_ref_diff(in_scene, ref_file):
    mc.listRelatives(in_scene)
    mc.listRelatives(ref_file)


def dup_delete_orig():
    pass


def get_ctrl_shape_as_list():
    sels = mc.ls(sl=True, fl=True)
    cp_list = []
    for each in sels:
        vtx_pos = tuple(
            [round(i, 4) for i in mc.xform(each, q=True, t=True, ws=True)]
        )

        cp_list.append(vtx_pos)


def create_space_switch(space_driver, space_driven, space_ctrl):
    """ """

    if isinstance(space_driver, dict):
        a = [i for i in space_driver.values()]
        b = [i for i in space_driver.keys()]

        par = mc.parentConstraint(a, space_driven, mo=True)[0]
        mc.addAttr(space_ctrl, ln="space", en=":".join(b), at="enum", k=True)
        for ix, each in enumerate(space_driver):
            con = mc.createNode(
                "condition",
                n="{}{}Space_Con".format(
                    each, str(space_driven).split("_")[0]
                ),
            )
            mc.setAttr("{}.st".format(con), ix)
            mc.setAttr("{}.colorIfFalseR".format(con), 0)
            mc.setAttr("{}.colorIfTrueR".format(con), 1)

            mc.connectAttr("{}.space".format(space_ctrl), "{}.ft".format(con))
            mc.connectAttr(
                "{}.outColorR".format(con), "{}.w{}".format(par, ix)
            )
    else:
        mc.parentConstraint(space_driver, space_driven, mo=True)


def set_ctrls_color(
    color: Union[None, rgb.Color],
    mainctrl_list: list[loc.Controller],
    subctrl_list: list[loc.Controller],
    dtlctrl_list: list[loc.Controller],
):
    """Set Control Color
    Args:
        color(None, rgb.Color):
        mainctrl_list():
        subctrl_list():
        dtlctrl_list():
    """
    for ctrl in mainctrl_list:
        ctrl.set_ctrl_color(color, 0)
    for ctrl in subctrl_list:
        ctrl.set_ctrl_color(color, 1)
    for ctrl in dtlctrl_list:
        ctrl.set_ctrl_color(color, 2)


def add_to_skin_set(jnt_list: list[loc.Joint]):
    """Add Jnt to Skin_Set
    Args:
        jnt_list(None, rgb.Color):

    """
    set_name = rgb.MainGroup.skin_set

    for jnt in jnt_list:
        mc.sets(jnt, add=set_name)


def connect_visiblity():
    pass
