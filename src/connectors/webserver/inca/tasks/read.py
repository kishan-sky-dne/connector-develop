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
import sys

# Sky Library
from isp_config import ConfigManagerException

# DNE Library
from connectors.core.config import connectors_config
from connectors.core.exceptions import ConnectorsException
from connectors.core.services.inca.connector import IncaService
from connectors.core.utils.exceptions import RestUtilityException
from connectors.core.utils.helpers import exception_handler
from connectors.core.utils.oauth import token_generator

logger = logging.getLogger(__name__)

try:
    config = connectors_config.ConnectorsConfigManager()
    config.load_config()
except ConfigManagerException:
    sys.exit(1)

"""
INCA/C-Auth Parameters
"""
# INCA
base_url = config.get(section="inca", key="base_url")
username = config.get(section="inca", key="username")
password = config.get(section="inca", key="password")
nexa_username = config.get(section="inca", key="nexa_username")
nexa_password = config.get(section="inca", key="nexa_password")
inca_type = {
    "gea": {
        "config-ready": {
            "url": "apex/incaREST/v0/GEAReadyForConfigJSON",
            "query_params": {"limit": {"key": "p_max_rows", "value": "kwargs.get('limit', 10)"}},
        },
        "plugup-ready": {
            "url": "apex/incaREST/v0/GEAPlugUpJSON",
            "query_params": {"limit": {"key": "p_max_rows", "value": "kwargs.get('limit', 10)"}},
        },
        "cease-requested": {
            "url": "apex/incaREST/v0/GEACeaseJSON",
            "query_params": {
                # limit not yet supported for this API
                "limit": {"key": "p_max_rows", "value": "kwargs.get('limit', 10)"},
                "cablelinkRef": {"key": "cablelink_ref", "value": "kwargs.get('cablelinkRef')"},
            },
        },
    },
    "device": {
        "url": "apex/incaREST/v0/getDevice",
        "query_params": {
            "hostname": {"key": "p_hostname", "value": "kwargs.get('hostname')"},
            "exchangeName": {"key": "p_mdf_id", "value": "kwargs.get('exchangeName')"},
        },
    },
}


@exception_handler
def get_inca_details(
    query_params: list | None = None, path_params: list | None = None, process_data: bool = True, **kwargs
) -> dict:
    """
    calling INCA module to retrieve the various type(e.g gea)  details
    query_params: list of query parameters key used in the INCA API
    path_params: list of path parameters key used in the INCA API
    process_data: Boolean to process the output or not
    kwargs:
        type: type of the INCA - Mandatory field
    Returns:
            formatted INCA data
    Raises:
        Exception

    """
    if query_params is None:
        query_params = (
            ["limit", "cablelinkRef"]
            if kwargs.get("cablelinkRef") and kwargs.get("state") == "cease-requested"
            else ["limit"]
        )
    if path_params is None:
        path_params = []
    if kwargs.get("state") in [None, "None"]:
        kwargs["state"] = "config-ready"
    logger.info(
        "Entering into INCA module to fetch details for "
        f"{kwargs['type']} with state {kwargs['state']} from INCA Inventory"
    )
    try:
        output = _get_inca_response(query_params, path_params, process_data, **kwargs)
    except RestUtilityException as err:
        message = f"Request Exception while accessing the URL {err.args[0]}"
        logger.exception(message, exc_info=True)
        return {"errorCategory": "FAILED", "errors": [{"code": "ERR-011-999-0001", "message": message}]}, 500
    except Exception as err:
        message = f"Connector exception raised while sending url for type {kwargs['type']} to INCA {err.args[0]}"
        logger.exception(message, exc_info=True)
        return {"errorCategory": "FAILED", "errors": [{"code": "ERR-011-999-0002", "message": message}]}, 500
    else:
        logger.info("Exiting INCA module after sending the api response")
        return output


def _get_inca_response(
    query_params: list | None = None, path_params: list | None = None, process_data: bool = True, **kwargs
) -> dict:
    """
    calling INCA module to retrieve the various type(e.g gea)  details
    query_params: list of query parameters key used in the INCA API
    path_params: list of path parameters key used in the INCA API
    process_data: Boolean to process the output or not
    kwargs:
        type: type of the INCA - Mandatory field
    Returns:
            formatted INCA data
    """
    access_token = token_generator(url=f"{base_url}apex/incaREST/oauth/token", username=username, password=password)
    kwargs["headers"] = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    output = {"items": []}
    service_type = kwargs["type"]
    if inca_type.get(service_type):
        url_query_details = (
            inca_type[service_type][kwargs["state"]]["query_params"]
            if service_type == "gea"
            else inca_type[service_type]["query_params"]
        )
        url = (
            inca_type[service_type][kwargs["state"]]["url"] if service_type == "gea" else inca_type[service_type]["url"]
        )
        inca_query = {}
        logger.debug(f"Construct url {url} with required parameters")

        # Construct path parameters by replacing path parameter keys in inca_type.url
        # Example:
        #    url : "apex/incaREST/##SERVICE_TYPE##/v0/##HOSTNAME##"
        #    path_params = ["hostname", "service_type"]
        for path_param in path_params:
            logger.debug(f"Construct path parameter for the {kwargs['type']}: {url}")
            url = url.replace(f"##{path_param.upper()}##", kwargs.get(path_param))

        # Construct key-value for query parameters
        for query_param in query_params:
            logger.debug(f"Construct query parameter for the {kwargs['type']}: {url}")
            value = eval(url_query_details[query_param]["value"])
            # Query parameters accepts only string. Join all list elements
            query_value = ",".join(value) if isinstance(value, list) else value
            inca_query[url_query_details[query_param]["key"]] = query_value

        # Join all query parameters
        query_url = "&".join(f"{key}={value}" for key, value in inca_query.items())
        kwargs["url"] = f"{url}?{query_url}"
        logger.info(f"Calling INCA API to get details for the {kwargs['type']}")
        output = IncaService().get_details(**kwargs)
        if process_data:
            logger.info(f"Process INCA response for the {kwargs['type']} with state {kwargs['state']}: {url}")
            output = _process_data(data=output, **kwargs)
        logger.info(f"Exiting INCA module after fetching details for {kwargs['type']} from INCA Inventory")
    return output


def _process_data(data: dict | None = None, **kwargs) -> dict:
    """
    method to format data received from various types
    :param type: gea
    :param data: gea_data
    :return:
    """
    try:
        service_type = kwargs.get("type", "gea")
        processed_data = {"state": kwargs["state"], "items": []}
        if service_type == "gea":
            if kwargs["state"] == "config-ready" and isinstance(data.get("items"), list):
                for item in data.get("items"):
                    gea_detail = {}
                    gea_detail.update(
                        l2s_id=item.get("l2s_id", None),
                        sw_name=item.get("sw_name", None),
                        sw_port=item.get("sw_port", None),
                        or_cablelink_reference=item.get("or_cablelink_reference", None),
                        cablelink_size=item.get("cablelink_size", None),
                        spark_ref=item.get("spark_ref", None),
                    )
                    processed_data["items"].append(gea_detail)
            elif kwargs["state"] == "plugup-ready":
                processed_data["items"] = data.get("orderList", [])
            elif kwargs["state"] == "cease-requested":
                processed_data = _process_cease_response(data, processed_data)
        if service_type == "device":
            processed_data = {"deviceList": []}
            errors = []
            if "exchangeName" in kwargs and not data["deviceList"]:
                error = {
                    "code": "ERR-011-999-0006",
                    "exchangeName": kwargs["exchangeName"],
                    "message": "No Records are available in INCA for the matching filter criteria",
                }
                errors.append(error)
            for device_info in data["deviceList"]:
                if "error_message" not in device_info:
                    processed_data["deviceList"].append(device_info)
                else:
                    hostname = device_info["hostname"]
                    error = {"code": "ERR-011-999-0006", "hostname": hostname, "message": device_info["error_message"]}
                    errors.append(error)
            if processed_data["deviceList"] and not errors:
                processed_data["status"] = "Success"
                return processed_data
            processed_data["status"] = "Partial Success" if (errors and processed_data["deviceList"]) else "Error"
            processed_data["errors"] = errors
            processed_data["errorCategory"] = "FAILED"
        return processed_data
    except (ValueError, TypeError, AttributeError) as err:
        raise ConnectorsException(f" {err.args[0]}") from err


def _process_cease_response(data: dict, processed_data: dict) -> dict:
    """
    Processes INCA response for GEA Cease circuit details
    """
    if data.get("error_message"):
        # Changing the error message can affect UBB decommissioning order validation
        processed_data = {
            "errorCategory": "FAILED",
            "errors": [{"code": "ERR-011-032-0001", "message": f"INCA Error: {data['error_message']}"}],
        }
    else:
        processed_data["items"] = data.get("items", [])
    return processed_data


@exception_handler
def get_inca_status(**kwargs):
    """
    calling INCA module to get config/update status for various INCA type (e.g gea) details

    kwargs:
        job-id: jobId to fetch the INCA circuit status

    Returns:
            jobID: GC-1234
            status: SUCCESS|FAILURE|IN-PROGRESS|PARTIAL-SUCCESS
            metadata: {circuitStatus: [{circuitId: OGHP12345678, status: success|failure}]}

    Raises:
        Exception

    """
    logger.info(f"Entering into INCA module to get config status for {kwargs} from INCA Inventory")
    token_url = base_url + "apex/nexaREST/oauth/token"
    access_token = token_generator(url=token_url, username=nexa_username, password=nexa_password)
    kwargs["headers"] = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    kwargs["url"] = "apex/nexaREST/v0/response"
    logger.debug(f"kwargs to send for getting job status is {kwargs}")
    inca_obj = IncaService()
    status = inca_obj.get_inca_update_status(**kwargs)
    logger.debug(f"Status is {status}")
    logger.info("Exiting INCA module after sending the api response")
    return status


@exception_handler
def get_device_details(**kwargs):
    """
    Returns the device details and associated subnets from the INCA system
    Args:
    Returns:
        INCA device details and it's associated subnet information
    """
    logger.info("Entering into INCA module to get device details from INCA Inventory")
    if (not kwargs.get("hostname") and not kwargs.get("exchangeName")) or (
        kwargs.get("hostname") and kwargs.get("exchangeName")
    ):
        return {
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-011-999-0001",
                    "message": "Validation failed: Either hostname or exchangeName is mandatory",
                }
            ],
        }
    kwargs["type"] = "device"
    query_params = ["hostname"] if kwargs.get("hostname") else ["exchangeName"]
    return get_inca_details(query_params=query_params, process_data=True, **kwargs)
