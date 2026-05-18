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
from connectors.core.services.admin.add_image_details import AddImageDetails
from connectors.core.utils.exceptions import GenericConnectorsException

logger = logging.getLogger(__name__)


def create_image_details(**kwargs: dict[str, str | list]) -> dict[str, str | list]:
    """
    Method to add image details
        Args:
           kwargs: request body
        Returns:
            status as success and osVersionDeviceRegionId and status failure with error category, message and code
            in case of failure
    """
    try:
        logger.debug(f"Entering into admin module to add device image")
        body = kwargs["body"]
        image_details_obj = AddImageDetails(body)
        # Bugfix: DNE-35671
        for data in body:
            if data["osStatus"] in ["Current", "Under_test"] and not data.get("osDetails"):
                return {
                    "status": "failure",
                    "errorCategory": "FAILED",
                    "errors": [
                        {
                            "code": "ERR-000-097-1001",
                            "message": "Validation Failed: Create image details osDetails is mandatory "
                            "when os status is in Current or Under_test",
                        }
                    ],
                }

        image_details = image_details_obj.add_device_image()
        return image_details
    except GenericConnectorsException as err:
        logger.debug(f"Generic connector exception for add device image: {err}")
        return connexion.problem(
            status=500,
            title=f"Connector exception raised while adding image",
            detail=err.args[0],
        )
    except Exception as err:
        logger.error(f"Exception for add device image: {err}")
        return {
            "status": "failure",
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-0500",
                    "message": f"Database Operation Failed : {err}",
                }
            ],
        }
