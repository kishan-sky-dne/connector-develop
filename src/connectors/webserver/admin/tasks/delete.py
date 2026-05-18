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
from connectors.core.services.admin.delete import DeleteAdminDetails
from connectors.core.utils.exceptions import GenericConnectorsException

logger = logging.getLogger(__name__)


def delete_image_details(**kwargs: dict[str, str]) -> dict[str, str | dict]:
    """
    Method to delete image details
        Args:
           kwargs: osVersionDeviceRegionId query parameter
        Returns:
            status as success and status as failure with error category, message and code
            in case of failure
    """
    try:
        logger.debug("Entering into admin module to add device image")
        image_details_obj = DeleteAdminDetails(**kwargs)
        return image_details_obj.delete_device_image()
    except GenericConnectorsException as err:
        logger.debug(f"Generic connector exception for delete device image: {err}")
        return connexion.problem(
            status=500,
            title="Connector exception raised while deleting image",
            detail=err,
        )
    except Exception as err:
        logger.error(f"Exception for delete device image: {err}")
        return {
            "status": "failure",
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-0500",
                    "message": f"Database Operation Failed {err.__class__.__name__} : {err}",
                }
            ],
        }


def delete_upgrade_details(**kwargs: dict[str, str]) -> dict[str, str | dict]:
    """
    Method to delete upgrade details
        Args:
           kwargs: osVersionUpgradeId query parameter
        Returns:
            status as success and status as failure with error category, message and code
            in case of failure
    """
    try:
        logger.debug("Entering into admin module to add device image")
        upgrade_details_obj = DeleteAdminDetails(**kwargs)
        return upgrade_details_obj.delete_upgrade_details()
    except GenericConnectorsException as err:
        logger.debug(f"Generic connector exception for delete upgrade details: {err}")
        return connexion.problem(
            status=500,
            title="Connector exception raised while deleting upgrade details",
            detail=err,
        )
    except Exception as err:
        logger.error(f"Exception for delete upgrade details: {err}")
        return {
            "status": "failure",
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-0500",
                    "message": f"Database Operation Failed {err.__class__.__name__} : {err}",
                }
            ],
        }
