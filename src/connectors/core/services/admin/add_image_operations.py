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


class AddImageOperations:
    def __init__(
        self, device_vendor, device_role, device_model, os, os_version, bootable_file_details, rpm_package_details, user
    ):
        self.device_vendor = device_vendor
        self.device_role = device_role
        self.device_model = device_model
        self.os = os
        self.os_version = os_version
        self.bootable_file_details = bootable_file_details
        self.rpm_package_details = rpm_package_details
        self.user = user
        self.sql_instance = MySQLDB()

    def add_device_image(self):
        """
        Add images to mysql db via sqlalchemy orm transactions
        Args: self
        Returns: device_os_version_identifier
        """
        with self.sql_instance.transactional_session() as session:
            device_master = DeviceMaster(
                DeviceVendor=self.device_vendor,
                DeviceRole=self.device_role,
                DeviceModel=self.device_model,
                CreatedBy=self.user,
            )
            session.add(device_master)
            session.commit()
            device_identifier = device_master.DeviceIdentifier
            os_version_master = OSVersionMaster(OS=self.os, OSVersion=self.os_version, CreatedBy=self.user)
            session.add(os_version_master)
            session.commit()
            os_version_identifier = os_version_master.OSVersionIdentifier
            device_os_version = DeviceOSVersion(
                DeviceIdentifier=device_identifier, OSVersionIdentifier=os_version_identifier, CreatedBy=self.user
            )
            session.add(device_os_version)
            session.commit()
            device_os_version_identifier = device_os_version.DeviceOSVersionIdentifier
            for each_boot_file in self.bootable_file_details:
                file_name = each_boot_file["fileName"]
                md5_value = each_boot_file["md5Value"]
                bootable_file = BootableFileDetails(
                    FileName=file_name,
                    MD5Checksum=md5_value,
                    DeviceOSVersionIdentifier=device_os_version_identifier,
                    CreatedBy=self.user,
                )
                session.add(bootable_file)
                session.commit()
            for each_rpm_package in self.rpm_package_details:
                file_name = each_rpm_package["fileName"]
                file_type = each_rpm_package["fileType"]
                rpm_package = RPMPackageDetails(
                    FileName=file_name,
                    FileType=file_type,
                    DeviceOSVersionIdentifier=device_os_version_identifier,
                    CreatedBy=self.user,
                )
                session.add(rpm_package)
                session.commit()
        return device_os_version_identifier
