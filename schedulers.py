####### SCHEDULERS

# Configure the Schedulers, which decide how to react to incoming changes.

from buildbot.schedulers.basic import SingleBranchScheduler, AnyBranchScheduler
from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.changes import filter

# If true, automatically build every commit.
buildOnCommit = True

def get_schedulers(builder_names):
    schedulers = []

    schedulers.append(ForceScheduler(
        name="force",
        builderNames=[name for key, blist in builder_names.iteritems() for name in blist]))

    schedulers.append(SingleBranchScheduler(
        name="translations-release",
        change_filter=filter.ChangeFilter(branch='master', repository='https://github.com/MultiMC/MultiMC5-translate'),
        treeStableTimer=30,
        builderNames=["translations-build"]))

    schedulers.append(SingleBranchScheduler(
        name="translations-update",
        change_filter=filter.ChangeFilter(branch='master', repository='https://github.com/MultiMC/MultiMC5'),
        treeStableTimer=30,
        builderNames=["translations-update"]))

    if buildOnCommit:
#        schedulers.append(SingleBranchScheduler(
#            name="stable",
#            change_filter=filter.ChangeFilter(branch='master', repository='git://github.com/MultiMC/MultiMC5'),
#            treeStableTimer=30,
#            builderNames=builder_names["stable"]))

        schedulers.append(SingleBranchScheduler(
            name="develop",
            change_filter=filter.ChangeFilter(branch='develop', repository='https://github.com/MultiMC/MultiMC5'),
            treeStableTimer=30,
            builderNames=builder_names["develop"]))

        schedulers.append(SingleBranchScheduler(
            name="quickmod",
            change_filter=filter.ChangeFilter(branch='feature_quickmod', repository='https://github.com/MultiMC/MultiMC5'),
            treeStableTimer=30,
            builderNames=builder_names["quickmod"]))

        return schedulers

