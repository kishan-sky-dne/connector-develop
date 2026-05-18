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
from connectors.core.services.ipam.connector import ReserveIpAddress
from connectors.core.utils.exceptions import ConnectorException, ResourceServiceNotAvailable, RestUtilityException

logger = logging.getLogger(__name__)


def reserve_netbox_ipaddress(**kwargs):
    """
    Method to reserve the ip address in netbox and get the status
    Args:
        kwargs: address, prefix, network, domain, vrf, routeDistinguisher, role, description, tags
    Returns:
            status as success if ip address is reserved successfully
            status as failure with metadata having list of available ip addresses
            status as failure with have error code with message if ip pool is exhausted
    """

    logger.info("Reserving the provided ip in netbox {0}".format({kwargs["body"]["address"]}))

    try:
        status_obj = ReserveIpAddress(kwargs["body"])
        return status_obj.reserve_ip()
    except ResourceServiceNotAvailable as err:
        return connexion.problem(
            status=404,
            title=f"Requested resource is not found",
            detail=err.args[0],
        )
    except RestUtilityException as err:
        return connexion.problem(
            status=403,
            title=f"Request Exception while accessing the URL",
            detail=err.args[0],
        )
    except ConnectorException as err:
        return connexion.problem(
            status=400,
            title=f"Connector exception during reserve ip validations",
            detail=err.args[0],
        )
    except Exception as err:
        logger.exception(f"{err.args[0]} while reserving the provided IP")
        connexion.problem(
            status=500,
            title=f"Reserving the provided IP failed",
            detail=f"Exception raised while reserving the provided IP",
        )
