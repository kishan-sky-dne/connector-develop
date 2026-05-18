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
from connectors.core.services.service_status.read import ServiceStatus
from connectors.core.utils.helpers import exception_handler

logger = logging.getLogger(__name__)


@exception_handler
def get_service_status(**kwargs):
    """
    calling service record status module to retrieve the required service status
    kwargs:
        orderId(string)
        serviceType(string)
        operationType(string)
    Returns:
            formatted service status data
    """
    order_id = kwargs.get("orderId")
    service_type = kwargs.get("serviceType")
    operation_type = kwargs.get("operationType")
    logger.debug(
        "Entering 'get_service_status' API for "
        + f"{service_type} service(s) with '{order_id}' order ID and '{operation_type}' operation"
    )
    result = ServiceStatus(**kwargs).get_service_status()
    logger.debug(
        "Successfully fetched service status "
        + f"for {service_type} service(s) with order ID: {order_id} and operation: {operation_type}. Exiting API"
    )
    return result
