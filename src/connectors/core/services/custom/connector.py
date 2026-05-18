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

# Third Party Library
import requests

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.exceptions import ConnectorsException
from connectors.core.utils.exceptions import ResourceServiceNotAvailable, RestUtilityException
from connectors.core.utils.rest_api_utility import RestUtility

logger = logging.getLogger(__name__)

username = config.get(section="cauth", key="username")
password = config.get(section="cauth", key="password")


class CustomService:
    def __init__(self):
        logger.info("Initializing Custom Service Class")
        self.rest = RestUtility()

    def read_tma(self, **kwargs):
        try:
            logger.info(f"Reading TMA output for the given site {kwargs['site']} and {kwargs['option']}")
            """
            Encoding the username and password with base64 before sending to CAUTH server
            """
            authentication = f"{username}:{password}"
            encoded_bytes = base64.b64encode(authentication.encode("utf-8"))
            encoded_string = encoded_bytes.decode("utf-8")
            headers = {
                "Authorization": f"Basic {encoded_string}",
                "accept": "application/json",
            }

            base_url = config.get(section="custom", key="tma_url")

            request = {"searchterm": f"{kwargs['site']}", "switches": f"{kwargs['option']}"}

            return self.rest.post(base_url, headers=headers, data=request).content
        except (ValueError, TypeError, AttributeError) as err:
            raise ConnectorsException(f"{err.args[0]}")
        except RestUtilityException as err:
            if err.response.status_code == requests.codes.not_found:
                raise ResourceServiceNotAvailable(f"{err.args[0]}")
            logger.exception(f"Response Code from the response: {err.response.status_code}")
            raise RestUtilityException(f"{err.args[0]}", err.response)

    def post_tma_cis_from_sparkid(self, **kwargs) -> dict:
        """
        Post TMA CIs from spark ID
        """
        try:
            logger.info(f"Reading TMA output for the given site {kwargs}")

            """
            Encoding the username and password with base64 before sending to TMA server
            """
            authentication = f"{username}:{password}"
            encoded_bytes = base64.b64encode(authentication.encode("utf-8"))
            encoded_string = encoded_bytes.decode("utf-8")
            headers = {
                "Authorization": f"Basic {encoded_string}",
                "accept": "application/json",
            }

            base_url = config.get(section="custom", key="tma_cis_from_sparkId")
            response = self.rest.post(base_url, headers=headers, data=kwargs)
            # Bugfix for DNE-29656 when devs list is empty
            return response if response["devs"] else {"devs": {"dne": {}}}
        except (KeyError, ValueError, TypeError, AttributeError) as err:  # noqa: F841
            # raise ConnectorsException(f"{err.args[0]}")
            return {"devs": {"dne": {}}}
        except RestUtilityException as err:  # noqa: F841
            # if err.response.status_code == requests.codes.not_found:
            # raise ResourceServiceNotAvailable(f"{err.args[0]}")
            logger.exception(f"Response Code from the response: {err.response.status_code}")
            # raise RestUtilityException(f"{err.args[0]}", err.response)
            return {"devs": {"dne": {}}}

    def read_grandma(self, **kwargs):
        try:
            logger.info(f"Reading Grandma output for the given site {kwargs['site']}")
            headers = {
                "accept": "application/json",
            }
            base_url = config.get(section="custom", key="grandma_url")
            request = f"?siteId={kwargs['site']}"
            return self.rest.get(base_url + request, headers=headers).content.decode("utf-8")
        except (ValueError, TypeError, AttributeError) as err:
            raise ConnectorsException(f"{err.args[0]}")
        except RestUtilityException as err:
            if err.response.status_code == requests.codes.not_found:
                raise ResourceServiceNotAvailable(f"{err.args[0]}")
            logger.exception(f"Response Code from the response: {err.response.status_code}")
            raise RestUtilityException(f"{err.args[0]}", err.response)
