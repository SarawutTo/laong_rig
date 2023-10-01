from . import core
from . import rig_base


class PointRig(rig_base.Rigbase):
    def __init__(
        self, tmp_jnts, desc_jnts, mod, desc, meta_parent, still_parent
    ):
        super(self, PointRig).__init__(mod, desc)

        self.meta = self.create_meta(meta_parent)
        self.still = self.create_still(still_parent)

        for tmp_jnt, desc_jnt in zip(tmp_jnts, desc_jnts):
            print(tmp_jnt)
            print(desc_jnt)
