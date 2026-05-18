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

# DNE Library
from connectors.core.utils.sqldb.model import DeviceOSVersion
from connectors.core.utils.sqldb.sqlDB import MySQLDB

logger = logging.getLogger(__name__)


class UpdateStatus:
    def __init__(self, device_os_version_id):
        self.device_os_version_id = device_os_version_id
        self.sql_instance = MySQLDB()

    def get_device_status(self):
        """
        Get the status for DeviceOSVersion
        Returns: status [('Active',)] or []

        """
        logger.info(f"Getting the status for DeviceOSVersion ")
        with self.sql_instance.transactional_session() as session:
            return (
                session.query(DeviceOSVersion.Status)
                .filter(DeviceOSVersion.DeviceOSVersionIdentifier == self.device_os_version_id)
                .all()
            )

    def update_status_active(self, status):
        """
        Update the status as active for DeviceOSVersionIdentifier
        Args:
            status: DeviceOSVersion status

        Returns: True after the update

        """
        logger.info(f"Updating the status for DeviceOSVersion as Active")
        with self.sql_instance.transactional_session() as session:
            session.query(DeviceOSVersion).filter(
                DeviceOSVersion.DeviceOSVersionIdentifier == self.device_os_version_id
            ).update({"Status": status})
            session.commit()
        return True

    def update_status_inactive(self, status):
        """
        Update the status as active for DeviceOSVersionIdentifier
        Args:
            status:

        Returns:True after the update

        """
        logger.info(f"Updating the status for DeviceOSVersion as Active")
        with self.sql_instance.transactional_session() as session:
            session.query(DeviceOSVersion).filter(
                DeviceOSVersion.DeviceOSVersionIdentifier != self.device_os_version_id
            ).update({"Status": status})
            session.commit()
        return True
