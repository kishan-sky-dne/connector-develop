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

# DNE Library
from connectors.core.services.admin.inventory_details import InventoryDetails
from connectors.core.utils.exceptions import GenericConnectorsException
from connectors.webserver.admin.tasks.inventory_details import get_inventory_details


@patch("connectors.core.services.admin.inventory_details.InventoryDetails.get_inventory_details")
def test_get_inventory_details_try_block(get_inventory_details_mock):
    """
    To test get inventory details
    :param get_inventory_details_mock:
    :return:
    """
    mock_include = ["deviceVendor", "deviceModel", "region", "deviceRole", "osState", "packageType", "fileType"]
    mock_inventory_details = {
        "deviceVendor": [],
        "deviceModel": [],
        "region": [],
        "deviceRole": [],
        "osState": [],
        "packageType": [],
        "fileType": [],
    }
    mock_inventory_details_obj = MagicMock()
    mock_inventory_details_obj.get_inventory_details.return_value = mock_inventory_details
    InventoryDetails.return_value = mock_inventory_details_obj

    get_inventory_details_mock.return_value = {
        "deviceVendor": [],
        "deviceModel": [],
        "region": [],
        "deviceRole": [],
        "osState": [],
        "packageType": [],
        "fileType": [],
    }
    result = get_inventory_details(_include=mock_include)

    assert result == mock_inventory_details


@patch("connectors.core.services.admin.inventory_details.InventoryDetails.get_inventory_details")
def test_get_inventory_details_except_block(get_inventory_details_mock):
    """
    To test the exception block of get inventory details
    :param get_inventory_details_mock:
    :return:
    """
    # Mock the necessary dependencies
    mock_include = None
    mock_error_message = "Test error message"
    mock_exception = GenericConnectorsException(mock_error_message)
    InventoryDetails.side_effect = mock_exception
    get_inventory_details_mock.return_value = {
        "status": "failure",
        "errorCategory": "FAILED",
        "errors": [{"code": "ERR-000-097-0500", "message": f"Database operation failure: {mock_error_message}"}],
    }
    result = get_inventory_details(_include=mock_include)
    expected_result = {
        "status": "failure",
        "errorCategory": "FAILED",
        "errors": [{"code": "ERR-000-097-0500", "message": f"Database operation failure: {mock_error_message}"}],
    }
    assert result == expected_result
