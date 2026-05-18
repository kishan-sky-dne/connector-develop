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

# Third Party Library
import jwt
import jwt.exceptions as jwtException  # noqa: N812
from msal import ConfidentialClientApplication
from requests import Session  # noqa: N812
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3.util.retry import Retry

# Sky Library
from isp_config import ConfigManagerException

# DNE Library
from connectors.core.config import connectors_config
from connectors.core.utils.exceptions import GenericConnectorsException, RestUtilityException

logger = logging.getLogger(__name__)

try:
    config = connectors_config.ConnectorsConfigManager()
    config.load_config()
except ConfigManagerException:
    sys.exit(1)

"""
OAuth Parameters
"""

oauth_url = config.get(section="oauth", key="url")
username = config.get(section="oauth", key="username")
password = config.get(section="oauth", key="password")
scope = config.get(section="oauth", key="scope")
verify = config.get(section="oauth", key="verify")
jwt_key_pub = config.get(section="internals", key="jwt_pub_key")

"""
Azure AD Parameters
"""

client_id = config.get(section="azureAdAuth", key="client_id")
client_credential = config.get(section="azureAdAuth", key="client_credential")
authority = config.get(section="azureAdAuth", key="authority")
scopes = config.get(section="azureAdAuth", key="scopes")
skip_token = config.get(section="oauth", key="skip_token")

"""
Session Parameters
"""
error_codes = config.get(section="session", key="error_codes")
error_codes = tuple([int(i) for i in error_codes.split(",")])
backoff_factor = config.get(section="session", key="backoff_factor")
max_retries = config.get(section="session", key="max_retries")

retries = Retry(
    total=max_retries,
    read=max_retries,
    connect=max_retries,
    backoff_factor=backoff_factor,
    status_forcelist=error_codes,
    raise_on_status=False,
)


def get_token_info(token: str) -> dict | None:
    """
    Retrieve oauth token_info remotely using HTTP
    :param token: oauth token from authorization header
    :type token: str
    :rtype: dict
    """
    # Flag-based workaround to skip token validation if needed
    skip_token_validation = str(skip_token).lower() == "true"
    logger.info(f"skip_token_validation flag is set to: {skip_token_validation}")
    if skip_token_validation:
        logger.warning("SKIP_TOKEN_VALIDATION is enabled. Skipping token validation and returning dummy user.")
        all_scopes = "connector:read connector:write orch:read orch:write dial:read dial:write"
        return {"sub": "dummy_user", "scopes": all_scopes}
    logger.info(f"Entering Token Validation")
    try:
        pubkey_file = open(jwt_key_pub, "r").read()
        try:
            token_request = jwt.decode(token, key=pubkey_file, algorithms="RS256")
            logger.debug(f"Fetching Token info {token_request} from headers")
            logger.info(
                f"Validating token for client: {token_request['clientId']}  with scopes " f"{token_request['scope']}"
            )
            logger.info(f"Exiting Token Validation")
            return {"sub": token_request["clientId"], "scopes": token_request["scope"]}
        except (
            jwtException.InvalidTokenError,
            jwtException.DecodeError,
            jwtException.InvalidSignatureError,
            jwtException.ExpiredSignatureError,
            jwtException.InvalidAudienceError,
            jwtException.InvalidIssuerError,
            jwtException.InvalidIssuedAtError,
            jwtException.ImmatureSignatureError,
            jwtException.InvalidKeyError,
            jwtException.InvalidAlgorithmError,
            jwtException.MissingRequiredClaimError,
        ) as err:
            logger.exception(f"Error from JWT Exception {err.args[0]} while decoding the token")
    except FileNotFoundError as err:
        logger.exception(f"{err.args[0]} while processing the file")


def token_generator(url: str = oauth_url, username: str = username, password: str = password, **kwargs: dict) -> str:
    """
    Generate oauth token remotely using HTTP/HTTPS from ISP Sky CAUTH
    Args:
        url: URl to generate token
        username: username to generate token
        password: password to generate token
    Returns:
        {
         "access_token":"",
         "expires_in":600
         "token_type":"Bearer"
        }

    Raises:
    """
    # Flag-based workaround to skip token generation if auth server is down
    skip_token_validation = str(skip_token).lower() == "true"
    if skip_token_validation:
        logger.warning("SKIP_TOKEN_VALIDATION is enabled. Skipping token generation and returning dummy token.")
        return "dummy_token"
    try:
        """
        Session Parameters
        """
        session = Session()
        session.mount(url, HTTPAdapter(max_retries=retries))
        session.verify = verify

        logger.debug(
            "Oauth Details before creating the token: "
            f"{url} with username: {username}, scope: "
            f"{kwargs.get('scope') or scope}, kwargs {kwargs}"
        )
        """
        Encoding the username and password with base64 before sending to CAUTH server
        """
        authentication = f"{username}:{password}"
        encoded_bytes = base64.b64encode(authentication.encode("utf-8"))
        encoded_string = encoded_bytes.decode("utf-8")

        """
        Headers and payload preparation
        """
        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {encoded_string}",
        }
        request = "grant_type=client_credentials" + "&scope=" + (kwargs.get("scope") or scope)
        logger.debug(f"Oauth Request Payload: {request}")  # Fix for DNE-8457
        if kwargs.get("token_in_body", False):
            headers = {"Content-Type": "application/json"}
            request = kwargs["request_body"]
        logger.info(f"url {url} headers {headers} request {request}")
        response = session.post(url, headers=headers, data=request)
        logger.debug(f"{response.json()}: {response.status_code}")
        response.raise_for_status()
        # if response.status_code == 200:
        data = response.json()
        return data.get("access_token") if not kwargs.get("token_in_body", False) else data.get("token")
    except RequestException as err:
        raise RestUtilityException(f"Problem in accessing c-auth url " f"{url}: {err.args[0]}") from err
    except (ValueError, TypeError, AttributeError) as err:
        raise GenericConnectorsException(f"Problem in accessing c-auth url: {err.args[0]}") from err


def azure_ad_token_generator(ad_username, ad_password):
    """
    Generate access token remotely from Azure with the provided username and password
    client_id -  id received after registering on AAD.
    client_credential - string containing client secret.
    authority - URL that identifies a token authority.
    :param ad_username: username - email
    :param ad_password: password
    :return: access token value
    """
    logger.info("Fetching auth token from Azure AD")
    try:

        app = ConfidentialClientApplication(
            client_id=client_id, client_credential=client_credential, authority=authority
        )
        response = app.acquire_token_by_username_password(
            username=ad_username, password=ad_password, scopes=scopes.split()
        )
        if "access_token" not in response:
            raise GenericConnectorsException(
                f"Failed to receive authentication token from Azure with error {response.get('error')}. "
                f"For more information on this error please visit {response.get('error_uri')}"
            )
        return response["access_token"]
    except (ValueError, RuntimeError) as err:
        raise GenericConnectorsException(f"Problem in acquiring access token from Azure: {err.args[0]}") from err
