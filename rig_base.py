from imp import reload
import core
import naming_tools as naming

reload(core)


class Rigbase(object):
    def __init__(self, mod, desc):
        self.mod = mod
        self.desc = desc

    def _init_dag(self, dag, name, index, side, _type):
        rigname = "{}{}{}".format(name, self.mod, self.desc)
        dag_name = naming.construct(rigname, index, side, _type)
        try:
            dag.name = dag_name
        except:
            raise TypeError("{} is not from Core".format(dag))

        return dag

    def _init_node(self, node, name, index, side, _type):
        rigname = "{}{}".format(name, self.mod, self.desc)
        node_name = naming.construct(rigname, index, side, _type)
        try:
            node.name = node_name
        except:
            raise TypeError("{} is not from Core".format(node))

        return node

    def create_meta(self, meta_par=None):
        """Create Meta
        Args:
            meta_par(str):
        Return:
            Loc.Dag : Meta_Grp
        """
        meta = core.Meta(name="{}{}Rig_Grp".format(self.mod, self.desc))

        # Add Data
        meta.add(
            ln="modName",
            nn="Mod Name :",
            dt="string",
        )
        meta.attr("modName").text = "{}{}".format(self.mod, self.desc)

        if meta_par:
            meta.snap(meta_par)
            meta.set_parent(meta_par)

        return meta

    def create_still(self, still_par=None):
        """Create Still Grp
        Args:
            still_par(str):
        Return:
            Loc.Dag : Still_Grp
        """
        still = core.create_null()
        still.name = "{}{}Still_Grp".format(self.mod, self.desc)
        if still_par:
            still.set_parent(still_par)
        return still

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
        rigname = "{}{}{}".format(name, self.mod, self.desc)
        ofst = core.Group(child)
        ex = core.Group(ofst)
        zr = core.Group(ex)

        ofst.name = naming.construct(rigname, index, side, "Ofst")
        ex.name = naming.construct(rigname, index, side, "Ex")
        zr.name = naming.construct(rigname, index, side, "Zr")

        return zr, ex, ofst

    def _init_tri_grp(self, child, name, index, side):
        """Create Zr Offset Group On Top of Childe Object
        Args:
            child(str):
            name(str):
            index(int):
            side('L'/'R'):
        Return:
            Loc.Dag : Zr Group
            Loc.Dag : Offset Group
        """
        rigname = "{}{}{}".format(name, self.mod, self.desc)
        ofst = core.Group(child)
        zr = core.Group(ofst)

        ofst.name = naming.construct(rigname, index, side, "Ofst")
        zr.name = naming.construct(rigname, index, side, "Zr")

        return zr, ofst

    def create_group_on_top(self, child, name, index, side, _type):
        """Create Group On Top of Childe Object
        Args:
            child(str):
            name(str):
            index(int):
            side('L'/'R'):
            _type(str):
        Return:
            Loc.Dag : Group
        """
        rigname = "{}{}{}".format(name, self.mod, self.desc)
        grp = core.Group(child)
        grp.name = naming.construct(rigname, index, side, _type)

        return grp
