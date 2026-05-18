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
from connectors.core.services.admin.get_device_os_version import DeviceDetails
from connectors.core.utils.exceptions import GenericConnectorsException

logger = logging.getLogger(__name__)


def get_image_details(**kwargs):
    """
    Method to get the metadata information about the Golden Image
    Args:
        kwargs: _include, limit
    Returns:
            status as success with metadata information about the Golden Image
             and for status failure have error code with message
    """
    try:
        logger.info(f"Entering into Admin module to get metadata information about the Golden Image")
        status = kwargs.get("status")
        include = kwargs.get("_include")
        limit = kwargs.get("limit")
        if status:
            kwargs.pop("status")
        if include:
            kwargs.pop("_include")
        kwargs.pop("limit")
        if status == "Inactive" or len(kwargs) >= 3:
            device_obj = DeviceDetails(
                include,
                limit,
                kwargs.get("deviceVendor"),
                kwargs.get("deviceRole"),
                kwargs.get("deviceModel"),
                kwargs.get("os"),
                kwargs.get("osVersion"),
                status,
                kwargs.get("createdOn"),
                kwargs.get("modifiedOn"),
                kwargs.get("deviceOsVersionId"),
            )
            result = device_obj.get_device_details()
        else:
            result = {
                "status": "failure",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-000-009-0002",
                        "message": "Filter criteria may result too much records, "
                        "Please argument with another filter",
                    }
                ],
            }
        return result
    except GenericConnectorsException as err:
        return connexion.problem(
            status=500,
            title=f"Connector exception raised to get metadata information about the Golden Image",
            detail=err.args[0],
        )
