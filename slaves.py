# BUILDSLAVES

# The 'slaves' list defines the set of recognized buildslaves. Each element is
# a BuildSlave object, specifying a unique slave name and password.  The same
# slave name and password must be configured on the slave.

import os
import copy

from buildbot.buildslave import BuildSlave
from buildbot.process.properties import Property, Interpolate

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

slaveParams = {}
    
defSlaveParams = {
    # Path to the CMake executable.
    "cmakeCmd": "cmake",
    # Path to the make executable.
    "makeCmd": "make",
    # The path the slave's Qt installation. This may be overridden by the
    # slave's QTPATH environment variable.
    "qtPath": None,
    # Path to install built files to. This is to fix an edge case on OS X where
    # an absolute path must be used.
    "installDir": "install",
    # Hack to prevent artifact uploader from touching the installDir path.
    # Normally it prepends 'out' to the string since the files are in the 'out'
    # folder.
    "absInstallDir": False,
    # Extra arguments to CMake.
    "cmakeArgs": []
}
    

def mkLinuxParams():
    p = copy.deepcopy(defSlaveParams)
    p["qtPath"] = "/usr/local/Qt-5.2.0"
    
    return p


def mkWinParams():
    p = copy.deepcopy(defSlaveParams)
    qtDir = "C:/Qt/5.3/"
    mingwName = "mingw482_32"
    p["qtPath"] = qtDir + mingwName
    p["makeCmd"] = "mingw32-make"
    cmakeArgs = p["cmakeArgs"]

    # Specify the zlib include directory.
    cmakeArgs.append("-DZLIB_INCLUDE_DIRS=%s" % qtDir + mingwName + "/include/QtZlib")

    # Tell CMake to generate MinGW makefiles.
    cmakeArgs.append("-G"); cmakeArgs.append("MinGW Makefiles")

    # Use Visual Studio's dumpbin utility to find binary prerequisites.
    cmakeArgs.append("-DCMAKE_GP_CMD_PATHS=C:/Program Files (x86)/Microsoft Visual Studio 11.0/VC/bin")
    cmakeArgs.append("-DCMAKE_GP_TOOL=dumpbin")

    return p


def mkMacParams():
    p = copy.deepcopy(defSlaveParams)
    p["qtPath"] = "/Users/user3555/Qt5.1.1/5.1.1/clang_64"
    # CMake path
    p["cmakeCmd"] = "/Users/user3555/cmake.app/Contents/bin/cmake"
    # Absolute path for installing.
    p["installDir"] = "/Users/user3555/bbslave/{buildername}/install"
    p["absInstallDir"] = True
    
    # Crazy compiler flags.
    cmakeArgs = p["cmakeArgs"]
    cmakeArgs.append("-DCMAKE_CXX_FLAGS=-std=gnu++0x -stdlib=libc++")
    #cfgcmd.append("-DCMAKE_C_FLAGS=-std=gnu++0x -stdlib=libc++")
    cmakeArgs.append("-DCMAKE_OSX_DEPLOYMENT_TARGET=10.7")
    cmakeArgs.append("-DCMAKE_OSX_SYSROOT=/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.8.sdk/")

    return p
   

slaveParams["mmc-win32"] = mkWinParams()

slaveParams["mmc-lin32"] = mkLinuxParams()
slaveParams["mmc-lin64"] = mkLinuxParams()

slaveParams["mmc-osx64"] = mkMacParams()

