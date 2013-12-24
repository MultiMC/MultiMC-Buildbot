####### STATUS TARGETS

# 'status' is a list of Status Targets. The results of each build will be
# pushed to these targets. buildbot/status/*.py has a variety to choose from,
# including web pages, email senders, and IRC bots.

from buildbot.status import html
from buildbot.status import words
from buildbot.status.web import authz, auth
import passwords

authz_cfg=authz.Authz(
    # change any of these to True to enable; see the manual for more
    # options
    auth=auth.BasicAuth([("forkk", passwords.accounts["forkk"])]),
    gracefulShutdown = False,
    forceBuild = 'auth',
    forceAllBuilds = False,
    pingBuilder = False,
    stopBuild = False,
    stopAllBuilds = False,
    cancelPendingBuild = False,
)


status_targets = []

status_targets.append(html.WebStatus(http_port=8010, authz=authz_cfg,
                                     change_hook_dialects={"github": True}))

status_targets.append(words.IRC("irc.esper.net", "buildbot-mmc", password=passwords.bot_nickserv,
                                channels=["#MultiMC"], allowForce=True, useRevisions=False,
                                notify_events={'started': 1, 'finished': 1}))


