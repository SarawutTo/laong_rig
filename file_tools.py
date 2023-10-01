import os
import sys
from imp import reload
from . import system_os as sos
import maya.cmds as mc
import re

reload(sos)


def _init_cwd(cwd=""):
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
        file_list(list):
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


def open_last(mod, cwd):
    """ """
    file_list = sos.list_dir(os.path.join(cwd, "version"))

    # Get File Name
    ma_files = []
    for file in file_list:
        if mod in file and ".ma" in file:
            ma_files.append(file)

    lastest_file = get_lasted_version(ma_files)
    file_path = sos.resolve_path(os.path.join(cwd, "version", lastest_file))

    modified_check = check_modified_choice()
    if modified_check == "Save":
        mc.file(s=True)
        mc.file(file_path, o=True)
        print("Open {}".format(file_path))
    elif modified_check == "Don't Save":
        mc.file(file_path, o=True, f=True)
    else:
        pass


def check_modified_choice():
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
    name, _ = sos.get_current_file_name()
    path = sos.get_cwd_python()
    import_py = "import {}".format(name)
    reload_py = "reload({})".format(name)
    run_function = "{}.main()".format(name)
    if not path in sys.path:
        sys.path.append(path)
    exec(import_py)
    exec(reload_py)
    exec(run_function)

