# Import System Modules.
import os
import re
import json
import maya.cmds as mc

# Import Rig Modules.
from . import core as loc
from . import system_os as sos


def read_weight():
    pass


def write_weight():
    pass


def read_control():
    _, _, _, _, name, _ = sos.get_current_path_data()
    path = sos.join_path(sos.get_cwd_ctrl(), f"{name}_Ctrl.json")
    if not os.path.exists(path):
        return mc.warning(f" # {name} Controller Data Do not Exists //")
    data = sos.read_json(path)
    ctrls = mc.ls("*_Ctrl")
    for ctrl in ctrls:
        if ctrl in data.keys():
            set_shape(ctrl, data)


def write_control():
    _, _, _, _, name, _ = sos.get_current_path_data()
    path = sos.join_path(sos.get_cwd_ctrl(), f"{name}_Ctrl.json")
    data = {}
    ctrls = mc.ls("*_Ctrl")
    if not ctrls:
        raise mc.warning("No Controller Found")

    for ctrl in ctrls:
        ctrl = loc.Dag(ctrl)
        ctrl_data = get_shape(ctrl)
        data[ctrl.name] = ctrl_data

    sos.write_json(data, path)
    print(f"Finish Writing to {path}")


def get_shape(ctrl: loc.Dag):
    shape = ctrl.get_shape()

    shape_dict = {
        "colour": shape.attr("overrideColor").v,
        "span": shape.attr("spans").v,
        "points": [],
        "form": shape.attr("form").v,
        "degree": shape.attr("degree").v,
    }
    points = []

    cp_list = mc.ls(shape.attr("cv[*]"), fl=True)
    for each in cp_list:
        vtx_pos = tuple(
            [round(i, 4) for i in mc.xform(each, q=True, t=True, os=True)]
        )
        points.append(vtx_pos)

    shape_dict["points"] = points

    return shape_dict


def set_shape(ctrl: str, shape_dict: dict):
    mc.rebuildCurve(
        ctrl,
        s=shape_dict[ctrl]["span"],
        d=shape_dict[ctrl]["degree"],
        ch=False,
    )

    cv_pos = shape_dict[ctrl]["points"]
    ctrl_cv = mc.ls(f"{ctrl}.cv[*]", fl=True)
    for cv, pos in zip(ctrl_cv, cv_pos):
        mc.setAttr(cv, *pos)
