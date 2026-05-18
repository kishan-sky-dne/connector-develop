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
from connectors.core.services.dcs.connector import DeviceConfigurationService
from connectors.core.utils.exceptions import ConflictException, RestUtilityException

logger = logging.getLogger(__name__)

cauth_username = config.get(section="cauth", key="username")
cauth_password = config.get(section="cauth", key="password")


def add_device(**kwargs: dict) -> dict:  # noqa: N802
    """
    calling dcs to add device details

    Args:
        data received from user

    Returns:
            success or error message

    Raises:
        Problem in adding the device data in DCS:

    """
    try:
        body = kwargs["body"]
        logger.info(f"Entering into DCS module to add device for {body['hostname']} in DCS system")
        model_mapper = {"NCS540L": "N540-24Q2C2DD-SYS"}
        data = {
            "hostname": body["hostname"],
            "vendor": body["deviceVendor"],
            "model": model_mapper.get(body["deviceModel"], body["deviceModel"]),
            "admin_group": body["adminGroup"],
            "status": body["status"],
            "owner": body["owner"],
            "tacacs_secret": body["tacacsSecret"],
            "tacacs_group": body["tacacsGroup"],
            "device_type": body["deviceType"],
            "os": body.get("os"),
            "os_version": body.get("osVersion"),
        }
        dcs = DeviceConfigurationService(
            hostname=body["hostname"], username=cauth_username, password=cauth_password, data=data
        )
        output = dcs.add_device()
    except RestUtilityException as err:
        return connexion.problem(
            status=403,
            title=f"Request Exception while accessing the URL",
            detail=err.args[0],
            ext={"errors": [{"code": "ERR-007-999-0403", "message": f"Add device failed: due to {err.args[0]}"}]},
        )
    except (ValueError, TypeError, AttributeError, KeyError) as err:
        logger.exception(f"Adding device to DCS failed : {err.args[0]}", exc_info=True)
        return connexion.problem(
            status=500,
            title=f"Exception raised while sending command for" f"{body['hostname']}" "to DCS",
            detail=err.args[0],
            ext={"errors": [{"code": "ERR-007-999-0500", "message": f"Add device failed: due to {err.args[0]}"}]},
        )
    except ConflictException as err:
        return {
            "status": "FAILURE",
            "errorCategory": "FAILED",
            "errors": [{"code": "ERR-007-999-4001", "message": f"{err.args[0]}"}],
        }
    except ConnectorsException as err:
        return connexion.problem(
            status=500,
            title=f"Connector exception raised while sending command for" f"{body['hostname']}" "to DCS",
            detail=err.args[0],
            ext={"errors": [{"code": "ERR-007-999-0500", "message": f"{err.args[0]}"}]},
        )
    else:
        logger.info("Exiting DCS module after sending the response")
        return output


def get_all_device_details(**kwargs):
    """
    calling dcs to get all device details

    Args:
        data received from user

    Returns:
            success or error message

    Raises:
        Problem in fetching the device details in DCS:

    """
    try:
        body = kwargs["body"]
        page_number = kwargs.get("pageNumber", 1)
        limit = kwargs.get("limit", 100)
        offset = kwargs.get("offset", 0)
        logger.info("Entering into DCS module to get all device details in DCS system")
        filters = body["filters"]
        dcs = DeviceConfigurationService(
            hostname=None,
            username=cauth_username,
            password=cauth_password,
            filters=filters,
            page_number=page_number,
            limit=limit,
            offset=offset,
        )
        output = dcs.get_all_device_details()
    except RestUtilityException as err:
        return connexion.problem(
            status=403,
            title="Request Exception while accessing the URL",
            detail=err.args[0],
        )
    except Exception as err:
        return connexion.problem(
            status=500,
            title="Connector exception raised while sending command to all devices in DCS",
            detail=err.args[0],
        )
    else:
        logger.info("Exiting DCS module after sending the response")
        return output
