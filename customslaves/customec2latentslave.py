# vim: set expandtab ts=4 sw=4:

from buildbot.buildslave.ec2 import EC2LatentBuildSlave

class CustomEC2LatentSlave(EC2LatentBuildSlave):
    def _soft_disconnect(self, fast=False):
        EC2LatentBuildSlave._soft_disconnect(self, fast)
        self.insubstantiate(fast)
