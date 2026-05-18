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
from connectors.core.services.admin.update import UpdateDetails
from connectors.core.utils.exceptions import GenericConnectorsException

logger = logging.getLogger(__name__)


def update_upgrade_details(**kwargs: dict[str, str | list]) -> dict[str, str | list]:
    """
    Method to update the upgrade image details
        Kwargs:
           osVersionUpgradeId (int): primary key of the phase upgrade table
        Returns:
            status as success and details and status failure with error category, message and code
            in case of failure
    """
    try:
        logger.info(f"Entering into admin module to update upgrade details for parameter : {kwargs}")
        if errors := update_upgrade_validation_check(kwargs["body"]):
            return {
                "status": "failure",
                "errorCategory": "FAILED",
                "errors": errors,
            }
        upgrade_details_obj = UpdateDetails(**kwargs)
        return upgrade_details_obj.update_upgrade_details()
    except GenericConnectorsException as err:
        logger.exception(f"Generic Connector Exception occured for update upgrade details : {err}")
        return connexion.problem(
            status=500,
            title="Connector exception raised while updating upgrade image details",
            detail=err.args[0],
        )
    except Exception as err:
        logger.exception(f"Exception occured for update upgrade details : {err}")
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


def update_image_details(**kwargs: dict[str, str | list]) -> dict[str, str | list]:
    """
    Method to update the image details
        Kwargs:
           osVersionDeviceRegionId (int): primary key of the os version device region table
        Returns:
            status as success and details and status failure with error category, message and code
            in case of failure
    """
    try:
        logger.info(f"Entering into admin module to update image details for parameter : {kwargs}")
        upgrade_details_obj = UpdateDetails(**kwargs)
        return upgrade_details_obj.update_image_details()
    except GenericConnectorsException as err:
        logger.exception(f"Generic Connector Exception occured for update upgrade details : {err}")
        return connexion.problem(
            status=500,
            title="Connector exception raised while updating image details",
            detail=err.args[0],
        )
    except Exception as err:
        logger.exception(f"Exception occured for update image details : {err}")
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


def update_upgrade_validation_check(body: dict[str, dict | list]) -> list[dict]:
    """Request body validation check for update upgrade details

    Args:
        body (dict[str, dict|list]): request body

    Returns:
        list[dict]: error list
    """
    upgrade_details: dict[str, dict | list] = body["upgradeDetails"]
    errors: list[dict] = [
        {
            "code": "ERR-000-097-1007",
            "message": "'beforeRollback' and 'afterRollback' is a required property when 'isRollbackRequired' "
            f"is true in upgradeDetails.targetOs.customConfig.{config_idx}",
        }
        for config_idx, config in enumerate(upgrade_details["targetOs"]["customConfig"])
        if config["isRollbackRequired"] and all(field not in config for field in {"beforeRollback", "afterRollback"})
    ]
    for inter_idx, intermediate in enumerate(upgrade_details.get("intermediateSteps", [])):
        for config_idx, config in enumerate(intermediate["customConfig"]):
            if config["isRollbackRequired"] and all(
                field not in config for field in {"beforeRollback", "afterRollback"}
            ):
                errors.append(
                    {
                        "code": "ERR-000-097-1007",
                        "message": "'beforeRollback' and 'afterRollback' is a required property when "
                        "'isRollbackRequired' is true in "
                        f"upgradeDetails.intermediateSteps.{inter_idx}.customConfig.{config_idx}",
                    }
                )
    return errors
