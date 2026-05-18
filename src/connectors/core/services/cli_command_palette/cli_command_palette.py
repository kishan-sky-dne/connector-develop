"""
__author__ = "Sky UK Ltd"
__copyright__ = Copyright © Sky CP Limited 2023.
All rights reserved. No part of this work may be reproduced,
stored in a retrieval system of any nature, or transmitted,
in any form or by any means including photocopying
and recording, without the prior written permission of Sky,
the copyright owner.
__licence__ = "subject to the terms of the licence with Sky UK Ltd'
__version__ = "1.0"
"""
# Standard Library
import logging
import re

# Third Party Library
import connexion
from sqlalchemy import desc, func, not_

# DNE Library
from connectors.core.utils.sqldb.model import SkybridgeCommands
from connectors.core.utils.sqldb.sqlDB import PostgresSingletonManager

logger = logging.getLogger(__name__)


class CliCommands:
    def __init__(self, **kwargs):
        """
        CLI Commands Constructor. Class to get CLI commands for a given device.
        kwargs:
            vendor(string)
            model(string)
            platform(string)
            version(string)
        """
        logger.info("Initializing CLI Commands")
        self.sql_instance = PostgresSingletonManager()
        self.vendor = kwargs["vendor"]
        self.platform = "iosxe" if kwargs["platform"] == "ios" else kwargs["platform"]
        self.model = kwargs.get("model")
        self.version = kwargs.get("version")
        self.hostname = kwargs.get("hostname") or "hostname"

    def get_commands(self):
        """
        Retrieves popular CLI commands
        Returns:
            List: Device specific CLI commands
        """
        logger.info("Getting all device specific CLI commands")
        with self.sql_instance.transactional_session() as session:
            total_commands = self._execute_query(session)

        if not total_commands:
            logger.debug("No commands found in sql db for the specified device")
            return connexion.problem(
                status=404,
                title="Data Not Found",
                detail="No commands found with the given device specification.",
            )
        return total_commands

    def _execute_query(self, session):
        """
        Builds and executes query
        Returns:
            List: Device specific CLI commands ordered by popularity
        """
        query = (
            session.query(
                func.sum(SkybridgeCommands.count).label("count_sum"),
                SkybridgeCommands.command.label("command"),
                func.string_agg(SkybridgeCommands.target_router, ", ").label("target_routers"),
            )
            .filter(SkybridgeCommands.device_vendor == self.vendor)
            .filter(SkybridgeCommands.device_os_type == self.platform)
            .filter(not_(SkybridgeCommands.output.contains("Not allowed.")))
            .filter(not_(SkybridgeCommands.output.contains("Invalid cli command.")))
            .filter(not_(SkybridgeCommands.output.contains("Unknown element")))
        )

        if self.model:
            query = query.filter(SkybridgeCommands.device_model == self.model)
        if self.version:
            query = query.filter(SkybridgeCommands.device_os_version == self.version)
        query = query.group_by(SkybridgeCommands.command).order_by(desc("count_sum"))

        result_proxy = session.execute(query)

        results = [dict(rowproxy.items()) for rowproxy in result_proxy]
        self._process_results(results)

        return [row["command"] for row in results]

    def _process_results(self, results):
        """
        Replaces device specific variables in a command
        If the command has not been executed on the given device
        """
        pattern = r" +((\w*-*\w*[\/_.]+\w*)+)|( +\d+)"
        for row in results:
            if self.hostname not in row["target_routers"]:
                row["command"] = re.sub(pattern, " <VAR>", row["command"])
