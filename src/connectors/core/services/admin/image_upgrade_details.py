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
import datetime
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
    DeviceMaster,
    DeviceRegion,
    DeviceRole,
    OsState,
    OSVersion,
    OSVersionDeviceRegionPackage,
    PhaseUpgrade,
    RegionMaster,
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


class ImageUpgradeDetails:
    def __init__(self, body):
        self.body = body
        self.sql_instance = MySQLDB(database_name=database_name)
        self.default_user = None

    def image_upgrade_details(self) -> dict:
        """
        Get the DeviceOSVersion, OSVersionMaster and DeviceMaster data
        Returns: device_os_version list
        """
        try:
            logger.debug("Entering image_upgrade_details module to insert into phase and sequence upgrade tables")
            status = []
            errors = []
            success_dict = {"success": []}
            failure_dict = {"failure": []}
            add_device_response = {"metadata": {}}
            self.default_user = "Admin"
            with self.sql_instance.transactional_session() as session:
                for data in self.body:
                    vendor: str = data.get("deviceVendor")
                    model: str = data.get("deviceModel")
                    region: str = data.get("region")
                    current_os: str = data.get("currentOsVersion")
                    current_label: str = data.get("currentOsLabel")
                    total_steps: int = data.get("upgrade", {}).get("upgradeSteps")
                    target_os: list[str] = data.get("upgrade", {}).get("targetOs", {}).get("osVersion")
                    target_label: list[str] = data.get("upgrade", {}).get("targetOs", {}).get("osLabel")
                    target_custom: list[dict] = data.get("upgrade", {}).get("targetOs", {}).get("customConfig", [])
                    comments: str = data.get("Comments")

                    (
                        intermediate_os,
                        intermediate_label,
                        intermediate_validity,
                        intermediate_sequence,
                        intermediate_custom,
                    ) = ([], [], [], [], [])
                    for steps in data.get("upgrade", {}).get("intermediateSteps", []):
                        intermediate_os.append(steps.get("osVersion"))
                        intermediate_label.append(steps.get("osLabel"))
                        intermediate_validity.append("Current")
                        intermediate_sequence.append(steps.get("sequence"))
                        intermediate_custom.append(steps.get("customConfig", []))

                    response = {
                        "image": {
                            "deviceVendor": vendor,
                            "deviceModel": model,
                            "region": region,
                            "currentOsVersion": current_os,
                            "currentOsLabel": current_label,
                            "targetOsVersion": target_os,
                            "targetOsLabel": target_label,
                        }
                    }
                    if int(total_steps) - 1 != len(data.get("upgrade", {}).get("intermediateSteps", [])):
                        status.append(False)
                        failure_dict["failure"].append(response)
                        add_device_response["metadata"].update(failure_dict)
                        ref_value = len(add_device_response["metadata"]["failure"]) - 1
                        errors.append(
                            {
                                "code": "ERR-000-097-1001",
                                "message": f"Validation Failed: UpgradeSteps steps is {int(total_steps)} but provided"
                                " intermediate details length is "
                                f"{len(data.get('upgrade', {}).get('intermediateSteps', []))}."
                                "Intermediate details length should one less than UpgradeSteps.",
                                "serviceReference": {"$ref": f"#/metadata/failure/{ref_value}"},
                            }
                        )
                        continue
                    # Querying Device Region ID
                    device_version_details = self.device_region_details(session, vendor, model, region)
                    dv_status = self.valid_query_check(device_version_details=device_version_details)
                    if not dv_status:
                        status.append(False)
                        failure_dict["failure"].append(response)
                        add_device_response["metadata"].update(failure_dict)
                        ref_value = len(add_device_response["metadata"]["failure"]) - 1
                        errors.append(
                            {
                                "code": "ERR-000-097-1002",
                                "message": f"Validation Failed: Device Region ID for given vendor {vendor}, "
                                f"model {model} and region {region} is not in DB",
                                "serviceReference": {"$ref": f"#/metadata/failure/{ref_value}"},
                            }
                        )
                        continue
                    # Querying OS Version Table
                    # Bugfix: DNE-28266
                    source_os_details, intermediate_os_details, target_os_details = self.os_version_details(
                        session,
                        total_steps=total_steps,
                        current_os=current_os,
                        current_label=current_label,
                        target_os=target_os,
                        target_label=target_label,
                        intermediate_os=intermediate_os,
                        intermediate_label=intermediate_label,
                    )
                    os_status = self.valid_query_check(
                        source_os_details=source_os_details,
                        intermediate_os_details=intermediate_os_details,
                        total_steps=total_steps,
                        target_os_details=target_os_details,
                    )
                    os_err_msg: str = self.os_status_error_message(current_label, intermediate_label, target_label)
                    if not os_status:
                        status.append(False)
                        failure_dict["failure"].append(response)
                        add_device_response["metadata"].update(failure_dict)
                        ref_value = len(add_device_response["metadata"]["failure"]) - 1
                        errors.append(
                            {
                                "code": "ERR-000-097-1003",
                                "message": f"Validation Failed: OS Version Details corresponding to {os_err_msg} not "
                                f"in DB",
                                "serviceReference": {"$ref": f"#/metadata/failure/{ref_value}"},
                            }
                        )
                        continue
                    # Querying OS Version Device Region Package Table
                    (
                        source_os_device_region_details,
                        intermediate_os_device_region_details,
                        target_os_device_region_details,
                    ) = self.os_version_device_region_details(
                        session,
                        total_steps=total_steps,
                        intermediate_os=intermediate_os,
                        device_version_details=device_version_details,
                        target_os_details=target_os_details,
                        source_os_details=source_os_details,
                        intermediate_os_details=intermediate_os_details,
                    )
                    os_version_dr_status = self.valid_query_check(
                        source_os_device_region_details=source_os_device_region_details,
                        target_os_device_region_details=target_os_device_region_details,
                        intermediate_os_device_region_details=intermediate_os_device_region_details,
                        total_steps=total_steps,
                    )
                    if not os_version_dr_status:
                        status.append(False)
                        failure_dict["failure"].append(response)
                        add_device_response["metadata"].update(failure_dict)
                        ref_value = len(add_device_response["metadata"]["failure"]) - 1
                        errors.append(
                            {
                                "code": "ERR-000-097-1004",
                                "message": "Validation Failed: OS Version Device Region Details corresponding to "
                                f"{os_err_msg} and for  given"
                                f" vendor {vendor}, model {model} and region {region} is not found in DB",
                                "serviceReference": {"$ref": f"#/metadata/failure/{ref_value}"},
                            }
                        )
                        continue
                    # Inserting into Phase upgrade table if intermediate upgrades are present

                    phase_upgrade_fk = self.phase_upgrade_insert(
                        session,
                        status=status,  # Bugfix : DNE-35758
                        failure_dict=failure_dict,
                        add_device_response=add_device_response,
                        response=response,
                        errors=errors,
                        total_steps=total_steps,
                        intermediate_os=intermediate_os,
                        intermediate_label=intermediate_label,
                        deviceregion_id=device_version_details[0].deviceRegionID,
                        source_os_device_region_details=source_os_device_region_details,
                        target_os_device_region_details=target_os_device_region_details,
                        intermediate_os_device_region_details=intermediate_os_device_region_details,
                        target_custom=target_custom,
                        intermediate_custom=intermediate_custom,
                    )
                    if not phase_upgrade_fk:
                        continue
                    sequence_upgrades = []
                    if int(total_steps) > 1:
                        for items in range(len(intermediate_os) + 1):
                            sequence_upgrade = SequenceUpgrade(  # sourcery skip
                                steps=int(total_steps),
                                sequence_no=int(total_steps)
                                if items == len(intermediate_os)
                                else intermediate_sequence[items],
                                comments=comments,
                                next_sequence_id=None,
                                phase_upgrade_id=phase_upgrade_fk[items],
                                deviceregion_id=device_version_details[0].deviceRegionID,
                                createdBy=self.default_user,
                                modifiedBy=self.default_user,
                                createdOn=datetime.datetime.utcnow(),
                                modifiedOn=datetime.datetime.utcnow(),
                            )
                            sequence_upgrades.append(sequence_upgrade)
                            session.add(sequence_upgrade)
                            session.commit()
                        for i in range(len(sequence_upgrades)):
                            if i == len(sequence_upgrades) - 1:
                                sequence_upgrades[i].next_sequence_id = None
                            else:
                                sequence_upgrades[i].next_sequence_id = sequence_upgrades[i + 1].id
                    else:
                        sequence_upgrade = SequenceUpgrade(
                            steps=int(total_steps),
                            sequence_no=1,
                            comments=comments,
                            next_sequence_id=None,
                            phase_upgrade_id=phase_upgrade_fk[0],
                            deviceregion_id=device_version_details[0].deviceRegionID,
                            createdBy=self.default_user,
                            modifiedBy=self.default_user,
                            createdOn=datetime.datetime.utcnow(),
                            modifiedOn=datetime.datetime.utcnow(),
                        )
                        sequence_upgrades.append(sequence_upgrade)
                        session.add(sequence_upgrade)
                    session.commit()
                    if sequence_upgrade:
                        status.append(True)
                        response["osVersionUpgradeId"] = sequence_upgrades[0].id
                        success_dict["success"].append(response)
                        add_device_response["metadata"].update(success_dict)
                    else:
                        status.append(False)
                        failure_dict["failure"].append(response)
                        add_device_response["metadata"].update(failure_dict)
                        ref_value = len(add_device_response["metadata"]["failure"]) - 1
                        add_device_response["errorCategory"] = "FAILED"
                        errors.append(
                            {
                                "code": "ERR-000-097-0500",
                                "message": "Database Operation Failed : Insertion into Sequence Table Failed",
                                "serviceReference": {"$ref": f"#/metadata/failure/{ref_value}"},
                            }
                        )
                        continue
            self.check_image_upgrade_status(errors, status, add_device_response)
            logger.debug("Exiting image_upgrade_details module")
            return add_device_response

        except Exception as err:
            logger.exception(
                f"Exception Occurred. Failed to update image upgrade details due to error"
                f" {err.__class__.__name__} {err}"
            )
            error_message = (
                f"Database Operation Failed while performing update image upgrade details : {db_errors[err.__class__]}"
                if err.__class__.__name__ in db_errors
                else f"Generic Exception occurred while performing update image upgrade details to "
                f"image and upgrade tables {err.__class__.__name__} : {err}"
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

    def check_image_upgrade_status(self, errors: list, status: list, add_device_response: dict) -> None:
        """
        Check image upgrade details and update status
        Args:
            errors (list): list of error details to update device response
            status (list): list of status to determine overall status
            add_device_response (dict): update the device response
        """
        if errors:
            add_device_response["errorCategory"] = "FAILED"
            add_device_response["errors"] = errors
        if all(status):
            add_device_response["status"] = "SUCCESS"
        elif any(status):
            add_device_response["status"] = "PARTIAL-SUCCESS"
        else:
            add_device_response["status"] = "FAILURE"

    def os_status_error_message(self, current_label: str, intermediate_label: str, target_label: str) -> str:
        """
        Check image upgrade details and update status
        Args:
            current_label (str): current label info
            intermediate_label (str): intermediate label info
            target_label (str): target label info
        Returns:
            (str): error message
        """
        return (
            f"current version {current_label} or intermediate version {intermediate_label}"
            f" or target version {target_label}"
            if intermediate_label
            else f"current version {current_label} or target version {target_label}"
        )

    def device_region_details(self, session: object, vendor: str, model: str, region: str) -> Query:
        """
        Method to get device_region_details from device_region table
        :param session:
        :return:
        """
        try:
            logger.debug("Entering device_region_details module to get device region details")
            return (
                session.query(
                    DeviceRegion.id.label("deviceRegionID"),
                    DeviceRegion.device_id,
                    DeviceRegion.region_id,
                    DeviceMaster.id.label("deviceID"),
                    RegionMaster.id.label("regionID"),
                    DeviceMaster.vendor,
                    DeviceMaster.model,
                    RegionMaster.region,
                )
                .join(DeviceMaster, DeviceMaster.id == DeviceRegion.device_id)
                .join(RegionMaster, RegionMaster.id == DeviceRegion.region_id)
            ).filter(
                DeviceMaster.vendor.like(f"%{vendor}%"),
                DeviceMaster.model.like(f"%{model}%"),
                RegionMaster.region.like(f"%{region}%"),
            )
        except (TypeError, AttributeError, KeyError, IndexError) as err:
            logger.exception(
                f"Exception occurred while querying data from device region table"
                f" : {err.__class__.__name__} {err.args[0]}"
            )
            return {
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-000-097-0500",
                        "message": f"Exception occurred while querying data from"
                        f" device region table : {err.__class__.__name__}",
                    }
                ],
            }
        except Exception as err:
            logger.exception(
                "Exception Occurred. Failed while querying data from device region table"
                f" due to error {err.__class__.__name__} {err.args[0]}"
            )
            error_message = (
                f"Database Operation Failed querying data from device region table : {db_errors[err.__class__]}"
                if err.__class__.__name__ in db_errors
                else f"Generic Exception occurred while querying data "
                f"from device region table : {err.__class__.__name__}"
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

    def os_version_details(self, session: object, **kwargs: dict) -> tuple[Query, Query, Query]:
        """
        Method to get os version id from os version table
        :param session:
        :param kwargs:
        :return:
        """
        try:
            logger.debug("Entering os_version_details module to get OS details")
            total_steps = kwargs["total_steps"]
            current_os = kwargs["current_os"]
            current_label = kwargs["current_label"]
            target_os = kwargs["target_os"]
            target_label = kwargs["target_label"]
            intermediate_os = kwargs["intermediate_os"]
            intermediate_label = kwargs["intermediate_label"]
            source_os_details = session.query(  # Bugfix: DNE-28266
                OSVersion.id,
                OSVersion.os,
                OSVersion.os_version,
                OSVersion.os_label,
                OsState.id.label("osValidityID"),
                OsState.validity_state,
            ).filter(
                (OSVersion.os == "IOSXR")
                & (
                    (OSVersion.os_version == current_os)
                    & (OSVersion.os_label == current_label)
                    & (OsState.validity_state == "Deprecated")
                )
            )
            target_os_details = session.query(
                OSVersion.id,
                OSVersion.os,
                OSVersion.os_version,
                OSVersion.os_label,
                OsState.id.label("osValidityID"),
                OsState.validity_state,
            ).filter(
                (OSVersion.os == "IOSXR")
                & (
                    (OSVersion.os_version == target_os)
                    & (OSVersion.os_label == target_label)
                    & (OsState.validity_state == "Current")
                )
            )
            if int(total_steps) > 1:
                intermediate_os_details = [
                    session.query(
                        OSVersion.id,
                        OSVersion.os,
                        OSVersion.os_version,
                        OSVersion.os_label,
                        OsState.id.label("osValidityID"),
                        OsState.validity_state,
                    ).filter(
                        (OSVersion.os == "IOSXR")
                        & (
                            (OSVersion.os_version == intermediate_os[details])
                            & (OSVersion.os_label == intermediate_label[details])
                            & (OsState.validity_state == "Current")
                        )
                    )
                    for details in range(len(intermediate_os))
                ]
                logger.debug("Exiting os_version_details module")
                return source_os_details, intermediate_os_details, target_os_details
            else:
                return source_os_details, None, target_os_details
        except (TypeError, AttributeError, KeyError, IndexError) as err:
            logger.exception(
                f"Exception occurred for image_upgrade_details module failed to update image upgrade details"
                f" : {err.__class__.__name__} {err.args[0]}"
            )
            return {
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-000-097-0500",
                        "message": f"Exception occurred while performing add image "
                        f"upgrade details to image and upgrade tables: {err.__class__.__name__}",
                    }
                ],
            }
        except Exception as err:
            logger.exception("Exception Occurred. Failed while querying data from os version table due to error {err}")
            error_message = (
                f"Database Operation Failed while querying data from os version table : {db_errors[err.__class__]}"
                if err.__class__.__name__ in db_errors
                else f"Exception occurred while querying data from os version table : {err.__class__.__name__}"
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

    def os_version_device_region_details(
        self, session: object, **kwargs: dict
    ) -> tuple[Query, None | list[Query], Query]:
        """
        Method to get os version device region details from os version device region table
        :param session:
        :param kwargs:
        :return:
        """
        try:
            logger.debug("Entering os_version_device_region_details module to get OS-deviceregion and validity details")
            device_version_details = kwargs["device_version_details"]
            source_os_details = kwargs["source_os_details"]  # Bugfix: DNE-28266
            target_os_details = kwargs["target_os_details"]
            intermediate_os_details = kwargs["intermediate_os_details"]
            source_os_device_region_details = session.query(
                OSVersionDeviceRegionPackage.id,
                OSVersionDeviceRegionPackage.device_region_id,
                OSVersionDeviceRegionPackage.os_version_id,
                OSVersionDeviceRegionPackage.os_validity_id,
            ).filter(
                (OSVersionDeviceRegionPackage.device_region_id == device_version_details[0].deviceRegionID)
                & (
                    (OSVersionDeviceRegionPackage.os_version_id == source_os_details[0].id)
                    & (OSVersionDeviceRegionPackage.os_validity_id == source_os_details[0].osValidityID)
                )
            )
            target_os_device_region_details = session.query(
                OSVersionDeviceRegionPackage.id,
                OSVersionDeviceRegionPackage.device_region_id,
                OSVersionDeviceRegionPackage.os_version_id,
                OSVersionDeviceRegionPackage.os_validity_id,
            ).filter(
                (OSVersionDeviceRegionPackage.device_region_id == device_version_details[0].deviceRegionID)
                & (
                    (OSVersionDeviceRegionPackage.os_version_id == target_os_details[0].id)
                    & (OSVersionDeviceRegionPackage.os_validity_id == target_os_details[0].osValidityID)
                )
            )

            if int(kwargs["total_steps"]) > 1:
                intermediate_os_device_region_details = []
                for details in range(len(kwargs["intermediate_os"])):
                    intermediate_os_device_region_details.append(
                        session.query(
                            OSVersionDeviceRegionPackage.id,
                            OSVersionDeviceRegionPackage.device_region_id,
                            OSVersionDeviceRegionPackage.os_version_id,
                            OSVersionDeviceRegionPackage.os_validity_id,
                        ).filter(
                            (OSVersionDeviceRegionPackage.device_region_id == device_version_details[0].deviceRegionID)
                            & (
                                (OSVersionDeviceRegionPackage.os_version_id == intermediate_os_details[details][0].id)
                                & (
                                    OSVersionDeviceRegionPackage.os_validity_id
                                    == intermediate_os_details[details][0].osValidityID
                                )
                            )
                        )
                    )
                    logger.debug("Exiting os_version_device_region_details module")
                return (
                    source_os_device_region_details,
                    intermediate_os_device_region_details,
                    target_os_device_region_details,
                )
            else:
                logger.debug("Exiting os_version_device_region_details module")
                return source_os_device_region_details, None, target_os_device_region_details

        except (TypeError, AttributeError, KeyError, IndexError) as err:
            logger.exception(
                f"Exception occurred while querying data from os version device region table"
                f" : {err.__class__.__name__} {err.args[0]}"
            )
            return {
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-000-097-0500",
                        "message": f"Exception occurred while querying data from"
                        f" os version device region table : {err.__class__.__name__}",
                    }
                ],
            }
        except Exception as err:
            logger.exception(
                "Exception Occurred. Failed while querying data from os version device region table"
                f" due to error {err.__class__.__name__} {err.args[0]}"
            )
            error_message = (
                "Database Operation Failed while querying data from os version device region table :"
                f" {db_errors[err.__class__]}"
                if err.__class__.__name__ in db_errors
                else f"Generic Exception occurred while querying data from os version device region table :"
                f" {err.__class__.__name__}"
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

    def phase_upgrade_query(self, session: object) -> dict[str, str | list]:
        """
        Query phase upgrade table with id
        Args:
            session (object): SQL transactional session object
        """
        return session.query(
            PhaseUpgrade.id,
            PhaseUpgrade.source_osv_dr_id,
            PhaseUpgrade.target_osv_dr_id,
            SequenceUpgrade.phase_upgrade_id,
            SequenceUpgrade.steps,
            SequenceUpgrade.sequence_no,
            SequenceUpgrade.deviceregion_id,
        ).join(SequenceUpgrade, PhaseUpgrade.id == SequenceUpgrade.phase_upgrade_id)

    def multi_step_phase_upgrade(
        self, session: object, phase_query: Query, **kwargs: dict[str, str | list]
    ) -> list[int]:
        """
        Multi step phase upgrade insertion
        Args:
            session (object): SQL transactional session object
            phase_query (Query): phase update query
        Kwargs:
            source_os_device_region_details (Query): source os device region query details
            target_os_device_region_details (Query): target os device region query details
            deviceregion_id (int): to update phase upgrade
            response (dict): to update response for output
            intermediate_label (str): intermediate label data
            total_steps (int): total number of steps
        Returns:
            (list): list of phase upgrade id
        """
        total_steps = kwargs["total_steps"]
        phase_upgrade_fk = []
        source_osv, target_osv = None, None
        for items, configs in enumerate(kwargs["intermediate_custom"]):
            source_osv, target_osv = self.find_source_and_target_details(items, **kwargs)
            phase_query_filter = phase_query.filter(
                PhaseUpgrade.source_osv_dr_id == source_osv,
                PhaseUpgrade.target_osv_dr_id == target_osv,
                SequenceUpgrade.deviceregion_id == kwargs["deviceregion_id"],
            )
            # Bugfix : DNE-35758
            if query_count(phase_query_filter.filter(SequenceUpgrade.steps < total_steps)):
                return self.error_message_builder(
                    **kwargs,
                    code="1006",
                    err_msg=f"Please delete single step upgrade with current version "
                    f"{kwargs['response']['image']['currentOsLabel']}, and target version "
                    f"{kwargs['intermediate_label']} or {kwargs['response']['image']['targetOsLabel']} "
                    f"before multi step image upgrade",
                )
            if query_count(phase_query_filter.filter(SequenceUpgrade.steps == total_steps)):
                return self.error_message_builder(
                    **kwargs,
                    code="1005",
                    err_msg=f"Duplication of multi step upgrade details with current version "
                    f"{kwargs['response']['image']['currentOsLabel']}, "
                    f"intermediate {kwargs['intermediate_label']} and target version "
                    f"{kwargs['response']['image']['targetOsLabel']} is not allowed",
                )
            # Bugfix: DNE-37793
            custom_config_id: int = self.insert_into_custom_config(session, configs) if configs else None
            self.commit_phase_upgrade(phase_upgrade_fk, session, source_osv, target_osv, custom_config_id)
        custom_config_id: int = self.insert_into_custom_config(session, kwargs["target_custom"])
        self.commit_phase_upgrade(
            phase_upgrade_fk, session, target_osv, kwargs["target_os_device_region_details"][0].id, custom_config_id
        )
        return phase_upgrade_fk

    def single_step_phase_upgrade(
        self, session: object, phase_query: Query, **kwargs: dict[str, str | list]
    ) -> list[int]:
        """
        Multi step phase upgrade insertion
        Args:
            session (object): SQL transactional session object
            phase_query (Query): phase update query
        Kwargs:
            target_custom (list): custom config details of target
            source_os_device_region_details (Query): source os device region query details
            target_os_device_region_details (Query): target os device region query details
            deviceregion_id (int): to update phase upgrade
            response (dict): to update response for output
            intermediate_label (str): intermediate label data
            total_steps (int): total number of steps
        Returns:
            (list): list of phase upgrade id
        """
        total_steps: int = kwargs["total_steps"]
        tar_custom: list = kwargs["target_custom"]
        phase_upgrade_fk: list = []
        phase_query_filter = phase_query.filter(
            PhaseUpgrade.source_osv_dr_id == kwargs["source_os_device_region_details"][0].id,
            PhaseUpgrade.target_osv_dr_id == kwargs["target_os_device_region_details"][0].id,
            SequenceUpgrade.deviceregion_id == kwargs["deviceregion_id"],
        )
        # Bugfix : DNE-35758
        if query_count(phase_query_filter.filter(SequenceUpgrade.steps == total_steps)):
            return self.error_message_builder(
                **kwargs,
                code="1005",
                err_msg=f"Duplication of single step upgrade details with current version "
                f"{kwargs['response']['image']['currentOsLabel']} and target version "
                f"{kwargs['response']['image']['targetOsLabel']} is not allowed",
            )
        if query_count(phase_query_filter.filter(SequenceUpgrade.steps > 1)):
            return self.error_message_builder(
                **kwargs,
                code="1006",
                err_msg=f"Please delete multi step upgrade with current version "
                f"{kwargs['response']['image']['currentOsLabel']}, and target or intermediate version"
                f" {kwargs['response']['image']['targetOsLabel']} before single step image upgrade",
            )
        # Bugfix: DNE-37793
        custom_config_id: int = self.insert_into_custom_config(session, tar_custom) if tar_custom else None
        self.commit_phase_upgrade(
            phase_upgrade_fk,
            session,
            kwargs["source_os_device_region_details"][0].id,
            kwargs["target_os_device_region_details"][0].id,
            custom_config_id,
        )
        return phase_upgrade_fk

    def phase_upgrade_insert(self, session: object, **kwargs: dict) -> list[str]:
        """
        Method to insert into phase upgrade table
        Args:
            session (object): db session object

        Kwargs:
            total_steps (int): total upgrade steps
            source_os_device_region_details (list[object]): source os version details
            target_os_device_region_details (list[object]): target os version details
            intermediate_os_device_region_details (list[object]): intermediate os version details
            target_custom (list): traget version custom configs
            intermediate_custom (list): intermediate versions custom configs

        Returns:
            list[str]: phase upgrade ids
        """
        try:
            logger.debug("Entering phase_upgrade_insert module to insert into phase_upgrade table")
            phase_query = self.phase_upgrade_query(session)  # Bugfix : DNE-35758
            if int(kwargs["total_steps"]) > 1:
                return self.multi_step_phase_upgrade(session, phase_query, **kwargs)
            else:
                return self.single_step_phase_upgrade(session, phase_query, **kwargs)
        except Exception as err:
            logger.exception(
                f"Exception Occurred. Failed while inserting data into phase upgrade table "
                f"due to error {err.__class__.__name__}{err}"
            )
            error_message = (
                f"Database Operation Failed while inserting data into phase upgrade table : {db_errors[err.__class__]}"
                if err.__class__.__name__ in db_errors
                else f"Generic Exception occurred while inserting data "
                f"into phase upgrade table {err.__class__.__name__} : {err}"
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

    def find_source_and_target_details(
        self, items: int, **kwargs: dict[str, str | list[Query] | Query]
    ) -> tuple[int, int]:
        """
        Insert single step phase upgrade details
        Args:
            source_os_device_region_details (Query): source os device region query details
            target_os_device_region_details (Query): target os device region query details
            intermediate_os_device_region_details (list[Query]): intermedate os device region query details
            items (int): no of steps
        Returns:
            tuple(int, int): source and target response to update phase upgrade
        """
        if items == 0:
            source_osv: int = kwargs["source_os_device_region_details"][0].id
        else:
            source_osv: int = kwargs["intermediate_os_device_region_details"][items - 1][0].id
        if items == len(kwargs["intermediate_os"]):
            target_osv: int = kwargs["target_os_device_region_details"][0].id
        else:
            target_osv: int = kwargs["intermediate_os_device_region_details"][items][0].id
        return source_osv, target_osv

    def error_message_builder(self, **kwargs: dict[str, str | list]) -> list:
        """
        To form error message details for already available upgrade one or multi steps and for duplication
        kwargs:
            status(list): to append status
            failure_dict(dict): to update failure details
            response(dict): image upgrade details response
            add_device_response(dict): to update device response with reference
            err_msg(str): to update error message details
        Returns:
            (list): empty list
        """
        kwargs["status"].append(False)
        kwargs["failure_dict"]["failure"].append(kwargs["response"])
        kwargs["add_device_response"]["metadata"].update(kwargs["failure_dict"])
        ref_value: int = len(kwargs["add_device_response"]["metadata"]["failure"]) - 1
        kwargs["errors"].append(
            {
                "code": f"ERR-000-097-{kwargs['code']}",
                "message": f"Validation Failed: {kwargs['err_msg']}",
                "serviceReference": {"$ref": f"#/metadata/failure/{ref_value}"},
            }
        )
        return []

    def commit_phase_upgrade(
        self,
        phase_upgrade_fk: list,
        session: object,
        source_osv: int,
        target_osv: int,
        custom_config_id: int,
    ) -> None:
        """
        To commit phase upgrade details to database
        Args:
            phase_upgrade_fk (list): to append phase upgrade id
            source_osv (int): source os version id
            target_osv (int): target os versin id
            custom_config_id (str): custom config id
        """
        phase_upgrade = PhaseUpgrade(
            source_osv_dr_id=source_osv,
            target_osv_dr_id=target_osv,
            createdBy=self.default_user,
            modifiedBy=self.default_user,
            createdOn=datetime.datetime.now(datetime.timezone.utc),
            modifiedOn=datetime.datetime.now(datetime.timezone.utc),
            custom_config_id=custom_config_id,
        )
        session.add(phase_upgrade)
        session.commit()
        phase_upgrade_fk.append(phase_upgrade.id)
        logger.debug("Exiting phase_upgrade_insert module")

    def insert_into_custom_config(self, session: object, custom_configs_list: list) -> None:
        """
        To commit phase upgrade details to database
        Args:
            phase_upgrade_fk (list): to append phase upgrade id
            target_custom (list): target custom config list details
        """
        custom_configs: list[Query] = []
        for target in custom_configs_list:
            role_list: list = target.get("deviceRole")
            role_list_id: int = self.update_role_list_table(session, role_list)
            custom_config: Query = CustomConfigList(
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
        session.commit()
        logger.debug("Exiting insert_into_custom_config module")
        return custom_configs[0].id

    def update_role_list_table(self, session: object, role_list: list) -> int:
        """Insert role details to role list table

        Args:
            session (object): db session object
            role_list (list): role list to update

        Returns:
            int: device role id
        """
        role_dict: dict[str, int] = {}
        for index, role in enumerate(role_list):
            role_id = (session.query(DeviceRole.id, DeviceRole.role)).filter(DeviceRole.role.like(f"{role}"))
            role_dict[f"role_id{index + 1}"] = role_id[0].id
        role_table: Query = RoleList(**role_dict)
        session.add(role_table)
        session.commit()
        return role_table.id

    def valid_query_check(self, **kwargs: dict) -> bool:
        """
        Method to validate query information from the tables
        :param kwargs:
        :return:
        """
        try:
            logger.debug("Entering into valid_query_check for validation the response of the queries obtained")
            if kwargs.get("device_version_details"):
                return kwargs["device_version_details"].count() == 1
            if kwargs.get("source_os_details") or kwargs.get("target_os_details"):
                target_os_details = kwargs["target_os_details"]
                total_steps = kwargs["total_steps"]
                intermediate_os_details = kwargs["intermediate_os_details"]
                source_os_details = kwargs["source_os_details"]
                if query_count(source_os_details) == 1 and query_count(target_os_details) == 1:
                    if (
                        query_count(source_os_details) == 1
                        and not source_os_details[0].id
                        or not source_os_details[0].osValidityID
                    ) or (
                        query_count(target_os_details) == 1
                        and not target_os_details[0].id
                        or not target_os_details[0].osValidityID
                    ):
                        return False
                    status = (
                        [intermediate_os_details[i].count() == 1 for i in range(int(total_steps) - 1)]
                        if int(total_steps) > 1
                        else []
                    )
                    return all(status)
                return False
            if kwargs.get("source_os_device_region_details") or kwargs.get("target_os_device_region_details"):
                return self.validate_os_device_region_details(**kwargs)
        except (TypeError, AttributeError, KeyError, IndexError) as err:
            logger.exception(
                f"Exception occurred for valid_query_check module while validating the query table"
                f" : {err.__class__.__name__} {err.args[0]}"
            )
            return {
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-000-097-0500",
                        "message": f" Exception occurred while validating the query table: {err.__class__.__name__}",
                    }
                ],
            }
        except Exception as err:
            logger.exception(
                f"Exception Occurred while validating the query table "
                f"due to error {err.__class__.__name__} {err.args[0]}"
            )
            error_message = (
                f"Database Operation Failed during validation check : {db_errors[err.__class__]}"
                if err.__class__.__name__ in db_errors
                else f"Generic Exception occurred during validation check : {err.__class__.__name__}"
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

    def validate_os_device_region_details(self, **kwargs) -> bool:
        """
        validate os device region details query
        Returns:
            bool:
        """
        source_os_device_region_details = kwargs["source_os_device_region_details"]
        target_os_device_region_details = kwargs["target_os_device_region_details"]
        intermediate_os_device_region_details = kwargs["intermediate_os_device_region_details"]
        total_steps = kwargs["total_steps"]
        if query_count(source_os_device_region_details) == 1 or query_count(target_os_device_region_details) == 1:
            # Bugfix : DNE-35758
            if not (query_count(source_os_device_region_details) == 1 and source_os_device_region_details[0].id) or (
                not query_count(target_os_device_region_details) == 1 and target_os_device_region_details[0].id
            ):
                return False
            status = (
                [intermediate_os_device_region_details[i].count() == 1 for i in range(int(total_steps) - 1)]
                if int(total_steps) > 1
                else []
            )
            return all(status)
        return False
