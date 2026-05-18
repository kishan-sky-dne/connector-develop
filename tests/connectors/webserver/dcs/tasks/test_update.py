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
import flask
import pytest

# DNE Library
from connectors.core.exceptions import ConnectorsException
from connectors.core.utils.exceptions import RestUtilityException
from connectors.webserver.dcs.tasks import update

app = flask.Flask(__name__)

payload_update_device = [
    {"op": "replace", "attribute": "status", "value": "production"},
    {"op": "add", "attribute": "owner", "value": "test"},
]

exception_update_device = [
    (RestUtilityException, 400),
    (ValueError, 500),
    (TypeError, 500),
    (AttributeError, 500),
    (KeyError, 500),
    (ConnectorsException, 500),
]


@patch("connectors.webserver.dcs.tasks.update.CacheController")
@patch("connectors.core.services.dcs.connector.DeviceConfigurationService.update_device")
def test_update_device_success(mock_core_update_device, cache_mock):
    """
    Test to check the functionality of update_device(webserver.dcs.tasks.update) success case.
    Note : update_device (core.services.dcs.connectors) is being mocked here. It is being tested separately under
    core.services.dcs.connectors
    """
    with app.test_request_context() as req_mock:
        req_mock.base_url = "test_url"
        req_mock.path = "test_path"
        mock_core_update_device.return_value = "SUCCESS"
        response = update.update_device(body=payload_update_device, hostname="xyz.test.bllab")
        assert response == "SUCCESS"


@patch("connectors.webserver.dcs.tasks.update.CacheController")
@patch("connectors.core.services.dcs.connector.DeviceConfigurationService.update_device")
def test_update_device_failed(mock_core_update_device, cache_mock):
    """
    Test to check the functionality of update_device(webserver.dcs.tasks.update) failure case.
    Note : update_device (core.services.dcs.connectors) is being mocked here. It is being tested separately under
    core.services.dcs.connectors
    """
    with app.test_request_context() as req_mock:
        req_mock.base_url = "test_url"
        req_mock.path = "test_path"
        mock_core_update_device.return_value = "FAILURE"
        response = update.update_device(body=payload_update_device, hostname="xyz.test.bllab")
        assert response == "FAILURE"


@patch("connectors.core.services.dcs.connector.DeviceConfigurationService.update_device")
@pytest.mark.parametrize("exception_type, error_code", exception_update_device)
def test_update_device_raises_exception(mock_core_update_device, exception_type, error_code):
    """
    Test to check if update_device raises different exceptions.
    """
    mock_core_update_device.side_effect = exception_type("dummy error message")
    response = update.update_device(body=payload_update_device, hostname="xyz.test.bllab")
    assert response.status_code == error_code


payload_update_device_1 = [
    {"op": "replace", "attribute": "status", "value": "production"},
    {"op": "add", "attribute": "owner"},
]


@patch("connectors.core.services.dcs.connector.DeviceConfigurationService.update_device")
def test_update_device_failed_case2(mock_core_update_device):
    """
    Test to check the functionality of update_device(webserver.dcs.tasks.update) failure case.
    Note : update_device (core.services.dcs.connectors) is being mocked here. It is being tested separately under
    core.services.dcs.connectors
    """
    response = update.update_device(body=payload_update_device_1, hostname="xyz.test.bllab")
    assert response == {
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-007-999-0001",
                "message": "value param must be provided for index 1 as op value is add",
            }
        ],
    }
