from imp import reload
from . import core as loc
from . import naming_tools as lont

reload(loc)
reload(lont)


class Rigbase(object):
    def __init__(self, mod, desc, side=None):
        self.mod = mod
        self.desc = desc
        self.side = side

        self.skin_jnts = []
        self.main_ctrl = []
        self.sub_ctrl = []
        self.dtl_ctrl = []

    def _init_dag(self, dag, name, index, side, _type):
        rigname = "{}{}{}".format(name, self.mod, self.desc)
        dag_name = lont.construct(rigname, index, side, _type)
        try:
            dag.name = dag_name
        except:
            raise TypeError("{} is not from Core".format(dag))

        return dag

    def _init_node(self, node, name, index, side, _type):
        rigname = "{}{}".format(name, self.mod, self.desc)
        node_name = lont.construct(rigname, index, side, _type)
        try:
            node.name = node_name
        except:
            raise TypeError("{} is not from Core".format(node))

        return node

    def create_meta(self, meta_par=None):
        """Create Meta
        Args:
            side(str):
            meta_par(str):
        Return:
            Loc.Dag : Meta_Grp
        """
        if self.side:
            n = "{}{}_{}_Rig".format(self.mod, self.desc, self.side)
        else:
            n = "{}{}_Rig".format(self.mod, self.desc)
        meta = loc.Meta(name=n)

        # Add Data
        meta.add(
            ln="modName",
            nn="Mod Name :",
            dt="string",
        )
        meta.attr("modName").text = "{}".format(self.mod)

        meta.add(
            ln="descName",
            nn="Desc Name :",
            dt="string",
        )
        meta.attr("descName").text = "{}".format(self.desc)

        meta.add(ln="side", nn="Side :", dt="string")
        meta.attr("side").text = self.side

        meta.add(ln="detailVis", k=True, min=0, max=1, dv=1)

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
        if self.side:
            n = "{}{}_{}_Still".format(self.mod, self.desc, self.side)
        else:
            n = "{}{}Still_Grp".format(self.mod, self.desc)
        still = loc.create_null()
        still.name = n

        if still_par:
            still.set_parent(still_par)
        return still

    def _init_tri_grp(self, child, name, index, side):
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
        ofst = loc.Group(child)
        ex = loc.Group(ofst)
        zr = loc.Group(ex)

        ofst.name = lont.construct(rigname, index, side, "Ofst")
        ex.name = lont.construct(rigname, index, side, "Ex")
        zr.name = lont.construct(rigname, index, side, "Zr")

        return zr, ex, ofst

    def _init_duo_grp(self, child, name, index, side):
        """Create Zr Offset Group On Top of Childe Object
        Args:
            child(Dag):
            name(str):
            index(int):
            side('L'/'R'):
        Return:
            Loc.Dag : Zr Group
            Loc.Dag : Offset Group
        """
        rigname = "{}{}{}".format(name, self.mod, self.desc)
        ofst = loc.Null()
        zr = loc.Group(ofst)
        child.set_parent(ofst)

        ofst.name = lont.construct(rigname, index, side, "Ofst")
        zr.name = lont.construct(rigname, index, side, "Zr")

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
        grp = loc.Group(child)
        grp.name = lont.construct(rigname, index, side, _type)

        return grp
