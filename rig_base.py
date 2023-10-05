import core
import naming_tools as naming


class Rigbase(object):
    def __init__(self, mod, desc):
        self.mod = mod
        self.desc = desc

    def _init_dag(self, dag, name, index, side, _type):
        rigname = "{}{}Rig".format(name, self.mod, self.desc)
        dag_name = naming.construct(rigname, index, side, _type)
        try:
            dag.name = dag_name
        except:
            raise TypeError("{} is not from Core".format(dag))

        return dag

    def _init_node(self, node, name, index, side, _type):
        rigname = "{}{}Rig".format(name, self.mod, self.desc)
        node_name = naming.construct(rigname, index, side, _type)
        try:
            node.name = node_name
        except:
            raise TypeError("{} is not from Core".format(node))

        return node

    def create_meta(self, meta_par=None):
        meta = core.create_null()
        meta.name = "{}{}Rig_Grp".format(self.mod, self.desc)
        if meta_par:
            meta.set_parent(meta_par)
        return meta.name

    def create_still(self, still_par=None):
        still = core.create_null()
        still.name = "{}{}Still_Grp".format(self.mod, self.desc)
        if still_par:
            still.set_parent(still_par)
        return still.name

    def _init_quad_grp(self, child, name, index, side):
        """Create Zr Extra Offset Group On Top of Childe Object
        Args:
            child(str):
            name(str):
            index(int):
            side('L'/'R'):
        Return:
            Loc.Dag : Zr Group
            Loc.Dag : Extra Group
            Loc.Dag : Offset Group
        """
        rigname = "{}{}Rig".format(name, self.mod, self.desc)
        ofst = core.Group(child)
        ex = core.Group(ofst)
        zr = core.Group(ex)

        ofst.name = naming.construct(rigname, index, side, "Ofst")
        ex.name = naming.construct(rigname, index, side, "Ex")
        zr.name = naming.construct(rigname, index, side, "Zr")

        return zr, ex, ofst
