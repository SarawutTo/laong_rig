# System Module
import math
import maya.cmds as mc
import maya.OpenMaya as om


def calculate_length(root_loc, end_loc):
    root_vec = om.MVector(*root_loc.world_pos)
    end_vec = om.MVector(*end_loc.world_pos)
    return (end_vec - root_vec).length()

def dot_product(vec_a, vec_b):
    if len(vec_a) != len(vec_b):
        raise ValueError("Vectors must have the same number of dimensions")
    result = 0
    for i in range(len(vec_a)):
        result += vec_a[i] * vec_b[i]
    return result

def vector_degree(u, v):

    u_ws = mc.xform(u, q=True, t=True, ws=True)
    v_ws = mc.xform(v, q=True, t=True, ws=True)
    
    u_vec = om.MVector(*u_ws)
    v_vec = om.MVector(*v_ws)
    dot = u_vec*v_vec
    return math.acos(dot) * 180 / math.pi

def _get_vector_a_to_b(a, b):
    a_pos = om.MVector(*a.world_pos)
    b_pos = om.MVector(*b.world_pos)
    vector = b_pos - a_pos
    vector.normalize()

    return vector

def aim_by_vec(obj, up_posi, aim_posi):
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
        v_vec.x, v_vec.y, v_vec.z, 0, 
        u_vec.x, u_vec.y, u_vec.z, 0, 
        w_vec.x, w_vec.y, w_vec.z, 0, 
        0, 0, 0, 1
    ]
    matx = om.MMatrix()
    om.MScriptUtil.createMatrixFromList(mtx_list, matx)
    xform_mtx = om.MTransformationMatrix(matx)

    euler_rot = xform_mtx.eulerRotation()
    rot_value = [
        math.degrees(euler_rot.x), 
        math.degrees(euler_rot.y), 
        math.degrees(euler_rot.z)
    ]
    # mc.xform(obj, t=pos, ws=True)
    mc.xform(obj, ro=rot_value, ws=True)

# sels = mc.ls(sl=True)
# A = sels[0]
# B = sels[1]

# A_pos = mc.xform(A, q=True, t=True)
# B_pos = mc.xform(B, q=True, t=True)


# curves = mc.curve(d=1, p=(A_pos,B_pos),n='Btw_Crv')

# cvs = mc.ls('{}.cv[:]'.format(curves), fl = True)

# A_cluster = mc.cluster(cvs[0], n='{}_Cst'.format(A))
# B_cluster = mc.cluster(cvs[1], n='{}_Cst'.format(B))
# mc.hide(A_cluster, B_cluster)
# mc.parent(A_cluster,A)
# mc.parent(B_cluster,B)

