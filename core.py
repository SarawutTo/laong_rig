from imp import reload
import maya.cmds as mc
import maya.OpenMaya as om
from . import rig_global as glb

reload(glb)

cp = glb.Cp


class Attribute(object):
    def __init__(self, node, attr):
        self.__name = "{}.{}".format(node, attr)

    def __str__(self):
        return self.__name

    @property
    def name(self):
        return self.__name

    @property
    def value(self):
        return mc.getAttr(self.name)

    @value.setter
    def value(self, new_value):
        mc.setAttr(self.name, new_value)

    v = value


class Core(object):
    def __init__(self, name):
        self.__name = name

    def __str__(self):
        return self.__name

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, new_name):
        mc.rename(self.__name, new_name)
        self.__name = new_name

    def attr(self, attr):
        obj_attr = Attribute(self.name, attr)
        return obj_attr


class Dag(Core):
    def __init__(self, name):
        super(Dag, self).__init__(name)
        sel_list = om.MSelectionList()
        sel_list.add(name)

        self.m_obj = om.MObject()
        self.m_dagpath = om.MDagPath()

        sel_list.getDependNode(0, self.m_obj)
        sel_list.getDagPath(0, self.m_dagpath)

    # List Relative
    def get_parent(self):
        return mc.listRelatives(self.name, p=True)[0]

    def get_shape(self):
        try:
            return mc.listRelatives(self.name, s=True)[0]
        except:
            raise TypeError("Check object type")

    def get_orig(self):
        shape = mc.listRelatives(self.name, type="mesh")
        if len(shape) == 2:
            return shape[1]
        else:
            raise TypeError("Check object OrigShape")

    def get_child(self):
        return mc.listRelatives(self.name, c=True)[0]

    def get_children(self):
        return mc.listRelatives(self.name, c=True)

    # Out-liner
    def set_parent(self, to_this, **kwargs):
        mc.parent(self.name, to_this, **kwargs)

    def set_world(self):
        mc.parent(self.name, w=True)

    @property
    def hide(self):
        value = self.attr("v").v
        if value == 0:
            return True
        elif value == 1:
            return False

    @hide.setter
    def hide(self, value):
        if value == True:
            self.attr("v").v = 0
        elif value == False:
            self.attr("v").v = 1

    # Chanel box
    def lhattr(self, list_attr):
        for attr in list_attr:
            mc.setAttr(self.attr(attr), l=True, k=False)

    def add(self, ln, *args, **kwargs):
        mc.addAttr(ln=ln, *args, **kwargs)
        return self.attr(ln)


class Null(Dag):
    def __init__(self):
        null = mc.createNode("transform")
        super(Null, self).__init__(null)

class Group(Dag):
    def __init__(self, child):
        grp = mc.group(child)
        super(Group, self).__init__(grp)


class Joint(Dag):
    def __init__(self, style=None):
        jnt = mc.createNode("joint")
        super(Joint, self).__init__(jnt)
        self.attr("radius").v = glb.GlobalAttr.radius
        if style:
            self.attr("drawStyle").v = 2


class Surface(Dag):
    def __init__(self, name):
        super(Surface, self).__init__(name)

    def get_point_on_sfc(self, param_u, param_v, space=glb.MSpace.world):
        """Get Point from Surface U V
        Args:
            u_param(int/float):
            v_param(int/float):
            space(Mspace):

        Return:
            point: MPoint
        """
        mfn_surface = om.MFnNurbsSurface(self.m_dagpath)
        point = om.MPoint()
        mfn_surface.getPointAtParam(param_u, param_v, point, space)

        return point

    def get_pnuv_on_sfc(self, param_u, param_v, space=glb.MSpace.world):
        """Get Point Normal TangentU TangentV from Surface U V
        Args:
            u_param(int/float):
            v_param(int/float):
            space(Mspace):

        Return:
            point: MPoint
            normal: MVector
            tangent_u: MVector
            tangent_v: MVector
        """
        mfn_surface = om.MFnNurbsSurface(self.m_dagpath)
        point = om.MPoint()
        mfn_surface.getPointAtParam(param_u, param_v, point, space)
        normal = mfn_surface.normal(param_u, param_v)
        tangent_u = om.MVector()
        tangent_v = om.MVector()
        mfn_surface.getTangents(param_u, param_v, tangent_u, tangent_v)

        return point, normal, tangent_u, tangent_v


class Controller(Dag):
    def __init__(self, cp):
        if cp == "nurbCircle":
            mc.circle(n="Controller")
        else:
            curve = mc.curve(d=1, p=cp, n="Controller")
        super(Controller, self).__init__(curve)


class Node(Core):
    def __init__(self, *args, **kwargs):
        node = mc.createNode(*args, **kwargs)
        super(Node, self).__init__(node)


def create_node(*args, **kwargs):
    return Node(*args, **kwargs)


def create_null(*args, **kwargs):
    return Null(*args, **kwargs)


def group():