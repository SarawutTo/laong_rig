import maya.cmds as mc
from imp import reload

# from typing import Union
from . import utils
from . import vector
from . import rig_base
from . import core as loc
from . import naming_tools as lnt

reload(loc)
reload(lnt)
reload(utils)
reload(vector)
reload(rig_base)


class FingerRig(rig_base.Rigbase):
    def __init__(
        self,
        tmpjnts,
        mod,
        desc="",
        side=None,
        tip_ctrl=False,
        ctrl_par=None,
        jnt_par=None,
    ):
        super(FingerRig, self).__init__(mod, desc, side)
        self.meta = self.create_meta(ctrl_par)
        self.meta.snap(tmpjnts[0])

        # Cast
        tmpjnts = loc.to_dags(tmpjnts)

        self.zrs = []
        self.exs = []
        self.keys = []
        self.ofsts = []
        self.ctrls = []
        self.jnts = []

        is_tip = False
        for ix, tmp_jnt in enumerate(tmpjnts):
            idx = ix + 1
            if tmp_jnt == tmpjnts[-1]:
                is_tip = True

            jnt = self.init_dag(loc.Joint(at=tmp_jnt), "", idx, side, "Jnt")
            jnt.ssc = False

            if is_tip and tip_ctrl:
                ctrl = self.init_dag(
                    loc.Controller(loc.cp.cube), "", idx, side, "Ctrl"
                )
                ctrl.set_color(None, 2)
                ctrl.lhattr("v")
                zr, ex, key, ofst = self._init_quad_grp(ctrl, "", idx, side)
                loc.parent_constraint(ctrl, jnt)
                loc.scale_constraint(ctrl, jnt)
                zr.snap(tmp_jnt)

            else:
                ctrl = self.init_dag(
                    loc.Controller(loc.cp.stick), "", idx, side, "Ctrl"
                )
                ctrl.rotate_shape(90, 0, -90)
                ctrl.set_color(None, 1)
                ctrl.lhattr("v")
                zr, ex, key, ofst = self._init_quad_grp(ctrl, "", idx, side)
                loc.parent_constraint(ctrl, jnt)
                loc.scale_constraint(ctrl, jnt)
                zr.snap(tmp_jnt)

            if self.ctrls:
                zr.set_parent(self.ctrls[-1])
                jnt.set_parent(self.jnts[-1])

            else:
                if jnt_par:
                    jnt.set_parent(jnt_par)
                zr.set_parent(self.meta)

            self.zrs.append(zr)
            self.exs.append(ex)
            self.keys.append(key)
            self.ofsts.append(ofst)
            self.jnts.append(jnt)
            self.ctrls.append(ctrl)


class HandRig(rig_base.Rigbase):
    def __init__(
        self,
        hand_tmpjnt,
        thumb_tmpjnts,
        index_tmpjnts,
        middle_tmpjnts,
        ring_tmpjnts,
        pinky_tmpjnts,
        desc="",
        side=None,
        tip_ctrl=False,
        ctrl_par=None,
        jnt_par=None,
    ):
        super(HandRig, self).__init__("Hand", desc, side)
        self.meta = self.create_meta(ctrl_par)

        # Cast
        finger_count = []  # finger_count: list[FingerRig] = []
        self.hand_jnt = self.init_dag(
            loc.Joint(at=hand_tmpjnt), "", None, self.side, "Jnt"
        )
        if jnt_par:
            self.hand_jnt.set_parent(jnt_par)

        if thumb_tmpjnts:
            self.thumb_rig = FingerRig(
                tmpjnts=thumb_tmpjnts,
                mod="Thumb",
                desc=self.desc,
                side=self.side,
                tip_ctrl=tip_ctrl,
                ctrl_par=self.meta,
                jnt_par=self.hand_jnt,
            )

        if index_tmpjnts:
            self.point_rig = FingerRig(
                tmpjnts=index_tmpjnts,
                mod="Index",
                desc=self.desc,
                side=self.side,
                tip_ctrl=tip_ctrl,
                ctrl_par=self.meta,
                jnt_par=self.hand_jnt,
            )
            finger_count.append(self.point_rig)

        if middle_tmpjnts:
            self.middle_rig = FingerRig(
                tmpjnts=middle_tmpjnts,
                mod="Middle",
                desc=self.desc,
                side=self.side,
                tip_ctrl=tip_ctrl,
                ctrl_par=self.meta,
                jnt_par=self.hand_jnt,
            )
            finger_count.append(self.middle_rig)

        if ring_tmpjnts:
            self.ring_rig = FingerRig(
                tmpjnts=ring_tmpjnts,
                mod="Ring",
                desc=self.desc,
                side=self.side,
                tip_ctrl=tip_ctrl,
                ctrl_par=self.meta,
                jnt_par=self.hand_jnt,
            )
            finger_count.append(self.ring_rig)

        if pinky_tmpjnts:
            self.pinky_rig = FingerRig(
                tmpjnts=pinky_tmpjnts,
                mod="Pinky",
                desc=self.desc,
                side=self.side,
                tip_ctrl=tip_ctrl,
                ctrl_par=self.meta,
                jnt_par=self.hand_jnt,
            )
            finger_count.append(self.pinky_rig)

        self.palm_ctrl = self.init_dag(
            loc.Controller(loc.cp.four_arrow), "", None, side, "Ctrl"
        )
        self.palm_ctrl.set_color(None, 0)
        self.palm_ctrl.lhattr("s", "v")
        self.palm_zr, self.palm_ex, self.palm_ofst = self._init_tri_grp(
            self.palm_ctrl, "", None, side
        )
        self.palm_zr.set_parent(self.meta)
        self.palm_zr.snap(self.middle_rig.zrs[0])

        # Palm Constraint
        middle_con = loc.parent_constraint(
            self.palm_ctrl,
            self.palm_ex,
            self.middle_rig.zrs[0],
            mo=True,
        )

        if len(finger_count) == 4:
            ring_con = loc.parent_constraint(
                self.palm_ctrl,
                self.palm_ex,
                self.ring_rig.zrs[0],
                mo=True,
            )
            loc.parent_constraint(
                self.palm_ctrl, self.pinky_rig.zrs[0], mo=True
            )

            middle_con.attr("w0").v = 0.33333
            middle_con.attr("w1").v = 0.66667

            ring_con.attr("w0").v = 0.66667
            ring_con.attr("w1").v = 0.33333

        elif len(finger_count) == 3:
            ring_con = loc.parent_constraint(
                self.palm_ctrl,
                self.palm_ex,
                self.ring_rig.zrs[0],
                mo=True,
            )
            middle_con.attr("w0").v = 0.2
            middle_con.attr("w1").v = 0.8

            ring_con.attr("w0").v = 0.5
            ring_con.attr("w1").v = 0.5
