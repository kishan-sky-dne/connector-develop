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
from connectors.core.config.connectors_config import config
from connectors.core.utils.exceptions import RestUtilityException
from connectors.core.utils.rest_api_utility import RestUtility

logger = logging.getLogger(__name__)

base_url = config.get(section="plannet", key="base_url")


class PlannetService:
    def __init__(self):
        """
        calling PLANNET Service

        Retrieves the details of plannet data from the plannet Inventory

        """
        logger.info("Initializing PLANNET Inventory Service")
        self.rest = RestUtility()

    def get_plannet_details(self, **kwargs):
        """
        Retrieves the details of plannet data from plannet inventory
        kwargs:
            url: plannet url from where data to be fetched
            headers:
        Returns:
            get response as JSON formatted data
        """
        logger.info("Inside get Plannet method to fetch plannet details")
        try:
            plannet_url = base_url + kwargs["url"]
            logger.debug(f"Fetching information from PLANNET url: {plannet_url}")
            return self.rest.get(url=plannet_url, timeout=120, headers=kwargs["headers"])
        except RestUtilityException as err:
            logger.exception(f"Response Code from the response: {err.response.status_code}")
            raise RestUtilityException(f"{err.args[0]}", err.response) from err

    def patch_plannet_details(self, **kwargs):
        """
        Updates the PlanNet inventory with the new details provided in the payload.
        kwargs:
          url: PlanNet API endpoint
          headers: API headers containing token information
        """
        logger.info("Inside patch PlanNet method to update PlanNet details")
        plannet_url = base_url + kwargs["url"]
        logger.debug(f"Fetching information from PLANNET url: {plannet_url} payload: {kwargs['payload']}")
        response = self.rest.patch(url=plannet_url, data=kwargs["payload"], headers=kwargs["headers"], timeout=20)
        logger.debug("Successfully updated PlanNet details.")
        return response
