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

        meta = loc.Meta(
            n=lont.construct(f"{self.mod}{self.desc}", None, self.side, "Rig")
        )

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
        still = loc.create_null(
            n=lont.construct(
                f"{self.mod}{self.desc}", None, self.side, "Still"
            )
        )

        if still_par:
            still.set_parent(still_par)
        return still

    def create_space(self, space_par=None):
        """Create Space Grp
        Args:
            space_par(str):
        Return:
            Loc.Dag : Space_Grp
        """

        space = loc.create_null(
            n=lont.construct(
                f"{self.mod}{self.desc}", None, self.side, "Space"
            )
        )

        if space_par:
            space.set_parent(space_par)
        return space

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

    def create_space_switch(
        self, space_driver, space_driven, space_ctrl: loc.Dag, par_grp
    ):
        """ """

        if isinstance(space_driver, dict):
            space_drivers = []
            for space_name, driver in space_driver.items():
                driven_name, _, _, _ = lont.deconstruct(space_driven)

                space_grp = loc.Null()
                space_grp.name = lont.construct(
                    f"{space_name}{driven_name}", None, self.side, "Spc"
                )
                space_piv = loc.Group(space_grp)
                space_piv.name = lont.construct(
                    f"{space_name}{driven_name}", None, self.side, "Piv"
                )

                space_piv.snap(driver)
                space_piv.set_parent(par_grp)
                loc.parent_constraint(driver, space_piv)
                space_drivers.append(space_grp)

            driver_name = [i for i in space_driver.keys()]
            par = loc.parent_constraint(space_drivers, space_driven, mo=True)

            # Space Attr
            space_ctrl.add(
                ln="space", en=":".join(driver_name), at="enum", k=True
            )
            for ix, each in enumerate(space_driver):
                con = loc.create_node(
                    "condition",
                    n="{}{}Space_Con".format(
                        each, str(space_driven).split("_")[0]
                    ),
                )
                con.attr("st").v = ix
                con.attr("colorIfFalseR").v = 0
                con.attr("colorIfTrueR").v = 1

                space_ctrl.attr("space") >> con.attr("ft")
                con.attr("outColorR") >> par.attr(f"w{ix}")
        else:
            loc.parent_constraint(space_driver, space_driven, mo=True)
