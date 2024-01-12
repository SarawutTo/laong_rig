# Import System Modules.
import os
import re
import json
import maya.cmds as mc


# Get Cwd Data
def get_cwd():
    """Get Current Maya Working Directory."""
    file_path = mc.file(q=True, sn=True)
    if not file_path:
        raise ValueError("No Path Detect")

    # Get Path For window
    cwd = os.path.dirname(file_path)
    return cwd.replace("/", "\\")


def back_one_dir(absolute_path):
    """Go Back One Directory.
    Args:
        absolute_path(path)
    """
    directory = os.path.dirname(absolute_path)

    return directory


def get_current_path_data() -> tuple[str, str, str, str, str, str]:
    """Get Current File Path Data.

    Args:
        None
    Returns:
        filepath(str): Full File Path.
        filename(str): FileName with Extension.
        version_name(str): FileName with Version.
        raw_name(str): Raw File Name witout Version.
        extension(str): Extension.
    """
    full_path = mc.file(q=True, sn=True)
    path = os.path.dirname(full_path)
    file_name = os.path.basename(full_path)
    version_name, extension = os.path.splitext(file_name)
    raw_name = version_name.split("_")[0]

    return full_path, path, file_name, version_name, raw_name, extension


def resolve_path(path):
    """Resolve Path
    Args:
        path(str):
    """
    parent_replace = ["\t", "\n", "\r", "\f", "\v", "\a", "\b", "\000", "\\"]
    child_replace = ["/t", "/n", "/r", "/f", "/v", "/a", "/b", "/000", "/"]
    for i in range(len(parent_replace)):
        path = path.replace(parent_replace[i], child_replace[i])
    return path


def join_path(*arg, **kwargs):
    """Function Like os.joint but resolve path for window."""
    return resolve_path(os.path.join(*arg, **kwargs))


def list_dir(path):
    """List All Item In Directory
    Args:
        path(list):
    Return:
        list : All Item in Directory
    """
    return os.listdir(r"{}".format(resolve_path(path)))


def check_extension(mod, extension):
    """Check if List file have specific Extension.
    Args:
        mod(str):
        extension(str):
    Return:
        list : All Item That Match Condition
    """
    file_list = []
    for file in file_list:
        if mod in file and extension in file:
            file_list.append(file)
    return file_list


def write_json(data, path):
    # Serializing json
    json_object = json.dumps(data, indent=4)

    # Writing to sample.json
    file = open(path, "w")
    file.write(json_object)

    file.close()


def get_cwd_rigdata():
    return os.path.join(os.path.dirname(get_cwd()), "rig_data")


def get_cwd_python():
    return os.path.join(os.path.dirname(get_cwd()), "rig_data", "python")


def get_cwd_ctrl():
    return os.path.join(os.path.dirname(get_cwd()), "rig_data", "ctrl")


def get_cwd_weight():
    return os.path.join(os.path.dirname(get_cwd()), "rig_data", "weight")


def get_cwd_blend():
    return os.path.join(os.path.dirname(get_cwd()), "rig_data", "blend")


def read_json(path):
    with open(path) as file:
        return json.load(file)
