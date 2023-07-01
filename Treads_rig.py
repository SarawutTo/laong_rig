import maya.cmds as mc


def treads_rig(curve, object, capacity ,circle=True):
    
    object = mc.ls(object)
    quantity = len(object)
    result = []
    capacity = float(capacity)
    each_dis = capacity/(quantity)

    if circle == True:
        offset = 0
    else :
        offset = 1

    for i in range(0,quantity+offset):
        out_num = i*each_dis
        result.append(out_num)

    path = mc.pathAnimation('pCube1',curve = 'curve1')
    mc.delete(mc.listConnections(path)[0])
    mc.setAttr('{path}.u'i*result)

def change_naming(object):
    sels = mc.ls(object)

    for each in sels:
        name = each.split('_')
        newname = '{n}{i}_{s}_{t}'.format(n=name[0], i=name[2], s=name[1], t=name[3])
        mc.rename(each,newname)
	
def rename(part,side,type):

    if side == 'L':
        side = '_L'
    if side == 'R':
        side = '_R'
    else:
        side = ''
    
    sels = mc.ls(sl=True)
    for ix, each in enumerate(sels):
        new_name = '{p}{i}{s}{t}'.format(p=part, i=ix, s=side, t=type)
        mc.rename(each,new_name)
