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
from connectors.core.utils.exceptions import RestUtilityException
from connectors.core.utils.rest_api_utility import RestUtility

logger = logging.getLogger(__name__)


class GitService:
    def __init__(self):
        """
        calling Git Service

        Retrieves the details of repository from git

        """
        logger.info("Initializing Git Service")
        self.rest = RestUtility()

    def get_repository_details(self, **kwargs):
        """
        Retrieves the details of repository from git
        kwargs:
            url: git url from where data to be fetched
            headers: { "PRIVATE-TOKEN": token }
        Returns:
            TBD
        """
        logger.info("Inside get Git method to fetch repository details")
        try:
            logger.debug(f"Fetching information from Git url: {kwargs.get('url')}")
            return self.rest.get(url=kwargs.get("url"), timeout=20, headers=kwargs.get("headers"))
        except RestUtilityException as err:
            logger.exception(f"Response Code from the response: {err.response.status_code}")
            raise RestUtilityException(f"{err.args[0]}", err.response) from err
