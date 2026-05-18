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
from sqlalchemy.orm.query import Query

# Sky Library
from isp_config import ConfigManagerException

# DNE Library
from connectors.core.config import connectors_config
from connectors.core.services.admin.utils import query_count
from connectors.core.utils.sqldb.sqlDB import MySQLDB
from connectors.core.utils.sqldb.sqlDB_errors import db_errors
from connectors.core.utils.sqldb.swlifecycle_model import (
    CustomConfigList,
    Image,
    OSVersion,
    OSVersionDeviceRegionPackage,
    Package,
    PhaseUpgrade,
    RoleList,
    SequenceUpgrade,
)

try:
    config = connectors_config.ConnectorsConfigManager()
    config.load_config()
except ConfigManagerException:
    sys.exit(1)

database_name = config.get(section="mysqlDB", key="sw_upgrade_database_name")

logger = logging.getLogger(__name__)


class DeleteAdminDetails:
    def __init__(self, **kwargs: dict[str, str]) -> None:
        """
        Initializes an instance of delete image upgrade details
        """
        self.os_version_device_region_id: int = kwargs.get("osVersionDeviceRegionId")
        self.os_version_upgrade_id: int = kwargs.get("osVersionUpgradeId")
        self.sql_instance = MySQLDB(database_name=database_name)

    def delete_device_image(self) -> dict[str, str | dict]:
        """
        Delete image details from mysql db via sqlalchemy orm transactions
        Args: self
        Returns: success or failure of delete image details
        """
        try:
            logger.debug(
                f"Entering delete_image_details module to delete image and package table by "
                f"os_version_device_regionId : {self.os_version_device_region_id}"
            )
            image_id: int = 0
            os_version_id: int = 0
            with self.sql_instance.transactional_session() as session:
                os_query: Query = session.query(OSVersionDeviceRegionPackage).filter(
                    OSVersionDeviceRegionPackage.id == self.os_version_device_region_id
                )
                if query_count(os_query) == 0:
                    return {
                        "status": "FAILURE",
                        "errorCategory": "FAILED",
                        "errors": [
                            {
                                "code": "ERR-000-097-1001",
                                "message": "Validation Failed: Invalid osVersionDeviceRegionId to "
                                "delete image details",
                            }
                        ],
                    }
                source_query = session.query(PhaseUpgrade).filter(
                    PhaseUpgrade.source_osv_dr_id == self.os_version_device_region_id
                )
                target_query = session.query(PhaseUpgrade).filter(
                    PhaseUpgrade.target_osv_dr_id == self.os_version_device_region_id
                )
                if query_count(source_query) != 0 or query_count(target_query) != 0:
                    return {
                        "status": "FAILURE",
                        "errorCategory": "FAILED",
                        "errors": [
                            {
                                "code": "ERR-000-097-1002",
                                "message": "Selected image is being used to upgrade "
                                "already. Please delete the upgrade entry before deleting the image",
                            }
                        ],
                    }
                image_query: Query = session.query(Image).filter(
                    Image.os_device_region_id == self.os_version_device_region_id
                )
                if query_count(image_query) == 0:
                    return {
                        "status": "FAILURE",
                        "errorCategory": "FAILED",
                        "errors": [
                            {
                                "code": "ERR-000-097-1003",
                                "message": f"For requested os version device region id "
                                f"{self.os_version_device_region_id} - image detail is not found",
                            }
                        ],
                    }
                for image_data in image_query:
                    image_id: int = image_data.id
                    session.query(Package).filter(Package.image_id == image_id).delete()
                    image_query.delete()
                    session.commit()
                os_query: Query = session.query(OSVersionDeviceRegionPackage).filter(
                    OSVersionDeviceRegionPackage.id == self.os_version_device_region_id
                )
                for os_data in os_query:
                    os_version_id = os_data.os_version_id
                # bug fixed:DNE-38069
                os_version_query: Query = session.query(OSVersionDeviceRegionPackage).filter(
                    OSVersionDeviceRegionPackage.os_version_id == os_version_id
                )
                if query_count(os_version_query) == 1:
                    os_query.delete()
                    session.query(OSVersion).filter(OSVersion.id == os_version_id).delete()
                else:
                    os_query.delete()
                session.commit()
            return {"status": "success"}
        except (TypeError, AttributeError, KeyError, IndexError) as err:
            logger.exception(
                f"Exception occurred for delete_device_image module to delete image and package tables"
                f" : {err.__class__.__name__} {err}"
            )
            return {
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-000-097-0500",
                        "message": f"Exception occurred while performing delete image "
                        f"details from image and package tables : {err.__class__.__name__} due to {err}",
                    }
                ],
            }
        except Exception as err:
            logger.exception(
                f"Exception occurred for delete_device_image module to delete image and package tables"
                f" : {err.__class__.__name__} {err}"
            )
            error_message = (
                f"Database Operation Failed while performing delete image details"
                f" from image and package tables : {db_errors[err.__class__.__name__]} due to {err}"
                if err.__class__.__name__ in db_errors
                else f"Generic Exception occurred while performing delete image"
                f" details to image and package tables : {err.__class__.__name__} due to {err}"
            )
            return {
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-000-097-0500",
                        "message": error_message,
                    }
                ],
            }

    def delete_upgrade_details(self) -> dict[str, str | dict]:
        """
        Delete upgrade details from mysql db via sqlalchemy orm transactions
        Args: self
        Returns: success or failure of delete upgrade details
        """
        try:
            logger.debug(
                f"Entering delete_upgrade_details module to delete phase and sequence table by "
                f"os_version_upgrade_id : {self.os_version_upgrade_id}"
            )
            with self.sql_instance.transactional_session() as session:
                phase_query: Query = session.query(PhaseUpgrade).filter(PhaseUpgrade.id == self.os_version_upgrade_id)
                if query_count(phase_query) == 0:
                    return {
                        "status": "FAILURE",
                        "errorCategory": "FAILED",
                        "errors": [
                            {
                                "code": "ERR-000-097-1004",
                                "message": "Validation Failed: Invalid osVersionUpgradeId to delete upgrade details",
                            }
                        ],
                    }
                custom_id: int = phase_query[0].custom_config_id
                custom_details_list: list[int] = []
                role_details_list: list[int] = []
                self.loop_phase_query(session, custom_id, custom_details_list, role_details_list)
                seq_details = session.query(SequenceUpgrade).filter(
                    SequenceUpgrade.phase_upgrade_id == self.os_version_upgrade_id
                )
                next_seq_id: int = seq_details[0].next_sequence_id
                seq_list: list[int] = [seq_details[0].id]
                phase_list: list[int] = [seq_details[0].phase_upgrade_id]
                while next_seq_id:
                    next_seq_details: Query = session.query(SequenceUpgrade).filter(SequenceUpgrade.id == next_seq_id)
                    seq_list.append(next_seq_details[0].id)
                    phase_query1: Query = session.query(PhaseUpgrade).filter(
                        PhaseUpgrade.id == next_seq_details[0].phase_upgrade_id
                    )
                    self.loop_phase_query(
                        session, phase_query1[0].custom_config_id, custom_details_list, role_details_list
                    )
                    phase_list.append(next_seq_details[0].phase_upgrade_id)
                    next_seq_id: int = next_seq_details[0].next_sequence_id
                for del_seq in seq_list:
                    session.query(SequenceUpgrade).filter(SequenceUpgrade.id == del_seq).delete()
                    session.commit()
                for del_phase in phase_list:
                    session.query(PhaseUpgrade).filter(PhaseUpgrade.id == del_phase).delete()
                    session.commit()
                for del_custom in custom_details_list:
                    session.query(CustomConfigList).filter(CustomConfigList.id == del_custom).delete()
                    session.commit()
                for del_role in role_details_list:
                    session.query(RoleList).filter(RoleList.id == del_role).delete()
                    session.commit()
            return {"status": "success"}
        except (TypeError, AttributeError, KeyError, IndexError) as err:
            logger.exception(
                f"Exception occurred for delete_upgrade_details module to delete phase and sequence tables entry"
                f" : {err.__class__.__name__} {err}"
            )
            return {
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-000-097-0500",
                        "message": f"Exception occurred while performing delete upgrade "
                        f"details from phase and sequence tables : {err.__class__.__name__} due to {err}",
                    }
                ],
            }
        except Exception as err:
            logger.exception(
                f"Exception occurred for delete_upgrade_details module to delete phase and sequence tables entry"
                f" : {err.__class__.__name__} {err}"
            )
            error_message = (
                f"Database Operation Failed while performing delete upgrade details"
                f" from phase and sequence tables : {db_errors[err.__class__.__name__]} due to {err}"
                if err.__class__.__name__ in db_errors
                else f"Generic Exception occurred while performing delete upgrade"
                f" details from phase and sequence tables : {err.__class__.__name__} due to {err}"
            )
            return {
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-000-097-0500",
                        "message": error_message,
                    }
                ],
            }

    def loop_phase_query(
        self, session: object, custom_id: int, custom_details_list: list, role_details_list: list
    ) -> None:
        """
        loop phase upgrade details to get custom_id, next_config_id
        Args:
            session (object): session object
            custom_id (int): custom_id of custom table
            custom_details_list (list): list of custom details
            role_details_list (list): list of role details
        Returns:
            None
        """
        if custom_id:  # bug fixed:DNE-38069
            custom_details_list.append(custom_id)
            custom_details: Query = session.query(CustomConfigList).filter(CustomConfigList.id == custom_id)
            next_id: int = custom_details[0].next_config_id
            role_details_list.append(custom_details[0].role_list_id)
            while next_id:
                next_custom_details: Query = session.query(CustomConfigList).filter(CustomConfigList.id == next_id)
                custom_details_list.append(next_id)
                role_details_list.append(next_custom_details[0].role_list_id)
                next_id: int = next_custom_details[0].next_config_id
