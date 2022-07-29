#!/usr/bin/env python3
# Copyright 2022 Stone
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Charm the service.

Refer to the following post for a quick-start guide that will help you
develop a new k8s charm using the Operator Framework:

    https://discourse.charmhub.io/t/4208
"""

import logging

from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus
from ops.manifests import Collector

from manifests import ControllerManagerManifests
logger = logging.getLogger(__name__)


class OpaManagerOperatorCharm(CharmBase):
    """Charm the service."""

    def __init__(self, *args):
        super().__init__(*args)
        self.manifests = ControllerManagerManifests(self.app.name, self.config)
        self.collector = Collector(self.manifests)
        self.framework.observe(self.on.controller_manager_pebble_ready, self._controller_manager_pebble_ready)
        self.framework.observe(self.on.list_resources_action, self._list_resources)
        self.framework.observe(self.on.list_versions_action, self._list_versions)
        self.framework.observe(self.on.install, self._install_or_upgrade)
        self.framework.observe(self.on.stop, self._cleanup)

    def _list_resources(self, event):
        logger.info(f"Resources: {self.manifests.resources}")
        return self.collector.list_resources(event, None, None)

    def _list_versions(self, event):
        self.collector.list_versions(event)

    def _controller_manager_pebble_ready(self, event):
        self.unit.status = ActiveStatus()

    def _install_or_upgrade(self, _event=None):
        self.manifests.apply_manifests()

    def _cleanup(self, _event):
        self.manifests.delete_manifests(ignore_unauthorized=True)



if __name__ == "__main__":
    main(OpaManagerOperatorCharm)
