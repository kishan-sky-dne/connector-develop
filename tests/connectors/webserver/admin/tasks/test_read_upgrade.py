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
from unittest.mock import MagicMock, patch

# Third Party Library
import pytest

# DNE Library
from connectors.core.services.admin.read_upgrade_details import UpgradeDetails
from connectors.core.utils.exceptions import GenericConnectorsException
from connectors.webserver.admin.tasks.read_upgrade import read_upgrade_details

upgrade_details = {
    "limit": 3,
    "offset": 0,
    "resultSet": [
        {
            "currentLabel": "7.1.0-V1",
            "currentState": "Deprecated",
            "currentVersion": "7.1.0",
            "deviceModel": "NCS5K",
            "deviceVendor": "CISCO",
            "osVersionUpgradeId": 2,
            "region": "UK",
            "targetLabel": "7.5.1-V1",
            "targetState": "Current",
            "targetVersion": "7.5.1",
        },
        {
            "currentLabel": "7.1.0-V1",
            "currentState": "Deprecated",
            "currentVersion": "7.1.0",
            "deviceModel": "NCS5K",
            "deviceVendor": "CISCO",
            "osVersionUpgradeId": 5,
            "region": "UK",
            "targetLabel": "7.3.0-V1",
            "targetState": "Current",
            "targetVersion": "7.3.0",
        },
        {
            "currentLabel": "7.3.0-V1",
            "currentState": "Current",
            "currentVersion": "7.3.0",
            "deviceModel": "NCS5K",
            "deviceVendor": "CISCO",
            "osVersionUpgradeId": 8,
            "region": "UK",
            "targetLabel": "7.5.1-V1",
            "targetState": "Current",
            "targetVersion": "7.5.1",
        },
    ],
    "total": 3,
}

exception_details = [
    (
        Exception,
        {
            "status": "failure",
            "errorCategory": "FAILED",
            "errors": [{"code": "ERR-000-097-0500", "message": "Database Operation Failed : dummy error message"}],
        },
    ),
]

params = {"include": "brief", "limit": 3, "offset": 0, "region": "UK", "deviceVendor": "CISCO", "deviceModel": "NCS5K"}


@patch("connectors.core.services.admin.read_upgrade_details.UpgradeDetails.get_upgrade_details")
def test_upgrade_details_try_block(get_upgrade_details_mock):
    """
    To test get upgrade details
    :param get_upgrade_details_mock:
    :return:
    """
    # Mock the necessary dependencies
    mock_upgrade_details = upgrade_details
    mock_upgrade_details_obj = MagicMock()
    mock_upgrade_details_obj.image_upgrade_details.return_value = mock_upgrade_details
    UpgradeDetails.return_value = mock_upgrade_details_obj

    get_upgrade_details_mock.return_value = upgrade_details
    # Call the function
    result = read_upgrade_details(**params)
    # Assert the result
    assert result == mock_upgrade_details


@patch("connectors.core.services.admin.read_upgrade_details.UpgradeDetails.get_upgrade_details")
@pytest.mark.parametrize("exception_type, error_resp", exception_details)
def test_upgrade_details_except_block(get_upgrade_details_mock, exception_type, error_resp):
    """
    To test the exception block of get upgrade details
    :param get_upgrade_details_mock:
    :return:
    """
    get_upgrade_details_mock.side_effect = exception_type("dummy error message")
    response = read_upgrade_details(**params)
    assert response == error_resp


@patch("connectors.core.services.admin.read_upgrade_details.UpgradeDetails.get_upgrade_details")
def test_upgrade_details_except_block_1(get_upgrade_details_mock):
    """
    To test the GenericConnectorsException block of get upgrade details
    :param get_upgrade_details_mock:
    :return:
    """
    get_upgrade_details_mock.side_effect = GenericConnectorsException
    response = read_upgrade_details(**params)
    assert response
