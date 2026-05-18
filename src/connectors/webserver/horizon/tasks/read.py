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
from connectors.core.services.horizon.connector import HorizonService
from connectors.core.utils.helpers import exception_handler

logger = logging.getLogger(__name__)


@exception_handler
def read_horizon_deliverable(**kwargs) -> dict:
    """
    Webserver function for reading horizon deliverable

    Returns:
        dict: horizon deliverable
    """

    logger.info("Entering into get_horizon_deliverable method to read horizon deliverable")
    horizon_obj = HorizonService()
    return horizon_obj.get_horizon_deliverable(
        order_id=kwargs.get("order_id"),
        unique_reference=kwargs.get("unique_reference"),
    )
