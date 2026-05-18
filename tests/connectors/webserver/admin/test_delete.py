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
from connectors.core.services.admin.delete import DeleteAdminDetails
from connectors.core.utils.exceptions import GenericConnectorsException
from connectors.webserver.admin.tasks.delete import delete_image_details, delete_upgrade_details

exception_add_device = [
    (
        Exception,
        {
            "status": "failure",
            "errorCategory": "FAILED",
            "errors": [
                {"code": "ERR-000-097-0500", "message": "Database Operation Failed Exception : dummy error message"}
            ],
        },
    ),
]


@patch("connectors.core.services.admin.delete.DeleteAdminDetails.delete_device_image")
def test_delete_image_details_try_block(delete_image_details_mock):
    """
    To test delete image details success scenario
    """
    # Mock the necessary dependencies
    mock_image_details_obj = MagicMock()
    mock_image_details_obj.delete_device_image.return_value = {"status": "success"}
    DeleteAdminDetails.return_value = mock_image_details_obj

    delete_image_details_mock.return_value = {"status": "success"}
    # Call the function
    result = delete_image_details(osVersionDeviceRegionId=2)

    # Assert the result
    assert result == {"status": "success"}


@patch("connectors.core.services.admin.delete.DeleteAdminDetails.delete_upgrade_details")
def test_delete_upgrade_details_try_block(delete_upgrade_details_mock):
    """
    To test delete upgrade details success scenario
    """
    # Mock the necessary dependencies
    mock_image_details_obj = MagicMock()
    mock_image_details_obj.delete_upgrade_details.return_value = {"status": "success"}
    DeleteAdminDetails.return_value = mock_image_details_obj

    delete_upgrade_details_mock.return_value = {"status": "success"}
    # Call the function
    result = delete_upgrade_details(osVersionUpgradeId=2)

    # Assert the result
    assert result == {"status": "success"}


@patch("connectors.core.services.admin.delete.DeleteAdminDetails.delete_device_image")
@pytest.mark.parametrize("exception_type, error_resp", exception_add_device)
def test_delete_image_details_except_block(delete_image_details_mock, exception_type, error_resp):
    """
    To test the exception block of delete image details
    1. Generic Exception occurred
    """
    delete_image_details_mock.side_effect = exception_type("dummy error message")
    response = delete_image_details(osVersionDeviceRegionId=2)
    assert response == error_resp


@patch("connectors.core.services.admin.delete.DeleteAdminDetails.delete_device_image")
def test_delete_image_details_except_block_1(delete_image_details_mock):
    """
    To test the GenericConnectorsException block of delete image details
    """
    delete_image_details_mock.side_effect = GenericConnectorsException
    response = delete_image_details(osVersionDeviceRegionId=2)
    assert response


@patch("connectors.core.services.admin.delete.DeleteAdminDetails.delete_upgrade_details")
@pytest.mark.parametrize("exception_type, error_resp", exception_add_device)
def test_delete_upgrade_details_except_block(delete_upgrade_details_mock, exception_type, error_resp):
    """
    To test the exception block of delete upgrade details
    1. Generic Exception occurred
    """
    delete_upgrade_details_mock.side_effect = exception_type("dummy error message")
    response = delete_upgrade_details(osVersionUpgradeId=2)
    assert response == error_resp


@patch("connectors.core.services.admin.delete.DeleteAdminDetails.delete_upgrade_details")
def test_delete_upgrade_details_except_block_1(delete_upgrade_details_mock):
    """
    To test the GenericConnectorsException block of delete upgrade details
    """
    delete_upgrade_details_mock.side_effect = GenericConnectorsException
    response = delete_upgrade_details(osVersionUpgradeId=2)
    assert response
