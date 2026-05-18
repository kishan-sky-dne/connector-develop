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
from connectors.core.services.admin.read_image_operations import DeviceversionDetailsInfo

logger = logging.getLogger(__name__)


class DeviceDetails:
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
        self.error = None

    def get_device_details(self):
        """
        Args:
            self
        Returns: status, deviceOsVersionDetails
        """
        logger.info(f"Fetching the device details")
        try:
            device_obj = DeviceversionDetailsInfo(
                self.include,
                self.limit,
                self.device_vendor,
                self.device_role,
                self.device_model,
                self.os,
                self.os_version,
                self.status,
                self.created_on,
                self.modified_on,
                self.device_os_version_id,
            )
            if self.include:
                device_master_data = device_obj.get_device_version_include()
            else:
                device_master_data = device_obj.get_device_version()
            if device_master_data:
                result = {"status": "success", "deviceOsVersionDetails": device_master_data}
            else:
                result = device_master_data
            return result
        except (KeyError, ValueError, AttributeError) as err:
            self.error = {
                "status": "failure",
                "errorCategory": "FAILED",
                "errors": [{"code": "ERR-000-009-0001", "message": "Database Operation Failed"}],
            }
            logger.error(f"Database Operation Failed due to {err.args[0]}")
            return self.error
