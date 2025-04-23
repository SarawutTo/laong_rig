from imp import reload
import os
import sys

from . import skin_tools
import maya.cmds as mc

# from . import bk_undo

from toe_scripts import qc_tools

from PyQt5 import QtWidgets, QtCore, QtGui


from PyQt5 import QtCore

from PyQt5.QtWidgets import (
    QMainWindow,
    QDialog,
    QPushButton,
    QMessageBox,
    QVBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
)

reload(skin_tools)

current_dirpath = os.path.dirname(os.path.realpath(__file__))


class WeightClusterUI(
    QWidget,
):
    """
    class to import qt widget
    """

    def __init__(self, parent=None):
        super(WeightClusterUI, self).__init__(parent)
        self.setupUi(self)


class WeightClusterTools(MayaQWidgetBaseMixin, QDialog):
    """
    class to run ui in maya
    """

    MAYA_UI_NAME = "Check Weight Cluster"

    def __init__(self, rootWidget=widget.get_main_window(), *args, **kwargs):
        # run main ui
        super(WeightClusterTools, self).__init__(rootWidget, *args, **kwargs)
        if mc.window(self.MAYA_UI_NAME, exists=True):
            mc.deleteUI(self.MAYA_UI_NAME)
        self.resize(385, 405)
        self.setStyleSheet("background-color: #3B3B3B;")
        self.setObjectName(self.MAYA_UI_NAME)
        self.setWindowTitle(self.MAYA_UI_NAME)
        self.init_ui()

    def init_ui(self):
        # call ui
        self.ui = WeightClusterUI()
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.ui)
        self.setLayout(main_layout)

        self.ui.getGeo_btn.clicked.connect(self.get_from_geo)
        self.ui.getNode_btn.clicked.connect(self.get_from_skinnode)

    def select_clicked(self, obj):
        special_key = self.handleButton()
        if special_key == "Shift":
            mc.select(obj, tgl=True)
        elif special_key == "Control":
            mc.select(obj, d=True)
        else:
            mc.select(obj)

    def handleButton(self):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            return "Shift"
        elif modifiers == QtCore.Qt.ControlModifier:
            return "Control"
        else:
            return ""

    def add_btn_to_layout_from_dict(self, weight_dict):
        for ix, (jnt, value) in enumerate(weight_dict.items()):
            jnt_box = QLineEdit(jnt)
            jnt_box.setAlignment(Qt.AlignCenter)
            jnt_box.setReadOnly(True)
            jnt_box.setMinimumWidth(130)

            jnt_box.setStyleSheet("background-color: #333333;")
            self.ui.weightList_layout.addWidget(jnt_box, ix, 0)
            for iy, cluster in enumerate(value[0]):
                btn = QPushButton(str(len(cluster)))
                btn.setFixedWidth(50)
                btn.setFixedWidth(50)

                btn.setObjectName("Btn{}{}_btn".format(ix, iy + 1))
                self.ui.weightList_layout.addWidget(btn, ix, iy + 1)
                btn.clicked.connect(
                    lambda obj=cluster: self.select_clicked(obj)
                )

    # @maya_decorator.openChunk
    def get_from_geo(self):
        self.clean_listwidget()

        try:
            sels = mc.ls(sl=True)[0]
            shape = mc.listRelatives(sels, s=True)[0]
            if mc.objectType(sels) != "mesh":
                raise ValueError()

        except:
            return mc.warning("Select Skined Geo")

        # Get Skin Cluster
        shape = mc.listRelatives(mc.ls(sl=True)[0], s=True)[0]
        self.ui.getGeo_lineEdit.setText(mc.ls(sl=True)[0])
        skin_node = mc.listConnections("{}.inMesh".format(shape))[0]
        if not mc.objectType(skin_node) == "skinCluster":
            return mc.warning("No skincluster")

        self.ui.getSkin_lineEdit.setText(skin_node)

        weight = qc_tools.seperate_vtx_skin_cluster(skin_node)

        if weight:
            self.add_btn_to_layout_from_dict(weight)
        else:
            label = QLabel("No Weight Cluster")
            label.setAlignment(Qt.AlignCenter)
            self.ui.weightList_layout.addWidget(label, 0, 0)

    # @maya_decorator.openChunk
    def get_from_skinnode(self):
        self.clean_listwidget()

        skin_node = self.ui.getNode_lineEdit.text()

        self.ui.getSkin_lineEdit.setText(skin_node)

        weight = qc_tools.seperate_vtx_skin_cluster(skin_node)

        if weight:
            self.add_btn_to_layout_from_dict(weight)
        else:
            label = QLabel("No Weight Cluster")
            label.setAlignment(Qt.AlignCenter)
            self.ui.weightList_layout.addWidget(label, 0, 0)

    def clean_listwidget(self):
        for i in reversed(range(self.ui.weightList_layout.count())):
            self.ui.weightList_layout.itemAt(i).widget().setParent(None)
