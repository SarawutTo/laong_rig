# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
## Copyright
"""
Copyright (C) Toshio Ishida. All rights reserved.
"""
# -------------------------------------------------------------------------------

__author__ = "Toshio Ishida [isd.toshio@gmail.com]"


import os
import sys

sys.dont_write_bytecode = True
import re

# from maya.common.utils import getSourceNodeFromPlug
from maya import cmds, mel

# humanIK Crash Bug
cmds.evaluationManager(mode="off")

# reference
from maya.app.quickRig import quickRigUI as qr


def set_HumanIK(name, hik_info):
    hikInitialize()
    if cmds.ls(name):
        hikDeleteControlRig(name)
        cmds.delete(name)

    hikCreateCharacter(name)
    hikSetCurrentCharacter(name)
    hikUpdateTool()

    set_definition(name, hik_info)
    hikUpdateTool()

    HIKCH = hikGetCurrentCharacter()
    HIKpp = cmds.listConnections(HIKCH + ".propertyState", s=1, d=0) or []
    for roll in hikRolls:
        cmds.setAttr(HIKpp[0] + "." + roll[0], roll[1])

    hikCreateControlRig(name)
    hikUpdateTool()


def get_definition(character):
    hikBones = {}
    hik_count = cmds.hikGetNodeCount()
    for i in range(hik_count):
        bone = mel.eval('hikGetSkNode( "%s" , %d )' % (character, i))
        # bone = getSourceNodeFromPlug( cmds.GetHIKNode( character , i ) )
        if bone:
            hik_name = cmds.GetHIKNodeName(i)
            hikBones[hik_name] = {"bone": bone, "hikid": i}
    return hikBones


def set_definition(character, definition_info):
    hikBones = {}
    for hik_name, d_info in definition_info.items():
        bone = d_info.get("bone")
        hikid = d_info.get("hikid")
        mel.eval(
            'setCharacterObject("%s", "%s", %s, 0)' % (bone, character, hikid)
        )


def assume_preferred_angle(definition_info):
    for hik_name, d_info in definition_info.items():
        bone = d_info.get("bone")
        try:
            cmds.joint(bone, e=1, apa=1, ch=1)
        except:
            pass


def hikui():
    mel.eval("HIKCharacterControlsTool;")


def hikUpdateTool():
    melCode = """
        if ( hikIsCharacterizationToolUICmdPluginLoaded() )
        {
            hikUpdateCharacterList();
            hikUpdateCurrentCharacterFromUI();
            hikUpdateContextualUI();
            hikControlRigSelectionChangedCallback;

            hikUpdateSourceList();
            hikUpdateCurrentSourceFromUI();
            hikUpdateContextualUI();
            hikControlRigSelectionChangedCallback;
        }
        """
    try:
        mel.eval(melCode)
    except:
        pass


def hikNoneString():
    return mel.eval("hikNoneString()") or ""


def hikCreateCharacter(nameHint):
    return mel.eval('hikCreateCharacter( "%s" )' % nameHint)


def hikInitialize():
    if mel.eval("exists hikGetCurrentCharacter"):
        character = hikGetCurrentCharacter()
    else:
        character = ""
    mel.eval("HIKCharacterControlsTool();")
    cmds.refresh()
    hikSetCurrentCharacter(character)


def hikGetCurrentCharacter():
    return mel.eval("hikGetCurrentCharacter()") or ""


def hikSetCurrentCharacter(character):
    return mel.eval('hikSetCurrentCharacter( "%s" )' % character)


def hikCreateControlRig(character):
    melCode = """hikSetCurrentCharacter( "%s" ); hikCreateControlRig();"""
    mel.eval(melCode % character)


def hikDeleteControlRig(character):
    melCode = """hikSetCurrentCharacter( "%s" ); hikDeleteControlRig();"""
    mel.eval(melCode % character)


def hikGetControlRig(character):
    return mel.eval('hikGetControlRig( "%s" )' % character) or ""


def hikGetSkeletonNodesMap(character):
    nodes = {}
    for i in range(cmds.hikGetNodeCount()):
        sourceNode = mel.eval('hikGetSkNode( "%s" , %d )' % (character, i))
        if sourceNode:
            nodes[cmds.GetHIKNodeName(i)] = sourceNode
    return nodes


# def hikSetCurrentSourceFromCharacter(character):
#     melCode = """hikSetCurrentSourceFromCharacter( "%s" );"""
#     mel.eval( melCode % character )


def hikSetSource(character, typeid):
    hikSetCurrentCharacter(character)
    _HUMAN_IK_SOURCE_MENU = "hikSourceList"
    _HUMAN_IK_SOURCE_MENU_OPTION = _HUMAN_IK_SOURCE_MENU + "|OptionMenu"
    cmds.optionMenu(_HUMAN_IK_SOURCE_MENU_OPTION, e=True, sl=typeid)
    mel.eval("hikUpdateCurrentSourceFromUI()")
    mel.eval("hikUpdateContextualUI()")
    mel.eval("hikControlRigSelectionChangedCallback")


def getEffFromHikNode(hikNode="Hips"):
    effCount = cmds.GetHIKEffectorCount()
    effecter = None
    for effid in range(effCount):
        effecter = cmds.GetHIKEffectorName(effid)
        FKId = cmds.GetFKIdFromEffectorId(effid)
        if hikNode == cmds.GetHIKNodeName(FKId):
            return effecter
    return None


def getCtrlFromHikCtrl(HIK_NAME, hikNode="Hips"):
    ctrlrig = hikGetControlRig(HIK_NAME)
    ctrl = cmds.listConnections(ctrlrig + "." + hikNode) or []
    if ctrl:
        return ctrl[0]
    return None


hik_info = {
    "RightInHandIndex": {"hikid": 153, "bone": "finger_R0_0_jnt"},
    "RightHandIndex1": {"hikid": 78, "bone": "finger_R0_1_jnt"},
    "RightHandIndex2": {"hikid": 79, "bone": "finger_R0_2_jnt"},
    "RightHandIndex3": {"hikid": 80, "bone": "finger_R0_3_jnt"},
    "RightHandIndex4": {"hikid": 81, "bone": "finger_R0_4_jnt"},
    "RightInHandPinky": {"hikid": 156, "bone": "finger_R3_0_jnt"},
    "RightHandPinky1": {"hikid": 90, "bone": "finger_R3_1_jnt"},
    "RightHandPinky2": {"hikid": 91, "bone": "finger_R3_2_jnt"},
    "RightHandPinky3": {"hikid": 92, "bone": "finger_R3_3_jnt"},
    "RightHandPinky4": {"hikid": 93, "bone": "finger_R3_4_jnt"},
    "LeftInHandMiddle": {"hikid": 148, "bone": "finger_L1_0_jnt"},
    "LeftHandMiddle1": {"hikid": 58, "bone": "finger_L1_1_jnt"},
    "LeftHandMiddle2": {"hikid": 59, "bone": "finger_L1_2_jnt"},
    "LeftHandMiddle3": {"hikid": 60, "bone": "finger_L1_3_jnt"},
    "LeftHandMiddle4": {"hikid": 61, "bone": "finger_L1_4_jnt"},
    "LeftInHandIndex": {"hikid": 147, "bone": "finger_L0_0_jnt"},
    "LeftHandIndex1": {"hikid": 54, "bone": "finger_L0_1_jnt"},
    "LeftHandIndex2": {"hikid": 55, "bone": "finger_L0_2_jnt"},
    "LeftHandIndex3": {"hikid": 56, "bone": "finger_L0_3_jnt"},
    "LeftHandIndex4": {"hikid": 57, "bone": "finger_L0_4_jnt"},
    "RightInHandRing": {"hikid": 155, "bone": "finger_R2_0_jnt"},
    "RightHandRing1": {"hikid": 86, "bone": "finger_R2_1_jnt"},
    "RightHandRing2": {"hikid": 87, "bone": "finger_R2_2_jnt"},
    "RightHandRing3": {"hikid": 88, "bone": "finger_R2_3_jnt"},
    "RightHandRing4": {"hikid": 89, "bone": "finger_R2_4_jnt"},
    "LeftHandThumb1": {"hikid": 50, "bone": "thumb_L0_0_jnt"},
    "LeftHandThumb2": {"hikid": 51, "bone": "thumb_L0_1_jnt"},
    "LeftHandThumb3": {"hikid": 52, "bone": "thumb_L0_2_jnt"},
    "LeftHandThumb4": {"hikid": 53, "bone": "thumb_L0_3_jnt"},
    "RightHandThumb1": {"hikid": 74, "bone": "thumb_R0_0_jnt"},
    "RightHandThumb2": {"hikid": 75, "bone": "thumb_R0_1_jnt"},
    "RightHandThumb3": {"hikid": 76, "bone": "thumb_R0_2_jnt"},
    "RightHandThumb4": {"hikid": 77, "bone": "thumb_R0_3_jnt"},
    "LeftInHandRing": {"hikid": 149, "bone": "finger_L2_0_jnt"},
    "LeftHandRing1": {"hikid": 62, "bone": "finger_L2_1_jnt"},
    "LeftHandRing2": {"hikid": 63, "bone": "finger_L2_2_jnt"},
    "LeftHandRing3": {"hikid": 64, "bone": "finger_L2_3_jnt"},
    "LeftHandRing4": {"hikid": 65, "bone": "finger_L2_4_jnt"},
    "LeftInHandPinky": {"hikid": 150, "bone": "finger_L3_0_jnt"},
    "LeftHandPinky1": {"hikid": 66, "bone": "finger_L3_1_jnt"},
    "LeftHandPinky2": {"hikid": 67, "bone": "finger_L3_2_jnt"},
    "LeftHandPinky3": {"hikid": 68, "bone": "finger_L3_3_jnt"},
    "LeftHandPinky4": {"hikid": 69, "bone": "finger_L3_4_jnt"},
    "RightInHandMiddle": {"hikid": 154, "bone": "finger_R1_0_jnt"},
    "RightHandMiddle1": {"hikid": 82, "bone": "finger_R1_1_jnt"},
    "RightHandMiddle2": {"hikid": 83, "bone": "finger_R1_2_jnt"},
    "RightHandMiddle3": {"hikid": 84, "bone": "finger_R1_3_jnt"},
    "RightHandMiddle4": {"hikid": 85, "bone": "finger_R1_4_jnt"},
    "Spine": {"hikid": 8, "bone": "spine_C0_0_jnt"},
    "Spine1": {"hikid": 23, "bone": "spine_C0_1_jnt"},
    "Spine2": {"hikid": 24, "bone": "spine_C0_2_jnt"},
    "LeftHand": {"hikid": 11, "bone": "wrist_L0_0_jnt"},
    "RightHand": {"hikid": 14, "bone": "wrist_R0_0_jnt"},
    "Neck": {"hikid": 20, "bone": "neck_C0_0_jnt"},
    "Neck1": {"hikid": 32, "bone": "neck_C0_1_jnt"},
    "Head": {"hikid": 15, "bone": "head_C0_0_jnt"},
    "LeftArm": {"hikid": 9, "bone": "uparm_L0_0_jnt"},
    "LeftUpLeg": {"hikid": 2, "bone": "upleg_L0_0_jnt"},
    "LeftLeg": {"hikid": 3, "bone": "lowleg_L0_0_jnt"},
    "LeftForeArm": {"hikid": 10, "bone": "lowarm_L0_0_jnt"},
    "RightForeArm": {"hikid": 13, "bone": "lowarm_R0_0_jnt"},
    "LeftShoulder": {"hikid": 18, "bone": "clavicle_L0_0_jnt"},
    "RightShoulder": {"hikid": 19, "bone": "clavicle_R0_0_jnt"},
    "Hips": {"hikid": 1, "bone": "hip_C0_0_jnt"},
    "RightArm": {"hikid": 12, "bone": "uparm_R0_0_jnt"},
    # "Reference": {
    #    "hikid": 0,
    #    "bone": "reference"
    # },
    "LeftToeBase": {"hikid": 16, "bone": "toe_L0_0_jnt"},
    "RightToeBase": {"hikid": 17, "bone": "toe_R0_0_jnt"},
    "LeftFoot": {"hikid": 4, "bone": "ankle_L0_0_jnt"},
    "RightUpLeg": {"hikid": 5, "bone": "upleg_R0_0_jnt"},
    "RightLeg": {"hikid": 6, "bone": "lowleg_R0_0_jnt"},
    "RightFoot": {"hikid": 7, "bone": "ankle_R0_0_jnt"},
}

# twist_hik
hik_info = {
    "Head": {"bone": "head_C0_0_jnt", "hikid": 15},
    "Hips": {"bone": "hip_C0_0_jnt", "hikid": 1},
    "LeafLeftArmRoll1": {"bone": "uparmTwist_L0_0_jnt", "hikid": 176},
    "LeafLeftArmRoll2": {"bone": "uparmTwist_L0_1_jnt", "hikid": 184},
    "LeafLeftArmRoll3": {"bone": "uparmTwist_L0_2_jnt", "hikid": 192},
    "LeafLeftArmRoll4": {"bone": "uparmTwist_L0_3_jnt", "hikid": 200},
    "LeafLeftArmRoll5": {"bone": "uparmTwist_L0_4_jnt", "hikid": 208},
    "LeafLeftForeArmRoll1": {"bone": "wristTwist_L0_0_jnt", "hikid": 177},
    "LeafLeftForeArmRoll2": {"bone": "wristTwist_L0_1_jnt", "hikid": 185},
    "LeafLeftForeArmRoll3": {"bone": "wristTwist_L0_2_jnt", "hikid": 193},
    "LeafLeftForeArmRoll4": {"bone": "wristTwist_L0_3_jnt", "hikid": 201},
    "LeafLeftForeArmRoll5": {"bone": "wristTwist_L0_4_jnt", "hikid": 209},
    "LeafLeftLegRoll1": {"bone": "ankleTwist_L0_0_jnt", "hikid": 173},
    "LeafLeftLegRoll2": {"bone": "ankleTwist_L0_1_jnt", "hikid": 181},
    "LeafLeftLegRoll3": {"bone": "ankleTwist_L0_2_jnt", "hikid": 189},
    "LeafLeftLegRoll4": {"bone": "ankleTwist_L0_3_jnt", "hikid": 197},
    "LeafLeftLegRoll5": {"bone": "ankleTwist_L0_4_jnt", "hikid": 205},
    "LeafLeftUpLegRoll1": {"bone": "uplegTwist_L0_00_jnt", "hikid": 172},
    "LeafLeftUpLegRoll2": {"bone": "uplegTwist_L0_01_jnt", "hikid": 180},
    "LeafLeftUpLegRoll3": {"bone": "uplegTwist_L0_02_jnt", "hikid": 188},
    "LeafLeftUpLegRoll4": {"bone": "uplegTwist_L0_03_jnt", "hikid": 196},
    "LeafLeftUpLegRoll5": {"bone": "uplegTwist_L0_04_jnt", "hikid": 204},
    "LeafRightArmRoll1": {"bone": "uparmTwist_R0_0_jnt", "hikid": 178},
    "LeafRightArmRoll2": {"bone": "uparmTwist_R0_1_jnt", "hikid": 186},
    "LeafRightArmRoll3": {"bone": "uparmTwist_R0_2_jnt", "hikid": 194},
    "LeafRightArmRoll4": {"bone": "uparmTwist_R0_3_jnt", "hikid": 202},
    "LeafRightArmRoll5": {"bone": "uparmTwist_R0_4_jnt", "hikid": 210},
    "LeafRightForeArmRoll1": {"bone": "wristTwist_R0_0_jnt", "hikid": 179},
    "LeafRightForeArmRoll2": {"bone": "wristTwist_R0_1_jnt", "hikid": 187},
    "LeafRightForeArmRoll3": {"bone": "wristTwist_R0_2_jnt", "hikid": 195},
    "LeafRightForeArmRoll4": {"bone": "wristTwist_R0_3_jnt", "hikid": 203},
    "LeafRightForeArmRoll5": {"bone": "wristTwist_R0_4_jnt", "hikid": 211},
    "LeafRightLegRoll1": {"bone": "ankleTwist_R0_0_jnt", "hikid": 175},
    "LeafRightLegRoll2": {"bone": "ankleTwist_R0_1_jnt", "hikid": 183},
    "LeafRightLegRoll3": {"bone": "ankleTwist_R0_2_jnt", "hikid": 191},
    "LeafRightLegRoll4": {"bone": "ankleTwist_R0_3_jnt", "hikid": 199},
    "LeafRightLegRoll5": {"bone": "ankleTwist_R0_4_jnt", "hikid": 207},
    "LeftArm": {"bone": "uparm_L0_0_jnt", "hikid": 9},
    "LeftFoot": {"bone": "ankle_L0_0_jnt", "hikid": 4},
    "LeftForeArm": {"bone": "lowarm_L0_0_jnt", "hikid": 10},
    "LeftHand": {"bone": "wrist_L0_0_jnt", "hikid": 11},
    "LeftHandIndex1": {"bone": "finger_L0_1_jnt", "hikid": 54},
    "LeftHandIndex2": {"bone": "finger_L0_2_jnt", "hikid": 55},
    "LeftHandIndex3": {"bone": "finger_L0_3_jnt", "hikid": 56},
    "LeftHandIndex4": {"bone": "finger_L0_4_jnt", "hikid": 57},
    "LeftHandMiddle1": {"bone": "finger_L1_1_jnt", "hikid": 58},
    "LeftHandMiddle2": {"bone": "finger_L1_2_jnt", "hikid": 59},
    "LeftHandMiddle3": {"bone": "finger_L1_3_jnt", "hikid": 60},
    "LeftHandMiddle4": {"bone": "finger_L1_4_jnt", "hikid": 61},
    "LeftHandPinky1": {"bone": "finger_L3_1_jnt", "hikid": 66},
    "LeftHandPinky2": {"bone": "finger_L3_2_jnt", "hikid": 67},
    "LeftHandPinky3": {"bone": "finger_L3_3_jnt", "hikid": 68},
    "LeftHandPinky4": {"bone": "finger_L3_4_jnt", "hikid": 69},
    "LeftHandRing1": {"bone": "finger_L2_1_jnt", "hikid": 62},
    "LeftHandRing2": {"bone": "finger_L2_2_jnt", "hikid": 63},
    "LeftHandRing3": {"bone": "finger_L2_3_jnt", "hikid": 64},
    "LeftHandRing4": {"bone": "finger_L2_4_jnt", "hikid": 65},
    "LeftHandThumb1": {"bone": "thumb_L0_0_jnt", "hikid": 50},
    "LeftHandThumb2": {"bone": "thumb_L0_1_jnt", "hikid": 51},
    "LeftHandThumb3": {"bone": "thumb_L0_2_jnt", "hikid": 52},
    "LeftHandThumb4": {"bone": "thumb_L0_3_jnt", "hikid": 53},
    "LeftInHandIndex": {"bone": "finger_L0_0_jnt", "hikid": 147},
    "LeftInHandMiddle": {"bone": "finger_L1_0_jnt", "hikid": 148},
    "LeftInHandPinky": {"bone": "finger_L3_0_jnt", "hikid": 150},
    "LeftInHandRing": {"bone": "finger_L2_0_jnt", "hikid": 149},
    "LeftLeg": {"bone": "lowleg_L0_0_jnt", "hikid": 3},
    "LeftShoulder": {"bone": "clavicle_L0_0_jnt", "hikid": 18},
    "LeftToeBase": {"bone": "toe_L0_0_jnt", "hikid": 16},
    "LeftUpLeg": {"bone": "upleg_L0_0_jnt", "hikid": 2},
    "Neck": {"bone": "neck_C0_0_jnt", "hikid": 20},
    "Neck1": {"bone": "neck_C0_1_jnt", "hikid": 32},
    "RightArm": {"bone": "uparm_R0_0_jnt", "hikid": 12},
    "RightFoot": {"bone": "ankle_R0_0_jnt", "hikid": 7},
    "RightForeArm": {"bone": "lowarm_R0_0_jnt", "hikid": 13},
    "RightHand": {"bone": "wrist_R0_0_jnt", "hikid": 14},
    "RightHandIndex1": {"bone": "finger_R0_1_jnt", "hikid": 78},
    "RightHandIndex2": {"bone": "finger_R0_2_jnt", "hikid": 79},
    "RightHandIndex3": {"bone": "finger_R0_3_jnt", "hikid": 80},
    "RightHandIndex4": {"bone": "finger_R0_4_jnt", "hikid": 81},
    "RightHandMiddle1": {"bone": "finger_R1_1_jnt", "hikid": 82},
    "RightHandMiddle2": {"bone": "finger_R1_2_jnt", "hikid": 83},
    "RightHandMiddle3": {"bone": "finger_R1_3_jnt", "hikid": 84},
    "RightHandMiddle4": {"bone": "finger_R1_4_jnt", "hikid": 85},
    "RightHandPinky1": {"bone": "finger_R3_1_jnt", "hikid": 90},
    "RightHandPinky2": {"bone": "finger_R3_2_jnt", "hikid": 91},
    "RightHandPinky3": {"bone": "finger_R3_3_jnt", "hikid": 92},
    "RightHandPinky4": {"bone": "finger_R3_4_jnt", "hikid": 93},
    "RightHandRing1": {"bone": "finger_R2_1_jnt", "hikid": 86},
    "RightHandRing2": {"bone": "finger_R2_2_jnt", "hikid": 87},
    "RightHandRing3": {"bone": "finger_R2_3_jnt", "hikid": 88},
    "RightHandRing4": {"bone": "finger_R2_4_jnt", "hikid": 89},
    "RightHandThumb1": {"bone": "thumb_R0_0_jnt", "hikid": 74},
    "RightHandThumb2": {"bone": "thumb_R0_1_jnt", "hikid": 75},
    "RightHandThumb3": {"bone": "thumb_R0_2_jnt", "hikid": 76},
    "RightHandThumb4": {"bone": "thumb_R0_3_jnt", "hikid": 77},
    "RightInHandIndex": {"bone": "finger_R0_0_jnt", "hikid": 153},
    "RightInHandMiddle": {"bone": "finger_R1_0_jnt", "hikid": 154},
    "RightInHandPinky": {"bone": "finger_R3_0_jnt", "hikid": 156},
    "RightInHandRing": {"bone": "finger_R2_0_jnt", "hikid": 155},
    "RightLeg": {"bone": "lowleg_R0_0_jnt", "hikid": 6},
    "RightShoulder": {"bone": "clavicle_R0_0_jnt", "hikid": 19},
    "RightToeBase": {"bone": "toe_R0_0_jnt", "hikid": 17},
    "RightUpLeg": {"bone": "upleg_R0_0_jnt", "hikid": 5},
    "Spine": {"bone": "spine_C0_0_jnt", "hikid": 8},
    "Spine1": {"bone": "spine_C0_1_jnt", "hikid": 23},
    "Spine2": {"bone": "spine_C0_2_jnt", "hikid": 24},
    "Spine3": {"bone": "spine_C0_3_jnt", "hikid": 25},
}


hikRolls = [
    ["ParamLeafLeftArmRoll1", 0],
    ["ParamLeafLeftArmRoll2", 0.25],
    ["ParamLeafLeftArmRoll3", 0.5],
    ["ParamLeafLeftArmRoll4", 0.75],
    ["ParamLeafLeftArmRoll5", 1],
    ["ParamLeafRightArmRoll1", 0],
    ["ParamLeafRightArmRoll2", 0.25],
    ["ParamLeafRightArmRoll3", 0.5],
    ["ParamLeafRightArmRoll4", 0.75],
    ["ParamLeafRightArmRoll5", 1],
    ["ParamLeafLeftForeArmRoll1", 0],
    ["ParamLeafLeftForeArmRoll2", 0.25],
    ["ParamLeafLeftForeArmRoll3", 0.5],
    ["ParamLeafLeftForeArmRoll4", 0.75],
    ["ParamLeafLeftForeArmRoll5", 1],
    ["ParamLeafRightForeArmRoll1", 0],
    ["ParamLeafRightForeArmRoll2", 0.25],
    ["ParamLeafRightForeArmRoll3", 0.5],
    ["ParamLeafRightForeArmRoll4", 0.75],
    ["ParamLeafRightForeArmRoll5", 1],
    ["ParamLeafLeftUpLegRoll1", 0],
    ["ParamLeafLeftUpLegRoll2", 0.2],
    ["ParamLeafLeftUpLegRoll3", 0.5],
    ["ParamLeafLeftUpLegRoll4", 0.75],
    ["ParamLeafLeftUpLegRoll5", 1],
    ["ParamLeafLeftLegRoll1", 0],
    ["ParamLeafLeftLegRoll2", 0.25],
    ["ParamLeafLeftLegRoll3", 0.5],
    ["ParamLeafLeftLegRoll4", 0.75],
    ["ParamLeafLeftLegRoll5", 1],
    ["ParamLeafRightUpLegRoll1", 0],
    ["ParamLeafRightUpLegRoll2", 0.2],
    ["ParamLeafRightUpLegRoll3", 0.5],
    ["ParamLeafRightUpLegRoll4", 0.75],
    ["ParamLeafRightUpLegRoll5", 1],
    ["ParamLeafRightLegRoll1", 0],
    ["ParamLeafRightLegRoll2", 0.25],
    ["ParamLeafRightLegRoll3", 0.5],
    ["ParamLeafRightLegRoll4", 0.75],
    ["ParamLeafRightLegRoll5", 1],
]

if __name__ == "main":
    set_HumanIK("CHARACTER", hik_info)
