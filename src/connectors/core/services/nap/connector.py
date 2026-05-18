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

base_url = config.get(section="nap", key="base_url")


class NapService:
    def __init__(self) -> None:
        """calling Nexus

        Retrieves the details of the given type of circuits from Nap system

        :kwargs: {
            region: Type of circuit,
            requestId=state of circuit
            }
        """
        logger.info("Initializing Nap Inventory for voip Service")
        self.rest = RestUtility()

    def get_nap_details(self, **kwargs: dict) -> tuple:
        """
        Retrieves the details of the Nap from Nexus system
        Args:
        Returns:
            dict formatted data
        """
        logger.info(f"Inside Nap method to update {kwargs['region']} circuit status details")
        region = kwargs.get("mapped_region", "roi")
        update_response, err_msg = [], ""
        try:
            url = kwargs.get("url", "")
            logger.debug(f"Fetching details for region {region} information from Nap url {url}")
            output = self.rest.get(
                url=url,
                timeout=20,
                headers=kwargs["headers"],
                status_code_flag=True,
            )
            if output.get("orders", []):
                update_response = output.get("orders", [])
                status = True
            else:
                status = False
                err_msg = f"Error response received from nexus: {output}"
                logger.error(err_msg)
            logger.debug(f"output from get api is: {output}")
            logger.info(f"Response received from nap system: {update_response}")
            return status, update_response, err_msg

        except (RestUtilityException, Exception) as err:
            err_msg = f"Exception raised while accessing nexus url for region {kwargs.get('region')} with error: {err}"
            logger.exception(err_msg, exc_info=True)
            return False, update_response, err_msg

    def update_nap_details(self, **kwargs: dict) -> tuple:
        """
        ReSubmit the details of the Nap from Nexus system
        Args:
        Returns:
            dict formatted data
        """
        logger.info(f"Inside Nap method to update {kwargs['region']} circuit status details")
        update_response = []
        try:

            for request_id in kwargs.get("request_ids"):
                url = kwargs.get("url", "")
                updated_url = url.replace("REQUESTID", str(request_id))
                logger.debug(f"Fetching request_id {request_id} information from Nap url {updated_url}")
                status_code, output = self.rest.post(
                    url=updated_url,
                    timeout=20,
                    headers=kwargs["headers"],
                    data=None,
                    status_code_flag=True,
                )
                logger.info(
                    f"Response received from url: {updated_url} is output: {output} with status_code: {status_code}"
                )
                if status_code in [200, 202]:
                    update_response.append({request_id: {"status": "SUCCESS", "errorMessage": ""}})
                else:
                    update_response.append(
                        {
                            request_id: {
                                "status": "FAIL",
                                "errorMessage": (
                                    f"Failed to reSubmit failed voip circuit with requestid {request_id}, {output}"
                                ),
                            }
                        }
                    )
                logger.debug(f"output from post api is: {output}")
            logger.info(f"Response received from update nap system: {update_response}")
            return True, update_response

        except (RestUtilityException, Exception) as err:
            err_msg = f"Exception raised while accessing nexus url for region {kwargs.get('region')} with error: {err}"
            logger.exception(err_msg, exc_info=True)
            update_response.append(
                {kwargs.get("request_ids", ["generic"])[0]: {"status": "FAIL", "errorMessage": err_msg}}
            )
            return False, update_response
