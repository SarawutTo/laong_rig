import maya.cmds as mc
import numpy

mat_list = mc.ls(type="RedshiftMaterial")

for mat_node in mat_list:
    lamb = mc.shadingNode("lambert", asShader=True)

    checkin_con = mc.listConnections(mat_node, c=True, s=True, d=False, p=True)
    in_attrs = checkin_con[1::2]
    out_attrs = checkin_con[::2]
    sf_shd = mc.listConnections("{}.outColor".format(mat_node), d=True)[0]
    mc.connectAttr(
        "{}.outColor".format(lamb), "{}.surfaceShader".format(sf_shd), f=True
    )

    for out_attr, in_attr in zip(out_attrs, in_attrs):
        node, attr = out_attr.split(".")
        newnode = node.replace(mat_node, lamb)
        if attr == "diffuse_color":
            attr = "color"
        if attr == "opacity_color":
            attr = "transparency"
        mc.connectAttr(in_attr, newnode + "." + attr, f=True)
        print(in_attr, newnode + "." + attr)

    mc.delete(mat_node)
