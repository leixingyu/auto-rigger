import maya.cmds as cmds

from autoRigger.module.base import bone
from autoRigger import util

from utility.algorithm import vector
from utility.rigging import joint
reload(vector)


class Chain(bone.Bone):
    """ Abstract chain module """

    def __init__(self, side, name, length=4.0, segment=6, direction=[0, 1, 0]):
        """ Initialize Tail class with side and name

        :param side: str
        :param name: str
        """

        self.segment = segment
        self.interval = length / (self.segment-1)
        self.dir = vector.Vector(direction).normalize()

        self.locs = list()
        self.jnts = list()
        self.ctrls = list()
        self.offsets = list()

        bone.Bone.__init__(self, side, name, rig_type='chain')

    def create_locator(self):
        for index in range(self.segment):
            cmds.spaceLocator(n=self.locs[index])

            if index:
                cmds.parent(self.locs[index], self.locs[index-1], relative=1)

                distance = (self.interval * self.dir).as_list
                util.move(self.locs[index], distance)

        cmds.parent(self.locs[0], util.G_LOC_GRP)
        return self.locs[0]

    def create_joint(self):
        # FK jnt
        cmds.select(clear=1)
        for index, loc in enumerate(self.locs):
            pos = cmds.xform(loc, q=1, t=1, ws=1)
            cmds.joint(p=pos, name=self.jnts[index])

        cmds.parent(self.jnts[0], util.G_JNT_GRP)
        joint.orient_joint(self.jnts[0])

        return self.jnts[0]

    def place_controller(self):
        # FK
        for index in range(self.segment):
            cmds.duplicate(self._shape, name=self.ctrls[index])
            cmds.group(em=1, name=self.offsets[index])
            util.matchXform(self.offsets[index], self.jnts[index])

            cmds.parent(self.ctrls[index], self.offsets[index],
                        relative=1)

            if index:
                cmds.parent(self.offsets[index], self.ctrls[index-1])

        # Cleanup
        cmds.parent(self.offsets[0], util.G_CTRL_GRP)
        return self.offsets[0]
