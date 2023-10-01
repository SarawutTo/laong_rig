# import the OpenMaya module
import maya.OpenMaya as om

# function that returns a node object given a name

sel_list = om.MSelectionList()
sel_list.add('nurbsPlane1')

m_obj = om.MObject()
m_dagpath = om.MDagPath()

sel_list.getDependNode(0, m_obj)
sel_list.getDagPath(0, m_dagpath)

sel_list.getDagPath(0, m_dagpath)

mfn_surface = om.MFnNurbsSurface(m_dagpath)
output = om.MPoint()
mfn_surface.getPointAtParam(0.5,0.5,output)
