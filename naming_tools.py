from imp import reload
import maya.cmds as mc
from . import core

reload(core)


def deconstruct(obj_name):
    try:
        compo = obj_name.split("_")
    except:
        return TypeError("Cant Split Name")

    if len(compo) == 2:
        return compo[0], None, None, compo[1]

    elif len(compo) == 3:
        if compo[1].isdigit():
            return compo[0], compo[1], None, compo[2]
        else:
            return compo[0], None, compo[1], compo[2]

    elif len(compo) == 4:
        return compo[0], compo[1], compo[2], compo[3]

    else:
        return False


def construct(name, index, side, _type):
    name_list = []
    for compo in [name, index, side, _type]:
        if compo:
            name_list.append(str(compo))

    return "_".join(name_list)
