import maya.cmds as mc


class Attribute(object):
    def __init__(self, node, attr):
        self.__name = '{}.{}'.format(node, attr)

    def __str__(self):
        return self.__name

    @ property
    def name(self):
        return self.__name

    @ property
    def value(self):
        return mc.getAttr(self.name)
    
    @ value.setter
    def value(self,new_value):
        mc.setAttr(self.name, new_value)

    v = value


class Core(object):
    def __init__(self, name):
        self.__name = name

    def __str__(self):
        return self.__name

    @ property
    def name(self):
        return self.__name
    
    @ name.setter
    def name(self, new_name):
        mc.rename(self.__name, new_name)
        self.__name = new_name

    def attr(self, attr):
        obj_attr = Attribute(self.name, attr)
        return obj_attr

    @ property
    def value(self):
        return mc.getAttr(self.attr)


class Dag(Core):
    def __init__(self, name):
        super(Node, self).__init__(name)


class Node(Core):
    def __init__(self, *args, **kwargs):
        node = mc.createNode(*args, **kwargs)
        super(Node, self).__init__(node)
    

def create_node(*args, **kwargs):
    return Node(*args, **kwargs)
    