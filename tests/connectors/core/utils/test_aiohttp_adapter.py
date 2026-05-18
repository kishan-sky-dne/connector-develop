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
from unittest.mock import AsyncMock, MagicMock, patch

# Third Party Library
import pytest

# # Third Party Library
from aiohttp import ClientResponseError

# DNE Library
from connectors.core.utils.aiohttp_adapter import AioRestUtility
from connectors.core.utils.helpers import generic_secret

secret = generic_secret()


def test_aio_rest_utility_constructor():
    """
    test case for checking constructor of AIO rest utility
    """
    aio_rest_obj = AioRestUtility(username="dummy-user", password=secret)
    assert aio_rest_obj.username == "dummy-user"
    assert aio_rest_obj.password == secret

    assert aio_rest_obj.authorization_via_tokens is None
    assert aio_rest_obj.timeout == 300


@patch("connectors.core.utils.oauth.token_generator", autospec=True, spec_set=True)
def test_access_token_validation(mocked):
    """
    test to validate if access token is present in the generated session obj
    """
    mocked.return_value = "dummy_token"
    aio_rest_obj = AioRestUtility(username="dummy-user", password=secret, authorization_via_tokens=True)
    assert aio_rest_obj.access_token == "dummy_token"
    expected_header = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer dummy_token",
    }
    assert aio_rest_obj.headers == expected_header


@pytest.mark.asyncio
async def test_aio_rest_api_get_status_code_200_case1():
    """
    positive test to validate the get aio rest api
    verified rest api called with correct params
    """
    dummy_url = "https://sparkproxyuat.azure-api.net/service3605/"
    mock_client_obj = AsyncMock()
    response = MagicMock(status=200)
    mock_client_obj.get.return_value = response
    aio_rest_obj = AioRestUtility(username="dummy-user", password=secret)
    response = await aio_rest_obj.get(mock_client_obj, dummy_url)
    assert response.status == 200


@pytest.mark.asyncio
@patch("connectors.core.utils.oauth.token_generator", autospec=True, spec_set=True)
async def test_aio_rest_api_get_status_200_with_headers(mocked):
    """
    positive test to validate the get aio rest api with headers
    """
    expect_head = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer dummy_token",
    }
    mocked.return_value = "dummy_token"
    dummy_url = "https://sparkproxyuat.azure-api.net/service3605/"
    mock_client_obj = AsyncMock()
    response = MagicMock(status_code=200, status="success")
    mock_client_obj.get.return_value = response
    aio_rest_obj = AioRestUtility(username="dummy-user", password=secret, authorization_via_tokens=True)
    response = await aio_rest_obj.get(mock_client_obj, dummy_url, headers=expect_head)
    assert response.status == "success"
    assert aio_rest_obj.headers == expect_head


@pytest.mark.asyncio
async def test_aio_rest_api_get_status_code_400():
    """
    negative test to validate the get rest api >> checks (response.raise_for_status())
    """
    aio_rest_obj = AioRestUtility(username="dummy-user", password=secret)
    dummy_url = "https://sparkproxyuat.azure-api.net/service3605/"
    client_session = MagicMock()
    client_session.get = AsyncMock()
    client_session.get.side_effect = ClientResponseError(
        status=404, message="FAILURE", request_info=MagicMock(), history=None
    )
    resp = await aio_rest_obj.get(client_session, url=dummy_url)
    assert resp.status == 404


@pytest.mark.asyncio
async def test_aio_rest_api_post_status_code_200_case1():
    """
    positive test to validate the post aio rest api
    verified rest api called with correct params
    """
    dummy_url = "https://sparkproxyuat.azure-api.net/service3605/"
    mock_client_obj = AsyncMock()
    response = MagicMock(status=200)
    mock_client_obj.post.return_value = response
    aio_rest_obj = AioRestUtility(username="dummy-user", password=secret)
    response = await aio_rest_obj.post(mock_client_obj, dummy_url)
    assert response.status == 200


@pytest.mark.asyncio
async def test_aio_rest_api_post_status_code_200_case2():
    """
    positive test to validate the post aio rest api
    verified rest api called with correct params
    """
    dummy_url = "https://sparkproxyuat.azure-api.net/service3605/"
    mock_client_obj = AsyncMock()
    response = MagicMock(status_code=200, status="SUCCESS")
    mock_client_obj.post.return_value = response
    aio_rest_obj = AioRestUtility(username="dummy-user", password=secret)
    response = await aio_rest_obj.post(mock_client_obj, dummy_url)
    assert response.status_code == 200
    assert response.status == "SUCCESS"


@pytest.mark.asyncio
@patch("connectors.core.utils.oauth.token_generator", autospec=True, spec_set=True)
async def test_aio_rest_api_post_status_200_with_headers(mocked):
    """
    positive test to validate the post aio rest api
    verified rest api called with correct headers
    """
    expect_head = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer dummy_token",
    }
    mocked.return_value = "dummy_token"
    dummy_url = "https://sparkproxyuat.azure-api.net/service3605/"
    mock_client_obj = AsyncMock()
    response = MagicMock(status_code=200, status="success")
    mock_client_obj.post.return_value = response
    aio_rest_obj = AioRestUtility(username="dummy-user", password=secret, authorization_via_tokens=True)
    response = await aio_rest_obj.post(mock_client_obj, dummy_url, headers=expect_head)
    assert response.status == "success"
    assert aio_rest_obj.headers == expect_head


@pytest.mark.asyncio
async def test_aio_rest_api_post_status_code_400():
    """
    negative test to validate the post rest api >> checks (response.raise_for_status())
    """
    aio_rest_obj = AioRestUtility(username="dummy-user", password=secret)
    dummy_url = "https://sparkproxyuat.azure-api.net/service3605/"
    client_session = MagicMock()
    client_session.post = AsyncMock()
    client_session.post.side_effect = ClientResponseError(
        status=404, message="FAILURE", request_info=MagicMock(), history=None
    )
    resp = await aio_rest_obj.post(client_session, url=dummy_url)
    assert resp.status == 404
