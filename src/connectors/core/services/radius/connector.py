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
import json
import logging

# Third Party Library
from requests import RequestException

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.utils import oauth
from connectors.core.utils.exceptions import GenericConnectorsException, RestUtilityException
from connectors.core.utils.helpers import validate_ipv4_prefix, validate_ipv6_prefix
from connectors.core.utils.rest_api_utility import RestUtility

logger = logging.getLogger(__name__)

base_url = config.get(section="radius", key="base_url")
username = config.get(section="radius", key="username")
password = config.get(section="radius", key="password")
scope = config.get(section="radius", key="scope")


def pre_value_update(func):
    def wrapper(*args, **kwargs):
        logger.info(f"Entering into pre_value_update with args {args} kwargs {kwargs}.")
        access_token = None
        status_code = None
        message = ""
        status = False
        func_obj = None
        try:
            if kwargs.get("status", True) is False:
                return func(*args, **kwargs)
            radius = RadiusService()
            # Code to generate access token Start
            try:
                access_token = radius.generate_token()
            except RestUtilityException as err:
                message = err.args[0]
                status_code = {err.args[0].split(" ")[0]} if isinstance(err.args[0].split(" ")[0], int) else "001"
                logger.exception(message, exc_info=True)
            except GenericConnectorsException as err:
                message = err.args[0]
                try:
                    status_code = int(err.args[0].split(" ")[0])
                except Exception:
                    status_code = "001"
                logger.exception(message, exc_info=True)

            # Code to generate access token End
            if access_token:
                kwargs.update({"access_token": access_token, "radius_obj": radius, "status": True})
                func_obj = func(*args, **kwargs)
            else:
                kwargs.update({"status": status, "message": message, "status_code": status_code})
                func_obj = func(*args, **kwargs)
        except (RestUtilityException, GenericConnectorsException) as err:
            logger.info("Inside pre value exception")
            status = False
            message = err.args[0]
            try:
                status_code = int(err.args[0].split(" ")[0])
            except Exception:
                status_code = "001"
            logger.exception(message, exc_info=True)
            kwargs.update({"status": status, "message": message, "status_code": status_code})
            logger.info(f"excepiton inside pre update kwargs {kwargs}")
            func_obj = func(*args, **kwargs)
        return func_obj

    return wrapper


def ipv6_validate(func):
    def wrapper(*args, **kwargs):
        try:
            status = True
            status_code = 200
            message = ""
            func_obj = None
            if kwargs.get("status", True) is False:
                func_obj = func(*args, **kwargs)
            else:
                ipv6_prefix = kwargs.get("ipv6Prefix") or kwargs.get("body", {}).get("ruleIpv6Prefix")
                ipv6_prefix_list = ipv6_prefix.split("/")
                if not (
                    validate_ipv6_prefix(ipv6_prefix)
                    and len(ipv6_prefix_list) == 2
                    and 0 <= int(ipv6_prefix_list[1]) <= 128
                ):
                    message = f"Invalid BMR Ipv6/Prefix {ipv6_prefix} provided."
                    logger.error(message)
                    status = False
                    status_code = "1002"
                kwargs.update({"status": status, "message": message, "status_code": status_code})
                func_obj = func(*args, **kwargs)
            return func_obj
        except RestUtilityException as err:
            raise RestUtilityException(err)
        except GenericConnectorsException as err:
            raise RestUtilityException(err)

    return wrapper


def ipv4_validate(func):
    def wrapper(*args, **kwargs):
        try:
            status = True
            status_code = 200
            message = ""
            func_obj = None
            if kwargs.get("status", True) is False:
                func_obj = func(*args, **kwargs)
            else:
                ipv4_prefix = kwargs.get("ipv4Prefix") or kwargs.get("body", {}).get("ruleIpv4Prefix")
                ipv4_prefix_list = ipv4_prefix.split("/")
                if not (
                    validate_ipv4_prefix(ipv4_prefix)
                    and len(ipv4_prefix_list) == 2
                    and 0 <= int(ipv4_prefix_list[1]) <= 32
                ):
                    message = f"Invalid BMR Ipv4/Prefix {ipv4_prefix} provided."
                    logger.error(message)
                    status = False
                    status_code = "1001"
                kwargs.update({"status": status, "message": message, "status_code": status_code})
                func_obj = func(*args, **kwargs)
            return func_obj
        except RestUtilityException as err:
            raise RestUtilityException(err)
        except GenericConnectorsException as err:
            raise RestUtilityException(err)

    return wrapper


def error_updation(kwargs):
    status_code_str = "0001"
    status_code = kwargs.get("status_code")
    if isinstance(status_code, int):
        status_code_str = f"0{status_code}" if len(str(status_code)) == 3 else status_code
    message = str(kwargs.get("message", ""))
    return {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": f"ERR-015-999-{status_code_str}",
                "message": message,
            }
        ],
    }, status_code


class RadiusService:
    def __init__(self, **kwargs):
        """
        calling Radius Service

        Radius Operations

        """
        logger.info("Initializing Radius Service")
        self.kwargs = {
            "username": kwargs.get("radius_username") or username,
            "password": kwargs.get("radius_password") or password,
        }
        self.rest = RestUtility()
        self.base_url = kwargs.get("radius_base_url") or base_url
        self.scope = kwargs.get("radius_scope") or scope

    def add_bmr_details(self, **kwargs):
        """_summary_

        Returns:
            _type_: _description_
        """
        try:
            logger.info(f"Adding BMR Details kwargs {kwargs}")
            payload = {
                "ruleipv6prefix": kwargs.get("body").get("ruleIpv6Prefix"),
                "ruleipv4prefix": kwargs.get("body").get("ruleIpv4Prefix"),
                "psid_length": kwargs.get("body").get("psidLength"),
                "psid_offset": kwargs.get("body").get("psidOffset"),
                "ea_length": kwargs.get("body").get("eaLength"),
            }
            url = f"{kwargs.get('version','v1')}/bmr"
            payload = json.dumps(payload)
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {kwargs.get('access_token')}",
            }
            radius_url = self.base_url + url
            logger.debug(f"Adding BMR details radius url: {radius_url} payload: {payload}")
            response = self.rest.post(
                url=radius_url,
                data=payload,
                timeout=20,
                headers=headers,
                get_full_response=True,
            )
            logger.debug("Successfully inserted radius details.")
            return response
        except RestUtilityException as err:
            logger.exception(f"Response Code from the response: {err.response}")
            raise RestUtilityException(f"{err.args[0]}", err.response) from err

    def get_bmr_details(self, **kwargs):
        """_summary_

        Returns:
            _type_: _description_
        """
        try:
            logger.info(f"Fetching BMR Details kwargs {kwargs}")
            url = f"{kwargs.get('version','v1')}/bmr/{kwargs.get('ipv6Prefix')}"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {kwargs.get('access_token')}",
            }
            radius_url = self.base_url + url
            logger.debug(f"Fetching information from radius url: {radius_url}")
            response = self.rest.get(url=radius_url, timeout=60, headers=headers, get_full_response=True)
            logger.debug("Successfully retrieved radius details.")
            return response
        except RestUtilityException as err:
            logger.exception(f"Response Code from the response: {err.response}")
            raise RestUtilityException(f"{err.args[0]}", err.response) from err

    def sync_bmr_details(self, **kwargs):
        """_summary_

        Returns:
            _type_: _description_
        """
        try:
            logger.info(f"Fetching BMR Details kwargs {kwargs}")
            url = f"{kwargs.get('version','v1')}/bmrstatus"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {kwargs.get('access_token')}",
            }
            radius_url = self.base_url + url
            logger.debug(f"Fetching information from radius url: {radius_url}")
            response = self.rest.get(url=radius_url, timeout=60, headers=headers, get_full_response=True)
            logger.debug("Successfully retrieved radius details.")
            return response
        except RestUtilityException as err:
            logger.exception(f"Response Code from the response: {err.response}")
            raise RestUtilityException(f"{err.args[0]}", err.response) from err

    def delete_bmr_details(self, **kwargs):
        """_summary_

        Returns:
            _type_: _description_
        """
        try:
            logger.info(f"Deleting BMR Details kwargs {kwargs}")
            url = f"v1/bmr/{kwargs.get('ipv6Prefix')}"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {kwargs.get('access_token')}",
            }
            get_full_response = True
            radius_url = self.base_url + url
            logger.debug(f"Deleting information from radius url: {radius_url}")
            response = self.rest.delete(
                url=radius_url,
                timeout=60,
                headers=headers,
                get_full_response=get_full_response,
            )
            logger.debug("Successfully deleted radius details.")
            return response
        except (RestUtilityException, GenericConnectorsException) as err:
            logger.exception(f"Response Code from the response: {err.response}")
            raise RestUtilityException(f"{err.args[0]}", err.response) from err

    def generate_token(self):
        """_summary_

        Raises:
            RestUtilityException: _description_
            GenericConnectorsException: _description_

        Returns:
            _type_: _description_
        """
        logger.info(f"Inside generate_token kwargs scope {self.scope}")
        try:
            oauth_generate_token = oauth
            generated_token = oauth_generate_token.token_generator(
                username=self.kwargs.get("username"), password=self.kwargs.get("password"), **{"scope": self.scope}
            )
            logger.info("Exit generate_token")
            return generated_token
        except RequestException as err:
            raise RestUtilityException(f"{err.args[0]}", err.response) from err
        except (ValueError, TypeError, AttributeError) as err:
            raise GenericConnectorsException(f"{err.args[0]}", err.response) from err
