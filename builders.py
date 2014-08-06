# BUILDERS

# The 'builders' list defines the Builders, which tell Buildbot how to perform a build:
# what steps, and which slaves can execute them.  Note that any particular build will
# only take place on one slave.

from buildbot.process.factory import BuildFactory
from buildbot.steps.source.git import Git
from buildbot.steps.shell import ShellCommand, SetProperty, Configure, Compile
from buildbot.steps.master import MasterShellCommand
from buildbot.steps.slave import SetPropertiesFromEnv
from buildbot.steps.transfer import DirectoryUpload
from buildbot.config import BuilderConfig
from buildbot.process.properties import Property, Interpolate

from slaves import slaveParams

import re
import os
from os import path

# This stuff is all similar, so we'll use a common function for it.
def bfSetup(osname, arch, channel, slave, deploy=True): # TODO: Allow multiple slaves per builder.
    """
    Returns a new MultiMC build factory with the given parameters.
    `osname` is a string indicating the build's operating system. It can be "win", "lin", or "osx", for Windows, Linux, and OS X, respectively.
    `arch` is a string indicating whether the build is 64-bit or not. If so, it should be "64", otherwise, "32".
    `channel` indicates the build's channel. Usually either `stable`, `develop`, or `rc`, but we may add more channels later.
    """

    # The build type is <channel>-<platform>,
    # while the builder name is the buildbot builder name and is <platform>-<channel>.
    platform = "%s%s" % (osname, arch)
    builder_name = "%s-%s" % (platform, channel)

    # Figure out where to put artifacts.
    artifactTemp = "/tmp/mmc-%s-artifacts" % platform

    # Determine the update repo name.
    gourepo = builder_name

    # Make sure we're on a valid channel.
    git_branch = None
    if channel == "stable":      git_branch = "master"
    elif channel == "develop":   git_branch = "develop"
    elif channel == "quickmod":  git_branch = "feature_quickmod"
    else: raise NotImplemented("Unknown build channel %s" % channel)

    # Get slave parameters.
    p = slaveParams[slave]

    cfgcmd = [p["cmakeCmd"], "-DMultiMC_INSTALL_SHARED_LIBS=ON", "-DCMAKE_BUILD_TYPE=Release", "-DMultiMC_NOTIFICATION_URL:STRING=http://files.multimc.org/notifications.json"]

    make = p["makeCmd"]
    defQtPath= p["qtPath"]
    installDir = p["installDir"]

    cfgcmd += p["cmakeArgs"]


    # Version type.
    versionType = "Custom"
    if channel == "stable": versionType = "Release"
    elif channel == "develop": versionType = "Development"

    # Qt path stuff.
    cfgcmd.append("-DCMAKE_INSTALL_PREFIX:PATH=%s" % installDir)
    cfgcmd.append(Interpolate("-DCMAKE_PREFIX_PATH=%(prop:QTPATH:-" + defQtPath + ")s"))
    cfgcmd.append(Interpolate("-DQt5_DIR=%(prop:QTPATH:-" + defQtPath + ")s"))

    # Update and version system configuration.
    cfgcmd.append("-DMultiMC_CHANLIST_URL=http://files.multimc.org/update/%s/channels.json" % platform)
    cfgcmd.append(Interpolate("-DMultiMC_VERSION_BUILD=%(prop:buildnumber:-0)s"))
    cfgcmd.append("-DMultiMC_VERSION_CHANNEL=%s" % channel)
    cfgcmd.append("-DMultiMC_VERSION_TYPE=%s" % versionType)
    cfgcmd.append("-DMultiMC_BUILD_PLATFORM=%s" % platform)

    cfgcmd.append("..")


    b = BuildFactory()

    b.addStep(SetPropertiesFromEnv(variables=["MAKEJOBS", "QTPATH"]))

    b.addStep(Git(repourl='git://github.com/MultiMC/MultiMC5', mode='incremental', branch=git_branch))

    b.addStep(Configure(workdir="build/out", command=cfgcmd))

    def getVersion(rc, stdout, stderr):
        vregex = r'Version: ([0-9.]*[0-9]+)'
        return { "buildversion": re.search(vregex, stdout).group(1) }

    b.addStep(SetProperty(name="check-version", description="checking version", descriptionDone="version check",
              command=[make, "version"], extract_fn=getVersion, workdir="build/out"))

    #, ("updater", "updater")
    for name, target in [("main", "all"), ("translations", "translations")]:
        b.addStep(Compile(workdir="build/out", command=[make, target, Interpolate("-j%(prop:MAKEJOBS:-2)s")],
                  name="compile-" + name, description=["compiling", name], descriptionDone=["compile", name]))

    if osname != "osx":
        b.addStep(Compile(workdir="build/out", command=[make, "test", Interpolate("-j%(prop:MAKEJOBS:-2)s")],
                  name="tests", description=["testing"], descriptionDone=["tests"], logfiles={"testlog": "Testing/Temporary/LastTest.log"}))

    inst_clean_cmd = ["rm", "-rf", installDir]
    if osname == "win":
        inst_clean_cmd = ["rmdir", installDir, "/s", "/q"]

    b.addStep(ShellCommand(name="clean install", description="cleaning install", descriptionDone="clean install",
              command=inst_clean_cmd, haltOnFailure=False, flunkOnFailure=False, warnOnFailure=False, workdir="build/out"))

    b.addStep(ShellCommand(name="install", env={"VERBOSE": "1"}, description="installing", descriptionDone="install",
          command=[make, "install"], haltOnFailure=True, workdir="build/out"))

    if osname == "win":
        # Install OpenSSL libs on Windows.
        b.addStep(ShellCommand(name="add-openssl", command=["copy", "C:\\OpenSSL-Win32\\*.dll", installDir], 
                  description="adding openssl", workdir="build/out", descriptionDone="add openssl", haltOnFailure=True))


    ###################################
    #### Upload the Finished Build ####
    ###################################

    if deploy:
        # Clear the old artifact upload.
        b.addStep(MasterShellCommand(name="clean-artifacts", description="cleaning old artifacts", descriptionDone="clean old artifacts",
                  command=["rm", "-rf", artifactTemp], haltOnFailure=False, flunkOnFailure=False))

        atmpInstallDir = os.path.join(artifactTemp, "MultiMC")

        # Upload artifacts to the main server.
        artifactsPath = installDir if p["absInstallDir"] else ("out/" + installDir)
        b.addStep(DirectoryUpload(name="artifact-dl", slavesrc=artifactsPath, masterdest=atmpInstallDir))

        # Deploy the uploaded artifacts to GoUpdate.
        webDir = "/var/www/files.multimc.org"
        b.addStep(MasterShellCommand(name="deploy-version", description="deploying to GoUpdate repo", descriptionDone="GoUpdate deploy", haltOnFailure=True, 
                command=["repoman", "update", 
                            webDir + "/update/%s/%s/" % (platform, channel), 
                            webDir + "/files/", "http://files.multimc.org/files/", 
                            atmpInstallDir, Interpolate("%(prop:buildversion)s"), Interpolate("%(prop:buildnumber)s")]))

        b.addStep(MasterShellCommand(name="chmod-repo", description=["fixing GoUpdate", "repo permissions"],
                                     descriptionDone=["fix GoUpdate", "repo permissions"], haltOnFailure=True, 
                                     command=["/bin/bash", "-c", "chmod 0644 %(webdir)s/files/* %(webdir)s/update/*/*/*.json" % {"webdir": webDir}]))

        # Finally, deploy a tarball to the downloads folder on the webserver.
        # TODO: Finish repoman's mkpkg command so we can generate tarballs from GoUpdate versions, rather than having to do this.
        atmpParent = path.abspath(path.join(atmpInstallDir, ".."))
        atmpRel = path.relpath(atmpInstallDir, atmpParent)

        if osname == "win": tbdCmd = ["/bin/bash", "-c", 
                "cd %s && zip -FSr /var/www/files.multimc.org/downloads/mmc-%s-%s.zip %s" % (atmpParent, channel, platform, atmpRel)]
        else: tbdCmd = ["tar", "cvzf", "/var/www/files.multimc.org/downloads/mmc-%s-%s.tar.gz" % (channel, platform), "--directory=" + atmpParent, atmpRel]

        b.addStep(MasterShellCommand(name="deploy-download", description="deploying to downloads", descriptionDone="download deploy", haltOnFailure=True, command=tbdCmd))

    return b, builder_name

def get_builders():
    builder_names = {}
    builder_list = []
    for channel in ["stable", "develop", "quickmod"]:
        for osname in ["lin", "win", "osx"]:
            for arch in ["64", "32"]:
                if (osname == "win" and arch == "64") or (osname == "osx" and arch == "32"):
                    continue

                slave = "mmc-%s%s" % (osname, arch)

                factory, builder_name = bfSetup(osname=osname, arch=arch, channel=channel, slave=slave)

                if not channel in builder_names:  builder_names[channel] = [builder_name]
                else:                             builder_names[channel].append(builder_name)
                builder_list.append(BuilderConfig(name=builder_name, slavenames=[slave], factory=factory))
    return builder_list, builder_names

