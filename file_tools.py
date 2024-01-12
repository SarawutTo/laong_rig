# Import System Modules.
import re
import os
import sys
from imp import reload

# Import Modules.
import maya.cmds as mc
from . import system_os as sos
from . import rig_global as rgb
from . import rig_data as rd

reload(sos)
reload(rgb)
reload(rd)


def _init_cwd(cwd=""):
    """Initilize woking directory

    Args:
        cwd(path): Working Directory.
    """
    if not cwd:
        cwd = sos.get_cwd()

    rig_data = os.path.join(cwd, "rig_data")
    hero = os.path.join(cwd, "hero")
    version = os.path.join(cwd, "version")
    wip = os.path.join(cwd, "wip")
    python = os.path.join(rig_data, "python")
    backup = os.path.join(rig_data, "backup")
    blend = os.path.join(rig_data, "blend")
    weight = os.path.join(rig_data, "weight")
    ctrl = os.path.join(rig_data, "ctrl")

    for path in [
        rig_data,
        python,
        version,
        blend,
        weight,
        ctrl,
        hero,
        backup,
        wip,
    ]:
        resolve = sos.resolve_path(path)
        if not os.path.exists(resolve):
            os.mkdir(resolve)
    print("# Finish initialize Path -- {}/".format(sos.resolve_path(cwd)))


def get_lasted_version(file_list):
    """Get Lastest Version File in List.
    Args:
        file_list(list): list of file name.
    Return:
        str : file name
    """
    versions = [
        int(re.findall(r"_v(\d+)", filename)[0])
        if re.findall(r"_v(\d+)", filename)
        else 0
        for filename in file_list
    ]

    return file_list[versions.index(max(versions))]


def get_next_version(file_name):
    """Get Lastest Version File in List.
    Args:
        file_name(list):
    Return:
        str : file name
    """

    match = re.findall(r"(.+)_v(\d+)", file_name)[0][1]

    if match:
        version_number = int(match)
        new_version = version_number + 1
        new_filename = re.sub(
            r"_v\d+", "_v{:03d}".format(new_version), file_name
        )

        return new_filename
    else:
        return "{}_v001".format(file_name)


def open_last(mod, cwd):
    """Open Last Module Last File.
    Args:
        mod(str):
        cwd(path):

    """
    file_list = sos.list_dir(os.path.join(cwd, "version"))

    # Get File Name
    ma_files = []
    for file in file_list:
        if mod in file and ".ma" in file:
            ma_files.append(file)

    lastest_file = get_lasted_version(ma_files)
    file_path = sos.join_path(cwd, "version", lastest_file)

    modified_check = check_modified_choice()
    if modified_check == "Save":
        mc.file(s=True)
        mc.file(file_path, o=True)
        print("Open {}".format(file_path))
    elif modified_check == "Don't Save":
        mc.file(file_path, o=True, f=True)
    else:
        mc.file(file_path, o=True, f=True)


def save_to(mod, cwd):
    """Save to New File if old version already exist use save next instead.
    Args:
        file_name(list):
    Return:
        str : file name
    """
    file_list = sos.list_dir(os.path.join(cwd, "version"))

    # Get File Name
    ma_files = []
    for file in file_list:
        if mod in file and ".ma" in file:
            ma_files.append(file)

    if ma_files:
        nextfile_path = sos.join_path(
            cwd,
            "version",
            get_next_version(get_lasted_version(ma_files)),
        )
        mc.file(rename=nextfile_path)
        mc.file(s=True)
        print("Save to {} //".format(nextfile_path))

    else:
        file_path = sos.join_path(cwd, "version", "{}_v001.ma".format(mod))
        mc.file(rename=file_path)
        mc.file(s=True)
        print("Save to {} //".format(file_path))


def save_next():
    """Save to Next Version."""
    cwd = sos.get_cwd()
    _, _, version_name, _, _ = sos.get_current_path_data()
    nextfile_path = sos.join_path(
        cwd,
        get_next_version(version_name),
    )

    mc.file(rename=nextfile_path)
    mc.file(s=True)

    print("Save to {} //".format(nextfile_path))


def check_modified_choice():
    """Check Modified Choice.
    Args:
        None

    Return:
        Bool : result True/False
    """
    if mc.file(q=True, modified=True):
        result = mc.confirmDialog(
            title="Unsaved Changes",
            message="The current scene has unsaved changes.",
            button=["Save", "Don't Save", "Cancel"],
            defaultButton="Save",
            cancelButton="Cancel",
            dismissString="Cancel",
        )

        return result
    else:
        return False


def rig_current():
    """Check Modified Choice.

    Return:
        Bool : result True/False
    """
    _, _, _, _, raw_name, _ = sos.get_current_path_data()
    path = sos.get_cwd_python()
    import_py = f"import {raw_name}"
    reload_py = f"reload({raw_name})"
    run_function = f"{raw_name}.main()"

    py_fullpath = sos.join_path(path, f"{raw_name}.py")
    if not os.path.exists(py_fullpath):
        raise ValueError(f"# This File Does Not Exist {py_fullpath} ")
    if not path in sys.path:
        sys.path.append(path)
    exec(import_py)
    exec(reload_py)
    exec(run_function)

    # Read Control
    rd.read_control()

    # Delete Grp
    if mc.objExists(rgb.MainGroup.delete_grp):
        mc.setAttr(f"{rgb.MainGroup.delete_grp}.v", 0)


def rig_and_hero():
    """Rig and Hero."""
    rig_current()
    _, path, _, _, raw_name, _ = sos.get_current_path_data()
    rig_path = sos.back_one_dir(path)
    hero_path = sos.join_path(rig_path, "hero", raw_name)

    mc.file(rename=hero_path)
    mc.file(s=True)


def write_ctrl_shape():
    ctrls = mc.ls("*Ctrl")
    print(ctrls)


def open_hero(mod, cwd):
    pass


def ref_hero(mod, cwd):
    pass


def hero_this():
    pass
