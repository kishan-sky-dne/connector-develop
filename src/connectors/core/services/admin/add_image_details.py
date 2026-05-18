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
    DeviceMaster,
    DeviceRegion,
    FileType,
    Image,
    OsState,
    OSVersion,
    OSVersionDeviceRegionPackage,
    Package,
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


class AddImageDetails:
    def __init__(self, body):
        self.body = body
        self.sql_instance = MySQLDB(database_name=database_name)
        self.default_user = None

    def add_device_image(self) -> dict[str, str | list]:  # sourcery skip
        """
        Add images to mysql db via sqlalchemy orm transactions
        Args: self
        Returns: device_os_version_identifier
        """
        try:
            logger.debug("Entering add_image_details module to insert into image and package tables")
            status = []
            errors = []
            success_dict = {"success": []}
            failure_dict = {"failure": []}
            add_device_response = {"metadata": {}}
            self.default_user = "Admin"
            with self.sql_instance.transactional_session() as session:
                for data in self.body:
                    image_id = []
                    vendor = data["deviceVendor"]
                    model = data["deviceModel"]
                    region = data["region"]
                    response_dict = {
                        "deviceVendor": vendor,
                        "deviceModel": model,
                        "region": region,
                        "osVersion": data["osVersion"],
                        "osLabel": data["osLabel"],
                        "osStatus": data["osStatus"],
                    }
                    error_len = len(errors)
                    device_version_details, os_status_id, image_file, package_list = self.validation_check(
                        session,
                        data,
                        add_device_response,
                        failure_dict,
                        status=status,
                        errors=errors,
                        response_dict=response_dict,
                    )

                    if len(errors) > error_len:
                        continue
                    # Inserting into OS version table
                    os_version_identifier = self.insert_os_version(
                        session,
                        os="IOSXR",
                        os_version=data["osVersion"],
                        os_label=data["osLabel"],
                        createdBy=self.default_user,
                        modifiedBy=self.default_user,
                    )

                    # Inserting os version device region package details
                    os_version_device_region_id = self.insert_os_version_device_region(
                        session,
                        device_region_id=device_version_details[0].deviceRegionID,
                        os_version_id=os_version_identifier,
                        os_validity_id=os_status_id,
                        createdBy=self.default_user,
                        modifiedBy=self.default_user,
                    )

                    # Inserting image details
                    for image_detail in image_file:
                        image_file_id = self.insert_image_file(
                            session,
                            url=image_detail["url"],
                            md5=image_detail["md5"],
                            file_type=image_detail["file_type"],
                            file_size=image_detail["file_size"],
                            comments=data.get("comments", ""),
                            os_version_id=os_version_identifier,
                            os_device_region_id=os_version_device_region_id,
                            createdBy=self.default_user,
                            modifiedBy=self.default_user,
                        )
                        image_id.append(image_file_id)

                    # Inserting package details
                    for package in package_list:
                        for package_name in package["package_name"]:
                            self.insert_package_details(
                                session,
                                package_name=package_name,
                                package_type=package["package_type"],
                                image_id=image_id[0],
                                createdBy=self.default_user,
                                modifiedBy=self.default_user,
                            )

                    if os_version_device_region_id:
                        status.append(True)
                        response = {"image": response_dict, "osVersionDeviceRegionId": os_version_device_region_id}
                        success_dict["success"].append(response)
                        add_device_response["metadata"].update(success_dict)
                    else:
                        status.append(False)
                        failure_dict["failure"].append(response_dict)
                        add_device_response["metadata"].update(failure_dict)
                        ref_value = len(add_device_response["metadata"]["failure"]) - 1
                        self.error_details(
                            errors,
                            code="0500",
                            message="Operation Failed : osVersionDeviceRegionId not found",
                            ref_value=ref_value,
                        )
                        continue
            if errors:
                add_device_response["errorCategory"] = "FAILED"
                add_device_response["errors"] = errors
            add_device_response["status"] = (
                "SUCCESS" if all(status) else "PARTIAL-SUCCESS" if any(status) else "FAILURE"
            )
            return add_device_response
        except (TypeError, AttributeError, KeyError, IndexError) as err:
            logger.exception(
                f"Exception occurred for add_device_image module to add image and package tables"
                f" : {err.__class__.__name__} {err.args[0]}"
            )
            return {
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-000-097-0500",
                        "message": f"Exception occurred while performing add image "
                        f"details to image and package tables : {err.__class__.__name__}",
                    }
                ],
            }
        except Exception as err:
            logger.exception(
                f"Exception occurred for image_upgrade_details module to add image and package tables"
                f" : {err.__class__.__name__} {err.args[0]}"
            )
            error_message = (
                f"Database Operation Failed while performing add image details"
                f" to image and package tables : {db_errors[err.__class__.__name__]}"
                if err.__class__.__name__ in db_errors
                else f"Generic Exception occurred while performing add image"
                f" details to image and package tables : {err.__class__.__name__}"
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

    def validation_check(
        self, session: object, data: dict, add_device_response: dict, failure_dict: dict, **kwargs: dict
    ) -> tuple[str, str, list, list]:  # sourcery skip
        """
        perform Validation check for request
        :param session:
        :param failure_dict:(type:dict)
        :param data:(type:dict)
        :param add_device_response:(type:dict)
        :return:
        """
        logger.debug("Entering validation_check module to validate the request data")
        error_resp = "", "", [], []
        response_dict = kwargs["response_dict"]
        # Querying Device Region Os Version ID to find duplicate
        os_version_id_details = self.query_os_version_details(
            session,
            vendor=data["deviceVendor"],
            model=data["deviceModel"],
            region=data["region"],
            os_version=data["osVersion"],
            os_label=data["osLabel"],
            os=data.get("osType", "IOSXR"),
        )  # Bugfix : DNE-21379
        if query_count(os_version_id_details) != 0:
            kwargs["status"].append(False)
            failure_dict["failure"].append(response_dict)
            add_device_response["metadata"].update(failure_dict)
            ref_value = len(add_device_response["metadata"]["failure"]) - 1
            self.error_details(
                kwargs["errors"],
                code="1006",
                message="Validation Failed: Duplication of os version device region details is not allowed",
                ref_value=ref_value,
            )
            return error_resp
        # Querying Device Region ID
        device_version_details = self.device_region_details(
            session, data["deviceVendor"], data["deviceModel"], data["region"]
        )
        if not device_version_details[0].region:
            kwargs["status"].append(False)
            failure_dict["failure"].append(response_dict)
            add_device_response["metadata"].update(failure_dict)
            ref_value = len(add_device_response["metadata"]["failure"]) - 1
            self.error_details(
                kwargs["errors"],
                code="1001",
                message="Validation Failed: Region is not matched with DB entry",
                ref_value=ref_value,
            )
            return error_resp

        os_status = data["osStatus"]
        os_status_id = self.os_version_details(session, os_status)
        if not os_status_id:
            kwargs["status"].append(False)
            failure_dict["failure"].append(response_dict)
            add_device_response["metadata"].update(failure_dict)
            ref_value = len(add_device_response["metadata"]["failure"]) - 1
            self.error_details(
                kwargs["errors"],
                code="1001",
                message="Validation Failed: OS Status is not matched with DB entry",
                ref_value=ref_value,
            )
            return error_resp
        default_image = [{"imageType": None, "fileName": None, "md5Value": None, "fileSize": None}]
        # Bugfix: DNE-35671
        image_details: list = data.get("osDetails", {}).get("imageFiles", default_image)
        package: list = data.get("osDetails", {}).get("packageDetails", [])
        image_file = []
        for image_detail in image_details:
            image_type = image_detail["imageType"]

            # Query image type details
            file_type = self.image_type_details(session, image_type)
            if image_detail["imageType"] and not file_type:
                kwargs["status"].append(False)
                failure_dict["failure"].append(response_dict)
                add_device_response["metadata"].update(failure_dict)
                ref_value = len(add_device_response["metadata"]["failure"]) - 1
                self.error_details(
                    kwargs["errors"],
                    code="1002",
                    message="Validation Failed: Image type is not matched with DB entry",
                    ref_value=ref_value,
                )
                return error_resp

            if image_detail["fileSize"] and int(image_detail["fileSize"]) / (1024**2 * 1024) >= 3:
                kwargs["status"].append(False)
                failure_dict["failure"].append(response_dict)
                add_device_response["metadata"].update(failure_dict)
                ref_value = len(add_device_response["metadata"]["failure"]) - 1
                self.error_details(
                    kwargs["errors"],
                    code="1003",
                    message="Validation Failed: Image size is greater than expected" " size in DB",
                    ref_value=ref_value,
                )
                return error_resp

            if image_detail["md5Value"] and (int(image_detail["md5Value"], 16).bit_length()) != 128:
                kwargs["status"].append(False)
                failure_dict["failure"].append(response_dict)
                add_device_response["metadata"].update(failure_dict)
                ref_value = len(add_device_response["metadata"]["failure"]) - 1
                self.error_details(
                    kwargs["errors"],
                    code="1004",
                    message="Validation Failed: MD5 checksum is not matching with" " expected bytes size in DB",
                    ref_value=ref_value,
                )
                return error_resp

            image_file.append(
                {
                    "file_type": file_type,
                    "url": image_detail["fileName"],
                    "md5": image_detail["md5Value"],
                    "file_size": int(image_detail["fileSize"])
                    if image_detail["fileSize"]
                    else image_detail["fileSize"],
                    "comments": data.get("comments", ""),
                }
            )
        package_list = []
        for package_detail in package:
            package_type = package_detail["type"]
            # Query package type details
            package_type_details = self.package_type(session, package_type)
            package_type_id = package_type_details[0].id
            if not package_type_id:
                kwargs["status"].append(False)
                failure_dict["failure"].append(response_dict)
                add_device_response["metadata"].update(failure_dict)
                ref_value = len(add_device_response["metadata"]["failure"]) - 1
                self.error_details(
                    kwargs["errors"],
                    code="1005",
                    message="Validation Failed: Package type is not matched with DB entry",
                    ref_value=ref_value,
                )
                return error_resp
            package_list.append({"package_name": package_detail["packages"], "package_type": package_type_id})

        return device_version_details, os_status_id, image_file, package_list

    def error_details(self, errors: list, **kwargs: dict) -> None:
        """
        build error details
        :param errors:(type:list)
        :return:
        """
        logger.debug("Entering error_details module to build error details")
        errors.append(
            {
                "code": f"ERR-000-097-{kwargs['code']}",
                "message": kwargs["message"],
                "serviceReference": {"$ref": f"#/metadata/failure/{kwargs['ref_value']}"},
            }
        )

    def device_region_details(self, session: object, vendor: str, model: str, region: str) -> Query | dict[str, str]:
        """
        Query device region details
        :param session:
        :param region:(type:string)
        :param model:(type:string)
        :param vendor:(type:string)
        :return:
        """
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
            DeviceMaster.vendor == vendor,
            DeviceMaster.model == model,
            RegionMaster.region == region,
        )

    def query_os_version_details(self, session: object, **kwargs: dict) -> Query | dict[str, str]:
        """
        Query device region details
        :return:
        """
        logger.info("Entering query_os_version_details module to query os version related details")
        return (
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
                DeviceMaster.vendor,
                DeviceMaster.model,
                RegionMaster.region,
            )
            .join(DeviceRegion, OSVersionDeviceRegionPackage.device_region_id == DeviceRegion.id)
            .join(OSVersion, OSVersionDeviceRegionPackage.os_version_id == OSVersion.id)
            .join(OsState, OSVersionDeviceRegionPackage.os_validity_id == OsState.id)
            .join(DeviceMaster, DeviceRegion.device_id == DeviceMaster.id)
            .join(RegionMaster, DeviceRegion.region_id == RegionMaster.id)
        ).filter(
            DeviceMaster.vendor == kwargs["vendor"],
            DeviceMaster.model == kwargs["model"],
            RegionMaster.region == kwargs["region"],
            OSVersion.os == kwargs["os"],
            OSVersion.os_version == kwargs["os_version"],
            OSVersion.os_label == kwargs["os_label"],
        )

    def image_type_details(self, session: object, image_type: str) -> int | None:
        """
        Query image type details
        :param session:
        :param image_type:(type:string)
        :return:
        """
        logger.debug("Entering image_type_details module to query image details")
        if image_type:
            image_type_details = (session.query(FileType.id, FileType.file_type)).filter(
                FileType.file_type == image_type
            )
            return image_type_details[0].id
        else:
            return None

    def os_version_details(self, session: object, os_status: str) -> int:
        """
        Query os version details
        :param session:
        :param os_status:(type:string)
        :return:
        """
        logger.debug("Entering os_version_details module to query os version details")
        os_status_details = (session.query(OsState.id, OsState.validity_state)).filter(
            OsState.validity_state == os_status
        )
        return os_status_details[0].id

    def insert_os_version(self, session: object, **kwargs: dict) -> str:
        """
        Insert os version details in sqlDB
        session(object): sql transaction object to connect to DB
        kwargs:
        os(str): type of os
        os_version(str): type of os version
        os_label(str): type of os label
        createdBy(str): username - admin
        modifiedBy(str): username - admin
        return:
            returns id of os version
        """
        logger.debug("Entering insert_os_version module to insert os version details in table")
        os_version_details = (
            session.query(OSVersion.id, OSVersion.os, OSVersion.os_version, OSVersion.os_label)
        ).filter(
            OSVersion.os == kwargs["os"],
            OSVersion.os_version == kwargs["os_version"],  # Bugfix: DNE-37932
            OSVersion.os_label == kwargs["os_label"],
        )
        if query_count(os_version_details) != 0:
            return os_version_details[0].id
        os_version = OSVersion(
            os=kwargs["os"],
            os_version=kwargs["os_version"],
            os_label=kwargs["os_label"],
            createdBy=kwargs["createdBy"],
            modifiedBy=kwargs["modifiedBy"],
        )
        session.add(os_version)
        session.commit()
        return os_version.id

    def insert_os_version_device_region(self, session: object, **kwargs: dict) -> int:
        """
        Insert os version device region details in sqlDB
        :param session:
        :param kwargs:
        :return:
        """
        logger.debug(
            "Entering insert_os_version_device_region module to insert os version device " "region details in tables"
        )
        os_version_device_region = OSVersionDeviceRegionPackage(
            device_region_id=kwargs["device_region_id"],
            os_version_id=kwargs["os_version_id"],
            os_validity_id=kwargs["os_validity_id"],
            createdBy=kwargs["createdBy"],
            modifiedBy=kwargs["modifiedBy"],
        )
        session.add(os_version_device_region)
        session.commit()
        return os_version_device_region.id

    def insert_image_file(self, session: object, **kwargs: dict) -> int:
        """
        insert image file details in sqlDB
        :param session:
        :param kwargs:
        :return:
        """
        logger.debug("Entering insert_image_file module to insert into image file details in table")
        image_file = Image(
            url=kwargs["url"],
            md5=kwargs["md5"],
            file_type=kwargs["file_type"],
            file_size=kwargs["file_size"],
            comments=kwargs["comments"],
            os_version_id=kwargs["os_version_id"],
            os_device_region_id=kwargs["os_device_region_id"],
            createdBy=kwargs["createdBy"],
            modifiedBy=kwargs["modifiedBy"],
        )
        session.add(image_file)
        session.commit()
        return image_file.id

    def package_type(self, session: object, package_type: str) -> Query:
        """
        query package type details
        :param session:
        :param package_type:(type:string)
        :return:
        """
        logger.debug("Entering package_type module to query package type details")
        return (session.query(PackageType.id, PackageType.package_type)).filter(
            PackageType.package_type == package_type
        )

    def insert_package_details(self, session: object, **kwargs: dict) -> None:
        """
        insert package details in sqlDB
        :param session:
        :param kwargs:
        :return:
        """
        logger.debug("Entering insert_package_details module to insert package details in table")
        package_file = Package(
            package_name=kwargs["package_name"],
            package_type=kwargs["package_type"],
            image_id=kwargs["image_id"],
            createdBy=kwargs["createdBy"],
            modifiedBy=kwargs["modifiedBy"],
        )
        session.add(package_file)
        session.commit()
