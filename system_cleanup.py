# Import System Modules.
import os
import re
import json
import maya.cmds as mc

DELETE_GRP = "Delete_Grp"


def clean_delete_grp():
    if mc.objExists(DELETE_GRP):
        mc.delete(DELETE_GRP)


def clean_meta_data():
    mc.dataStructure(ral=True)


def clean_all():
    clean_delete_grp()
    clean_meta_data()
