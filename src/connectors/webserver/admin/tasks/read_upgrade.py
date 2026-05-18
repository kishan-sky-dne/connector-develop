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
from connectors.core.services.admin.read_upgrade_details import UpgradeDetails
from connectors.core.utils.exceptions import GenericConnectorsException

logger = logging.getLogger(__name__)


def read_upgrade_details(**kwargs: dict[str, str | list]) -> dict[str, str | list]:
    """
    Method to get upgrade details
        Args:
           kwargs: request body
        Returns:
            status as success and details and status failure with error category, message and code
            in case of failure
    """
    try:
        logger.info(f"Entering into admin module to get upgrade details for parameter : {kwargs}")
        upgrade_details_obj = UpgradeDetails(**kwargs)
        upgrade_details = upgrade_details_obj.get_upgrade_details()
        return upgrade_details
    except GenericConnectorsException as err:
        logger.exception(f"Generic Connector Exception occured for read upgrade details : {err}")
        return connexion.problem(
            status=500,
            title=f"Connector exception raised while adding image",
            detail=err.args[0],
        )
    except Exception as err:
        logger.exception(f"Exception occured for read upgrade details : {err}")
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
