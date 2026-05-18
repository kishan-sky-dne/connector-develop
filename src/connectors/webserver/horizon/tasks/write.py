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
def update_horizon_deliverable(**kwargs) -> dict:
    """
    Webserver function for updating horizon deliverable

    Returns:
        dict: status and horizon deliverable id
    """

    logger.info("Entering into update_horizon_deliverable method to update horizon deliverable")
    horizon_obj = HorizonService()
    data = horizon_obj.update_deliverable_details(**kwargs)
    logger.debug(f"Updated horizon deliverable details: {data}")
    return data
