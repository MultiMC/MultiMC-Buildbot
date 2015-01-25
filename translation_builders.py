# TRANSLATION BUILDERS

from buildbot.process.factory import BuildFactory
from buildbot.steps.source.git import Git
from buildbot.steps.shell import ShellCommand
from buildbot.steps.master import MasterShellCommand
from buildbot.steps.slave import SetPropertiesFromEnv
from buildbot.steps.transfer import DirectoryUpload
from buildbot.config import BuilderConfig
from buildbot.process.properties import Property, Interpolate

# Makes the builder for the translation source files.
def mkTransSourceBuilder():
    b = BuildFactory()
    b.addStep(Git(repourl='git@github.com:MultiMC/MultiMC5-translate.git', mode='incremental', branch='master'))
    b.addStep(ShellCommand(name="update translations", description="updating translations", descriptionDone="update translations",
            command="./update.sh", env={"MMC_TRANSLATIONS_REMOTE": "origin" }))
    return b
transUpdateBuilder = mkTransSourceBuilder()

def mkTransReleaseBuilder():
    b = BuildFactory()
    b.addStep(Git(repourl='git@github.com:MultiMC/MultiMC5-translate.git', mode='incremental', branch='master'))
    b.addStep(ShellCommand(name="build translations", description="building translations", descriptionDone="build translations",
              command="./release.sh"))
    b.addStep(DirectoryUpload(name="deploy-translations", slavesrc="build", masterdest="/var/www/files.multimc.org/translations"))
    b.addStep(MasterShellCommand(name="chmod", description=["fixing", "permissions"],
                                 descriptionDone=["fix", "permissions"], haltOnFailure=True,
                                 command=["/bin/bash", "-c", "chmod -R 0755 /var/www/files.multimc.org/translations/"]))
    return b
transReleaseBuilder = mkTransReleaseBuilder()

