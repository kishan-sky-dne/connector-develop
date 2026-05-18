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
from itertools import groupby
from typing import Dict, Iterator, Tuple

# Third Party Library
from sqlalchemy.orm.query import Query

# Sky Library
from isp_config import ConfigManagerException

# DNE Library
from connectors.core.config import connectors_config
from connectors.core.services.admin.utils import UPDATE_REGION_BY_MODEL, query_count
from connectors.core.utils.sqldb.sqlDB import MySQLDB
from connectors.core.utils.sqldb.sqlDB_errors import db_errors
from connectors.core.utils.sqldb.swlifecycle_model import (
    CustomConfigList,
    DeviceMaster,
    DeviceRegion,
    DeviceRole,
    FileType,
    Image,
    OsState,
    OSVersion,
    OSVersionDeviceRegionPackage,
    Package,
    PackageType,
    PhaseUpgrade,
    RegionMaster,
    RoleList,
    SequenceUpgrade,
    ServiceCheck,
    TrafficDiversion,
    TrafficProtocol,
)

try:
    config = connectors_config.ConnectorsConfigManager()
    config.load_config()
except ConfigManagerException:
    sys.exit(1)

database_name = config.get(section="mysqlDB", key="sw_upgrade_database_name")

logger = logging.getLogger(__name__)


class UpgradeDetails:
    def __init__(self, **kwargs: dict[str, str | list]) -> None:
        """
        Initializes an instance of read upgrade details
        """
        self.include = kwargs.get("_include")
        self.limit = kwargs.get("limit")
        self.offset = kwargs.get("offset", 0)
        self.region = kwargs.get("region")
        self.current_version = kwargs.get("currentVersion")
        self.current_label = kwargs.get("currentLabel")
        self.current_state = kwargs.get("currentState")
        self.device_vendor = kwargs.get("deviceVendor")
        self.device_role = kwargs.get("deviceRole")
        self.device_model = kwargs.get("deviceModel")
        self.target_version = kwargs.get("targetVersion")
        self.target_label = kwargs.get("targetLabel")
        self.target_state = kwargs.get("targetState")
        self.os_version_upgrade_id = kwargs.get("osVersionUpgradeId")
        self.os_version_device_region_id = kwargs.get("osVersionDeviceRegionId")
        self.sql_instance = MySQLDB(database_name=database_name)
        self.body = kwargs.get("body")
        self.length = len(kwargs)
        self.query_params = {  # Bugfix: DNE_35431
            "vendor": self.device_vendor,
            "region": self.region,
            "role": self.device_role,
            "model": self.device_model,
            "os_version_upgrade_id": self.os_version_upgrade_id,
            "os_version_device_region_id": self.os_version_device_region_id,
            "current_version": self.current_version,
            "current_label": self.current_label,
            "current_state": self.current_state,
            "target_version": self.target_version,
            "target_label": self.target_label,
            "target_state": self.target_state,
        }

    def get_upgrade_details(self) -> dict[str, str | list] | list:
        """
        Fetch upgrade and image details from mysql db via sqlalchemy orm transactions
        Returns:
        """
        try:
            logger.info("Entering get_upgrade_details module to fetch required table details")
            with self.sql_instance.transactional_session() as session:
                # os_version_device_region_id and os_version_upgrade_id should not combine with other parameters
                if self.length > 3 and (self.os_version_device_region_id or self.os_version_upgrade_id):
                    return {
                        "status": "FAILURE",
                        "errorCategory": "FAILED",
                        "errors": [
                            {
                                "code": "ERR-000-097-1011",
                                "message": "Validation Failed: Unsupported parameter combination",
                            }
                        ],
                    }
                source_table = self.source_query(session)
                target_table = self.target_query(session)
                if self.os_version_device_region_id:
                    return self.filter_os_version_id_details(session)
                if self.os_version_upgrade_id:
                    source_table = source_table.filter(PhaseUpgrade.id == self.os_version_upgrade_id)
                    if query_count(source_table) == 0 or query_count(target_table) == 0:
                        return {
                            "status": "FAILURE",
                            "errorCategory": "FAILED",
                            "errors": [
                                {
                                    "code": "ERR-000-097-1012",
                                    "message": "Validation Failed: Invalid osVersionUpgradeId ID",
                                }
                            ],
                        }
                    if source_table[0].sequence_no != 1:
                        return {
                            "status": "FAILURE",
                            "errorCategory": "FAILED",
                            "errors": [
                                {
                                    "code": "ERR-000-097-1013",
                                    "message": "Validation Failed: osVersionUpgradeId ID is not matching current os id",
                                }
                            ],
                        }
                    return self.get_source_target_os(session, source_table, target_table)
                if self.include and self.include in ("trafficDiversion", "serviceChecks"):  # bugfix: DNE-38029
                    include_dict = {
                        "trafficDiversion": self.filter_traffic_diversion_details,
                        "serviceChecks": self.get_service_check_details,
                    }
                    return include_dict[self.include](session)
                source_table, target_table = self.filter_parameter(source_table, target_table)
                if query_count(source_table) == 0 or query_count(target_table) == 0:
                    return self.unrecognized_parameter()
                if self.include not in ("brief", "imageDetail"):  # bugfix: DNE-38029
                    return self.get_source_target_os(session, source_table, target_table)
                target_table: Query = self.filter_target_table(target_table)
                if query_count(target_table) == 0:  # bugfix: DNE-36270
                    return self.unrecognized_parameter()
                # bugfix: DNE-38029
                final_resp = self.get_image_and_brief_details(session, target_table, source_table)
                total = len(final_resp)
                if total <= self.offset:  # bugfix: DNE-23415
                    return {
                        "status": "FAILURE",
                        "errorCategory": "FAILED",
                        "errors": [
                            {
                                "code": "ERR-000-097-1016",
                                "message": "Given offset is exceeding than total response",
                            }
                        ],
                    }
                start_index = self.offset
                end_index = start_index + self.limit if self.limit else total
                results = final_resp[start_index:end_index]
                limit = self.limit or total - start_index
                return {
                    "limit": limit,
                    "status": "SUCCESS",
                    "offset": start_index,
                    "total": total,
                    "resultSet": results,
                }
        except Exception as err:
            logger.exception(
                f"Exception while performing read upgrade details from os device region tables"
                f" : {err.__class__.__name__} {err.args[0]}"
            )
            error_message = (
                f"Database Operation Failed while performing read upgrade details : {db_errors[err.__class__]}"
                if err.__class__.__name__ in db_errors
                else f"Generic Exception occurred while performing read upgrade details"
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

    # bugfix: DNE-38029
    def get_image_and_brief_details(self, session: object, target_table: Query, source_table: Query) -> list:
        """
        method to parse the data based on inclue value imageDetail and brief
        Args:
            session (obj): sql session object
            target_table (query) : target table data
            source_table (query) : source_table data
        Returns:
            list : list of parsed data based on include value
        """
        if self.include == "imageDetail":
            return self.get_all_image_details(session)
        else:
            return self.get_source_target_brief(target_table, source_table)

    def filter_target_table(self, target_table: Query) -> Query:
        """
        Filter sqlDB by query parameter
        Args:
            target_table:(type: query)
        Returns:
            (Query): filtered target table details
        """
        logger.info("Entering filter_target_table module to filter query with params")
        if self.target_version:
            target_table = target_table.filter(OSVersion.os_version.like(f"%{self.target_version}%"))
        if self.target_label:
            target_table = target_table.filter(OSVersion.os_label.like(f"%{self.target_label}%"))
        if self.target_state:
            target_table = target_table.filter(OsState.validity_state.like(f"%{self.target_state}%"))
        logger.info("Exiting filter_target_table module after filter query with params")
        return target_table

    def filter_os_version_id_details(self, session: object) -> dict[str, str | list]:
        """
        Build response for os_version_device_region_id by query data
        Args:
            session (object): SQL transactional session object
        Returns:
            os version image details response
        """
        logger.info("Entering filter_os_version_id_details module to filter os version details by id")
        os_query = self.os_details_query(session)
        os_query = os_query.filter(OSVersionDeviceRegionPackage.id == self.os_version_device_region_id)
        if query_count(os_query) == 0:
            return {
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-000-097-1014",
                        "message": "Validation Failed: Invalid osVersionDeviceRegionId ID",
                    }
                ],
            }
        return self.build_image_response(session, os_query)[0]

    def get_all_image_details(self, session: object) -> dict[str, str | list]:
        """
        Build response for all image details from query data
        Args:
            session(object): SQL transactional session object
        Returns:
            Filtered image response
        """
        logger.info("Entering get_all_image_details module to get all os version details")
        os_query = self.os_details_query(session)
        os_query, _ = self.filter_parameter(os_query, None)
        if query_count(os_query) == 0:
            return self.unrecognized_parameter()
        return self.build_image_response(session, os_query)

    def build_image_response(self, session: object, os_query: Query) -> dict[str, str | list]:
        """
        Build response for image details from query data
        Args:
            session (object): SQL transactional session object
            os_query (Query): image details query data

        Returns:
            dict: Response of os version image details
        """
        logger.info("Entering build_image_response module to bulid image details")
        os_response: dict = {}
        image_details: list = []
        final_response: list = []
        old_img_id: str = ""
        for count, os_data in enumerate(os_query):
            new_img_id = os_data.OsVersionDeviceRegionId
            if old_img_id and new_img_id != old_img_id:
                final_response.append(os_response)
            # Bugfix: DNE-37963
            image_type: str = self.file_query(session, os_data.file_type) if os_data.file_type else os_data.file_type
            image_file = {
                "imageType": image_type,
                "fileName": os_data.url,
                "md5Value": os_data.md5,
                "imageSize": os_data.file_size,  # Bugfix: DNE-28299
            }
            if new_img_id == old_img_id:
                image_details = self.update_image_details(image_file, image_type, image_details)
                os_response["osDetails"] |= {"imageFiles": image_details}
            else:
                image_details = []
                os_response = {}
                image_id = os_data.image_id
                os_response["deviceVendor"] = os_data.vendor
                os_response["osVersionDeviceRegionId"] = os_data.OsVersionDeviceRegionId
                os_response["deviceModel"] = os_data.model
                os_response["region"] = os_data.region
                os_response["osVersion"] = os_data.os_version
                os_response["osLabel"] = os_data.os_label
                os_response["osStatus"] = os_data.validity_state
                os_response["comments"] = os_data.comments
                os_response["status"] = "SUCCESS"
                # Bugfix: DNE-37963
                image_details = self.update_image_details(image_file, image_type, image_details)
                os_response["osDetails"] = {"imageFiles": image_details}
                package_query = self.package_query(session, image_id)
                package_dict = {"XR": [], "SYSADMIN-FIX": [], "SYSADMIN-MOD": []}
                for package in package_query:
                    if package.package_type_value in package_dict:
                        package_dict[package.package_type_value].append(package.package_name)
                package_list: tuple = (
                    {"type": "XR", "packages": package_dict["XR"]},
                    {"type": "SYSADMIN-FIX", "packages": package_dict["SYSADMIN-FIX"]},
                    {"type": "SYSADMIN-MOD", "packages": package_dict["SYSADMIN-MOD"]},
                )
                os_response["osDetails"] |= {"packageDetails": package_list}
            old_img_id = new_img_id
            if query_count(os_query) - 1 == count:
                final_response.append(os_response)
        logger.info("Exiting build_image_response module after build image details")
        return final_response

    def update_image_details(self, image_file: dict, image_type: str, image_details: list) -> list[dict]:
        """
        To update image details list when image files are present
        Args:
            image_file (dicr): image file details to update
            image_type (str): image type (iso, tar)
            image_details (list): to append image details
        Returns:
            image_details (list): Updated image details
        """
        if image_type:
            image_details.append(image_file)
        return image_details

    def filter_traffic_diversion_details(self, session: object) -> dict[str, str]:
        """
        Build response for traffic diversion by querying it by _include=trafficDiversion
        :return:
        """
        try:
            logger.info("Entering filter_traffic_diversion_details module to filter os version details by id")
            traffic_query = self.traffic_diversion_query(session)
            traffic_query, _ = self.filter_parameter(traffic_query, None)
            if query_count(traffic_query) == 0:
                return self.unrecognized_parameter()
            final_resp = []
            diversion_resp = [
                {
                    "deviceVendor": traffic_data.vendor,
                    "deviceModel": traffic_data.model,
                    # for ASR9K device, all protocol will support ALL region
                    "region": self.region if self.region and traffic_data.region == "ALL" else traffic_data.region,
                    "deviceRole": traffic_data.role,
                    "sequence": traffic_data.sequence,
                    "step": traffic_data.protocol,
                    "exclusion": traffic_data.exclusion,
                    "waitTimeSec": traffic_data.wait_time,
                    "trafficType": traffic_data.traffic_type,
                }
                for traffic_data in traffic_query
            ]
            diversion_resp = sorted(diversion_resp, key=self.key_func)
            for key, value in groupby(diversion_resp, self.key_func):
                traffic_dict = {"deviceModel": key[0], "deviceRole": key[1], "deviceVendor": key[2], "region": key[3]}
                group_by = list(value)
                traffic_dict["trafficOnStep"] = [
                    {
                        "sequence": grp_data["sequence"],
                        "step": grp_data["step"],
                        "exclusion": grp_data["exclusion"],
                        "waitTimeSec": grp_data["waitTimeSec"],
                    }
                    for grp_data in group_by
                    if grp_data["trafficType"] == "On"
                ]
                traffic_dict["trafficOffStep"] = [
                    {
                        "sequence": grp_data["sequence"],
                        "step": grp_data["step"],
                        "exclusion": grp_data["exclusion"],
                        "waitTimeSec": grp_data["waitTimeSec"],
                    }
                    for grp_data in group_by
                    if grp_data["trafficType"] == "Off"
                ]
                traffic_dict["status"] = "SUCCESS"
                final_resp.append(traffic_dict)
            return final_resp
        except (TypeError, AttributeError, KeyError, IndexError) as err:
            logger.exception(
                f"Exception occurred while querying data from traffic diversion table"
                f" : {err.__class__.__name__} {err.args[0]}"
            )
            return {
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-000-097-0500",
                        "message": f"Exception occurred while performing filter_traffic_diversion_details"
                        f" from traffic protocol table : {err.__class__.__name__}",
                    }
                ],
            }
        except Exception as err:
            logger.exception(
                f"Exception Occurred. Failed while querying data from traffic diversion table "
                f"due to error {err.__class__.__name__} {err.args[0]}"
            )
            error_message = (
                f"Database Operation Failed while performing filter_traffic_diversion_details "
                f"from traffic protocol table : {db_errors[err.__class__]}"
                if err.__class__.__name__ in db_errors
                else f"Generic Exception occurred while performing filter_traffic_diversion_details "
                f"from traffic protocol table : {err.__class__.__name__}"
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

    def key_func(self, k: dict) -> list:
        return [k["deviceModel"], k["deviceRole"], k["deviceVendor"], k["region"]]

    def package_query(self, session, image_id: str):
        """
        Query package table to get detail
        :param image_id:(type: int)
        :param session:
        :return:
        """
        logger.info("Entering package_query module to query package details by image id")
        return (
            session.query(
                Package.package_type.label("package_type_id"),
                Package.package_name,
                PackageType.package_type.label("package_type_value"),
            ).join(PackageType, Package.package_type == PackageType.id)
        ).filter(Package.image_id == image_id)

    def file_query(self, session: object, image_type: str) -> str:  # Bugfix: DNE-37963
        """
        Query file type table to get file detail
        :param image_type:(type: int)
        :param session:
        :return:
        """
        logger.info("Entering file_query module to query file details by image id")
        return (session.query(FileType.id, FileType.file_type).filter(FileType.id == image_type))[0].file_type

    def filter_parameter(self, source_table, target_table) -> Tuple[dict, dict]:
        """
        Filter sqlDB by query parameter
        :param source_table:(type: query)
        :param target_table:(type: query)
        :return:
        """
        logger.info("Entering filter_parameter module to filter query with params")
        if self.device_vendor:
            source_table = source_table.filter(DeviceMaster.vendor.like(f"%{self.device_vendor}%"))
            target_table = (
                target_table.filter(DeviceMaster.vendor.like(f"%{self.device_vendor}%")) if target_table else None
            )
        if self.device_model:
            source_table = source_table.filter(DeviceMaster.model.like(f"%{self.device_model}%"))
            target_table = (
                target_table.filter(DeviceMaster.model.like(f"%{self.device_model}%")) if target_table else None
            )
        if self.region:
            local_device_model = self.device_model.upper() if self.device_model else self.device_model
            local_region = UPDATE_REGION_BY_MODEL.get(local_device_model, self.region)
            source_table = source_table.filter(RegionMaster.region.like(f"%{local_region}%"))
            target_table = target_table.filter(RegionMaster.region.like(f"%{local_region}%")) if target_table else None
        if self.device_role:
            source_table = source_table.filter(DeviceRole.role == self.device_role)  # bugfix: DNE-22783
        if self.current_version:
            source_table = source_table.filter(OSVersion.os_version.like(f"%{self.current_version}%"))
        if self.current_label:
            source_table = source_table.filter(OSVersion.os_label.like(f"%{self.current_label}%"))
        if self.current_state:
            source_table = source_table.filter(OsState.validity_state.like(f"%{self.current_state}%"))
        logger.info("Exiting filter_parameter module after filter query with params")
        return source_table, target_table

    def source_query(self, session: object) -> Query | dict[str, str]:
        """
        Query source details
        :param session:
        :return:
        """
        try:
            logger.info("Entering source_query module to query source related image details")
            return (  # Bugfix: DNE-37963
                session.query(
                    SequenceUpgrade.id.label("sequence_id"),
                    SequenceUpgrade.phase_upgrade_id,
                    SequenceUpgrade.steps,
                    SequenceUpgrade.sequence_no,
                    SequenceUpgrade.next_sequence_id,
                    SequenceUpgrade.comments,
                    SequenceUpgrade.modifiedOn,
                    SequenceUpgrade.createdOn,
                    SequenceUpgrade.createdBy,
                    SequenceUpgrade.modifiedBy,
                    PhaseUpgrade.id.label("osVersionUpgradeId"),
                    PhaseUpgrade.source_osv_dr_id.label("source_id"),
                    PhaseUpgrade.target_osv_dr_id.label("target_id"),
                    PhaseUpgrade.custom_config_id,
                    OSVersionDeviceRegionPackage.id.label("sourceOsVersionDeviceRegionId"),
                    OSVersionDeviceRegionPackage.device_region_id,
                    OSVersionDeviceRegionPackage.os_version_id,
                    OSVersionDeviceRegionPackage.os_validity_id,
                    DeviceRegion.id.label("parent_device_region_id"),
                    OSVersion.id.label("parent_os_version_id"),
                    OSVersion.os,
                    OSVersion.os_label.label("source_label"),
                    OSVersion.os_version.label("source_version"),
                    OsState.validity_state.label("source_state"),
                    DeviceMaster.vendor,
                    DeviceMaster.model,
                    RegionMaster.region,
                )
                .join(PhaseUpgrade, SequenceUpgrade.phase_upgrade_id == PhaseUpgrade.id)
                .join(OSVersionDeviceRegionPackage, PhaseUpgrade.source_osv_dr_id == OSVersionDeviceRegionPackage.id)
                .join(DeviceRegion, OSVersionDeviceRegionPackage.device_region_id == DeviceRegion.id)
                .join(OSVersion, OSVersionDeviceRegionPackage.os_version_id == OSVersion.id)
                .join(OsState, OSVersionDeviceRegionPackage.os_validity_id == OsState.id)
                .join(DeviceMaster, DeviceRegion.device_id == DeviceMaster.id)
                .join(RegionMaster, DeviceRegion.region_id == RegionMaster.id)
            )
        except (TypeError, AttributeError, KeyError, IndexError) as err:
            logger.exception(
                f"Exception occurred while querying source data from table" f" : {err.__class__.__name__} {err.args[0]}"
            )
            return {
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-000-097-0500",
                        "message": f"Exception occurred while performing source query"
                        f" from sequence and phase tables : {err.__class__.__name__}",
                    }
                ],
            }
        except Exception as err:
            logger.exception(
                f"Exception Occurred. Failed while querying source data from table "
                f"due to error {err.__class__.__name__} {err.args[0]}"
            )
            error_message = (
                f"Database Operation Failed while performing source query"
                f" from sequence and phase tables : {db_errors[err.__class__]}"
                if err.__class__.__name__ in db_errors
                else f"Generic Exception occurred while performing source query "
                f"from sequence and phase tables : {err.__class__.__name__}"
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

    def target_query(self, session: object) -> Query | dict[str, str]:
        """
        Query target details
        :param session:
        :return:
        """
        try:
            logger.info("Entering target_query module to query target related image details")
            return (  # Bugfix: DNE-37963
                session.query(
                    SequenceUpgrade.id.label("sequence_id"),
                    SequenceUpgrade.phase_upgrade_id,
                    SequenceUpgrade.steps,
                    SequenceUpgrade.sequence_no,
                    SequenceUpgrade.next_sequence_id,
                    SequenceUpgrade.comments,
                    SequenceUpgrade.modifiedOn,
                    SequenceUpgrade.createdOn,
                    SequenceUpgrade.createdBy,
                    SequenceUpgrade.modifiedBy,
                    PhaseUpgrade.id.label("osVersionUpgradeId"),
                    PhaseUpgrade.source_osv_dr_id.label("source_id"),
                    PhaseUpgrade.target_osv_dr_id.label("target_id"),
                    PhaseUpgrade.custom_config_id,
                    OSVersionDeviceRegionPackage.id.label("targetOsVersionDeviceRegionId"),
                    OSVersionDeviceRegionPackage.device_region_id,
                    OSVersionDeviceRegionPackage.os_version_id,
                    OSVersionDeviceRegionPackage.os_validity_id,
                    DeviceRegion.id.label("parent_device_region_id"),
                    OSVersion.id.label("parent_os_version_id"),
                    OSVersion.os,
                    OSVersion.os_label.label("target_label"),
                    OSVersion.os_version.label("target_version"),
                    OsState.validity_state.label("target_state"),
                    DeviceMaster.vendor,
                    DeviceMaster.model,
                    RegionMaster.region,
                )
                .join(PhaseUpgrade, SequenceUpgrade.phase_upgrade_id == PhaseUpgrade.id)
                .join(OSVersionDeviceRegionPackage, PhaseUpgrade.target_osv_dr_id == OSVersionDeviceRegionPackage.id)
                .join(DeviceRegion, OSVersionDeviceRegionPackage.device_region_id == DeviceRegion.id)
                .join(OSVersion, OSVersionDeviceRegionPackage.os_version_id == OSVersion.id)
                .join(OsState, OSVersionDeviceRegionPackage.os_validity_id == OsState.id)
                .join(DeviceMaster, DeviceRegion.device_id == DeviceMaster.id)
                .join(RegionMaster, DeviceRegion.region_id == RegionMaster.id)
            )
        except (TypeError, AttributeError, KeyError, IndexError) as err:
            logger.exception(
                f"Exception occurred while querying target data from tables"
                f" : {err.__class__.__name__} {err.args[0]}"
            )
            return {
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-000-097-0500",
                        "message": f"Exception occurred while performing target query"
                        f" from sequence and phase tables : {err.__class__.__name__}",
                    }
                ],
            }
        except Exception as err:
            logger.exception(
                f"Exception Occurred. Failed while querying target data from tables "
                f"due to error {err.__class__.__name__} {err.args[0]}"
            )
            error_message = (
                f"Database Operation Failed while performing target query"
                f" from sequence and phase tables : {db_errors[err.__class__]}"
                if err.__class__.__name__ in db_errors
                else f"Generic Exception occurred while performing target query "
                f"from sequence and phase tables : {err.__class__.__name__}"
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

    def os_details_query(self, session: object) -> Query | dict[str, str]:
        """
        Query source details
        :param session:
        :return:
        """
        try:
            logger.info("Entering os_details_query module to query os related details")
            return (  # Bugfix: DNE-37963
                session.query(
                    OSVersionDeviceRegionPackage.id.label("OsVersionDeviceRegionId"),
                    OSVersionDeviceRegionPackage.modifiedOn,
                    OSVersionDeviceRegionPackage.createdOn,
                    OSVersionDeviceRegionPackage.createdBy,
                    OSVersionDeviceRegionPackage.modifiedBy,
                    OSVersionDeviceRegionPackage.device_region_id,
                    OSVersionDeviceRegionPackage.os_version_id,
                    OSVersionDeviceRegionPackage.os_validity_id,
                    DeviceRegion.id.label("parent_device_region_id"),
                    OSVersion.id.label("parent_os_version_id"),
                    OSVersion.os,
                    OSVersion.os_label,
                    OSVersion.os_version,
                    OsState.validity_state,
                    Image.id.label("image_id"),
                    Image.url,
                    Image.md5,
                    Image.file_size,
                    Image.file_type,
                    Image.comments,
                    DeviceMaster.vendor,
                    DeviceMaster.model,
                    RegionMaster.region,
                )
                .join(DeviceRegion, OSVersionDeviceRegionPackage.device_region_id == DeviceRegion.id)
                .join(OSVersion, OSVersionDeviceRegionPackage.os_version_id == OSVersion.id)
                .join(OsState, OSVersionDeviceRegionPackage.os_validity_id == OsState.id)
                .join(Image, OSVersionDeviceRegionPackage.id == Image.os_device_region_id)
                .join(DeviceMaster, DeviceRegion.device_id == DeviceMaster.id)
                .join(RegionMaster, DeviceRegion.region_id == RegionMaster.id)
            )
        except (TypeError, AttributeError, KeyError, IndexError) as err:
            logger.exception(
                f"Exception occurred while performing os details query from os device region tables"
                f" : {err.__class__.__name__} {err.args[0]}"
            )
            return {
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-000-097-0500",
                        "message": f"Exception occurred while performing os details query"
                        f" from os device region tables : {err.__class__.__name__}",
                    }
                ],
            }
        except Exception as err:
            logger.exception(
                f"Exception Occurred. Failed while querying os details from tables "
                f"due to error {err.__class__.__name__} {err.args[0]}"
            )
            error_message = (
                f"Database Operation Failed while performing os details query "
                f"from os device region tables : {db_errors[err.__class__]}"
                if err.__class__.__name__ in db_errors
                else f"Generic Exception occurred while performing os details query "
                f"from os device region tables : {err.__class__.__name__}"
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

    def traffic_diversion_query(self, session: object) -> Query | dict[str, str]:
        """
        Query traffic diversion details
        :param session:
        :return:
        """
        try:
            logger.info("Entering traffic_diversion_query module to query traffic diversion details")
            return (
                session.query(
                    TrafficDiversion.id.label("TrafficDiversionId"),
                    TrafficDiversion.protocol_step,
                    TrafficDiversion.device_region_id,
                    TrafficDiversion.device_role_id,
                    TrafficDiversion.traffic_type,
                    TrafficDiversion.exclusion,
                    TrafficDiversion.sequence,
                    TrafficDiversion.wait_time,
                    TrafficProtocol.protocol,
                    TrafficProtocol.id.label("protocol_id"),
                    DeviceRegion.id.label("parent_device_region_id"),
                    DeviceRole.id.label("parent_device_role_id"),
                    DeviceRole.role,
                    DeviceMaster.vendor,
                    DeviceMaster.model,
                    RegionMaster.region,
                )
                .join(DeviceRegion, TrafficDiversion.device_region_id == DeviceRegion.id)
                .join(DeviceRole, TrafficDiversion.device_role_id == DeviceRole.id)
                .join(TrafficProtocol, TrafficDiversion.protocol_step == TrafficProtocol.id)
                .join(DeviceMaster, DeviceRegion.device_id == DeviceMaster.id)
                .join(RegionMaster, DeviceRegion.region_id == RegionMaster.id)
            )
        except (TypeError, AttributeError, KeyError, IndexError) as err:
            logger.exception(
                f"Exception occurred while querying traffic diversion data from traffic and protocol tables"
                f" : {err.__class__.__name__} {err.args[0]}"
            )
            return {
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-000-097-0500",
                        "message": f"Exception occurred while performing traffic diversion query"
                        f" from traffic and protocol tables : {err.__class__.__name__}",
                    }
                ],
            }
        except Exception as err:
            logger.exception(
                f"Exception Occurred. Failed while querying traffic diversion data from traffic and protocol tables"
                f" due to error {err.__class__.__name__} {err.args[0]}"
            )
            error_message = (
                f"Database Operation Failed while performing traffic diversion query "
                f"from traffic and protocol tables : {db_errors[err.__class__]}"
                if err.__class__.__name__ in db_errors
                else f"Generic Exception occurred while performing traffic diversion query "
                f"from traffic and protocol tables : {err.__class__.__name__}"
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

    def get_source_target_os(self, session: object, source_table: dict, target_table: dict) -> list:
        """
        get source and target details with os version
        :param source_table:(type: query)
        :param target_table:(type: query)
        :return:
        """
        logger.info("Entering get_source_target_os module to get source and target related os details")
        response_records = []
        for sour_data in source_table:
            response_record = {}
            if sour_data.sequence_no == 1:
                response_record = {
                    "osVersionDeviceRegionId": sour_data.sourceOsVersionDeviceRegionId,
                    "deviceVendor": sour_data.vendor,
                    "deviceModel": sour_data.model,
                    "region": sour_data.region,
                    "currentOsVersion": sour_data.source_version,
                    "currentOsLabel": sour_data.source_label,
                    "createdBy": sour_data.createdBy,
                    "createdOn": sour_data.createdOn,
                    "modifiedBy": sour_data.modifiedBy,
                    "modifiedOn": sour_data.modifiedOn,
                    "status": "SUCCESS",
                }
                if sour_data.next_sequence_id is not None:
                    # check for intermediate and target steps
                    response_record: dict[str, str] = self.get_intermediate_target_os(
                        session, sour_data, target_table, response_record
                    )

                else:
                    target = list(filter(lambda x: x.phase_upgrade_id == sour_data.phase_upgrade_id, target_table))
                    if self.target_version and self.target_version != target[0].target_version:
                        continue
                    if self.target_label and self.target_label != target[0].target_label:
                        continue
                    if self.target_state and self.target_state != target[0].target_state:
                        continue
                    response_record["upgradeDetails"] = self.insert_upgrade_details_record(session, target)
            if response_record and response_record.get("upgradeDetails", {}).get("targetOs"):
                response_records.append(response_record)
        if (
            (self.target_version or self.target_label or self.target_state)
            or (self.current_version or self.current_label or self.current_state)
        ) and not response_records:
            return self.unrecognized_parameter()
        logger.info("Exiting get_source_target_os module after fetch os details")
        return response_records

    def insert_upgrade_details_record(self, session: object, target: list[Query]) -> dict[str, str] | str:
        """
        insert upgradeDetails in the response record
        Args:
            session (object): db session object
            target (list[Query]): Filtered upgrade query object

        Returns:
            dict[str, str] | str: upgrade details response dict
        """
        logger.info("Entering get_ module to insert upgradeDetails in the response record")
        return (
            {
                "upgradeSteps": target[0].steps,
                "targetOs": {
                    "osVersionDeviceRegionId": target[0].targetOsVersionDeviceRegionId,
                    "osVersion": target[0].target_version,
                    "osLabel": target[0].target_label,
                    "sequence": target[0].sequence_no,
                    "customConfig": [
                        {
                            "beforeUpgrade": next_config.pre_target_upgrade_conf,
                            "afterUpgrade": next_config.post_target_upgrade_conf,
                            "isRollbackRequired": next_config.is_rollback_required,
                            "beforeRollback": next_config.before_rollback,
                            "afterRollback": next_config.after_rollback,
                            "configMode": next_config.config_mode,
                            "deviceRole": [
                                session.query(DeviceRole).get({"id": getattr(next_config, f"role_id{i}")}).role
                                for i in range(1, 39)
                                if getattr(next_config, f"role_id{i}")
                            ],
                        }
                        for next_config in self.get_custom_config(session, target[0].custom_config_id)
                    ]
                    if target[0].custom_config_id
                    else [],
                },
                "comments": target[0].comments,
            }
            if target
            else ""
        )

    def get_custom_config(self, session: object, next_config_id: int) -> Iterator[Query]:
        """Generator to fetch all the custom configs

        Args:
            session (object): db session object
            next_config_id (int): config id to be fetched

        Yields:
            Iterator[Query]: custom config details
        """
        next_config: Query = (
            session.query(
                CustomConfigList.id.label("custom_config_id"),
                CustomConfigList.pre_target_upgrade_conf,
                CustomConfigList.post_target_upgrade_conf,
                CustomConfigList.is_rollback_required,
                CustomConfigList.before_rollback,
                CustomConfigList.after_rollback,
                CustomConfigList.config_mode,
                CustomConfigList.next_config_id,
                RoleList.id.label("role_list_id"),
                RoleList.role_id1,
                RoleList.role_id2,
                RoleList.role_id3,
                RoleList.role_id4,
                RoleList.role_id5,
                RoleList.role_id6,
                RoleList.role_id7,
                RoleList.role_id8,
                RoleList.role_id9,
                RoleList.role_id10,
                RoleList.role_id11,
                RoleList.role_id12,
                RoleList.role_id13,
                RoleList.role_id14,
                RoleList.role_id15,
                RoleList.role_id16,
                RoleList.role_id17,
                RoleList.role_id18,
                RoleList.role_id19,
                RoleList.role_id20,
                RoleList.role_id21,
                RoleList.role_id22,
                RoleList.role_id23,
                RoleList.role_id24,
                RoleList.role_id25,
                RoleList.role_id26,
                RoleList.role_id27,
                RoleList.role_id28,
                RoleList.role_id29,
                RoleList.role_id30,
                RoleList.role_id31,
                RoleList.role_id32,
                RoleList.role_id33,
                RoleList.role_id34,
                RoleList.role_id35,
                RoleList.role_id36,
                RoleList.role_id37,
                RoleList.role_id38,
            )
            .join(RoleList, CustomConfigList.role_list_id == RoleList.id)
            .filter(CustomConfigList.id == next_config_id)
        )
        yield next_config[0]
        if next_config[0].next_config_id and isinstance(next_config[0].next_config_id, int):
            yield from self.get_custom_config(session, next_config[0].next_config_id)

    def unrecognized_parameter(self) -> dict[str, str]:
        """
        unrecognized parameter error details
        :return:
        """
        logger.info("Entering unrecognized_parameter module to form error details for not found")
        err_msg: str = self.build_error_message()  # Bugfix: DNE_35431
        message: str = err_msg or "No data found for software upgrade"
        return {
            "status": "FAILURE",
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-1010",
                    "message": f"Validation Failed: {message}",
                }
            ],
        }

    def build_error_message(self) -> str:
        """
        Build error message for unrecognized parameter
        """
        logger.info("Build error message for unrecognized parameter")
        # Bugfix: DNE-35431
        err_msg: str = ", ".join(f"{key}: {value}" for key, value in self.query_params.items() if value)
        return f"For the device {err_msg} data is not found" if err_msg else ""

    def get_intermediate_target_os(
        self, session: object, source: Query, target_records: Query, res_record: dict
    ) -> dict[str, str]:
        """
        get intermediate and target details with os version
        Args:
            session (object): db session object
            source (Query): current version details query
            target_records (Query): target version details query
            res_record (dict): response data to be returned

        Returns:
            dict[str, str]: intermedial details response
        """
        logger.info("Entering get_intermediate_target_os module to fetch intermediate and target os details")
        # find target record
        intermediate_data = []
        for target_record in target_records:
            if source.sequence_id == target_record.sequence_id:
                if target_record.next_sequence_id is None:
                    if self.target_version and self.target_version != target_record.target_version:
                        continue
                    if self.target_label and self.target_label != target_record.target_label:
                        continue
                    if not self.target_state or self.target_state == target_record.target_state:
                        res_record["upgradeDetails"] = {
                            "upgradeSteps": target_record.steps,
                            "targetOs": self.format_intermediate_response(session, target_record),
                            "comments": target_record.comments,
                        }
                else:
                    inter_resp: dict[str, str | list] = self.format_intermediate_response(session, target_record)
                    intermediate_data.append(inter_resp)
                    # change the source to next sequence id
                    record: list[Query] = list(
                        filter(lambda x: x.sequence_id == target_record.next_sequence_id, target_records)
                    )
                    source = record[0] if record else source
        if intermediate_data:
            res_record.get("upgradeDetails", {})["intermediateSteps"] = intermediate_data
        logger.info("Exiting get_intermediate_target_os module after fetch intermediate and target os details")
        return res_record

    def format_intermediate_response(self, session: object, record: object) -> dict[str, str | list]:
        """formate the response data for intermediate steps

        Args:
            session (object): db session object
            record (object): db record object

        Returns:
            dict[str, str | list]: formatted response
        """
        return {
            "osVersionDeviceRegionId": record.targetOsVersionDeviceRegionId,
            "osVersion": record.target_version,
            "osLabel": record.target_label,
            "sequence": record.sequence_no,
            "customConfig": [
                {
                    "beforeUpgrade": next_config.pre_target_upgrade_conf,
                    "afterUpgrade": next_config.post_target_upgrade_conf,
                    "isRollbackRequired": next_config.is_rollback_required,
                    "beforeRollback": next_config.before_rollback,
                    "afterRollback": next_config.after_rollback,
                    "configMode": next_config.config_mode,
                    "deviceRole": [
                        session.query(DeviceRole).get({"id": getattr(next_config, f"role_id{i}")}).role
                        for i in range(1, 39)
                        if getattr(next_config, f"role_id{i}")
                    ],
                }
                for next_config in self.get_custom_config(session, record.custom_config_id)
            ]
            if record.custom_config_id
            else [],
        }

    def get_source_target_brief(self, target_table: dict, source_table: dict) -> Dict[str, str]:
        """
        get source and target details for include=brief
        :param target_table:(type: query)
        :param source_table:(type: query)
        :return:
        """
        logger.info("Entering get_source_target_brief module to fetch source and target details in brief")
        final_resp = []
        for tar_data in target_table:
            for sour_data in source_table:
                if sour_data.osVersionUpgradeId == tar_data.osVersionUpgradeId:
                    resp = {
                        "osVersionUpgradeId": sour_data.osVersionUpgradeId,
                        "deviceVendor": sour_data.vendor,
                        "deviceModel": sour_data.model,
                        "region": sour_data.region,
                        "currentVersion": sour_data.source_version,
                        "currentLabel": sour_data.source_label,
                        "currentState": sour_data.source_state,
                        "targetVersion": tar_data.target_version,
                        "targetLabel": tar_data.target_label,
                        "targetState": tar_data.target_state,
                    }
                    final_resp.append(resp)
        logger.info("Exiting get_source_target_brief module after fetch source and target details in brief")
        return final_resp

    def get_service_check_details(self, session: object) -> list | dict[str, str | list]:
        """
        Build response for all image details from query data
        Args:
            session(object): SQL transactional session object
        Returns:
            list | dict : service check response of image details
        """
        logger.info("Entering get_all_image_details module to get all os version details")
        service_query = self.service_check_query(session)
        service_query, _ = self.filter_parameter(service_query, None)
        if query_count(service_query) == 0:
            return self.unrecognized_parameter()
        return [
            {
                "deviceVendor": service_data.vendor,
                "deviceModel": service_data.model,
                "region": service_data.region,
                "deviceRole": service_data.role,
                "isServiceCheckRequired": service_data.is_service_required,
            }
            for service_data in service_query
        ]

    def service_check_query(self, session: object) -> tuple | dict[str, str]:
        """
        Query service check details
        Args:
            session(object): SQL transactional session object
        Returns:
            tuple | dict : sql query data of service check
        """
        try:
            logger.info("Entering service_check_query module to query service check details")
            return (
                session.query(
                    ServiceCheck.id.label("ServiceCheckId"),
                    ServiceCheck.device_region_id,
                    ServiceCheck.device_role_id,
                    ServiceCheck.is_service_required,
                    DeviceRegion.id.label("parent_device_region_id"),
                    DeviceRole.id.label("parent_device_role_id"),
                    DeviceRole.role,
                    DeviceMaster.vendor,
                    DeviceMaster.model,
                    RegionMaster.region,
                )
                .join(DeviceRegion, ServiceCheck.device_region_id == DeviceRegion.id)
                .join(DeviceRole, ServiceCheck.device_role_id == DeviceRole.id)
                .join(DeviceMaster, DeviceRegion.device_id == DeviceMaster.id)
                .join(RegionMaster, DeviceRegion.region_id == RegionMaster.id)
            )
        except (TypeError, AttributeError, KeyError, IndexError) as err:
            logger.exception(
                f"Exception occurred while querying service check data from service_check table"
                f" : {err.__class__.__name__} {err}"
            )
            return {
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-000-097-0500",
                        "message": f"Exception occurred while performing service check query"
                        f" from service_check table : {err.__class__.__name__}",
                    }
                ],
            }
        except Exception as err:
            logger.exception(
                f"Exception Occurred. Failed while querying service check data from service_check table"
                f" due to error {err.__class__.__name__} {err}"
            )
            error_message = (
                f"Database Operation Failed while performing service check query "
                f"from service_check table : {db_errors[err.__class__]}"
                if err.__class__.__name__ in db_errors
                else f"Generic Exception occurred while performing service check query "
                f"from service_check table : {err.__class__.__name__}"
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
