JOINT_RADIUS = 2
CTRL_SCALE = 1

# Naming Tools
NAME = 0
INDEX = 1
SIDE = 2
KIND = 3


class GlobalAttr(object):
    # World Scale
    radius = JOINT_RADIUS
    ctrl_scale = CTRL_SCALE


class MSpace(object):
    obj = 2
    world = 4
