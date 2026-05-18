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
from unittest.mock import Mock, mock_open, patch

# Third Party Library
import jwt.exceptions as jwtException  # noqa: N812
import pytest
import requests
from requests.exceptions import RequestException

# DNE Library
from connectors.core.utils import oauth
from connectors.core.utils.exceptions import GenericConnectorsException, RestUtilityException
from connectors.core.utils.helpers import generic_secret
from connectors.core.utils.oauth import jwt

secret = generic_secret()

exception = [
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
]

logger = logging.getLogger(__name__)


@patch("requests.Session.post")
def test_token_generator(mock_session):
    """
    negative test to validate the token generator raises RestUtilityException
    """
    # session.post call will result in Exception
    mock_session.side_effect = RequestException("unit test triggered")
    with pytest.raises(RestUtilityException):
        oauth.token_generator()


@patch("requests.Session.post")
def test_access_token(mock_session):
    """
    positive test case to test access token generation
    """
    response_json = {"access_token": "dummy_token", "expires_in": 600, "token_type": "Bearer"}
    mock_session.return_value = response_simulation_function(status_code=200, json_data=response_json)
    token_gen = oauth.token_generator()
    assert token_gen == response_json["access_token"]


@patch("builtins.open", new_callable=mock_open, read_data="data")
def test_get_token_info_open_jwt_pub_file(mock_file, caplog):
    """
    test to check if File not Found Error Exception is handled
    """
    mock_file.side_effect = FileNotFoundError("manually created")
    oauth.get_token_info("dummy_token")
    assert " manually created while processing the file" in caplog.text


@patch("builtins.open", mock_open(read_data="data"))
@patch.object(jwt, "decode")
@pytest.mark.parametrize("jwt_exceptions", exception)
def test_get_token_with_jwt_exceptions(jwt_patch, jwt_exceptions, caplog):
    """
    test to check jwt.decode handles all Exceptions and logs in the logger
    """
    expected_log_message = "Error from JWT Exception manually created while decoding the token"
    jwt_patch.side_effect = jwt_exceptions("manually created")
    oauth.get_token_info("dummy token")
    assert expected_log_message in caplog.text


@patch("builtins.open", mock_open(read_data="data"))
@patch.object(jwt, "decode")
def test_get_token_verify_check(jwt_patch):
    """
    positive test to check get token utility retrives correct values
    """
    jwt_patch.return_value = {"clientId": "mocked_client", "scope": "read", "exp": 1666237367}
    oauth.token_expiration_validator = Mock()
    oauth.token_expiration_validator.return_value = False
    obj = oauth.get_token_info("dummy token")
    assert obj["sub"] == "mocked_client"
    assert obj["scopes"] == "read"


def response_simulation_function(status_code=200, json_data=None):
    """
    helper function to simulate the response object
    """
    resp = requests.Response()
    resp.status_code = status_code
    # the below function is added so that Json decoder call "response.json()" succeeds

    def json_func():
        return json_data

    resp.json = json_func
    return resp


@patch("connectors.core.utils.oauth.ConfidentialClientApplication")
def test_azure_ad_token_generator(mock_app):
    response_json = {
        "access_token": secret,
        "token_type": "example",
        "expires_in": 3600,
        "refresh_token": secret,
        "example_parameter": "example_value",
    }
    mock_app.return_value.acquire_token_by_username_password.return_value = response_json
    obj = oauth.azure_ad_token_generator("username", "password")
    assert obj == secret


@patch("connectors.core.utils.oauth.ConfidentialClientApplication")
def test_azure_ad_token_generator_fail(mock_app):
    response_json = {
        "error": "invalid_scope",
        "error_description": "AADSTS70011: The provided value for the input parameter 'scope' isn't valid.",
        "error_codes": [70011],
        "timestamp": "2016-01-09 02:02:12Z",
        "trace_id": "255d1aef-8c98-452f-ac51-23d051240864",
        "correlation_id": "fb3d2015-bc17-4bb9-bb85-30c5cf1aaaa7",
        "error_uri": "https://login.microsoftonline.com/error?code=70011",
    }
    mock_app.return_value.acquire_token_by_username_password.return_value = response_json
    with pytest.raises(GenericConnectorsException):
        oauth.azure_ad_token_generator("username", "password")


@patch("connectors.core.utils.oauth.ConfidentialClientApplication")
def test_azure_ad_token_generator_incorrect_username(mock_app):

    mock_app.return_value.acquire_token_by_username_password.side_effect = RuntimeError("authentication failed")
    with pytest.raises(GenericConnectorsException):
        oauth.azure_ad_token_generator("username", "password")
