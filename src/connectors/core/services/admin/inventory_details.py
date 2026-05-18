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
import sys

# Third Party Library
from sqlalchemy.exc import SQLAlchemyError

# Sky Library
from isp_config import ConfigManagerException

# DNE Library
from connectors.core.config import connectors_config
from connectors.core.utils.sqldb.sqlDB import MySQLDB
from connectors.core.utils.sqldb.sqlDB_errors import db_errors
from connectors.core.utils.sqldb.swlifecycle_model import (
    DeviceMaster,
    DeviceRole,
    FileType,
    OsState,
    PackageType,
    RegionMaster,
)

try:
    config = connectors_config.ConnectorsConfigManager()
    config.load_config()
except ConfigManagerException:
    sys.exit(1)

database_name = config.get(section="mysqlDB", key="sw_upgrade_database_name")

logger = logging.getLogger(__name__)


class InventoryDetails:
    def __init__(
        self,
        include,
    ):
        self.include = include
        self.sql_instance = MySQLDB(database_name=database_name)
        self.inventory_details = {}

    def get_inventory_details(self) -> dict[str, str | list]:
        """
        Get inventory details from mysql db via sqlalchemy orm transactions
        Args: self
        Returns: inventory_details
        """
        logger.info("Entering into core services module to get inventory details")
        inventory_details = {}
        try:
            with self.sql_instance.transactional_session() as session:
                inventory = {
                    "deviceVendor": {
                        "data": ["deviceId", "vendor"],
                        "query": session.query(DeviceMaster.id, DeviceMaster.vendor),
                    },
                    "deviceModel": {
                        "data": ["deviceId", "model"],
                        "query": session.query(DeviceMaster.id, DeviceMaster.model),
                    },
                    "region": {
                        "data": ["regionId", "region"],
                        "query": session.query(RegionMaster.id, RegionMaster.region),
                    },
                    "currentState": {
                        "data": ["stateId", "state"],
                        "query": session.query(OsState.id, OsState.validity_state),
                    },
                    "deviceRole": {"data": ["roleId", "role"], "query": session.query(DeviceRole.id, DeviceRole.role)},
                    "packageType": {
                        "data": ["packageId", "package"],
                        "query": session.query(PackageType.id, PackageType.package_type),
                    },
                    "fileType": {"data": ["fileId", "file"], "query": session.query(FileType.id, FileType.file_type)},
                }
                for param in self.include:
                    inventory_list = []
                    inventory_data = {}
                    details = inventory[param]["query"]
                    logger.info(f"inventory details query {details}")
                    for each_device in details:
                        inventory_data[(inventory[param]["data"][0])] = str(each_device[0])
                        inventory_data[(inventory[param]["data"][1])] = each_device[1]
                        inventory_list.append(inventory_data.copy())
                    inventory_details[str(param)] = inventory_list
            logger.info(f"inventory details after query are {inventory_details}")
            self.inventory_details = inventory_details
            return self.inventory_details

        except (SQLAlchemyError) as err:  # added for bug DNE_31568
            logger.error(f"error in SQL statements inventory details {err}")
            logger.exception(f"{err.__class__.__name__} exception occured {err}")
            return {
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "errors": [
                    {"code": "ERR-000-097-0501", "message": f"SQL exception in getting inventory details {err}"}
                ],
            }
        except (TypeError, AttributeError, KeyError, IndexError) as err:
            logger.error(f"error in getting inventory details {err}")  # updated for bug DNE_31568
            logger.exception(
                f"Exception occurred for get_inventory_details module failed to update image upgrade details"
                f" : {err.__class__.__name__} {err}"
            )
            return {
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-000-097-0500",
                        "message": f"Exception occurred while performing get inventory details"
                        f" from tables : {err.__class__.__name__}",
                    }
                ],
            }
        except Exception as err:
            logger.exception(
                f"Exception Occurred. Failed while getting inventory details from tables "
                f"due to error {err.__class__.__name__} {err}"
            )  # updated for bug DNE_31568
            error_message = (
                f"Database Operation Failed while performing get inventory details"
                f" from tables : {db_errors[err.__class__]}"
                if err.__class__.__name__ in db_errors
                else f"Generic Exception occurred while performing get inventory details "
                f"from tables : {err.__class__.__name__}"
            )

            return {
                "status": "failure",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-000-097-0500",
                        "message": error_message,
                    }
                ],
            }
