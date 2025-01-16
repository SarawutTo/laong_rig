from imp import reload
import maya.cmds as mc
from . import skin_tools
from functools import partial

reload(skin_tools)


class WeightClusterUI(object):
    """
    Class to create a Maya native UI for weight cluster tools (Python 2 compatible).
    """

    WINDOW_NAME = "WeightClusterUI"

    def __init__(self):
        """
        Initialize the UI.
        """
        self.window = None
        self.geo_text_field = None
        self.skin_text_field = None

    def show(self):
        """
        Display the UI.
        """
        if mc.window(self.WINDOW_NAME, exists=True):
            mc.deleteUI(self.WINDOW_NAME, window=True)

        self.window = mc.window(
            self.WINDOW_NAME,
            title="Weight Cluster Tools",
            widthHeight=(250, 755),
            sizeable=True,
        )
        self.layout_ui()
        mc.showWindow(self.window)

    def layout_ui(self):
        """
        Layout the UI components.
        """
        main_layout = mc.columnLayout(adjustableColumn=1, parent=self.window)
        mc.text(label="Check Weight Cluster", h=40)

        mc.rowLayout(
            numberOfColumns=3,
            adjustableColumn=2,
            columnAlign3=("left", "center", "left"),
            columnAttach=(1, "both", 5),
            columnWidth3=[105, 50, 40],
        )

        # Geometry Section
        mc.text(label="Working on Geo:")
        self.geo_text_field = mc.text(
            label="Select a skinned geometry", bgc=(0.168, 0.168, 0.168), h=25
        )
        mc.button(label="Get From Geo", command=lambda _: self.get_from_geo())
        mc.setParent("..")

        mc.rowLayout(
            numberOfColumns=4,
            adjustableColumn=2,
            columnAlign3=("left", "center", "left"),
            columnAttach=(1, "both", 5),
            columnWidth3=[105, 50, 40],
        )

        # Skin Cluster Section
        mc.text(label="Selected Skin Node:")
        self.skin_text_field = mc.textField(
            text="skinCluster17", placeholderText="Skin cluster node", h=27
        )
        self.lock = mc.checkBox(
            "lockField",
            label="Lock",
            changeCommand=self.lock_line,
        )
        mc.button(
            label="Get From Skin Node",
            command=lambda _: self.get_from_skin_node(),
        )
        mc.setParent("..")

        # Weight List Section
        mc.text(label="Weight Clusters:", h=40)
        mc.text(label="", backgroundColor=[0.2, 0.2, 0.2])
        scroll_base = mc.columnLayout(
            adjustableColumn=True,
            parent=main_layout,
        )

        self.scroll_layout = mc.scrollLayout(
            childResizable=True,
            parent=scroll_base,
            h=280,
        )

        mc.setParent("..")
        # Bottom Line
        mc.text(label="", backgroundColor=[0.2, 0.2, 0.2])
        mc.button(label="Clear Vertex Select", command=self.clear_vtx, h=40)

    def get_from_geo(self):
        """
        Handle the "Get From Geo" button click.
        """
        geo = mc.ls(sl=True)[0]
        skin_node = skin_tools.get_related_skin_cluster(geo)

        if not skin_node:
            mc.warning("Skin cluster not found.")
            return

        skin = skin_tools.SkinCluster(skin_node)
        mc.text(self.geo_text_field, e=True, label=skin.bind_obj)

        mc.textField(self.skin_text_field, edit=True, text=skin_node)
        self.populate_weight_list(skin_node)

    def get_from_skin_node(self):
        """
        Handle the "Get From Skin Node" button click.
        """
        skin_node = mc.textField(self.skin_text_field, query=True, text=True)
        if not mc.objExists(skin_node):
            mc.warning("Skin cluster not found.")
            return
        skin = skin_tools.SkinCluster(skin_node)
        mc.text(self.geo_text_field, e=True, label=skin.bind_obj)

        self.populate_weight_list(skin_node)

    def populate_weight_list(self, skin_node):
        """
        Populate the weight list section with buttons representing weight clusters.
        """
        # Clear existing list
        children = (
            mc.scrollLayout(self.scroll_layout, query=True, childArray=True)
            or []
        )
        for child in children:
            mc.deleteUI(child, control=True)

        # Weight data
        skin_func = skin_tools.SkinCluster(skin_node)
        data = skin_func.get_vtx_weight_cluster()
        if not data:
            mc.text(
                label="Clean !",
                p=self.scroll_layout,
                h=50,
                bgc=(0.2, 0.5, 0.2),
            )
            return

        for jnt, vtx_cluster in data.items():
            column_count = len(vtx_cluster) + 1

            row = mc.rowLayout(
                numberOfColumns=column_count,
                parent=self.scroll_layout,
            )

            mc.button(
                label="  {}".format(jnt),
                align="left",
                parent=row,
                bgc=(0.4, 0.4, 0.4),
                h=23,
                w=150,
            )

            for vtx_cluster in vtx_cluster:
                btn_command = partial(self.select_clicked, vtx_cluster)
                btn = mc.button(
                    label=len(vtx_cluster),
                    parent=row,
                    command=btn_command,
                    w=35,
                )
        mc.checkBox(self.lock, e=True, v=True)
        mc.textField(self.skin_text_field, e=True, en=False)

    def select_clicked(self, vtx_group, *args):
        modifiers = mc.getModifiers()
        is_shift = modifiers & 1  # Shift key
        is_ctrl = modifiers & 4  # Ctrl key
        geo = mc.text(self.geo_text_field, q=True, label=True)

        if is_shift:
            mc.select(geo, d=True)
            mc.select(vtx_group, geo, tgl=True)
        elif is_ctrl:
            mc.select(vtx_group, d=True)
        else:
            mc.select(vtx_group, geo)

    def lock_line(self, *arg):
        state = mc.checkBox(self.lock, query=True, value=True)
        if state:
            mc.textField(self.skin_text_field, e=True, en=False)
        else:
            mc.textField(self.skin_text_field, e=True, en=True)

    def clear_vtx(self, *arg):
        geo = mc.text(self.geo_text_field, q=True, label=True)
        mc.select(geo)


# To launch the UI
def show_weight_cluster_ui():
    tool = WeightClusterUI()
    tool.show()
