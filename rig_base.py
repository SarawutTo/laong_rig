from imp import reload
from . import core as loc
from . import naming_tools as lnt

reload(loc)
reload(lnt)


class Rigbase(object):
    def __init__(self, mod, desc, side=None):
        self.mod = mod
        self.desc = desc
        if not side:
            side = ""
        self.side = side

        self.skin_jnts = []
        self.main_ctrl = []
        self.sub_ctrl = []
        self.dtl_ctrl = []

    def init_dag(self, dag, name, index, side, _type):
        rigname = "{}{}{}".format(name, self.mod, self.desc)
        dag_name = lnt.construct(rigname, index, side, _type)
        try:
            dag.name = dag_name
        except:
            raise TypeError("{} is not from Core".format(dag))

        return dag

    def init_node(self, node, name, index, side, _type):
        rigname = "{}{}".format(name, self.mod, self.desc)
        node_name = lnt.construct(rigname, index, side, _type)
        try:
            node.name = node_name
        except:
            raise TypeError("{} is not from Core".format(node))

        return node

    def create_meta(self, par=None):
        """Create Meta
        Args:
            side(str):
            meta_par(str):
        Return:
            Loc.Dag : Meta_Grp
        """
        meta = loc.Meta(
            n=lnt.construct(
                "{}{}".format(self.mod, self.desc), None, self.side, "Rig"
            )
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
        if par:
            meta.snap(par)
            meta.set_parent(par)

        return meta

    def create_still(self, par=None):
        """Create Still Grp
        Args:
            still_par(str):
        Return:
            Loc.Dag : Still_Grp
        """
        still = loc.create_null(
            n=lnt.construct(
                "{}{}".format(self.mod, self.desc), None, self.side, "Still"
            )
        )

        if par:
            still.set_parent(par)
        return still

    def create_space(self, par=None):
        """Create Space Grp
        Args:
            space_par(str):
        Return:
            Loc.Dag : Space_Grp
        """
        space = loc.create_null(
            n=lnt.construct(
                "{}{}".format(self.mod, self.desc), None, self.side, "Space"
            )
        )

        if par:
            space.set_parent(par)
        return space

    def create_driver(self, par=None):
        """Create ShapeDriver Grp
        Args:
            par(str):
        Return:
            Loc.Dag : ShapeDriver_Grp
        """
        sd = loc.create_null(
            n=lnt.construct(
                "{}{}".format(self.mod, self.desc),
                None,
                self.side,
                "ShapeDriver",
            )
        )
        sd.lhattr("t", "r", "s", "v")

        if par:
            sd.set_parent(par)
        return sd

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

        ofst.name = lnt.construct(rigname, index, side, "Ofst")
        zr.name = lnt.construct(rigname, index, side, "Zr")

        return zr, ofst

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
        ofst = loc.Null()
        ex = loc.Group(ofst)
        zr = loc.Group(ex)
        child.set_parent(ofst)

        ofst.name = lnt.construct(rigname, index, side, "Ofst")
        ex.name = lnt.construct(rigname, index, side, "Ex")
        zr.name = lnt.construct(rigname, index, side, "Zr")

        return zr, ex, ofst

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
            Loc.Dag : Key Group
            Loc.Dag : Offset Group
        """
        rigname = "{}{}{}".format(name, self.mod, self.desc)
        ofst = loc.Null()
        key = loc.Group(ofst)
        ex = loc.Group(key)
        zr = loc.Group(ex)
        child.set_parent(ofst)

        ofst.name = lnt.construct(rigname, index, side, "Ofst")
        ex.name = lnt.construct(rigname, index, side, "Ex")
        key.name = lnt.construct(rigname, index, side, "Key")
        zr.name = lnt.construct(rigname, index, side, "Zr")

        return zr, ex, key, ofst

    def split_to_pos_neg(self, node, shape, name, attr, neg, pos):
        cap_attr = lnt.upfirst(attr)
        rigname_pos = "{}{}Pos{}{}".format(name, cap_attr, self.mod, self.desc)
        rigname_neg = "{}{}Neg{}{}".format(name, cap_attr, self.mod, self.desc)

        pos_clamp = loc.create_node("clamp")
        neg_clamp = loc.create_node("clamp")

        pos_clamp.name = lnt.construct(rigname_pos, None, self.side, "Clamp")
        neg_clamp.name = lnt.construct(rigname_neg, None, self.side, "Clamp")

        # Set clamp ranges
        pos_clamp.attr("minR").v = 0
        pos_clamp.attr("maxR").v = pos

        neg_clamp.attr("minR").v = neg
        neg_clamp.attr("maxR").v = 0

        # Connect the input attribute to the clamps
        node.attr(attr) >> pos_clamp.attr("inputR")
        node.attr(attr) >> neg_clamp.attr("inputR")

        node.attr(attr).limit(neg, pos)

        pos_attr = shape.add(ln="{}{}Pos".format(name, cap_attr), k=False)
        neg_attr = shape.add(ln="{}{}Neg".format(name, cap_attr), k=False)

        pos_clamp.attr("outputR") >> pos_attr
        neg_clamp.attr("outputR") >> neg_attr

        return pos_attr, neg_attr

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
        grp.name = lnt.construct(rigname, index, side, _type)

        return grp

    def create_space_switch(
        self, space_driver, space_driven, space_ctrl, par_grp
    ):
        """ """

        if isinstance(space_driver, dict):
            space_drivers = []
            for space_name, driver in space_driver.items():
                driven_name, _, _, _ = lnt.deconstruct(space_driven)

                space_grp = loc.Null()
                space_grp.name = lnt.construct(
                    "{}{}".format(space_name, driven_name),
                    None,
                    self.side,
                    "Spc",
                )
                space_piv = loc.Group(space_grp)
                space_piv.name = lnt.construct(
                    "{}{}".format(space_name, driven_name),
                    None,
                    self.side,
                    "Piv",
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
                    n=lnt.construct(
                        "{}{}Space".format(
                            each, str(space_driven).split("_")[0]
                        ),
                        None,
                        self.side,
                        "Con",
                    ),
                )
                con.attr("st").v = ix
                con.attr("colorIfFalseR").v = 0
                con.attr("colorIfTrueR").v = 1

                space_ctrl.attr("space") >> con.attr("ft")
                con.attr("outColorR") >> par.attr("w{}".format(ix))
        else:
            loc.parent_constraint(space_driver, space_driven, mo=True)
