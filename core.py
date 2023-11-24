from imp import reload
import maya.cmds as mc
import maya.OpenMaya as om
from . import rig_global as glb

reload(glb)

cp = glb.Cp


class Attribute(object):
    def __init__(self, node, attr):
        self.__attr = "{}.{}".format(node, attr)

    def __str__(self):
        return self.__attr

    @property
    def attr(self):
        return self.__attr

    @property
    def value(self):
        return mc.getAttr(self.attr)

    @value.setter
    def value(self, new_value):
        mc.setAttr(self.attr, new_value)

    @property
    def text(self):
        return mc.getAttr(self.attr)

    @text.setter
    def text(self, new_value):
        mc.setAttr(self.attr, new_value, type="string")

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
        try:
            sel_list.add(name)
        except:
            raise mc.error("{} Doesn't Exist".format(name))

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

    # Space
    def snap(self, to_this):
        mc.matchTransform(self.name, to_this)

    def snap_pos(self, to_this):
        mc.matchTransform(self.name, to_this, pos=True)

    def snap_rot(self, to_this):
        mc.matchTransform(self.name, to_this, rot=True)

    def snap_scl(self, to_this):
        mc.matchTransform(self.name, to_this, scl=True)

    def set_pos(self, to_this):
        mc.xform(self.name, t=(to_this))

    def set_rot(self, to_this):
        mc.xform(self.name, r=(to_this))

    def set_scl(self, to_this):
        mc.xform(self.name, s=(to_this))

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
    def __init__(self, n=None):
        if n:
            null = mc.createNode("transform", n=n)
        else:
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


class Meta(Dag):
    def __init__(self, name=None):
        meta_grp = mc.createNode("transform", n=name)
        super(Meta, self).__init__(meta_grp)


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


class Curve(Dag):
    def __init__(self, name):
        super(Curve, self).__init__(name)

    def get_point_at_param(self, param, space=glb.MSpace.world):
        """Get Point from Curve Param
        Args:
            param(int/float):
            space(Mspace):

        Return:
            point: MPoint
        """
        mfn_crv = om.MFnNurbsCurve(self.m_dagpath)
        point = om.MPoint()
        mfn_crv.getPointAtParam(param, point, space)

        return point


class Controller(Dag):
    def __init__(self, cp, n=None):
        if not n:
            n = "Controller"
        if cp == "nurbCircle":
            curve = mc.circle(name=n, ch=False)[0]
        else:
            curve = mc.curve(d=1, p=cp, name=n)
        super(Controller, self).__init__(curve)

    def scale_shape(self, scalev):
        getpivot = mc.xform(self.name, q=True, ws=True, t=True)
        compo = mc.ls("{}.cv[*]".format(self.name), fl=True)
        mc.select(compo)
        mc.scale(scalev, scalev, scalev, p=getpivot, r=True)
        mc.select(cl=True)


class Node(Core):
    def __init__(self, *args, **kwargs):
        node = mc.createNode(*args, **kwargs)
        super(Node, self).__init__(node)


def cast_dags(object_list):
    return [Dag(obj) for obj in object_list]


def create_node(*args, **kwargs):
    return Node(*args, **kwargs)


def create_null(*args, **kwargs):
    return Null(*args, **kwargs)


def parent_constraint(*args, **kwargs):
    return mc.parentConstraint(*args, **kwargs)
