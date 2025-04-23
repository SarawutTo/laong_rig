from imp import reload
import maya.cmds as mc
import maya.OpenMaya as om
from . import rig_global as rgb
from . import naming_tools as lnt

reload(rgb)

cp = rgb.Cp
main_grp = rgb.MainGroup


class Attribute(object):
    def __init__(self, node, attr):
        self.__nodeattr = "{}.{}".format(node, attr)
        self.__attr = attr
        self.__node = node

    def __str__(self):
        return self.__nodeattr

    def __rshift__(self, destination):
        mc.connectAttr(self, destination, f=True)

    @property
    def attr(self):
        return self.__nodeattr

    @property
    def value(self):
        return mc.getAttr(self.attr)

    @value.setter
    def value(self, new_value):
        mc.setAttr(self.attr, new_value)

    def limit(self, min, max):
        min_enable = 1 if min is not None else 0
        max_enable = 1 if max is not None else 0
        min_value = min if min is not None else 0
        max_value = max if max is not None else 0

        support_attr = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]
        if not self.__attr in support_attr:
            raise ValueError(
                "{} Attribute not support transform limit".format(self.__attr)
            )

        limits_dict = {self.__attr: (min_value, max_value)}
        enable_dict = {"e{}".format(self.__attr): (min_enable, max_enable)}

        # Merge dictionaries for keyword arguments
        command_dict = limits_dict.copy()
        command_dict.update(enable_dict)

        mc.transformLimits(self.__node, **command_dict)

    @property
    def text(self):
        return mc.getAttr(self.attr)

    @text.setter
    def text(self, new_value):
        mc.setAttr(self.attr, new_value, type="string")

    @property
    def lock(self):
        return mc.getAttr(self.attr, q=True, l=True)

    @lock.setter
    def lock(self, lock):
        mc.setAttr(self.attr, l=lock)

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

    def add(self, ln, k=True, *args, **kwargs):
        mc.addAttr(self.name, ln=ln, k=k, *args, **kwargs)
        return self.attr(ln)


class Dag(Core):
    def __init__(self, name):
        super(Dag, self).__init__(name)
        sel_list = om.MSelectionList()
        if not mc.objExists(name) or (len(mc.ls(name)) > 1):
            raise ValueError(
                "{} Object Doesn't Exist or Have Duplicate Name".format(name)
            )

        if isinstance(name, Dag):
            sel_list.add(name.name)
        else:
            sel_list.add(name)

        self.m_obj = om.MObject()
        self.m_dagpath = om.MDagPath()

        sel_list.getDependNode(0, self.m_obj)
        sel_list.getDagPath(0, self.m_dagpath)

    # List Relative
    def get_parent(self):
        return mc.listRelatives(self.name, p=True)[0]

    @property
    def shape(self):
        try:
            return Dag(mc.listRelatives(self.name, s=True)[0])
        except:
            raise TypeError("Check {} object type".format(self.name))

    def get_shape(self):
        try:
            return Dag(mc.listRelatives(self.name, s=True)[0])
        except:
            raise TypeError("Check {} object type".format(self.name))

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

    # Outliner
    def set_parent(self, to_this, **kwargs):
        if to_this:
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

    def center_pivot(self):
        mc.xform(self.name, cp=True)

    def freeze(self):
        mc.makeIdentity(self.name, a=True)

    @property
    def world_pos(self):
        world_pos = mc.xform(self.name, q=True, t=True, ws=True)
        return world_pos

    @property
    def world_vec(self):
        world_pos = mc.xform(self.name, q=True, t=True, ws=True)
        world_vec = om.MVector(*world_pos)
        return world_vec

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
    def lhattr(self, *args):
        for attr in args:
            if attr in ["t", "r", "s"]:
                attr_list = [
                    "{}x".format(attr),
                    "{}y".format(attr),
                    "{}z".format(attr),
                ]
                for xyz_attr in attr_list:
                    mc.setAttr(self.attr(xyz_attr), l=True, k=False, cb=False)

            else:
                mc.setAttr(self.attr(attr), l=True, k=False, cb=False)


class Null(Dag):
    def __init__(self, n=None):
        if n:
            null = mc.createNode("transform", n=n)
        else:
            null = mc.createNode("transform")
        super(Null, self).__init__(null)


class Locator(Dag):
    def __init__(self, n=None):
        if n:
            locator = mc.spaceLocator(n=n)[0]
        else:
            locator = mc.spaceLocator()[0]
        super(Locator, self).__init__(locator)


class Group(Dag):
    def __init__(self, child):
        grp = mc.group(child)
        super(Group, self).__init__(grp)


class Joint(Dag):
    def __init__(self, at=None, style=None):
        jnt = mc.createNode("joint")
        super(Joint, self).__init__(jnt)
        self.attr("radius").v = rgb.GlobalAttr.radius

        if at:
            self.snap(at)
            self.freeze()

        if style:
            self.attr("drawStyle").v = style

    @property
    def ssc(self):
        return self.attr("ssc").v

    @ssc.setter
    def ssc(self, value):
        self.attr("ssc").v = value


class Meta(Dag):
    def __init__(self, n=None):
        meta_grp = mc.createNode("transform", n=n)
        super(Meta, self).__init__(meta_grp)


class Surface(Dag):
    def __init__(self, name):
        super(Surface, self).__init__(name)

    def get_point_on_sfc(self, param_u, param_v, space=rgb.MSpace.world):
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

    def get_pnuv_on_sfc(self, param_u, param_v, space=rgb.MSpace.world):
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

    def rotate_shape(self, x, y, z):
        getpivot = mc.xform(self.name, q=True, rp=True, ws=True)
        compo = mc.ls("{}.cv[*]".format(self.name), fl=True)
        mc.select(compo)
        mc.rotate(x, y, z, p=getpivot, r=True)
        mc.select(cl=True)

    def scale_shape(self, scale):
        getpivot = mc.xform(self.name, q=True, sp=True, ws=True)
        compo = mc.ls("{}.cv[*]".format(self.name), fl=True)
        mc.select(compo)
        mc.scale(scale, scale, scale, p=getpivot, r=True)
        mc.select(cl=True)
        print(getpivot)

    def rebuild(self, *args, **kwargs):
        mc.rebuildCurve(self.name, *args, **kwargs)

    def get_point_at_param(self, param, space=rgb.MSpace.world):
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


class Controller(Curve):
    def __init__(self, cp, n=None):
        if not n:
            n = "Controller"
        if cp == "nurbCircle":
            curve = mc.circle(ch=False, nr=(1, 0, 0))[0]
        else:
            curve = mc.curve(
                d=1,
                p=cp,
            )

        super(Controller, self).__init__(curve)
        self.name = n

    def set_color(self, color=None, tone=0):
        shape = self.get_shape()
        shape.attr("overrideEnabled").v = 1

        if not color:
            _, _, side, _ = lnt.deconstruct(self.name)
            color_dict = {
                (0, None): rgb.Color.yellow,
                (1, None): rgb.Color.yellow_soft,
                (2, None): rgb.Color.yellow_dark,
                (0, "L"): rgb.Color.blue,
                (1, "L"): rgb.Color.blue_soft,
                (2, "L"): rgb.Color.blue_dark,
                (0, "R"): rgb.Color.red,
                (1, "R"): rgb.Color.red_soft,
                (2, "R"): rgb.Color.red_dark,
            }
            color = color_dict.get((tone, side))

        shape.attr("overrideColor").v = color


class Node(Core):
    def __init__(self, *args, **kwargs):
        node = mc.createNode(*args, **kwargs)
        super(Node, self).__init__(node)


def to_dags(object_list):
    return [Dag(obj) for obj in object_list]


def create_node(*args, **kwargs):
    return Node(*args, **kwargs)


def create_remap(in_min, in_max, out_min, out_max):
    remap = create_node("remapValue")
    remap.attr("inputMin").v = in_min
    remap.attr("inputMax").v = in_max
    remap.attr("outputMin").v = out_min
    remap.attr("outputMax").v = out_max

    return remap


def create_follicle(u=0, v=0, surface=None):
    """
    Return:
        Dag: Follicle Transform
        Dag: Follicle Shape
    """
    folshp = Dag(mc.createNode("follicle"))
    foltrans = Dag(mc.listRelatives(folshp, p=True)[0])

    folshp.attr("parameterU").v = u
    folshp.attr("parameterV").v = v
    folshp.attr("outRotate") >> foltrans.attr("rotate")
    folshp.attr("outTranslate") >> foltrans.attr("translate")
    foltrans.attr("inheritsTransform").v = False

    if surface:
        surface = Surface(surface)
        surface.attr("local") >> folshp.attr("inputSurface")
        surface.attr("worldMatrix[0]") >> folshp.attr("inputWorldMatrix")

    return foltrans, folshp


def create_nsurface(span, uv, axis=rgb.Axis.z):
    if uv == "U" or uv == "u":
        surface = mc.nurbsPlane(
            ax=axis,
            u=(span - 1),
            v=1,
            w=1,
            lr=0.1,
            ch=False,
        )[0]
    elif uv == "V" or uv == "v":
        surface = mc.nurbsPlane(
            ax=axis, u=1, v=(span - 1), w=0.1, lr=10, ch=False
        )[0]

    return Surface(surface)


def create_null(*args, **kwargs):
    return Null(*args, **kwargs)


def create_curve(*args, **kwargs):
    return Curve(mc.curve(*args, **kwargs))


def parent_constraint(*args, **kwargs):
    con = mc.parentConstraint(*args, **kwargs)
    return Dag(con[0])


def point_constraint(*args, **kwargs):
    con = mc.pointConstraint(*args, **kwargs)
    return Dag(con[0])


def orient_constraint(*args, **kwargs):
    con = mc.orientConstraint(*args, **kwargs)
    return Dag(con[0])


def scale_constraint(*args, **kwargs):
    con = mc.scaleConstraint(*args, **kwargs)
    return Dag(con[0])


def aim_constraint(*args, **kwargs):
    con = mc.aimConstraint(*args, **kwargs)
    return Dag(con[0])
