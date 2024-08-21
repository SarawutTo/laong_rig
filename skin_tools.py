import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma


class SkinCluster(object):
    """
    skinCluster class for get and set skin weights

    Args:
        skin_cluster_node(str)

    """

    def __init__(self, skin_cluster):
        bind_obj = mc.listConnections(skin_cluster, type="shape")[0]
        sel_mesh = om.MSelectionList()
        sel_mesh.add(bind_obj)
        self.dag_mesh = om.MDagPath()
        sel_mesh.getDagPath(0, self.dag_mesh)

        sel_skin = om.MSelectionList()
        sel_skin.add(skin_cluster)
        mobj_skin = om.MObject()
        sel_skin.getDependNode(0, mobj_skin)
        self.skin_fn = oma.MFnSkinCluster(mobj_skin)

        self.influ = mc.skinCluster(self.skin_fn.name(), q=True, inf=True)
        self.influ_count = len(
            mc.skinCluster(self.skin_fn.name(), q=True, inf=True)
        )

    def get_weights(self):
        get_weights = om.MDoubleArray()
        empty_object = om.MObject()
        util = om.MScriptUtil()
        util.createFromInt(0)
        influ = util.asUintPtr()

        self.skin_fn.getWeights(
            self.dag_mesh, empty_object, get_weights, influ
        )

        weights = []
        list_indx = 0
        while list_indx < len(get_weights):
            slicing = get_weights[list_indx : (list_indx + self.influ_count)]
            weights.append(tuple(slicing))
            list_indx += self.influ_count

        weights = tuple(weights)
        return weights

    def set_weights(self, weight, vtx_id, slicing=False):
        """
        set current skin weight of the "vtx_id" from "weight"
        "index_slicing" set to enable slicing ~ Ex.[0, 5] = [0:5]

        Args:
            weight (tuple): A tuple of weight from "get_weights" Method.
            vtx_id (list): List of the target vertex id.
            index_slicing (bolean) : enable index slicing

        """
        if slicing == False:
            ids = vtx_id
        else:
            ids = range(min(vtx_id), max(vtx_id) + 1)
        for i in ids:
            mc.setAttr(
                "{sk}.weightList[{id}].weights[*]".format(
                    sk=self.skin_fn.name(), id=i
                ),
                *weight[i]
            )


# from imp import reload
# import os
# import sys

# import maya.cmds as mc
# from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
# from mnk_maya_utils import maya_decorator

# sys.path.append(r"/proj/asset/TD/sarawut/")
# sys.path.append(r"/proj/asset/rig/mnkrig")
# sys.path.append(r"/proj/asset/TD/pongsopon/")
# from toe_scripts import qc_tools


# from mnk_qt.Qt.QtCore import Qt
# from mnk_qt.Qt import QtGui, QtWidgets, QtCore
# from mnk_qt.Qt.QtGui import QColor

# from mnk_qt.Qt.QtWidgets import (
#     QMainWindow,
#     QDialog,
#     QPushButton,
#     QMessageBox,
#     QVBoxLayout,
#     QWidget,
#     QLabel,
#     QLineEdit,
# )

# from mnk_qt import qt_utils
# from mnk_maya_utils import widget

# current_dirpath = os.path.dirname(os.path.realpath(__file__))
# setup_path = os.path.join(current_dirpath, "UI/check_cluster_ui.ui")
# UI_class, QtBaseClass = qt_utils.loadUiType(setup_path)


# class WeightClusterUI(QWidget, UI_class):
#     """
#     class to import qt widget
#     """

#     def __init__(self, parent=None):
#         super(WeightClusterUI, self).__init__(parent)
#         self.setupUi(self)
#         # qt_utils.setStyleSheet(
#         #     self, os.path.join(current_dirpath, "UI/style.qss")
#         # )


# class WeightClusterTools(MayaQWidgetBaseMixin, QDialog):
#     """
#     class to run ui in maya
#     """

#     MAYA_UI_NAME = "Check Weight Cluster"

#     def __init__(self, rootWidget=widget.get_main_window(), *args, **kwargs):
#         # run main ui
#         super(WeightClusterTools, self).__init__(rootWidget, *args, **kwargs)
#         if mc.window(self.MAYA_UI_NAME, exists=True):
#             mc.deleteUI(self.MAYA_UI_NAME)
#         self.resize(385, 405)
#         self.setStyleSheet("background-color: #3B3B3B;")
#         self.setObjectName(self.MAYA_UI_NAME)
#         self.setWindowTitle(self.MAYA_UI_NAME)
#         self.init_ui()

#     def init_ui(self):
#         # call ui
#         self.ui = WeightClusterUI()
#         main_layout = QVBoxLayout(self)
#         main_layout.addWidget(self.ui)
#         self.setLayout(main_layout)

#         self.ui.getGeo_btn.clicked.connect(self.get_from_geo)
#         self.ui.getNode_btn.clicked.connect(self.get_from_skinnode)

#     def select_clicked(self, obj):
#         special_key = self.handleButton()
#         if special_key == "Shift":
#             mc.select(obj, tgl=True)
#         elif special_key == "Control":
#             mc.select(obj, d=True)
#         else:
#             mc.select(obj)

#     def handleButton(self):
#         modifiers = QtWidgets.QApplication.keyboardModifiers()
#         if modifiers == QtCore.Qt.ShiftModifier:
#             return "Shift"
#         elif modifiers == QtCore.Qt.ControlModifier:
#             return "Control"
#         else:
#             return ""

#     def add_btn_to_layout_from_dict(self, weight_dict):
#         for ix, (jnt, value) in enumerate(weight_dict.items()):
#             jnt_box = QLineEdit(jnt)
#             jnt_box.setAlignment(Qt.AlignCenter)
#             jnt_box.setReadOnly(True)
#             jnt_box.setMinimumWidth(130)

#             jnt_box.setStyleSheet("background-color: #333333;")
#             self.ui.weightList_layout.addWidget(jnt_box, ix, 0)
#             for iy, cluster in enumerate(value[0]):
#                 btn = QPushButton(str(len(cluster)))
#                 btn.setFixedWidth(50)
#                 btn.setFixedWidth(50)

#                 btn.setObjectName("Btn{}{}_btn".format(ix, iy + 1))
#                 self.ui.weightList_layout.addWidget(btn, ix, iy + 1)
#                 btn.clicked.connect(
#                     lambda obj=cluster: self.select_clicked(obj)
#                 )

#     @maya_decorator.openChunk
#     def get_from_geo(self):
#         self.clean_listwidget()

#         try:
#             sels = mc.ls(sl=True)[0]
#             shape = mc.listRelatives(sels, s=True)[0]
#             if mc.objectType(sels) != "mesh":
#                 raise ValueError()

#         except:
#             return mc.warning("Select Skined Geo")

#         # Get Skin Cluster
#         shape = mc.listRelatives(mc.ls(sl=True)[0], s=True)[0]
#         self.ui.getGeo_lineEdit.setText(mc.ls(sl=True)[0])
#         skin_node = mc.listConnections("{}.inMesh".format(shape))[0]
#         if not mc.objectType(skin_node) == "skinCluster":
#             return mc.warning("No skincluster")

#         self.ui.getSkin_lineEdit.setText(skin_node)

#         weight = qc_tools.seperate_vtx_skin_cluster(skin_node)

#         if weight:
#             self.add_btn_to_layout_from_dict(weight)
#         else:
#             label = QLabel("No Weight Cluster")
#             label.setAlignment(Qt.AlignCenter)
#             self.ui.weightList_layout.addWidget(label, 0, 0)

#     @maya_decorator.openChunk
#     def get_from_skinnode(self):
#         self.clean_listwidget()

#         skin_node = self.ui.getNode_lineEdit.text()

#         self.ui.getSkin_lineEdit.setText(skin_node)

#         weight = qc_tools.seperate_vtx_skin_cluster(skin_node)

#         if weight:
#             self.add_btn_to_layout_from_dict(weight)
#         else:
#             label = QLabel("No Weight Cluster")
#             label.setAlignment(Qt.AlignCenter)
#             self.ui.weightList_layout.addWidget(label, 0, 0)

#     def clean_listwidget(self):
#         for i in reversed(range(self.ui.weightList_layout.count())):
#             self.ui.weightList_layout.itemAt(i).widget().setParent(None)
