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
from unittest.mock import patch

# Third Party Library
import pytest

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.utils.exceptions import RestUtilityException
from connectors.core.utils.helpers import generic_secret
from connectors.core.utils.rest_api_utility import RestUtility, requests

secret = generic_secret()

error_codes = config.get(section="session", key="error_codes")
error_codes = tuple(int(i) for i in error_codes.split(","))
backoff_factor = float(config.get(section="session", key="backoff_factor"))
max_retries = int(config.get(section="session", key="max_retries") or 1)
verify = config.get(section="session", key="verify")


def test_rest_api_utility_constructor():
    """
    test for checking __init__ of rest api
    """
    obj = RestUtility(username="dummy-user", password=secret)
    assert obj.username == "dummy-user"
    assert obj.password == secret
    assert obj.authorization_via_tokens is None
    assert obj.timeout == 300
    assert obj.authorization_via_tokens is None
    # session obj
    # ssl_cert
    assert obj.session.client is None
    assert isinstance(obj.session, requests.sessions.Session)
    assert obj.session.auth == ("dummy-user", secret)
    assert obj.session.verify == verify


def test_session_attributes_without_validation():
    """
    test to validate the header , retry attribute in the session object
    """
    # header
    expected_header = {"accept": "application/json", "Content-Type": "application/json"}
    obj = RestUtility(username="dummy-user", password=secret)
    assert obj.headers == expected_header
    assert obj.headers.get("Authorization") is None
    # retry object
    retry_obj = obj.max_retries.max_retries
    assert retry_obj.total == max_retries
    assert retry_obj.connect == max_retries
    assert retry_obj.read == max_retries
    assert retry_obj.backoff_factor == backoff_factor
    assert retry_obj.raise_on_status is False
    assert retry_obj.status_forcelist == error_codes
    with pytest.raises(AttributeError):
        assert obj.access_token is None


@patch("connectors.core.utils.oauth.token_generator", autospec=True, spec_set=True)
def test_access_token_validation(mocked):
    """
    test to validate if access token is present in the generated session obj
    """
    mocked.return_value = "dummy_token"
    obj = RestUtility(username="dummy-user", password=secret, authorization_via_tokens=True)
    assert obj.access_token == "dummy_token"
    # header
    expect_head = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer dummy_token",
    }
    assert obj.headers == expect_head


@patch("connectors.core.utils.rest_api_utility.requests.Session.get", autospec=True, spec_set=True)
def test_rest_api_get_status_code_400(mocked):
    """
    negative test to validate the get rest api >> checks (response.raise_for_status())
    """
    obj = RestUtility(username="dummy-user", password=secret)
    mocked.return_value = response_simulation_function("failed", 400)
    with pytest.raises(RestUtilityException):
        obj.get(url="http://hello.com")


@patch("connectors.core.utils.rest_api_utility.requests.Session.get")
def test_rest_api_get_status_code_200(mocked):
    """
    positive test to validate the get rest api
    verified rest api called with correct params
    """
    expect_head = {"accept": "application/json", "Content-Type": "application/json"}
    obj = RestUtility(username="dummy-user", password=secret)
    mocked.return_value = response_simulation_function("success", 200)
    response = obj.get(url="http://hello.com")
    assert isinstance(response, dict)
    mocked.assert_called_once_with(url="http://hello.com", params=None, timeout=300, headers=expect_head)


@patch("connectors.core.utils.rest_api_utility.requests.Session.get")
def test_rest_api_get_status_code_200_with_headers(mocked):
    """
    positive test to validate the get rest api
    """
    expect_head = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "X-Request-ID": None,
        "Authorization": "Bearer dummy_token",
    }
    obj = RestUtility(username="dummy-user", password=secret)
    mocked.return_value = response_simulation_function("success", 200)
    response = obj.get(url="http://hello.com", params="dummy", timeout=30, headers=expect_head)
    assert isinstance(response, dict)
    mocked.assert_called_once_with(url="http://hello.com", params="dummy", timeout=30, headers=expect_head)


@patch("connectors.core.utils.rest_api_utility.requests.Session.get")
def test_rest_api_get_status_code_200_1(mocked):
    """
    positive test to validate the get rest api
    """
    expect_head = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "X-Request-ID": None,
        "Authorization": "Bearer dummy_token",
    }
    json_data = {"admin_group": "sky", "tacacs_secret": "fdskfslfkslad", "os": ""}
    obj = RestUtility(username="dummy-user", password=secret)
    mocked.return_value = response_simulation_function("success", 200, json_data=json_data)
    response = obj.get(url="http://hello.com", params="dummy", timeout=30, headers=expect_head)
    assert response == json_data


@patch.object(requests.Session, "get")
@patch("connectors.core.utils.rest_api_utility.oauth")
def test_rest_api_get_with_authorization_patch(mock_oauth, mock_get):
    """
    get api with authorization token enabled and token_info mocked to None
    verified the response is dict and validating the get rest api called with expected header
    """
    expect_head = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer valid_token",
    }
    mock_oauth.token_generator.return_value = "valid_token"
    mock_oauth.get_token_info.return_value = None
    mock_get.return_value = response_simulation_function("success", 200)
    obj = RestUtility(username="dummy-user", password=secret, authorization_via_tokens=True)
    response = obj.get(url="http://hello.com", data="iron", params="dummy", timeout=30)
    assert isinstance(response, dict)
    mock_get.assert_called_once_with(url="http://hello.com", params="dummy", timeout=30, headers=expect_head)


@patch.object(requests.Session, "get")
@patch("connectors.core.utils.rest_api_utility.oauth")
def test_rest_api_get_with_authorization_patch_with_token(mock_oauth, mock_get):
    """
    get api with authorization token enabled and token_info is enabled
    verified the response is dict and validating the get rest api called with expected header
    """
    expect_head = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer dummy_token",
    }
    mock_oauth.token_generator.return_value = "dummy_token"
    mock_oauth.get_token_info.return_value = True
    obj = RestUtility(username="dummy-user", password=secret, authorization_via_tokens=True)
    mock_get.return_value = response_simulation_function("success", 200)
    response = obj.get(url="http://hello.com", data="iron", params="dummy", timeout=30)
    assert isinstance(response, dict)
    mock_get.assert_called_once_with(url="http://hello.com", params="dummy", timeout=30, headers=expect_head)


@patch("connectors.core.utils.rest_api_utility.requests.Session.post", autospec=True, spec_set=True)
def test_rest_api_post_status_code_400(mocked):
    """
    negative test to validate the post rest api
    verified response raise status
    """
    mocked.return_value = response_simulation_function("failed", 400)
    obj = RestUtility(username="dummy-user", password=secret)
    with pytest.raises(RestUtilityException):
        obj.post(url="http://hello.com", data="iron-man")


@patch("connectors.core.utils.rest_api_utility.requests.Session.post")
def test_rest_api_post_status_code_200(mocked):
    """
    positive test to validate the post rest api
    """
    expect_head = {"accept": "application/json", "Content-Type": "application/json"}
    mocked.return_value = response_simulation_function("success", 200)
    obj = RestUtility(username="dummy-user", password=secret)
    response = obj.post(url="http://hello.com", data="iron-man", status_code_flag=False)
    assert isinstance(response, dict)
    mocked.assert_called_once_with(
        url="http://hello.com", data="iron-man", params=None, timeout=300, headers=expect_head
    )


@patch("connectors.core.utils.rest_api_utility.requests.Session.post")
def test_rest_api_post_status_code_200_with_headers(mocked):
    """
    positive test to validate the post rest api
    """
    expect_head = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer dummy_token",
    }
    obj = RestUtility(username="dummy-user", password=secret)
    mocked.return_value = response_simulation_function("success", 200)
    response = obj.post(url="http://hello.com", data="iron", params="dummy", timeout=30, headers=expect_head)
    assert isinstance(response, dict)
    mocked.assert_called_once_with(url="http://hello.com", data="iron", params="dummy", timeout=30, headers=expect_head)


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.oauth")
def test_rest_api_post_with_authorization_patch(mock_oauth, mock_post):
    """
    post api with authorization token enabled and token_info mocked to None
    verified the response is dict and validating the get rest api called with expected header
    """
    expect_head = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer dummy_token",
    }
    mock_oauth.token_generator.return_value = "dummy_token"
    mock_oauth.get_token_info.return_value = None
    obj = RestUtility(username="dummy-user", password=secret, authorization_via_tokens=True)
    mock_post.return_value = response_simulation_function("success", 200)
    response = obj.post(url="http://hello.com", data="iron", params="dummy", timeout=30)
    assert isinstance(response, dict)
    mock_post.assert_called_once_with(
        url="http://hello.com", data="iron", params="dummy", timeout=30, headers=expect_head
    )


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.oauth")
def test_rest_api_post_with_authorization_patch_with_token(mock_oauth, mock_post):
    """
    post api with authorization token enabled and token_info mocked to True
    verified the response is dict and validating the get rest api called with expected header
    """
    expect_head = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer dummy_token",
    }
    mock_oauth.token_generator.return_value = "dummy_token"
    mock_oauth.get_token_info.return_value = True
    obj = RestUtility(username="dummy-user", password=secret, authorization_via_tokens=True)
    mock_post.return_value = response_simulation_function("success", 200)
    response = obj.post(url="http://hello.com", data="iron", params="dummy", timeout=30)
    assert isinstance(response, dict)
    mock_post.assert_called_once_with(
        url="http://hello.com", data="iron", params="dummy", timeout=30, headers=expect_head
    )


@patch("connectors.core.utils.rest_api_utility.requests.Session.patch", autospec=True, spec_set=True)
def test_rest_api_patch_status_code_400(mocked):
    """
    negative test to validate the patch rest api
    verified response raise status
    """
    mocked.return_value = response_simulation_function("failed", 400)
    obj = RestUtility(username="dummy-user", password=secret)
    with pytest.raises(RestUtilityException):
        obj.patch(url="http://hello.com", data="iron-man")


@patch("connectors.core.utils.rest_api_utility.requests.Session.patch")
def test_rest_api_patch_status_code_200(mocked):
    """
    positive test to validate the patch rest api
    """
    expect_head = {"accept": "application/json", "Content-Type": "application/json"}
    mocked.return_value = response_simulation_function("success", 200)
    obj = RestUtility(username="dummy-user", password=secret)
    response = obj.patch(url="http://hello.com", data="iron-man")
    assert isinstance(response, dict)
    mocked.assert_called_once_with(
        url="http://hello.com", data="iron-man", params=None, timeout=300, headers=expect_head
    )


@patch("connectors.core.utils.rest_api_utility.requests.Session.patch")
def test_rest_api_patch_status_code_200_with_headers(mocked):
    """
    positive test to validate the patch rest api
    """
    expect_head = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer dummy_token",
    }
    obj = RestUtility(username="dummy-user", password=secret)
    mocked.return_value = response_simulation_function("success", 200)
    response = obj.patch(url="http://hello.com", data="iron", params="dummy", timeout=30, headers=expect_head)
    assert isinstance(response, dict)
    mocked.assert_called_once_with(url="http://hello.com", data="iron", params="dummy", timeout=30, headers=expect_head)


@patch.object(requests.Session, "patch")
@patch("connectors.core.utils.rest_api_utility.oauth")
def test_rest_api_patch_with_authorization_patch(mock_oauth, mock_patch):
    """
    patch api with authorization token enabled and token_info mocked to None
    verified the response is dict and validating the get rest api called with expected header
    """
    expect_head = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer dummy_token",
    }
    mock_oauth.token_generator.return_value = "dummy_token"
    mock_oauth.get_token_info.return_value = None
    obj = RestUtility(username="dummy-user", password=secret, authorization_via_tokens=True)
    mock_patch.return_value = response_simulation_function("success", 200)
    response = obj.patch(url="http://hello.com", data="iron", params="dummy", timeout=30)
    assert isinstance(response, dict)
    mock_patch.assert_called_once_with(
        url="http://hello.com", data="iron", params="dummy", timeout=30, headers=expect_head
    )


@patch.object(requests.Session, "patch")
@patch("connectors.core.utils.rest_api_utility.oauth")
def test_rest_api_patch_with_authorization_patch_with_token(mock_oauth, mock_patch):
    """
    patch api with authorization token enabled and token_info mocked to True
    verified the response is dict and validating the get rest api called with expected header
    """
    expect_head = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer dummy_token",
    }
    mock_oauth.token_generator.return_value = "dummy_token"
    mock_oauth.get_token_info.return_value = True
    obj = RestUtility(username="dummy-user", password=secret, authorization_via_tokens=True)
    mock_patch.return_value = response_simulation_function("success", 200)
    response = obj.patch(url="http://hello.com", data="iron", params="dummy", timeout=30)
    assert isinstance(response, dict)
    mock_patch.assert_called_once_with(
        url="http://hello.com", data="iron", params="dummy", timeout=30, headers=expect_head
    )


@patch("connectors.core.utils.rest_api_utility.requests.Session.put", autospec=True, spec_set=True)
def test_rest_api_put_status_code_400(mocked):
    """
    test for checking rest api put with 400 status code
    """
    mocked.return_value = response_simulation_function("failed", 400)
    obj = RestUtility(username="dummy-user", password=secret)
    with pytest.raises(RestUtilityException):
        obj.put(url="http://hello.com", data="iron-man")


@patch("connectors.core.utils.rest_api_utility.requests.Session.put")
def test_rest_api_put_status_code_200(mocked):
    """
    test for checking rest api put with 200 status code
    """
    expect_head = {"accept": "application/json", "Content-Type": "application/json"}
    mocked.return_value = response_simulation_function("success", 200)
    obj = RestUtility(username="dummy-user", password=secret)
    response = obj.put(url="http://hello.com", data="iron-man")
    assert isinstance(response, dict)
    mocked.assert_called_once_with(
        url="http://hello.com", data="iron-man", params=None, timeout=300, headers=expect_head
    )


@patch("connectors.core.utils.rest_api_utility.requests.Session.put")
def test_rest_api_put_status_code_200_with_headers(mocked):
    """
    positive test to validate the patch rest api
    """
    expect_head = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer dummy_token",
    }
    obj = RestUtility(username="dummy-user", password=secret)
    mocked.return_value = response_simulation_function("success", 200)
    response = obj.put(url="http://hello.com", data="iron", params="dummy", timeout=30, headers=expect_head)
    assert isinstance(response, dict)
    mocked.assert_called_once_with(url="http://hello.com", data="iron", params="dummy", timeout=30, headers=expect_head)


@patch.object(requests.Session, "put")
@patch("connectors.core.utils.rest_api_utility.oauth")
def test_rest_api_put_with_authorization_patch(mock_oauth, mock_put):
    """
    put api with authorization token enabled and token_info mocked to None
    verified the response is dict and validating the get rest api called with expected header
    """
    expect_head = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer dummy_token",
    }
    mock_oauth.token_generator.return_value = "dummy_token"
    mock_oauth.get_token_info.return_value = None
    obj = RestUtility(username="dummy-user", password=secret, authorization_via_tokens=True)
    mock_put.return_value = response_simulation_function("success", 200)
    response = obj.put(url="http://hello.com", data="iron", params="dummy", timeout=30)
    assert isinstance(response, dict)
    mock_put.assert_called_once_with(
        url="http://hello.com", data="iron", params="dummy", timeout=30, headers=expect_head
    )


@patch.object(requests.Session, "put")
@patch("connectors.core.utils.rest_api_utility.oauth")
def test_rest_api_put_with_authorization_patch_with_token(mock_oauth, mock_put):
    """
    put api with authorization token enabled and token_info mocked to True
    verified the response is dict and validating the get rest api called with expected header
    """
    expect_head = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer dummy_token",
    }
    mock_oauth.token_generator.return_value = "dummy_token"
    mock_oauth.get_token_info.return_value = True
    obj = RestUtility(username="dummy-user", password=secret, authorization_via_tokens=True)
    mock_put.return_value = response_simulation_function("success", 200)
    response = obj.put(url="http://hello.com", data="iron", params="dummy", timeout=30)
    assert isinstance(response, dict)
    mock_put.assert_called_once_with(
        url="http://hello.com", data="iron", params="dummy", timeout=30, headers=expect_head
    )


def response_simulation_function(title="empty", status_code=200, json_data=None):
    """
    helper function to simulate the response object
    """
    data = json_data or {"title": title}
    resp = requests.Response()
    resp.status_code = status_code
    # the below function is added so that Json decoder call "response" succeeds

    def json_func():
        return data

    resp.json = json_func
    return resp
