# BUILDSLAVES

# The 'slaves' list defines the set of recognized buildslaves. Each element is
# a BuildSlave object, specifying a unique slave name and password.  The same
# slave name and password must be configured on the slave.

import os

from buildbot.buildslave import BuildSlave

from customslaves.openstack import OpenStackLatentBuildSlave
from customslaves.customec2latentslave import CustomEC2LatentSlave
from customslaves.dockerslave import DockerLatentBuildSlave
from customslaves.sshlatentslave import SSHLatentBuildSlave

import passwords

def get_slaves():
    return [
        BuildSlave("mmc-lin64", passwords.slaves["lin64"]),
        #DockerLatentBuildSlave("mmc-lin64", passwords.slaves["lin64"], "unix://var/run/docker.sock", "forkk/mmc-deb64-bs:qt51", "sh /run_slave.sh",
        #    env={"BBSLAVE_MASTER_HOST": "ci.multimc.org", "BBSLAVE_MASTER_PORT": "9989", "BBSLAVE_ADMIN": "Forkk <forkk@forkk.net>", "BBSLAVE_PASSWORD": passwords.slaves["lin64"]}),

        BuildSlave("mmc-lin32", passwords.slaves["lin32"]),
        #DockerLatentBuildSlave("mmc-lin32", passwords.slaves["lin32"], "unix://var/run/docker.sock", "forkk/mmc-deb32-bs:qt51", "sh /run_slave.sh",
        #    env={"BBSLAVE_MASTER_HOST": "ci.multimc.org", "BBSLAVE_MASTER_PORT": "9989", "BBSLAVE_ADMIN": "Forkk <forkk@forkk.net>", "BBSLAVE_PASSWORD": passwords.slaves["lin32"]}),

        # BuildSlave("win32-rootbear", passwords.slaves["win32-rootbear"]),

        # BuildSlave("forkk-buildbox-win32", passwords.slaves["win32-forkk-buildbox"]),

        # BuildSlave("win32-ec2", passwords.slaves["win32-ec2"]),

        BuildSlave("mmc-win32", passwords.slaves["win32"]),

        SSHLatentBuildSlave("mmc-osx64", passwords.slaves["osx64"], "l060.macincloud.com", "user3555", os.path.expanduser("~/.ssh/id_rsa")),
    ]

