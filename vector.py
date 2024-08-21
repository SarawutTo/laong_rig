# System Module
import math
import maya.cmds as mc
import maya.OpenMaya as om

from . import core as loc

# from typing import Union # Uncomment if you need this for Python 3

### Formula Document ###
# dot product = ((ax*bx)+(ay*by)+(az*bz)) * cosine


def lerp(a, b, t):  # lerp(a: float, b: float, t: float) -> float:
    """Linear interpolate on the scale given by a to b, using t as the point on that scale.

    By laundmo
    """
    return (1 - t) * a + t * b


def inv_lerp(a, b, v):  # inv_lerp(a: float, b: float, v: float) -> float:
    """Inverse Linear Interpolation, get the fraction between a and b on which v resides.

    By laundmo
    """
    return (v - a) / (b - a)


def reverse(value):  # reverse(value: float) -> float:
    """Inverse value of value in 1-0 table."""
    return 1 - value


def remap(
    i_min, i_max, o_min, o_max, v
):  # remap(i_min: float, i_max: float, o_min: float, o_max: float, v: float) -> float:
    """Remap values from one linear scale to another, a combination of lerp and inv_lerp.
    i_min and i_max are the scale on which the original value resides,
    o_min and o_max are the scale to which it should be mapped.

    By laundmo
    """
    return lerp(o_min, o_max, inv_lerp(i_min, i_max, v))


def distance_btw(
    root_loc, end_loc
):  # distance_btw(root_loc: loc.Dag, end_loc: loc.Dag) -> float:
    root_vec = om.MVector(*root_loc.world_pos)
    end_vec = om.MVector(*end_loc.world_pos)
    return (end_vec - root_vec).length()


def dot_product(
    vec_a, vec_b
):  # dot_product(vec_a: list[float], vec_b: list[float]) -> float:
    if len(vec_a) != len(vec_b):
        raise ValueError("Vectors must have the same number of dimensions")
    result = 0
    for i in range(len(vec_a)):
        result += vec_a[i] * vec_b[i]
    return result


def vector_degree(u, v):  # vector_degree(u: str, v: str) -> float:
    u_ws = mc.xform(u, q=True, t=True, ws=True)
    v_ws = mc.xform(v, q=True, t=True, ws=True)

    u_vec = om.MVector(*u_ws)
    v_vec = om.MVector(*v_ws)
    dot = u_vec * v_vec
    return math.acos(dot) * 180 / math.pi


def get_vector_a_to_b(
    a, b
):  # get_vector_a_to_b(a: loc.Dag, b: loc.Dag) -> om.MVector:
    a_vec = a.world_vec
    b_vec = b.world_vec
    vector = b_vec - a_vec  # vector: om.MVector = b_vec - a_vec

    return vector


def get_point_btw_2_vector(
    a, b, weight
):  # get_point_btw_2_vector(a: loc.Dag, b: loc.Dag, weight: float) -> om.MVector:
    aim_vec = get_vector_a_to_b(a, b)
    weighted_vec = aim_vec * weight

    return a.world_vec + weighted_vec


def aim_by_vec(
    obj, up_posi, aim_posi
):  # aim_by_vec(obj: str, up_posi: list[float], aim_posi: list[float]) -> None:
    # Positioning
    # pos, norm, _, tv = pru.get_pnuv_at_surface_param(
    #     nrb=self.rbl_nrb, pu = 0.5, pv = ix)

    obj_pos = om.MVector(0, 0, 0)
    up_pos = om.MVector(*up_posi)
    up_pos.normalize()
    aim_pos = om.MVector(*aim_posi)
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
    # mc.xform(obj, t=pos, ws=True)
    mc.xform(obj, ro=rot_value, ws=True)


def get_object_ws_trs(obj):  # get_object_ws_trs(obj: str) -> tuple:
    """Get Object world space trs value.

    Args:
        obj(str): Object name.

    Return:
        trans_value(tuple):
        rotate_value(tuple):
        scale_value(tuple):
    """

    trans_value = mc.xform(obj, q=True, ws=True, t=True)
    obj_mtx = mc.xform(obj, q=True, ws=True, m=True)
    mmtx = om.MMatrix()
    om.MScriptUtil.createMatrixFromList(obj_mtx, mmtx)
    xform_mtx = om.MTransformationMatrix(mmtx)

    euler_rot = xform_mtx.eulerRotation()
    rotate_value = (
        math.degrees(euler_rot.x),
        math.degrees(euler_rot.y),
        math.degrees(euler_rot.z),
    )

    x_vec = om.MVector(obj_mtx[0], obj_mtx[1], obj_mtx[2])
    y_vec = om.MVector(obj_mtx[4], obj_mtx[5], obj_mtx[6])
    z_vec = om.MVector(obj_mtx[8], obj_mtx[9], obj_mtx[10])

    scale_value = (x_vec.length(), y_vec.length(), z_vec.length())

    return trans_value, rotate_value, scale_value


def decompose_matrix(
    matrix,
):  # decompose_matrix(matrix: list[float]) -> tuple:
    mmtx = om.MMatrix()
    om.MScriptUtil.createMatrixFromList(matrix, mmtx)
    xform_mtx = om.MTransformationMatrix(mmtx)

    euler_rot = xform_mtx.eulerRotation()

    x_vec = om.MVector(matrix[0], matrix[1], matrix[2])
    y_vec = om.MVector(matrix[4], matrix[5], matrix[6])
    z_vec = om.MVector(matrix[8], matrix[9], matrix[10])

    translate_value = (matrix[12], matrix[13], matrix[14])
    rotate_value = (
        math.degrees(euler_rot.x),
        math.degrees(euler_rot.y),
        math.degrees(euler_rot.z),
    )
    scale_value = (x_vec.length(), y_vec.length(), z_vec.length())

    return translate_value, rotate_value, scale_value


def get_ik_pole_vector(
    root, mid, end, amp=1.5
):  # get_ik_pole_vector(root: str, mid: str, end: str, amp: float = 1.5) -> om.MVector:
    root_vec = loc.Dag(root).world_vec
    mid_vec = loc.Dag(mid).world_vec
    end_vec = loc.Dag(end).world_vec

    root_end = end_vec - root_vec
    root_mid = mid_vec - root_vec

    half_vector = projection_b_on_a(root_end, root_mid)
    pole_vector_dir = root_mid - half_vector
    pole_vector_dir.normalize()
    ofst_vec = pole_vector_dir * (root_mid.length() * amp)
    pole_vector = ofst_vec + half_vector + root_vec

    return pole_vector


def projection_b_on_a(
    vec_a, vec_b
):  # projection_b_on_a(vec_a: om.MVector, vec_b: om.MVector) -> om.MVector:
    """Formula : b*a/a.length() * a.normalize()
    Args:
        vec_a(om.MVector)
        vec_b(om.MVector)
    Return:
        result(om.MVector)
    """
    new_vec_a = om.MVector(vec_a.x, vec_a.y, vec_a.z)

    dot_prod = new_vec_a * vec_b
    div_length = dot_prod / new_vec_a.length()

    new_vec_a.normalize()
    projection_vector = new_vec_a * div_length

    return projection_vector
