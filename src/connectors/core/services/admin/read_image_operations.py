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
from connectors.core.utils.sqldb.model import (
    BootableFileDetails,
    DeviceMaster,
    DeviceOSVersion,
    OSVersionMaster,
    RPMPackageDetails,
)
from connectors.core.utils.sqldb.sqlDB import MySQLDB

logger = logging.getLogger(__name__)


class DeviceversionDetailsInfo:
    def __init__(
        self,
        include,
        limit,
        device_vendor,
        device_role,
        device_model,
        os,
        os_version,
        status,
        created_on,
        modified_on,
        device_os_version_id,
    ):
        self.include = include
        self.limit = limit
        self.device_vendor = device_vendor
        self.device_role = device_role
        self.device_model = device_model
        self.os = os
        self.os_version = os_version
        self.status = status
        self.created_on = created_on
        self.modified_on = modified_on
        self.device_os_version_id = device_os_version_id
        self.sql_instance = MySQLDB()

    def get_device_version(self):
        """
        Get the DeviceOSVersion, OSVersionMaster and DeviceMaster data
        Returns: device_os_version list

        """
        logger.info(f"Getting the DeviceOSVersion, OSVersionMaster and DeviceMaster data")
        with self.sql_instance.transactional_session() as session:
            device_version_details = (
                session.query(
                    DeviceOSVersion.DeviceOSVersionIdentifier,
                    DeviceMaster.DeviceRole,
                    DeviceMaster.DeviceVendor,
                    DeviceMaster.DeviceModel,
                    OSVersionMaster.OS,
                    OSVersionMaster.OSVersion,
                    DeviceOSVersion.Status,
                    DeviceOSVersion.CreatedBy,
                    DeviceOSVersion.CreatedOn,
                    DeviceOSVersion.ModifiedBy,
                    DeviceOSVersion.ModifiedOn,
                )
                .join(DeviceMaster, DeviceMaster.DeviceIdentifier == DeviceOSVersion.DeviceIdentifier)
                .join(OSVersionMaster, OSVersionMaster.OSVersionIdentifier == DeviceOSVersion.OSVersionIdentifier)
            )
            if self.device_vendor:
                device_version_details = device_version_details.filter(
                    DeviceMaster.DeviceVendor.like("%" + self.device_vendor + "%")
                )
            if self.device_role:
                device_version_details = device_version_details.filter(
                    DeviceMaster.DeviceRole.like("%" + self.device_role + "%")
                )
            if self.device_model:
                device_version_details = device_version_details.filter(
                    DeviceMaster.DeviceModel.like("%" + self.device_model + "%")
                )
            if self.os:
                device_version_details = device_version_details.filter(OSVersionMaster.OS.like("%" + self.os + "%"))
            if self.os_version:
                device_version_details = device_version_details.filter(
                    OSVersionMaster.OSVersion.like("%" + self.os_version + "%")
                )
            if self.status:
                device_version_details = device_version_details.filter(
                    DeviceOSVersion.Status.like("%" + self.status + "%")
                )
            if self.created_on:
                device_version_details = device_version_details.filter(DeviceOSVersion.CreatedOn == self.created_on)
            if self.modified_on:
                device_version_details = device_version_details.filter(DeviceOSVersion.CreatedOn == self.modified_on)
            if self.device_os_version_id:
                device_version_details = device_version_details.filter(
                    DeviceOSVersion.DeviceOSVersionIdentifier == self.device_os_version_id
                )
            device_version_details = device_version_details.limit(self.limit).all()
            if device_version_details:
                for each_device in device_version_details:
                    bootable_file_details = (
                        session.query(
                            BootableFileDetails.FileIdentifier,
                            BootableFileDetails.FileName,
                            BootableFileDetails.MD5Checksum,
                        )
                        .filter(BootableFileDetails.DeviceOSVersionIdentifier == each_device.DeviceOSVersionIdentifier)
                        .all()
                    )
                    bootable_file_data = [
                        {
                            "fileId": each_efd.FileIdentifier,
                            "fileName": each_efd.FileName,
                            "md5Value": each_efd.MD5Checksum,
                        }
                        for each_efd in bootable_file_details
                    ]
                    rpm_package_details = (
                        session.query(
                            RPMPackageDetails.PackageIdentifier, RPMPackageDetails.FileName, RPMPackageDetails.FileType
                        )
                        .filter(RPMPackageDetails.DeviceOSVersionIdentifier == each_device.DeviceOSVersionIdentifier)
                        .all()
                    )
                    rpm_package_data = [
                        {
                            "packageId": each_rpd.PackageIdentifier,
                            "fileName": each_rpd.FileName,
                            "fileType": each_rpd.FileType,
                        }
                        for each_rpd in rpm_package_details
                    ]
                    device_os_version_data = [
                        {
                            "device_os_version_id": each_device.DeviceOSVersionIdentifier,
                            "device_role": each_device.DeviceRole,
                            "device_vendor": each_device.DeviceVendor,
                            "device_model": each_device.DeviceModel,
                            "os": each_device.OS,
                            "os_version": each_device.OSVersion,
                            "status": each_device.Status,
                            "bootableFileDetails": bootable_file_data,
                            "rpmPackageDetails": rpm_package_data,
                            "createdBy": each_device.CreatedBy,
                            "createdOn": each_device.CreatedOn,
                            "modifiedBy": each_device.ModifiedBy,
                            "modifiedOn": each_device.ModifiedOn,
                        }
                    ]
            else:
                device_os_version_data = []
        return device_os_version_data

    def get_device_version_include(self):  # noqa: C901
        """
        Getting the DeviceOSVersion, OSVersionMaster and DeviceMaster data for the include parameters
        Returns: device_os_version list

        """
        logger.info(f"Getting the DeviceOSVersion, OSVersionMaster and DeviceMaster data for the include parameters")
        include = self.include.split(",")
        with self.sql_instance.transactional_session() as session:
            device_version_details = (
                session.query(DeviceOSVersion.DeviceOSVersionIdentifier)
                .join(DeviceMaster, DeviceMaster.DeviceIdentifier == DeviceOSVersion.DeviceIdentifier)
                .join(OSVersionMaster, OSVersionMaster.OSVersionIdentifier == DeviceOSVersion.OSVersionIdentifier)
            )
            if "status" in include:
                device_version_details = device_version_details.add_column(DeviceOSVersion.Status)
            if self.status:
                device_version_details = device_version_details.filter(
                    DeviceOSVersion.Status.like("%" + self.status + "%")
                )
            if "modifiedOn" in include:
                device_version_details = device_version_details.add_column(DeviceOSVersion.ModifiedOn)
            if self.modified_on:
                device_version_details = device_version_details.filter(DeviceOSVersion.ModifiedOn == self.modified_on)
            if "createdOn" in include:
                device_version_details = device_version_details.add_column(DeviceOSVersion.CreatedOn)
            if self.created_on:
                device_version_details = device_version_details.filter(DeviceOSVersion.CreatedOn == self.created_on)
            if "deviceVendor" in include:
                device_version_details = device_version_details.add_column(DeviceMaster.DeviceVendor)
            if self.device_vendor:
                device_version_details = device_version_details.filter(
                    DeviceMaster.DeviceVendor.like("%" + self.device_vendor + "%")
                )
            if "deviceRole" in include:
                device_version_details = device_version_details.add_column(DeviceMaster.DeviceRole)
            if self.device_role:
                device_version_details = device_version_details.filter(
                    DeviceMaster.DeviceRole.like("%" + self.device_role + "%")
                )
            if "deviceModel" in include:
                device_version_details = device_version_details.add_column(DeviceMaster.DeviceModel)
            if self.device_model:
                device_version_details = device_version_details.filter(
                    DeviceMaster.DeviceModel.like("%" + self.device_model + "%")
                )
            if "os" in include:
                device_version_details = device_version_details.add_column(OSVersionMaster.OS)
            if self.os:
                device_version_details = device_version_details.filter(OSVersionMaster.OS.like("%" + self.os + "%"))
            if "osVersion" in include:
                device_version_details = device_version_details.add_column(OSVersionMaster.OSVersion)
            if self.os_version:
                device_version_details = device_version_details.filter(
                    OSVersionMaster.OSVersion.like("%" + self.os_version + "%")
                )
            if self.device_os_version_id:
                device_version_details = device_version_details.filter(
                    DeviceOSVersion.DeviceOSVersionIdentifier == self.device_os_version_id
                )
            device_version_details = device_version_details.limit(self.limit).all()
            device_os_version_list = []
            if device_version_details:
                device_os_version_data = {}
                for each_device in device_version_details:
                    if "deviceVendor" in include:
                        device_os_version_data["deviceVendor"] = each_device.DeviceVendor
                    if "deviceRole" in include:
                        device_os_version_data["deviceRole"] = each_device.DeviceRole
                    if "deviceModel" in include:
                        device_os_version_data["deviceModel"] = each_device.DeviceModel
                    if "os" in include:
                        device_os_version_data["os"] = each_device.OS
                    if "osVersion" in include:
                        device_os_version_data["osVersion"] = each_device.OSVersion
                    if "status" in include:
                        device_os_version_data["status"] = each_device.Status
                    if "modifiedOn" in include:
                        device_os_version_data["modifiedOn"] = each_device.ModifiedOn
                    if "createdOn" in include:
                        device_os_version_data["createdOn"] = each_device.CreatedOn
                    device_os_version_list.append(device_os_version_data)
        return device_os_version_list
