# -*- python -*-
# ex: set syntax=python:
# vim: set expandtab ts=4 sw=4 softtabstop=4:

from twisted.internet import defer, threads
from twisted.python import log

from buildbot.buildslave.base import AbstractLatentBuildSlave
from buildbot import interfaces

from paramiko import SSHClient, PKey

import os
import os.path

class SSHLatentBuildSlave(AbstractLatentBuildSlave):
    """
    Build slave that runs a command over SSH to start and stop the build slave.
    """

    def __init__(self, name, password, ssh_host, username, key_path, host_key_file=os.path.expanduser("~/.ssh/known_hosts"), **kwargs):
        """
        Creates a new SSH latent build slave with the given parameters.
        """
        AbstractLatentBuildSlave.__init__(self, name, password, **kwargs)
        self.client = SSHClient()
        self.client.load_system_host_keys(host_key_file)

        self.hostname = ssh_host
        self.username = username
        self.key_path = key_path
        self.started = False

    def is_connected(self):
        self.client.get_transport() != None and self.client.get_transport().is_active()


    def start_instance(self, build):
        if self.started:
            raise ValueError('already started')
        return threads.deferToThread(self._start_instance)

    def _start_instance(self):
        log.msg("connecting to SSH server")
        self.client.connect(self.hostname, username=self.username, key_filename=self.key_path)
        self.client.get_transport().set_keepalive(True)
        log.msg("executing start command")
        stdin, stdout, stderr = self.client.exec_command("~/bbvenv/bin/env_exec buildslave start ~/bbslave")
        self.started = True
        return True


    def stop_instance(self, fast=False):
        if not self.started:
            return defer.succeed(None)
        return self._stop_instance()

    def _stop_instance(self):
        if not self.is_connected(): self.client.connect(self.hostname, username=self.username, key_filename=self.key_path)
        log.msg("stopping build slave")
        self.client.exec_command("~/bbvenv/bin/env_exec buildslave stop ~/bbslave")
        log.msg("closing connection")
        self.client.close()
        log.msg("finished")
        self.started = False

    def buildFinished(self, sb):
        log.msg("finished build. insubstantiating")
        self.insubstantiate()


# ssh_host, username=username, key_filename=key_path
