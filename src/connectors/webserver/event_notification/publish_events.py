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
from connectors.core.services.event_notification.publish_events import OrderStatus
from connectors.core.utils.helpers import exception_handler

logger = logging.getLogger(__name__)


@exception_handler
def publish_order_status(**kwargs):
    """
    calling order status module to publish DNE order status
    kwargs:
        keyId(string)
        message(dict)
        eventTime(int)
        eventSource(string)
    Returns:
        dictionary with (success/failure) publication status
    """
    payload = kwargs["body"]
    logger.debug(f"Entering 'publish_order_status' API with payload '{payload}")
    result = OrderStatus(**kwargs).publish()
    logger.debug("Returning the status of the publication request")
    return result
