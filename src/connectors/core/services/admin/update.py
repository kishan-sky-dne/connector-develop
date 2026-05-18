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
    DeviceRole,
    Image,
    OsState,
    OSVersionDeviceRegionPackage,
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


class UpdateDetails:
    def __init__(self, **kwargs: dict[str, str | list]) -> None:
        """
        Initializes an instance of update upgrade details
        """
        self.body = kwargs.get("body")
        self.sql_instance = MySQLDB(database_name=database_name)
        self.os_version_upgrade_id = kwargs.get("osVersionUpgradeId")
        self.os_version_device_region_id = kwargs.get("osVersionDeviceRegionId")

    def update_upgrade_details(self) -> dict[str, str | dict]:
        """
        Update the OS version upgrade details from source to target.
        Args: self
        Returns: success or failure of update upgrade details
        """
        try:
            logger.info("Entering update_upgrade_details module to update required table details")
            with self.sql_instance.transactional_session() as session:
                phase_query: Query = session.query(PhaseUpgrade).filter(PhaseUpgrade.id == self.os_version_upgrade_id)
                seq_query: Query = session.query(SequenceUpgrade).filter(
                    SequenceUpgrade.phase_upgrade_id == self.os_version_upgrade_id
                )
                if query_count(phase_query) == 0:
                    return {
                        "status": "FAILURE",
                        "errorCategory": "FAILED",
                        "errors": [
                            {
                                "code": "ERR-000-097-1001",
                                "message": "Validation Failed: Invalid osVersionUpgradeId to update upgrade details",
                            }
                        ],
                    }
                if query_count(seq_query) == 0:
                    return {
                        "status": "FAILURE",
                        "errorCategory": "FAILED",
                        "errors": [
                            {
                                "code": "ERR-000-097-1002",
                                "message": "Validation Failed: osVersionUpgradeId found in phase upgrade table "
                                "but not available in sequence upgrade table",
                            }
                        ],
                    }
                target_custom_config: dict = self.body["upgradeDetails"]["targetOs"]["customConfig"]
                inter_details: list = self.body["upgradeDetails"].get("intermediateSteps", [])
                comments: str = self.body.get("Comments")
                phase_id_dict: dict = self.get_sequence_upgrade_details(session, comments, inter_details)
                if not phase_id_dict:
                    return {
                        "status": "FAILURE",
                        "errorCategory": "FAILED",
                        "errors": [
                            {
                                "code": "ERR-000-097-1003",
                                "message": "Validation Failed: Cannot update single step details with "
                                "multi step details given in payload",
                            }
                        ],
                    }
                target_phase_id: list[int] = list(phase_id_dict.values())[-1]
                phase_id_dict.pop(list(phase_id_dict.keys())[-1])
                self.update_custom_config_data(session, target_custom_config, target_phase_id)
                for seq_no, phase_id in phase_id_dict.items():
                    for data in inter_details:
                        if data.get("customConfig") and seq_no == data["sequence"]:
                            self.update_custom_config_data(session, data["customConfig"], phase_id)
            logger.info("Successfully updated upgrade details in table from update_custom_config_data method")
            return {
                "status": "success",
                "comments": self.body.get("Comments"),
                "osVersionUpgradeId": self.os_version_upgrade_id,
            }
        except (TypeError, AttributeError, KeyError, IndexError) as err:
            logger.exception(
                f"Exception occurred for update_upgrade_details module to update phase upgrade table entry"
                f" : {err.__class__.__name__} {err}"
            )
            return {
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-000-097-0500",
                        "message": f"Exception occurred while performing update upgrade details: "
                        f"{err.__class__.__name__}",
                    }
                ],
            }
        except Exception as err:
            logger.exception(
                f"Exception while performing update upgrade details from os device region tables"
                f" : {err.__class__.__name__} {err}"
            )
            error_message = (
                f"Database Operation Failed while performing update upgrade details : {db_errors[err.__class__]}"
                if err.__class__.__name__ in db_errors
                else f"Generic Exception occurred while performing update upgrade details"
                f" from os device region tables : {err.__class__.__name__}"
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

    def update_custom_config_data(self, session: object, custom_configs_list: list, id: int) -> None:
        """
        Update the custom config details in the phase upgrade table
        Args:
            session(object): SQL transactional session object
            custom_configs_list(dict): to update custm config data in table
            id(int): id to find the data in table
        Returns: None
        """
        logger.info("Entering update_custom_config_data module to update upgrade details")
        phase_details: Query = session.query(PhaseUpgrade).filter(PhaseUpgrade.id == id)
        custom_id: int = phase_details[0].custom_config_id
        custom_details_list: list[int] = [custom_id]
        custom_details: Query = session.query(CustomConfigList).filter(CustomConfigList.id == custom_id)
        next_id: int = custom_details[0].next_config_id
        role_details_list: list[int] = [custom_details[0].role_list_id]
        while next_id:
            next_custom_details: Query = session.query(CustomConfigList).filter(CustomConfigList.id == next_id)
            custom_details_list.append(next_id)
            role_details_list.append(next_custom_details[0].role_list_id)
            next_id: int = next_custom_details[0].next_config_id
        session.query(PhaseUpgrade).filter(PhaseUpgrade.id == id).update({"custom_config_id": None})
        session.commit()
        for del_custom in custom_details_list:
            session.query(CustomConfigList).filter(CustomConfigList.id == del_custom).delete()
            session.commit()
        for del_role in role_details_list:
            session.query(RoleList).filter(RoleList.id == del_role).delete()
            session.commit()
        custom_configs: list = []
        for target in custom_configs_list:
            role_list: list = target.get("deviceRole")
            role_list_id: int = self.update_role_list_table(session, role_list)
            custom_config = CustomConfigList(
                role_list_id=role_list_id,
                pre_target_upgrade_conf=target.get("beforeUpgrade"),
                post_target_upgrade_conf=target.get("afterUpgrade"),
                is_rollback_required=target.get("isRollbackRequired"),
                before_rollback=target.get("beforeRollback"),
                after_rollback=target.get("afterRollback"),
                config_mode=target.get("configMode"),
                next_config_id=None,
            )
            custom_configs.append(custom_config)
            session.add(custom_config)
            session.commit()
        for i in range(len(custom_configs)):
            if i == len(custom_configs) - 1:
                custom_configs[i].next_config_id = None
            else:
                custom_configs[i].next_config_id = custom_configs[i + 1].id
        session.query(PhaseUpgrade).filter(PhaseUpgrade.id == id).update({"custom_config_id": custom_configs[0].id})
        session.commit()
        logger.info("Successfully updated custom config data details for upgrade")

    def update_role_list_table(self, session: object, role_list: list[str]) -> int:
        """
        Insert role details to role list table
        Args:
            session (object): db session object
            role_list (list[str]): role list to update

        Returns:
            int: device role id
        """
        role_dict: dict = {}
        for index, role in enumerate(role_list):
            role_id: Query = (session.query(DeviceRole.id, DeviceRole.role)).filter(DeviceRole.role.like(f"{role}"))
            role_dict[f"role_id{index + 1}"] = role_id[0].id
        role_table = RoleList(**role_dict)
        session.add(role_table)
        session.commit()
        return role_table.id

    def get_sequence_upgrade_details(self, session: object, comments: str, inter_custom_config: list) -> list[dict]:
        """
        Query sequence upgrade details and find sequence & phase id if intermediate steps are there
        Args:
            session(object): SQL transactional session object
            comments(str): comments to update the table
            inter_custom_config(list): to check intermediate details is there or not
        Returns:
            (list): list of dict with sequence number and phase id
        """
        logger.info("Entering get_sequence_upgrade_details module to query sequence upgrade details")
        seq_details: Query = session.query(SequenceUpgrade).filter(
            SequenceUpgrade.phase_upgrade_id == self.os_version_upgrade_id
        )
        phase_id_dict: dict[int, int] = {seq_details[0].sequence_no: self.os_version_upgrade_id}
        total_steps: int = seq_details[0].steps
        if inter_custom_config and total_steps == 1:
            return {}
        for _ in range(total_steps):
            if comments:
                seq_details.update({"comments": comments})
            iter_seq_details: dict = seq_details[0]
            if iter_seq_details.next_sequence_id:
                seq_details: Query = session.query(SequenceUpgrade).filter(
                    SequenceUpgrade.id == iter_seq_details.next_sequence_id
                )
                phase_id_dict[seq_details[0].sequence_no] = seq_details[0].phase_upgrade_id
        logger.info("Successfully fetched phase upgrade id details from get_sequence_upgrade_details module")
        return phase_id_dict

    def update_image_details(self) -> dict[str, str | dict]:
        """
        Update the OS version device region details.
        Args: self
        Returns: success or failure of update image details
        """
        try:
            logger.info("Entering update_image_details module to update image and os status details in table")
            with self.sql_instance.transactional_session() as session:
                os_query: Query = session.query(OSVersionDeviceRegionPackage).filter(
                    OSVersionDeviceRegionPackage.id == self.os_version_device_region_id
                )
                valid_id: int = os_query[0].os_validity_id
                os_status_details: Query = (session.query(OsState.id, OsState.validity_state)).filter(
                    OsState.id == valid_id
                )
                os_status_exist: str = os_status_details[0].validity_state
                image_query: Query = session.query(Image).filter(
                    Image.os_device_region_id == self.os_version_device_region_id
                )
                err_details = {
                    "status": "FAILURE",
                    "errorCategory": "FAILED",
                    "errors": [
                        {
                            "code": "ERR-000-097-1005",
                            "message": "Validation Failed: This state cannot be changed because there is no "
                            "image detail, Please delete this image and recreate with the image detail",
                        }
                    ],
                }
                if (
                    os_status_exist == "Target"
                    and self.body["osStatus"] in ["Under_test", "Current", "Deprecated"]
                    and not image_query[0].file_type
                ):
                    return err_details
                if (
                    os_status_exist == "Deprecated"
                    and self.body["osStatus"] == "Current"
                    and not image_query[0].file_type
                ):
                    return err_details
                if query_count(os_query) == 0:
                    return {
                        "status": "FAILURE",
                        "errorCategory": "FAILED",
                        "errors": [
                            {
                                "code": "ERR-000-097-1004",
                                "message": "Validation Failed: Invalid osVersionDeviceRegionId to update "
                                "image details",
                            }
                        ],
                    }
                if query_count(image_query) == 0:
                    return {
                        "status": "FAILURE",
                        "errorCategory": "FAILED",
                        "errors": [
                            {
                                "code": "ERR-000-097-1005",
                                "message": "Validation Failed: osVersionDeviceRegionId found in os version device"
                                " region table but not available in image table",
                            }
                        ],
                    }
                if self.body.get("comments"):
                    session.query(Image).filter(Image.os_device_region_id == self.os_version_device_region_id).update(
                        {"comments": self.body["comments"]}
                    )
                os_status_id: int = self.get_os_validity_id(session, self.body["osStatus"])
                session.query(OSVersionDeviceRegionPackage).filter(
                    OSVersionDeviceRegionPackage.id == self.os_version_device_region_id
                ).update({"os_validity_id": os_status_id})
                session.commit()
            logger.info("Successfully updated image and os status details in table from update_image_details method")
            return {
                "status": "success",
                "comments": self.body.get("comments"),
                "osVersionDeviceRegionId": self.os_version_device_region_id,
            }
        except (TypeError, AttributeError, KeyError, IndexError) as err:
            logger.exception(
                f"Exception occurred for update_image_details module to update image table entry"
                f" : {err.__class__.__name__} {err}"
            )
            return {
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-000-097-0500",
                        "message": f"Exception occurred while performing update image details: "
                        f"{err.__class__.__name__}",
                    }
                ],
            }
        except Exception as err:
            logger.exception(
                f"Exception while performing update image details from os device region tables"
                f" : {err.__class__.__name__} {err}"
            )
            error_message = (
                f"Database Operation Failed while performing update image details : {db_errors[err.__class__]}"
                if err.__class__.__name__ in db_errors
                else f"Generic Exception occurred while performing update image details"
                f" from os device region tables : {err.__class__.__name__}"
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

    def get_os_validity_id(self, session: object, os_status: str) -> int:
        """
        Query os state details and find validity id
        Args:
            session(object): SQL transactional session object
            os_status(string): os status to update the table
        Returns:
            (int): os status id
        """
        logger.debug("Entering get_os_validity_id module to query os state details")
        os_status_details: Query = (session.query(OsState.id, OsState.validity_state)).filter(
            OsState.validity_state.like(f"{os_status}")
        )
        return os_status_details[0].id
