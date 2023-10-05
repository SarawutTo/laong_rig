import os
import sys
import json
import maya.cmds as mc


def get_cwd():
    filepath = mc.file(q=True, sn=True)
    if not filepath:
        raise ValueError("No Path Detect")
    # Get Path For window
    cwd = os.path.dirname(filepath)
    return cwd.replace("/", "\\")


def resolve_path(path):
    parent_replace = ["\t", "\n", "\r", "\f", "\v", "\a", "\b", "\000", "\\"]
    child_replace = ["/t", "/n", "/r", "/f", "/v", "/a", "/b", "/000", "/"]
    for i in range(len(parent_replace)):
        path = path.replace(parent_replace[i], child_replace[i])
    return path


def read_json(path):
    with open(path) as file:
        return json.load(file)


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


def get_current_file_name():
    filepath = mc.file(q=True, sn=True)
    if filepath:
        filename = os.path.basename(filepath)
        raw_name, extension = os.path.splitext(filename)
        return raw_name, extension
    else:
        raise TypeError("File is untitled")


def get_current_file_folder():
    filepath = mc.file(q=True, sn=True)
    if filepath:
        filename = os.path.basename(filepath)
        return filepath.replace(filename, "")
    else:
        raise TypeError("File is untitled")
