from imp import reload
import maya.OpenMaya as om
from . import core as loc
from . import rig_base
from . import naming_tools as lnt
from . import vector
from . import rig_global as rgb

# from typing import Union
import maya.cmds as mc

reload(loc)
reload(lnt)
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


def set_ctrls_color(
    color,
    mainctrl_list,
    subctrl_list,
    dtlctrl_list,
):
    # color: Union[None, rgb.Color],
    # mainctrl_list: list[loc.Controller],
    # subctrl_list: list[loc.Controller],
    # dtlctrl_list: list[loc.Controller],
    """Set Control Color
    Args:
        color (None, rgb.Color):
        mainctrl_list ():
        subctrl_list ():
        dtlctrl_list ():

    """
    for ctrl in mainctrl_list:
        ctrl.set_color(color, 0)
    for ctrl in subctrl_list:
        ctrl.set_color(color, 1)
    for ctrl in dtlctrl_list:
        ctrl.set_color(color, 2)


def add_to_skin_set(jnt_list):  # jnt_list: list[loc.Joint]
    """Add Jnt to Skin_Set
    Args:
        jnt_list (None, rgb.Color):

    """
    set_name = rgb.MainGroup.skin_set

    for jnt in jnt_list:
        mc.sets(jnt, add=set_name)


def connect_visiblity():
    pass


def add_divide_attr(
    ctrl, attr_name
):  # (ctrl: loc.Dag, attr_name: str) -> loc.Attribute:
    """Add Divide Attribute.
    Args:
        ctrl (loc.Dag):
        attr_name (str):

    Return:
        loc.Attr : added attribute.
    """
    div_attr = ctrl.add(ln=attr_name, en="--------------", at="enum", k=True)
    div_attr.lock = True

    return div_attr


def get_double_jnt_pos(
    jnt_a, jnt_b, jnt_c, weight
):  # jnt_a: loc.Dag, jnt_b: loc.Dag, jnt_c: loc.Dag, weight: float) -> tuple[om.MVector, om.MVector]:
    up_vec = vector.get_point_btw_2_vector(jnt_a, jnt_b, weight)
    low_vec = vector.get_point_btw_2_vector(
        jnt_b, jnt_c, vector.reverse(weight)
    )

    return up_vec, low_vec


def wrap(
    this_geo,
    tothis_geo,
    still_par,
    max_dis=1,
    exclusive_bind=0,
    mode=0,
):
    this_geo = loc.Dag(this_geo)
    tothis_geo = loc.Dag(tothis_geo)
    wrap_node = loc.Node(mc.deformer(this_geo, type="wrap")[0])
    wrap_node.name = "Fcl_wrap"
    tothis_geobase = loc.dup_and_clean_unused_intermediate_shape(tothis_geo)
    this_geo.add(ln="dropoff", dv=4)
    this_geo.add(ln="inflType", dv=2)
    this_geo.add(ln="smoothness", dv=0)
    this_geo.attr("dropoff") >> wrap_node.attr("dropoff[0]")
    this_geo.attr("inflType") >> wrap_node.attr("inflType[0]")
    this_geo.attr("smoothness") >> wrap_node.attr("smoothness[0]")

    name, _, _, _ = lnt.construct(tothis_geo.name)
    tothis_geobase.name = tothis_geo.name.replace(name, "{}Base".format(name))
    tothis_geobase.hide = True
    tothis_geobase.set_parent(still_par)

    tothis_geobase.attr("worldMesh") >> wrap_node.attr("basePoints[0]")
    tothis_geo.attr("worldMesh") >> wrap_node.attr("driverPoints[0]")
    wrap_node.attr("maxDistance").v = max_dis
    wrap_node.attr("exclusiveBind").v = exclusive_bind
    wrap_node.attr("falloffMode").v = mode


def checkexist_and_add_attr(obj, attrname, *args, **kwargs):
    """Check Attribute Exist and Add Attribute.
    Args:
        obj(str): Object to Add Attr to.
        attrname(str):

    Return:
        str: object.attrName
    """
    if not mc.objExists("{}.{}".format(obj, attrname)):
        mc.addAttr(obj, ln=attrname, *args, **kwargs)

    return "{}.{}".format(obj, attrname)


def checkexist_and_create_node(node, name, idx, side, _type):
    """Check Node Exist and Create Node.
    Args:
        node(str): Node Type
        name(str): Node Name
        idx(int): index
        side(str): L/R
        _type(str): "Mdl" "Add"

    Return:
        str: node_name
    """
    node_name = prnt.compose(name, idx, side, _type)
    if not mc.objExists(node_name):
        node_name = mc.createNode(node, n=node_name)

    return node_name


def check_and_connect_attr(source, destination):
    """Check Connection and Connect Attribute.
    Args:
        source(str): Source Attribute
        destination(str): Destination Attribute

    """
    if not mc.objExists(destination):
        return "{} Not Exist".format(destination)

    list_con = mc.listConnections(destination, p=True)
    if list_con:
        if source in list_con:
            return "skip connect {} to {}".format(source, destination)
        else:
            mc.connectAttr(source, destination, f=True)
    else:
        mc.connectAttr(source, destination, f=True)
        return "Connect {} to {}".format(source, destination)


def transfer_weight(geo, skin, fromthis_jnt, tothis_jnt):
    """Transfer Weight form Joint to Joint.
    Args:
        fromthis_jnt(str): Source Joint
        tothis_jnt(str): Destination Joint

    """
    # his = mc.listHistory(geo)
    # for each in his:
    #     if mc.nodeType(each) == "skinCluster":
    #         skincluser = each
    mc.skinCluster(skin, e=True, siv=fromthis_jnt)
    mc.skinPercent(skin, tmw=(fromthis_jnt, tothis_jnt))


def get_fbf_matrix_from_trs(dag_translate, dag_matrix, name):
    """Convert Translate/Rotate/Scale to Fbf Matrix"""
    x_vec = mc.createNode("vectorProduct", n="{}X_Vec".format(name))
    y_vec = mc.createNode("vectorProduct", n="{}Y_Vec".format(name))
    z_vec = mc.createNode("vectorProduct", n="{}Z_Vec".format(name))

    fbf = mc.createNode("fourByFourMatrix", n="{}Matrix_Fbf".format(name))

    mc.setAttr("{}.input1X".format(x_vec), 1)
    mc.setAttr("{}.input1Y".format(y_vec), 1)
    mc.setAttr("{}.input1Z".format(z_vec), 1)

    mc.setAttr("{}.op".format(x_vec), 3)
    mc.setAttr("{}.op".format(y_vec), 3)
    mc.setAttr("{}.op".format(z_vec), 3)

    mc.connectAttr(dag_matrix, "{}.matrix".format(x_vec))
    mc.connectAttr(dag_matrix, "{}.matrix".format(y_vec))
    mc.connectAttr(dag_matrix, "{}.matrix".format(z_vec))

    # Connect Four-By-Four
    mc.connectAttr("{}.outputX".format(x_vec), "{}.in00".format(fbf))
    mc.connectAttr("{}.outputY".format(x_vec), "{}.in01".format(fbf))
    mc.connectAttr("{}.outputZ".format(x_vec), "{}.in02".format(fbf))

    mc.connectAttr("{}.outputX".format(y_vec), "{}.in10".format(fbf))
    mc.connectAttr("{}.outputY".format(y_vec), "{}.in11".format(fbf))
    mc.connectAttr("{}.outputZ".format(y_vec), "{}.in12".format(fbf))

    mc.connectAttr("{}.outputX".format(z_vec), "{}.in20".format(fbf))
    mc.connectAttr("{}.outputY".format(z_vec), "{}.in21".format(fbf))
    mc.connectAttr("{}.outputZ".format(z_vec), "{}.in22".format(fbf))

    mc.connectAttr(dag_translate, "{}.in30".format(fbf))
    mc.connectAttr(dag_translate, "{}.in31".format(fbf))
    mc.connectAttr(dag_translate, "{}.in32".format(fbf))


def addn_connect_shapedriver(
    attr, from_attr, to_shapedriver, imin, inmax, omin, omax
):
    to_attr = to_shapedriver.add(attr)
    remap = loc.create_remap(imin, inmax, omin, omax)
    remap.name = attr + "_Remap"
    from_attr >> remap.attr("i")
    remap.attr("ov") >> to_attr

    return remap


# path = "maya.ma"

# with open(path, "r") as f:
#     lines = f.readlines()
# with open(path, "w") as f:
#     for line in lines:
#         if not "dataStructure" in line.strip("\n"):
#             pass
#             f.write(line)
#         else:
#             print(line.strip("\n"))

# import maya.cmds as mc

# import maya.OpenMaya as om

# surface_geo = "pPlane1"
# ref_loc = "locator2"

# sels_list = om.MSelectionList()
# sels_list.add(surface_geo)

# m_obj = om.MObject()
# m_dagpath = om.MDagPath()

# sels_list.getDependNode(0,m_obj)
# sels_list.getDagPath(0,m_dagpath)

# mesh_fuction = om.MFnMesh(m_dagpath)
# clostest_point = om.MPoint()

# ref_pos = mc.xform(ref_loc,q=True,t=True,ws=True)
# ref_point = om.MPoint(*ref_pos)
# ref_point = om.MPoint(-1.2257143832372566, 1.4443925591792293, 1.5293110282863798)


# mesh_fuction.getClosestPoint(ref_point,clostest_point,om.MSpace.kWorld)
def mirrorShape(search, raplace):
    curve_list = mc.ls(
        "*" + search + "*Ctrl",
        "*" + search + "*ctrl",
        "*" + search + "*Gmbl",
    )
    for i in curve_list:
        new_crv = i.replace(search, raplace)
        if not mc.objExists(new_crv):
            print("{} does not exist").format(new_crv)
            continue
        crvShape = mc.listRelatives(i, s=True)
        if not crvShape:
            continue
        crv_degree = mc.getAttr(crvShape[0] + ".degree")
        crv_spans = mc.getAttr(crvShape[0] + ".spans")
        crv_cvs = crv_degree + crv_spans
        for j in range(0, crv_cvs + 1):
            pos = mc.xform(i + ".cv[ " + str(j) + "]", q=True, ws=True, t=True)
            mc.xform(
                new_crv + ".cv[ " + str(j) + "]",
                ws=True,
                t=(-pos[0], pos[1], pos[2]),
            )


def copy_shape_ctrl():
    sels = mc.ls(sl=True)
    from_shp = mc.listRelatives(sels[0], s=True)[0]
    tar_shp = mc.listRelatives(sels[1], s=True)[0]
    fromid_list = mc.ls("{}.cv[*]".format(from_shp), fl=True)
    tarid_list = mc.ls("{}.cv[*]".format(tar_shp), fl=True)
    pos_val = []
    for fro, tar in zip(fromid_list, tarid_list):
        pos = mc.xform(fro, q=True, t=True, os=True)
        mc.xform(tar, t=pos, os=True)


def connect_trs(from_this, to_this):
    for attribute in ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]:
        loc.Dag(from_this).attr(attribute) >> loc.Dag(to_this).attr(attribute)


def openChunk(func):
    def funcWrapper(*args, **kwargs):
        mc.undoInfo(openChunk=True)
        try:
            value = func(*args, **kwargs)
        finally:
            mc.undoInfo(closeChunk=True)
        return value

    return funcWrapper
