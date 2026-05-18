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
from typing import Any

# Third Party Library
import connexion

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.services.dcs.cache_controller import CacheController
from connectors.core.services.dcs.connector import DeviceConfigurationService
from connectors.core.utils.exceptions import ResourceServiceNotAvailable, RestUtilityException
from connectors.core.utils.helpers import exception_handler
from connectors.core.utils.sanitize import encrypt_sensitive_data, sanitize_response

logger = logging.getLogger(__name__)

cauth_username = config.get(section="cauth", key="username")
cauth_password = config.get(section="cauth", key="password")


def getDeviceDetails(**kwargs):  # noqa: N802
    """
    calling dcs to retrieve the device details

    Args:
        hostname: hostname of the device

    Returns:
            {
              "admin_group": "Italia_SP",
              "collection": {
                "datetime": "2019-12-10T09:05:35Z",
                "errors": [
                  "no response to ping"
                ],
                "issues": null
                "errors": [
                  "no response to ping"
                ],
                "issues": null
              },
              "device_type": "HuaweiOLT",
              "hostname": "olt2.test.bllab.it.bb.sky.com",
              "ipaddr": "10.42.250.162",
              "location": "MC3_brick_lane",
              "model": null,
              "model_family": null,
              "os": null,
              "os_version": null,
              "owner": "MD_IPAccess",
              "ports": null,
              "rev": "240-b8c9978a45c2203830dc29223de184c7",
              "snmp_sysdescr": "Huawei Integrated Access Software",
              "status": "development",
              "vendor": "huawei"
            }

    Raises:
        Exception

    """
    logger.info(f"Entering into DCS module to fetch details for {kwargs['hostname']} from DCS")
    try:
        dcs = DeviceConfigurationService(hostname=kwargs["hostname"], username=cauth_username, password=cauth_password)
        output = encrypt_sensitive_data(dcs.device())
        logger.debug(f"Details from DCS for {kwargs['hostname']} : {sanitize_response(output)}")  # Fix for DNE-8457
    except RestUtilityException as err:
        return connexion.problem(
            status=403,
            title="Request Exception while accessing the URL",
            detail=err.args[0],
        )
    except ResourceServiceNotAvailable as err:
        return connexion.problem(
            status=404,
            title=f"Device {kwargs['hostname']} not available in DCS",
            detail=err.args[0],
        )
    except Exception as err:
        return connexion.problem(
            status=500,
            title=f"Connector exception raised while sending command to " f"{kwargs['hostname']}" "to DCS",
            detail=err.args[0],
        )
    else:
        logger.info("Exiting DCS module after sending the response")
        return output


@exception_handler
def get_all_devices(**kwargs):
    """
    calling dcs to retrieve all devices

    Returns:
        List of devices' matching the given hostname
    """
    hostname = kwargs.get("regex", "")
    logger.info("Entering into DCS Cache Controller module to fetch all devices from DCS. " f" Hostname: {hostname}")
    output = CacheController().get_filtered_devices(filtering_mechanism="filter_by_hostname", hostname=hostname)
    logger.info("Exiting DCS module after sending the response")
    return output


@exception_handler
def get_all_device_vendors(**kwargs) -> dict[str, Any]:
    """
    Finds all vendors of devices currently in DCS

    Returns:
        dict: Names of all vendors
    """
    logger.info("Entering into DCS module to get all device vendors in DCS system")
    dcs = DeviceConfigurationService(
        hostname=None,
        username=cauth_username,
        password=cauth_password,
        filters=[],
        page_number=1,
        limit=100,
        offset=0,
    )
    output = dcs.find_all_vendors()
    logger.info("Exiting DCS module after sending the response")
    return output


@exception_handler
def get_all_device_platforms(**kwargs) -> dict[str, Any]:
    """
    Finds all platforms under a given vendor in DCS

    Returns:
        dict: Names of all platforms
    """
    logger.info("Entering into DCS module to get all device platforms in DCS system")
    dcs = DeviceConfigurationService(
        hostname=None,
        username=cauth_username,
        password=cauth_password,
        filters=[],
        page_number=1,
        limit=100,
        offset=0,
    )
    output = dcs.find_all_platforms(vendor=kwargs["vendor"])
    logger.info("Exiting DCS module after sending the response")
    return output


@exception_handler
def get_all_device_os_versions(**kwargs) -> dict[str, Any]:
    """
    Finds all os versions of devices under given vendor AND platform

    Returns:
        dict: Names of all os versions
    """
    logger.info("Entering into DCS module to get all device os versions in DCS system")
    dcs = DeviceConfigurationService(
        hostname=None,
        username=cauth_username,
        password=cauth_password,
        filters=[],
        page_number=1,
        limit=100,
        offset=0,
    )
    output = dcs.find_all_os_versions(vendor=kwargs["vendor"], platform=kwargs["platform"])
    logger.info("Exiting DCS module after sending the response")
    return output


@exception_handler
def get_all_device_chassis(**kwargs) -> dict[str, Any]:
    """
    Finds all chassis of devices under given vendor AND platform AND os version

    Returns:
        dict: Names of all chassis
    """
    logger.info("Entering into DCS module to get all device chassis in DCS system")
    dcs = DeviceConfigurationService(
        hostname=None,
        username=cauth_username,
        password=cauth_password,
        filters=[],
        page_number=1,
        limit=100,
        offset=0,
    )
    output = dcs.find_all_chassis(vendor=kwargs["vendor"], platform=kwargs["platform"], os_version=kwargs["os_version"])
    logger.info("Exiting DCS module after sending the response")
    return output


@exception_handler
def dcs_fetch(**kwargs) -> dict:
    """
    Sends DCS config fetch from DCS for the given network device .

    Returns:
        Status of config fetch request from DCS.
    """
    hostname = kwargs.get("hostname")
    logger.info(f"Entering into DCS config fetch module for hostname : {hostname}")
    try:
        dcs = DeviceConfigurationService(hostname=kwargs["hostname"], username=cauth_username, password=cauth_password)
        output = dcs.send_dcs_fetch_request()
        logger.debug(f"Response for DCSFetch from hostname {kwargs['hostname']} : {output}")
    except RestUtilityException as err:
        return connexion.problem(
            status=403,
            title="Request Exception while accessing the URL",
            detail=err.args[0],
        )
    except ResourceServiceNotAvailable as err:
        return connexion.problem(
            status=404,
            title=f"Device {kwargs['hostname']} not available in DCS",
            detail=err.args[0],
        )
    except Exception as err:
        return connexion.problem(
            status=500,
            title=f"Connector exception raised while sending DCS Fetch request to {kwargs['hostname']}",
            detail=err.args[0],
        )
    else:
        logger.info("Exiting DCS module after sending DCSFetch response")
        return output
