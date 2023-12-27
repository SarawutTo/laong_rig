# Import System Modules.
import os
import re
import json
import maya.cmds as mc

from . import rig_global as rgb


def clean_delete_grp():
    if mc.objExists(rgb.MainGroup.delete_grp):
        mc.delete(rgb.MainGroup.delete_grp)


def clean_meta_data():
    mc.dataStructure(ral=True)


def clean_all():
    clean_delete_grp()
    clean_meta_data()
