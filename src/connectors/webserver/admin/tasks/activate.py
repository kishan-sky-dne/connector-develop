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
from connectors.core.services.admin.activate_operation import UpdateStatus
from connectors.core.utils.exceptions import GenericConnectorsException

logger = logging.getLogger(__name__)


def update_status(**kwargs):
    """
    Method to update the status of DeviceOSVersion
        Args:
           kwargs: deviceOsVersionId
        Returns:
            status as success if updated and  status failure if not get updated
    """
    try:
        logger.info(f"Entering into Admin module to activate a image ")
        status_obj = UpdateStatus(kwargs["deviceOsVersionId"])
        device_status = status_obj.get_device_status()
        if device_status:
            if device_status[0][0] != "Active":  # device_status [('Active',)]
                active_status = status_obj.update_status_active("Active")
                if active_status:
                    status_obj.update_status_inactive("Inactive")
                    response = {"status": "success"}
            else:
                response = {
                    "status": "failure",
                    "errorCategory": "FAILED",
                    "errors": [{"code": "ERR-000-009-0008", "message": "Device OS Version is already in Active State"}],
                }
        else:
            response = {
                "status": "failure",
                "errorCategory": "FAILED",
                "errors": [
                    {"code": "ERR-000-009-0001", "message": "Database Operation Failed.deviceOsVersionId doesn't exist"}
                ],
            }
        return response
    except (KeyError, ValueError, AttributeError, GenericConnectorsException) as err:
        return connexion.problem(
            status=500,
            title=f"Connector exception raised while activating an image",
            detail=err.args[0],
        )
