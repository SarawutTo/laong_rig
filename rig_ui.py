import maya.cmds as cmds
from imp import reload
from . import file_tools as ft
from . import rig_data as rd

# Reload the modules
reload(ft)
reload(rd)


def show():
    if cmds.window("RigUI", exists=True):
        cmds.deleteUI("RigUI")

    window = cmds.window(
        "RigUI",
        title=" Rig Tools",
        sizeable=True,
        widthHeight=(300, 400),
    )

    cmds.columnLayout(adjustableColumn=True)

    # Create a frame layout (border group) for all UI elements
    cmds.frameLayout(
        label="",
        collapsable=False,
        marginWidth=10,
        marginHeight=10,
    )

    cmds.rowLayout(
        numberOfColumns=3,
        adjustableColumn=2,
        columnAlign3=("left", "left", "left"),
        columnAttach=(1, "both", 5),
        columnWidth3=[75, 50, 40],
    )
    cmds.text(label="Directory :")
    path_field = cmds.textField(placeholderText="Working Directory")
    cmds.button(label="Browse", command=lambda _: browse_directory(path_field))
    cmds.setParent("..")

    cmds.rowLayout(
        numberOfColumns=2,
        adjustableColumn=2,
        columnAlign=(1, "center"),
        columnAttach=(1, "both", 5),
    )
    cmds.text(label="Part :")
    body_name_field = cmds.textField(placeholderText="Enter Part", w=10)
    cmds.setParent("..")

    # Buttons for operations
    cmds.button(
        label="Init Workspace",
        command=lambda _: open_last(body_name_field, path_field),
        h=35,
    )

    cmds.button(
        label="Open Last",
        command=lambda _: open_last(body_name_field, path_field),
        h=35,
    )

    cmds.button(label="Save increment", command=lambda _: ft.save_next(), h=35)

    cmds.frameLayout(
        label="Controller",
        collapsable=False,
        marginWidth=10,
        marginHeight=10,
    )
    cmds.rowLayout(
        numberOfColumns=2, columnAttach2=("both", "both"), columnOffset2=(5, 5)
    )

    cmds.button(
        label="Write Control",
        command=lambda _: rd.write_control(),
        h=35,
        w=120,
    )
    cmds.button(
        label="Read Control",
        command=lambda _: rd.read_control(),
        h=35,
        w=120,
    )
    cmds.setParent("..")
    cmds.setParent("..")

    cmds.frameLayout(
        label="Rig",
        collapsable=False,
        marginWidth=10,
        marginHeight=10,
    )
    cmds.button(label="Rig Current", command=lambda _: ft.rig_current(), h=35)
    cmds.button(
        label="Rig and Hero", command=lambda _: ft.rig_and_hero(), h=35
    )

    cmds.showWindow(window)


def browse_directory(cwd_field):
    directory = cmds.fileDialog2(fileMode=2, dialogStyle=2)
    if directory:
        cmds.textField(cwd_field, edit=True, text=directory[0])


def open_last(body_name_field, cwd_field):
    cwd = cmds.textField(cwd_field, query=True, text=True)
    body_name = cmds.textField(body_name_field, query=True, text=True)

    if not cwd or not body_name:
        return

    ft.open_last(body_name, cwd)
