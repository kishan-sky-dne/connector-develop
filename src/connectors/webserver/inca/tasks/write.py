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
from connectors.core.services.inca.connector import IncaService
from connectors.core.utils.helpers import exception_handler
from connectors.core.utils.oauth import token_generator

logger = logging.getLogger(__name__)

try:
    config = connectors_config.ConnectorsConfigManager()
    config.load_config()
except ConfigManagerException:
    sys.exit(1)


base_url = config.get(section="inca", key="base_url")
nexa_username = config.get(section="inca", key="nexa_username")
nexa_password = config.get(section="inca", key="nexa_password")


inca_type = {
    "gea": {"nexa_url": "apex/nexaREST/v0/message"},
}


@exception_handler
def write_inca_details(**kwargs) -> dict:
    """
    calling INCA module to cease circuit
    kwargs:
        type: type of the INCA
        requestType: cease
    Returns:
            jobID
    Raises:
        Exception
    """
    logger.info(f"Entering into INCA module to {kwargs['type']} {kwargs['requestType']} " f"from INCA Inventory")
    logger.debug(f"kwargs to write INCA for type {kwargs['type']} is: {kwargs}")
    output = {}
    token_url = f"{base_url}apex/nexaREST/oauth/token"
    access_token = token_generator(url=token_url, username=nexa_username, password=nexa_password)
    kwargs["headers"] = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "message_type": "BU",
        "Authorization": f"Bearer {access_token}",
    }
    inca_obj = IncaService()
    for key in inca_type:
        if kwargs["type"] == key:
            kwargs["url"] = inca_type[key]["nexa_url"]
            output = inca_obj.cease_circuit(**kwargs)
    logger.info("Exiting INCA module after sending the api response")
    return output
