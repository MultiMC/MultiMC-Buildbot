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
			DockerLatentBuildSlave("mmc-lin64", passwords.slaves["lin64"], "unix://var/run/docker.sock", "forkk/mmc-lin64-bs", "sh /run_slave.sh",
				env={"BBSLAVE_MASTER_HOST": "ci.multimc.org", "BBSLAVE_MASTER_PORT": "9989", "BBSLAVE_ADMIN": "Forkk <forkk@forkk.net>", "BBSLAVE_PASSWORD": "Fz1L87k0dQr6t"}),

			BuildSlave("mmc-lin32", passwords.slaves["lin32"]),

			BuildSlave("win32-rootbear", passwords.slaves["win32-rootbear"]),

			#   CustomEC2LatentSlave("mmc-win32", passwords.slaves["win32-ec2"], "c3.large", ami="ami-d84bd5e8", region="us-west-2", 
			#                        properties={"MAKEJOBS": 8}),

			#   OpenStackLatentBuildSlave("mmc-rs-win32", passwords.slaves["win32-rs"],
			#                             flavor=4, image="4df23f20-c21b-493c-93b6-8b90492926b5",
			#                             os_username="buildbot", os_password="rA9PXDEgyZb6M", os_tenant_name="876055",
			#                             os_auth_url="https://identity.api.rackspacecloud.com/v2.0/", region_name="DFW"),

			#BuildSlave("mmc-rs-win32", passwords.slaves["win32-rs"]),
			BuildSlave("forkk-buildbox-win32", passwords.slaves["win32-forkk-buildbox"]),

			#BuildSlave("mmc-osx64", passwords.slaves["osx64"]),
			SSHLatentBuildSlave("mmc-osx64", passwords.slaves["osx64"], "l060.macincloud.com", "user3555", os.path.expanduser("~/.ssh/id_rsa")),
			]

