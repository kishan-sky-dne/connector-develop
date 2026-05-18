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
import base64
import logging
import sys

# Sky Library
from isp_config import ConfigManagerException

# DNE Library
from connectors.core.config import connectors_config
from connectors.core.services.nap.connector import NapService
from connectors.core.utils.helpers import exception_handler

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
base_url = config.get(section="nap", key="base_url")
nap_username = config.get(section="nap", key="username")
nap_password = config.get(section="nap", key="password")
region_mapper = {"ireland": "roi", "uk": "uk", "italy": "it"}


@exception_handler
def get_nap_details(**kwargs: dict) -> dict:

    """
    calling NEXUS module to update status for various Nexus request id and region

    kwargs:
        request_id(list):
        region(IRELAND):
        userName:

    Returns:
            {}
    """
    region = kwargs.get("region", "Ireland").lower()
    logger.info(f"Entering into NEXUS Api module to fetch details for region {region} with kwargs: {kwargs}")
    query_url = (
        f"{base_url.replace('REGION', region_mapper.get(region, 'roi'))}/support/api/order/v1/voice/network/in-flight"
    )
    authentication = f"{nap_username}:{nap_password}"
    encoded_bytes = base64.b64encode(authentication.encode("utf-8"))
    encoded_string = encoded_bytes.decode("utf-8")
    headers = {"Authorization": f"Basic {encoded_string}", "accept": "application/json"}
    input_kwargs = {
        "headers": headers,
        "url": query_url,
        "region": region,
        "mapped_region": region_mapper.get(region, "roi"),
    }
    nap_obj = NapService()
    status, output, err_msg = nap_obj.get_nap_details(**input_kwargs)
    response = (
        {"status": "SUCCESS", "orders": output}
        if status
        else {"status": "FAIL", "orders": None, "errorMessage": err_msg}
    )
    logger.info(f"Exiting Negetxus update module after sending the api response: {response}")
    return response
