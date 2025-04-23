import maya.cmds as mc
import maya.OpenMaya as om

from . import core as loc


def _move_diff(obj, tar, ori, amp=1):
    x_sum = (tar[0] - ori[0]) * amp
    y_sum = (tar[1] - ori[1]) * amp
    z_sum = (tar[2] - ori[2]) * amp
    if not (x_sum, y_sum, z_sum) == (0, 0, 0):
        mc.move(x_sum, y_sum, z_sum, obj, r=True)


def get_all_point_positions(mesh):
    """Returns a list of world positions for all vertices in the given mesh.

    Args:
        mesh (str): The name of the mesh.

    Returns:
        list: A list of tuples representing world space coordinates of each vertex.
    """
    vertices = mc.ls(mesh.name + ".vtx[*]", fl=True)
    return [mc.xform(vtx, os=True, q=True, t=True) for vtx in vertices]


def get_all_point_names(mesh):
    """Returns a list of all vertex names in the given mesh.

    Args:
        mesh (str): The name of the mesh.

    Returns:
        list: A list of vertex names as strings.
    """
    return mc.ls(mesh.name + ".vtx[*]", fl=True)


def _copy_shape(from_this, to_this):
    """All vertices with x values more than 0 in to_this are set to
    the position of from_this.

    Args:
        from_this (str):
        to_this (str):
    """

    from_this = loc.Dag(from_this)
    to_this = loc.Dag(to_this)

    tg_poses = prst.get_all_point_positions(from_this)
    pntnames = prst.get_all_point_names(to_this)

    for pntname, tgpos in zip(pntnames, tg_poses):
        pos = mc.xform(pntname, q=True, os=True, t=True)
        _move_diff(pntname, tgpos, pos, 1)


def copy_shape(target_geo, blended_geo):
    """Copy shape from "target_geo" to blended_geo

    Args:
        target_geo(str):
        blended_geo(str):
    """
    shape_node = mc.listRelatives(target_geo, s=True)
    if not shape_node:
        return False
    if len(shape_node) > 1:
        shape_node = shape_node[0]

    check_type = mc.objectType(shape_node)

    if check_type == "mesh":
        object_type = ".vtx"
        data_type = "[*]"
    elif check_type == "nurbsCurve":
        object_type = ".cv"
        data_type = "[*]"
    elif check_type == "nurbsSurface":
        object_type = ".cv"
        data_type = "[*][*]"

    mesh_compo = mc.ls(
        "{b}{t}{d}".format(b=target_geo, t=object_type, d=data_type), fl=True
    )

    for each in mesh_compo:
        vtx_num = each.split(".")[1]

        target_pos = mc.xform(
            "{b}.{v}".format(b=target_geo, v=vtx_num), q=True, t=True, os=True
        )
        blended_pos = mc.xform(
            "{b}.{v}".format(b=blended_geo, v=vtx_num), q=True, t=True, os=True
        )

        x = target_pos[0] - blended_pos[0]
        y = target_pos[1] - blended_pos[1]
        z = target_pos[2] - blended_pos[2]

        target_vtx = "{t}.{v}".format(t=blended_geo, v=vtx_num)
        mc.move(x, y, z, target_vtx, r=True)


def copy_lr_shape(from_this, to_this, side):
    """All vertices with x values more than 0 in to_this are set to
    the position of from_this.
    All middle vertices move only half way.

    Args:
        from_this (str):
        to_this (str):
        side (str):
    """

    from_this = loc.Dag(from_this)
    to_this = loc.Dag(to_this)

    tg_poses = get_all_point_positions(from_this)
    pntnames = get_all_point_names(to_this)

    tol = 0.002

    for pntname, tgpos in zip(pntnames, tg_poses):
        pos = mc.xform(pntname, q=True, os=True, t=True)

        if -tol < pos[0] < tol:
            _move_diff(pntname, tgpos, pos, 0.5)
            continue

        if side == "L":
            if pos[0] > tol:
                _move_diff(pntname, tgpos, pos, 1)
        elif side == "R":
            if pos[0] < tol:
                _move_diff(pntname, tgpos, pos, 1)


def mirror_asym_shape(base_geo, mirrorthis_geo, tol=0.01):
    """Mirror the shape of the given target_geo.
    The given base_geo is used as the based symetrical shape
    for the calculation.

        Args:
            base_geo (loc.Dag):
            target_geo (loc.Dag):
            tol (float):
    """

    base_geo = loc.Dag(base_geo)
    mirrorthis_geo = loc.Dag(mirrorthis_geo)

    basedag = loc.Dag(base_geo).m_dagpath
    targetdag = loc.Dag(mirrorthis_geo).m_dagpath

    bmfn = om.MFnMesh(basedag)
    tmfn = om.MFnMesh(targetdag)

    bpa = om.MPointArray()
    bmfn.getPoints(bpa, om.MSpace.kObject)

    tpa = om.MPointArray()
    tmfn.getPoints(tpa, om.MSpace.kObject)

    not_sym = []

    for ix in range(bpa.length()):
        px, py, pz = bpa[ix].x, bpa[ix].y, bpa[ix].z

        if px > tol:
            l_vtx = "{t}.vtx[{id}]".format(t=mirrorthis_geo.name, id=ix)
            l_mpos = om.MPoint(tpa[ix].x, tpa[ix].y, tpa[ix].z)

            # Finds a matched right ID.
            flip_point = om.MPoint(-px, py, pz)
            vtxdist = []
            for ix in range(bpa.length()):
                vtxdist.append([bpa[ix].distanceTo(flip_point)])

            # if min(vtxdist)[0] > tol:
            #     continue

            r_id = vtxdist.index(min(vtxdist))
            r_vtx = "{t}.vtx[{id}]".format(t=mirrorthis_geo, id=r_id)
            r_mpos = om.MPoint(tpa[r_id].x, tpa[r_id].y, tpa[r_id].z)

            mc.xform(r_vtx, t=(l_mpos.x * (-1), l_mpos.y, l_mpos.z))
            # mc.xform(l_vtx, t=(r_mpos.x * (-1), r_mpos.y, r_mpos.z))

        elif -tol < px < tol:
            m_id = ix
            m_vtx = "{t}.vtx[{m}]".format(t=mirrorthis_geo.name, m=m_id)
            m_mpos = om.MPoint(tpa[m_id].x, tpa[m_id].y, tpa[m_id].z)

            # mc.xform(m_vtx, t=(m_mpos.x * (-1), m_mpos.y, m_mpos.z))

    # mc.select(not_sym)


# import pymel.core as pm
import maya.OpenMaya as om


def snap_vertex_to_closest(source_vertex, target_object):
    """
    Snaps the given source vertex to the closest vertex on the target object.

    :param source_vertex: The vertex to be snapped (e.g., "pCube1.vtx[0]").
    :param target_object: The object whose vertices will be searched for the closest one.
    """
    # Get the position of the source vertex
    source_pos = pm.PyNode(source_vertex).getPosition(space="world")

    # Get the MFnMesh for the target object
    sel = om.MSelectionList()
    sel.add(target_object)
    dag_path = om.MDagPath()
    sel.getDagPath(0, dag_path)
    mfn_mesh = om.MFnMesh(dag_path)

    # Find the closest point on the mesh to the source vertex
    closest_point = om.MPoint()
    mfn_mesh.getClosestPoint(
        om.MPoint(source_pos[0], source_pos[1], source_pos[2]),
        closest_point,
        om.MSpace.kWorld,
    )

    # Find the closest vertex
    closest_vertex_iter = om.MItMeshVertex(dag_path)
    min_dist = float("inf")
    closest_vertex_index = None

    while not closest_vertex_iter.isDone():
        vert_pos = closest_vertex_iter.position(om.MSpace.kWorld)
        dist = (vert_pos - closest_point).length()
        if dist < min_dist:
            min_dist = dist
            closest_vertex_index = closest_vertex_iter.index()
        closest_vertex_iter.next()

    # Snap the source vertex to the closest vertex
    closest_vertex = "{}.vtx[{}]".format(target_object, closest_vertex_index)
    closest_pos = pm.PyNode(closest_vertex).getPosition(space="world")
    pm.PyNode(source_vertex).setPosition(closest_pos, space="world")

    print(
        "Snapped {} to {} at {}".format(
            source_vertex, closest_vertex, closest_pos
        )
    )


# sels = mc.ls(sl=True,fl=True)
# # Example usage
# for sel in sels:
# 	mc.refresh()
# 	snap_vertex_to_closest(sel, "AvatarBodyLibContainerFBXASC046007")
