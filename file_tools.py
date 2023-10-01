import os
import sys
from imp import reload
from . import system_os as sos
import maya.cmds as mc

reload(sos)


def _init_cwd(cwd=""):
    if not cwd:
        cwd = sos.get_cwd()

    rig_data = os.path.join(cwd, "rig_data")
    hero = os.path.join(cwd, "hero")
    wip = os.path.join(cwd, "wip")
    python = os.path.join(rig_data, "python")
    backup = os.path.join(rig_data, "backup")
    blend = os.path.join(rig_data, "blend")
    weight = os.path.join(rig_data, "weight")
    ctrl = os.path.join(rig_data, "ctrl")

    for path in [rig_data, python, blend, weight, ctrl, hero, backup, wip]:
        if not os.path.exists(path):
            os.mkdir(path)
    print("initialize Path : {}".format(cwd))


def open_last(mod, cwd):
    filepath = sos.resolve_path(os.path.join(cwd, "{}.ma".format(mod)))
    modified_check = check_modified_choice()
    if modified_check == "Save":
        mc.file(s=True)
        mc.file(filepath, o=True)
    elif modified_check == "Don't Save":
        mc.file(filepath, o=True, f=True)
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
