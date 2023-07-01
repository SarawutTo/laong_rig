
import maya.cmds as mc

def get_ws_center(object):
    bbx = mc.xform(object, q=True, bb=True, ws=True) # world space
    x = (bbx[0] + bbx[3]) / 2.0
    y = (bbx[1] + bbx[4]) / 2.0
    z = (bbx[2] + bbx[5]) / 2.0

    return (x, y, z)

def snap_to_pos(object,pos):
    mc.xform(object, t=pos, ws=True)

def get_rml_vtx(object):

    # Get the number of vertices in the mesh
    vtx_count = mc.polyEvaluate(object, vertex=True)

    # Loop through all the vertices in the mesh
    for vtx_id in range(vtx_count):
        # Get the X position of the vertex
        pos = mc.xform(vtx_id,t=True,q=True)
        x_pos = pos[0]
        
        # Check if the X position is less than zero
        if x_pos < 0:
            # If it is, select the vertex
            mc.select('{}.vtx[{}]'.format(object,vtx_id), add=True)


def check_ref_diff(in_scene,ref_file):
    mc.listRelatives(in_scene)
    mc.listRelatives(ref_file)