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

# DNE Library
from connectors.core.services.lookup.domain_classifier import Domain
from connectors.core.utils.helpers import exception_handler

logger = logging.getLogger(__name__)


@exception_handler
def get_network_domain(**kwargs):
    """
    API landing function to get TSR domain of a hostname

    Args:
        hostname (string): hostname to query

    Returns:
        dict: TSR domain and Sky Group of the requested hostname or error response if not matched.
    """
    hostname = kwargs.get("hostname")
    logger.debug(f"Entering `get_network_domain` API for {hostname}")

    domain = Domain()
    result = domain.get_network_domain(hostname)
    if result:
        logger.debug(f"Successfully mapped {hostname} to '{result['network-domain']}' domain. Exiting API")
        return result
    logger.warning(f"Failed to get network domain for {hostname}")
    return {
        "status": "failure",
        "errorCategory": "FAILED",
        "errors": [{"code": "ERR-010-999-0002", "message": f"Failed to get network domain for {hostname}"}],
    }, 404
