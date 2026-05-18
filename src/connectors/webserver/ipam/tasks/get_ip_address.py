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
from connectors.core.services.ipam.connector import PrefixAvailableIps
from connectors.core.utils.exceptions import ConnectorException, ResourceServiceNotAvailable, RestUtilityException

logger = logging.getLogger(__name__)


def get_available_ips(**kwargs):
    """
    Method to get the available IP
    Args:
        kwargs: prefix, domain, quantity
    Returns:
            status as success with list of ip adresses as metadata and for status failure
             have error code with message
    """
    logger.info(f"Entering into IPAM module to fetch available ip addresses for {kwargs['prefix']}")
    try:
        available_ip_obj = PrefixAvailableIps(kwargs)
        return available_ip_obj.get_prefix_available_ips()
    except RestUtilityException as err:
        return connexion.problem(
            status=403,
            title=f"Request Exception while accessing the URL",
            detail=err.args[0],
        )
    except ResourceServiceNotAvailable as err:
        return connexion.problem(
            status=404,
            title=f"{kwargs['prefix']} not available in Netbox",
            detail=err.args[0],
        )
    except ConnectorException as err:
        return connexion.problem(
            status=500,
            title=f"Connector exception raised for getting the available ips " f"{kwargs['prefix']} from IPAM",
            detail=err.args[0],
        )
