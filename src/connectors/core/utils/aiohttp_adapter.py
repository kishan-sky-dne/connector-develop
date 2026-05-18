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

# Third Party Library
from aiohttp import (
    BasicAuth,
    ClientConnectionError,
    ClientConnectorError,
    ClientError,
    ClientResponse,
    ClientResponseError,
)

# Sky Library
from isp_config import ConfigManagerException

# DNE Library
from connectors.core.config import connectors_config
from connectors.core.utils import oauth

logger = logging.getLogger(__name__)


try:
    config = connectors_config.ConnectorsConfigManager()
    config.load_config()
except ConfigManagerException:
    sys.exit(1)


max_retries = config.get(section="session", key="max_retries")
verify = config.get(section="session", key="verify")


class AioRestUtility:
    def __init__(self, **kwargs):
        self.timeout = 300
        self.authorization_via_tokens = kwargs.get("authorization_via_tokens")
        self.headers = {"accept": "application/json", "Content-Type": "application/json"}
        self.max_retries = max_retries
        self.ssl_verify = kwargs.get("ssl_verify", True)
        if self.authorization_via_tokens:
            self.access_token = oauth.token_generator()
            self.headers["Authorization"] = f"Bearer {self.access_token}"
        self.username = kwargs.get("username")
        self.password = kwargs.get("password")
        self.basic_auth = None
        # TODO-TEST: username/password based authentication
        if self.username is not None and self.password is not None:
            logger.info("Using username and password for authentication")
            self.basic_auth = BasicAuth(self.username, self.password)

    async def get(self, client_session, url, timeout=None, headers=None, params=None, **kwargs) -> ClientResponse:
        """
        Asynchronous AIOHTTP get
        :param client_session
        :param url: REST URL
        :param timeout:
        :param headers:
        :param params: any parameters
        :return: @response as json
        """
        logger.info(f"Get request to server url: {url}")
        try:
            timeout = timeout or self.timeout
            if self.authorization_via_tokens and not headers:
                token_info = oauth.get_token_info(self.access_token)
                if token_info is None:
                    logger.exception("Regenerating the token as the token validity has expired")
                    self.access_token = oauth.token_generator()
                    self.headers["Authorization"] = f"Bearer {self.access_token}"
            headers = headers or self.headers
            response = client_session.get(
                url=url,
                auth=self.basic_auth,
                params=params,
                timeout=timeout,
                headers=headers,
                ssl=self.ssl_verify,
                raise_for_status=True,
            )
            client_response = await response
            logger.info(f"Response code from target: {client_response.status}")
            client_response.raise_for_status()
            return client_response
        except (ClientConnectorError, ClientConnectionError, ClientResponseError, ClientError) as err:
            logger.exception(f"Response code from target: {err.status}")
            return err

    async def post(
        self, client_session, url, data=None, timeout=None, headers=None, params=None, **kwargs
    ) -> ClientResponse:
        """
        Asynchronous AIOHTTP POST
        :param client_session
        :param headers:
        :param params:
        :param url: REST URL
        :param data:
        :param timeout:
        :return: @response as json
        """
        logger.info(f"Post request to target url: {url}")
        try:
            timeout = timeout or self.timeout
            if self.authorization_via_tokens and not headers:
                token_info = oauth.get_token_info(self.access_token)
                if token_info is None:
                    logger.exception("Regenerating the token as the token validity has expired")
                    self.access_token = oauth.token_generator()
                    self.headers["Authorization"] = f"Bearer {self.access_token}"
            headers = headers or self.headers
            response = client_session.post(
                url=url,
                auth=self.basic_auth,
                json=data,
                params=params,
                timeout=timeout,
                headers=headers,
                ssl=self.ssl_verify,
            )
            client_response = await response
            logger.info(f"Response Code from target: {client_response.status}")
            client_response.raise_for_status()
            return client_response
        except (ClientConnectorError, ClientConnectionError, ClientResponseError, ClientError) as err:
            logger.exception(f"Response code from target: {err.status}")
            return err

    async def put(
        self, client_session, url, data=None, timeout=None, headers=None, params=None, **kwargs
    ) -> ClientResponse:
        """
        TODO: Doc
        Asynchronous AIOHTTP PUT

        """
        pass

    async def patch(
        self, client_session, url, data=None, timeout=None, headers=None, params=None, **kwargs
    ) -> ClientResponse:
        """
        TODO: Doc
        Asynchronous AIOHTTP PATCH

        """
        pass

    async def delete(self, client_session, url, timeout=None, headers=None, params=None, **kwargs) -> ClientResponse:
        """
        TODO: Doc
        Asynchronous AIOHTTP DELETE

        """
        pass
