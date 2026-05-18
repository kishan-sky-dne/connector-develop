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

# Third Party Library
import connexion

# DNE Library
from connectors.core.services.admin.add_image_operations import AddImageOperations
from connectors.core.utils.exceptions import GenericConnectorsException

logger = logging.getLogger(__name__)


def add_image_details(**kwargs):
    """
    Method to add image
        Args:
           kwargs: request body
        Returns:
            status as success and deviceOsVersionId and status failure with error category, message and code
            incase of failure
    """
    try:
        logger.info(f"Entering into admin module to add device image")
        body = kwargs["body"]
        size_list = [len(each_boot_file["md5Value"]) for each_boot_file in body["bootableFileDetails"]]
        for size in size_list:
            if size == 128:
                operations = True
            else:
                operations = False
                break
        if operations:
            image_operations_obj = AddImageOperations(
                device_vendor=body["deviceVendor"],
                device_role=body["deviceRole"],
                device_model=body["deviceModel"],
                os=body["os"],
                os_version=body["osVersion"],
                bootable_file_details=body["bootableFileDetails"],
                rpm_package_details=body["rpmPackageDetails"],
                user=kwargs["user"],
            )
            device_os_version_id = image_operations_obj.add_device_image()
            result = {"status": "success", "deviceOsVersionId": device_os_version_id}
        else:
            result = {
                "status": "failure",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-000-009-0001",
                        "message": "Database Operation Failed. md5Value must be equal to 128 characters",
                    }
                ],
            }
        return result
    except GenericConnectorsException as err:
        return connexion.problem(
            status=500,
            title=f"Connector exception raised while adding image",
            detail=err.args[0],
        )
