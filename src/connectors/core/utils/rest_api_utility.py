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
from json import JSONDecodeError

# Third Party Library
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError  # noqa: N812
from requests.exceptions import RequestException
from urllib3.util.retry import Retry

# Sky Library
from isp_config import ConfigManagerException

# DNE Library
from connectors.core.config import connectors_config
from connectors.core.utils import oauth
from connectors.core.utils.exceptions import ResourceServiceNotAvailable, RestUtilityException
from connectors.core.utils.sanitize import sanitize_response

logger = logging.getLogger(__name__)

try:
    config = connectors_config.ConnectorsConfigManager()
    config.load_config()
except ConfigManagerException:
    sys.exit(1)

error_codes = config.get(section="session", key="error_codes")
error_codes = tuple(int(i) for i in error_codes.split(","))
backoff_factor = float(config.get(section="session", key="backoff_factor"))
max_retries = int(config.get(section="session", key="max_retries"))
verify = config.get(section="session", key="verify")

retries = Retry(
    total=max_retries,
    read=max_retries,
    connect=max_retries,
    backoff_factor=backoff_factor,
    status_forcelist=error_codes,
    raise_on_status=False,
)


class RestUtility:
    def __init__(self, **kwargs):
        self.session = requests.Session()
        retries.respect_retry_after_header = kwargs.get("respect_retry_after", True)
        self.max_retries = HTTPAdapter(max_retries=retries)
        self.timeout = 300
        self.authorization_via_tokens = kwargs.get("authorization_via_tokens")
        self.headers = {"accept": "application/json", "Content-Type": "application/json"}
        if self.authorization_via_tokens:
            self.access_token = oauth.token_generator()
            self.headers["Authorization"] = f"Bearer {self.access_token}"
        self.username = kwargs.get("username")
        self.password = kwargs.get("password")
        if self.username is not None and self.password is not None:
            logger.info(f"Using username and password for authentication")
            self.session.auth = (self.username, self.password)
            self.session.client = kwargs.get("ssl_cert", None)
        self.session.verify = verify

    def get(self, url, params=None, timeout=None, headers=None, log_results=True, **kwargs):  # noqa: C901
        """
        :param headers:
        :param url: REST URL
        :param params: any parameters
        :param timeout:
        :return: @response as json
        """
        logger.debug(f"Error Codes: {error_codes}")
        logger.debug(f"Retries with urlib3 in back-off time: {retries.get_backoff_time()}")
        self.session.mount(url, self.max_retries)
        try:
            timeout = timeout or self.timeout
            logger.info(f"Get request to server URL: {url}")
            if self.authorization_via_tokens and not headers:
                token_info = oauth.get_token_info(self.access_token)
                if token_info is None:
                    logger.exception("Regenerating the token as the token validity has expired")
                    self.access_token = oauth.token_generator()
                self.headers["Authorization"] = f"Bearer {self.access_token}"  # production bug fixed : DNE:156991
            headers = headers or self.headers
            response = self.session.get(url=url, params=params, timeout=timeout, headers=headers)
            logger.debug(f"Response Code from target: {response.status_code}")

            # If the response was successful, no Exception will be raised
            if not kwargs.get("get_full_response"):
                response.raise_for_status()
            try:
                if log_results:
                    logger.debug(f"Response from target in TEXT format : {sanitize_response(response.json())}")
                response = response.json()
            except JSONDecodeError:
                response = response
                logger.debug(f"Response from target in TEXT format : {response}")
            return response
        except HTTPError as err:
            if err.response.status_code == requests.codes.not_found:
                raise ResourceServiceNotAvailable(f"{err.args[0]}") from err
            logger.exception(f"Response Code from the response: {err.response}")
            raise RestUtilityException(f"{err.args[0]}", err.response) from err
        except RequestException as err:
            logger.exception(f"Response Code from the response: {err.response}")
            raise RestUtilityException(f"{err.args[0]}", err.response) from err

    def post(
        self,
        url: str,
        data: dict | None,
        params: dict | None = None,
        timeout: int = None,
        headers: dict | None = None,
        status_code_flag: bool = False,
        **kwargs: dict,
    ) -> any:
        """
        :param headers:
        :param params:
        :param url: REST URL
        :param data:
        :param timeout:
        :param headers:
        :param status_code_flag:
        :return: @response as json
        """
        logger.debug(f"Error Codes: {error_codes}")
        logger.debug(f"Retries with urlib3 in back-off time: {retries.get_backoff_time()}")
        self.session.mount(url, self.max_retries)
        try:
            timeout = timeout or self.timeout
            logger.info(f"Post request to server URL: {url}")
            if self.authorization_via_tokens and not headers:
                token_info = oauth.get_token_info(self.access_token)
                if token_info is None:
                    logger.exception("Regenerating the token as the token validity has expired")
                    self.access_token = oauth.token_generator()
                self.headers["Authorization"] = f"Bearer {self.access_token}"  # production bug fixed : DNE:15699
            headers = headers or self.headers
            response = self.session.post(url=url, params=params, data=data, timeout=timeout, headers=headers)
            logger.debug(f"Response Code from target: {response.status_code}")
            logger.debug(f"Response from target in TEXT format : {response.text}")
            # If the response was successful, no Exception will be raised
            api_status_code = response.status_code
            if not kwargs.get("get_full_response"):
                response.raise_for_status()
            try:
                response = response.json()
            except JSONDecodeError:
                response = response
            return (api_status_code, response) if status_code_flag else response
        except (RequestException, HTTPError) as err:
            logger.exception(f"Response Code from the response: {err.response}")
            raise RestUtilityException(f"{err.args[0]}", err.response) from err

    def put(self, url, data, params=None, timeout=None, headers=None, **kwargs):  # noqa: C901
        # sourcery skip: raise-from-previous-error
        """
        :param params:
        :param headers:
        :param url: REST URL
        :param data:
        :param timeout:
        :return: @response as json
        """
        logger.debug(f"Error Codes: {error_codes}")
        logger.debug(f"Retries with urlib3 in back-off time: {retries.get_backoff_time()}")
        self.session.mount(url, self.max_retries)
        try:
            timeout = timeout or self.timeout
            logger.info(f"Put request to server URL: {url}")
            if self.authorization_via_tokens and not headers:
                token_info = oauth.get_token_info(self.access_token)
                if token_info is None:
                    logger.exception("Regenerating the token as the token validity has expired")
                    self.access_token = oauth.token_generator()
                self.headers["Authorization"] = f"Bearer {self.access_token}"  # production bug fixed : DNE:15699
            headers = headers or self.headers
            response = self.session.put(url=url, params=params, data=data, timeout=timeout, headers=headers)
            logger.debug(f"Response Code from target: {response.status_code}")
            logger.debug(f"Response from target in TEXT format : {response.text}")
            # If the response was successful, no Exception will be raised
            response.raise_for_status()
            return response.json()
        except (RequestException, HTTPError) as err:
            logger.exception(f"Response Code from the response: {err.response}")
            raise RestUtilityException(f"{err.args[0]}", err.response)

    def patch(self, url, data, params=None, timeout=None, headers=None, **kwargs):  # noqa: C901
        """
        :param params:
        :param headers:
        :param url: REST URL
        :param data:
        :param timeout:
        :return: @response as json
        """
        logger.debug(f"Error Codes: {error_codes}")
        logger.debug(f"Retries with urlib3 in back-off time: {retries.get_backoff_time()}")
        self.session.mount(url, self.max_retries)
        try:
            timeout = timeout or self.timeout

            logger.info(f"Patch request to server URL: {url}")
            if self.authorization_via_tokens and not headers:
                token_info = oauth.get_token_info(self.access_token)
                if token_info is None:
                    logger.exception("Regenerating the token as the token validity has expired")
                    self.access_token = oauth.token_generator()
                self.headers["Authorization"] = f"Bearer {self.access_token}"  # production bug fixed : DNE:15699
            headers = headers or self.headers
            response = self.session.patch(url=url, params=params, data=data, timeout=timeout, headers=headers)
            logger.debug(f"Response Code from target: {response.status_code}")
            logger.debug(f"Response from target in TEXT format : {response.text}")
            # If the response was successful, no Exception will be raised
            response.raise_for_status()
            return response.json()
        except (RequestException, HTTPError) as err:
            logger.exception(f"Response Code from the response: {err.response.status_code}")
            raise RestUtilityException(f"{err.args[0]}", err.response.status_code)

    def delete(self, url, params=None, timeout=None, headers=None, **kwargs):  # noqa: C901
        """
        :param headers:
        :param url: REST URL
        :param params: any parameters
        :param timeout:
        :return: @response as json
        """
        logger.debug(f"Error Codes: {error_codes}")
        logger.debug(f"Retries with urlib3 in back-off time: {retries.get_backoff_time()}")
        self.session.mount(url, self.max_retries)
        try:
            timeout = timeout or self.timeout
            logger.info(f"Get request to server URL: {url}")
            if self.authorization_via_tokens and not headers:
                token_info = oauth.get_token_info(self.access_token)
                if token_info is None:
                    logger.exception("Regenerating the token as the token validity has expired")
                    self.access_token = oauth.token_generator()
                self.headers["Authorization"] = f"Bearer {self.access_token}"  # production bug fixed : DNE:15699
            headers = headers or self.headers
            response = self.session.delete(url=url, params=params, timeout=timeout, headers=headers)
            logger.debug(f"Response Code from target: {response.status_code}")
            logger.debug(f"Response from target in TEXT format : {response.text}")
            return response.json(), response.status_code if kwargs.get("get_full_response") else response.status_code
        except RequestException as err:
            logger.exception(f"Response Code from the response: {err.response}")
            raise RestUtilityException(f"{err.args[0]}", err.response) from err
