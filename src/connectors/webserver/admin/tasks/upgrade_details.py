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
from connectors.core.services.admin.image_upgrade_details import ImageUpgradeDetails
from connectors.core.utils.exceptions import GenericConnectorsException

logger = logging.getLogger(__name__)


def image_upgrade_details(**kwargs: dict[str, str | list]) -> dict[str, str | list]:
    """
    Method to get the metadata information about the Golden Image
    Args:
        kwargs: _include, limit
    Returns:
            status as success with metadata information about the Golden Image
             and for status failure have error code with message
    """
    try:
        logger.info(f"Entering into Admin module to get metadata information about the image upgrade details")
        body = kwargs["body"]
        if errors := validation_check(body):
            return {
                "status": "failure",
                "errorCategory": "FAILED",
                "errors": errors,
            }
        device_obj: object = ImageUpgradeDetails(body=body)
        result = device_obj.image_upgrade_details()
        return result
    except GenericConnectorsException as err:
        return connexion.problem(
            status=500,
            title=f"Connector exception raised while adding image",
            detail=err.args[0],
        )
    except Exception as err:
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


def validation_check(body: list[dict]) -> list[dict]:
    """Request body validation check

    Args:
        body (list[dict]): request body

    Returns:
        list[dict]: error list
    """
    errors: list[dict] = []
    for image_idx, upgrade_details in enumerate(body):
        # Bugfix: DNE-37793
        errors.extend(
            {
                "code": "ERR-000-097-1007",
                "message": "'beforeUpgrade' or 'afterUpgrade' or 'beforeRollback' or 'afterRollback' is a "
                f"required property when custom config in upgrade.{image_idx}.targetOs.customConfig.{config_idx}",
            }
            for config_idx, config in enumerate(upgrade_details["upgrade"]["targetOs"].get("customConfig", []))
            if all(
                field not in config for field in {"beforeUpgrade", "afterUpgrade", "beforeRollback", "afterRollback"}
            )
        )
        if "intermediateSteps" in upgrade_details["upgrade"]:
            for inter_idx, intermediate in enumerate(upgrade_details["upgrade"]["intermediateSteps"]):
                # Bugfix: DNE-37793
                errors.extend(
                    {
                        "code": "ERR-000-097-1007",
                        "message": "'beforeUpgrade' or 'afterUpgrade' or 'beforeRollback' or 'afterRollback' is a "
                        f"required property when custom config  in upgrade.{image_idx}.intermediateSteps.{inter_idx}."
                        f"customConfig.{config_idx}",
                    }
                    for config_idx, config in enumerate(intermediate.get("customConfig", []))
                    if all(
                        field not in config
                        for field in {"beforeUpgrade", "afterUpgrade", "beforeRollback", "afterRollback"}
                    )
                )
    return errors
