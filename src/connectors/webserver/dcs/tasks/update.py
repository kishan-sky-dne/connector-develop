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
from connectors.core.config.connectors_config import config
from connectors.core.exceptions import ConnectorsException
from connectors.core.services.dcs.cache_controller import CacheController
from connectors.core.services.dcs.connector import DeviceConfigurationService
from connectors.core.services.dcs.exceptions import DisallowedOperation
from connectors.core.utils.exceptions import ResourceServiceNotAvailable, RestUtilityException

logger = logging.getLogger(__name__)

cauth_username = config.get(section="cauth", key="username")
cauth_password = config.get(section="cauth", key="password")
api_gateway_url = config.get(section="internals", key="api_gw_url")


def update_device(**kwargs: dict) -> dict:
    """
    calling dcs to update device details

    Args:
        data received from user

    Returns:
            success or error message

    Raises:
        Problem in adding the device data in DCS:

    """
    try:
        body = kwargs["body"]
        hostname = kwargs["hostname"]
        status, errors = _validate_dcs_device_update_data(**kwargs)
        if not status:  # Fix for Bug DNE-19174
            return {"errorCategory": "FAILED", "errors": errors}
        logger.info(f"Entering into DCS module to update device for {hostname} in DCS system")
        model_mapper = {"NCS540L": "N540-24Q2C2DD-SYS"}
        data = [
            {
                "op": attr.get("op"),
                "path": attr.get("attribute"),
                **(
                    {
                        "value": model_mapper.get(attr.get("value"), attr.get("value"))
                        if attr.get("attribute") == "/model"
                        else attr.get("value")
                    }
                    if attr.get("value")
                    else {}
                ),
            }
            for attr in body
        ]  # Fix for Bug DNE-19035
        dcs = DeviceConfigurationService(hostname=hostname, username=cauth_username, password=cauth_password, data=data)
        output = dcs.update_device()
        key: str = connexion.request.path.replace("updateDevice", "getDevice")
        CacheController().purge_cache(base_url=f"{api_gateway_url}/remove-cache", key=key)  # Fix for Bug DNE-37327
    except RestUtilityException as err:
        return connexion.problem(
            status=400,
            title="Request Exception while accessing the URL",
            detail=err.args[0],
            ext={"errors": [{"code": "ERR-007-999-0400", "message": f"Update device failed: due to {err.args[0]}"}]},
        )
    except (ValueError, TypeError, AttributeError, KeyError) as err:
        logger.exception(f"Updating device data to DCS failed : {err.args[0]}", exc_info=True)
        return connexion.problem(
            status=500,
            title=f"Exception raised while sending command for" f"{kwargs['hostname']}" "to DCS",
            detail=err.args[0],
            ext={"errors": [{"code": "ERR-007-999-0500", "message": f"Update device failed: due to {err.args[0]}"}]},
        )
    except ResourceServiceNotAvailable as err:
        return connexion.problem(
            status=404,
            title=f"Device {kwargs['hostname']} not available in DCS",
            detail=err.args[0],
            ext={"errors": [{"code": "ERR-007-999-0404", "message": f"Update device failed: due to {err.args[0]}"}]},
        )
    except DisallowedOperation as err:
        return connexion.problem(
            status=422,
            title="Request Exception while accessing the URL",
            detail=err.args[0],
            ext={"errors": [{"code": "ERR-007-999-0422", "message": f"Update device failed: due to {err.args[0]}"}]},
        )
    except ConnectorsException as err:
        return connexion.problem(
            status=500,
            title=f"Connector exception raised while sending command for" f"{kwargs['hostname']}" "to DCS",
            detail=err.args[0],
            ext={"errors": [{"code": "ERR-007-999-0500", "message": f"{err.args[0]}"}]},
        )
    else:
        logger.info("Exiting DCS module after sending the response")
        return output


def _validate_dcs_device_update_data(**kwargs):
    """
    Method to validate the request body for DCS device update
    request:
        data: Request body
    response:
        True/False with errors if any
    """
    body = kwargs["body"]
    logger.info("Validating request body data for DCS device update")
    errors = [
        {
            "code": "ERR-007-999-0001",
            "message": (f"value param must be provided for index {idx} as op value is {item.get('op')}"),
        }
        for idx, item in enumerate(body)
        if item.get("op") in ["add", "replace"] and not item.get("value")
    ]
    return (True, []) if not errors else (False, errors)
