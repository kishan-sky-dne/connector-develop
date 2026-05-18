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
from unittest.mock import MagicMock

# Third Party Library
import pytest

# DNE Library
from connectors.core.services.admin.inventory_details import InventoryDetails


def test_inventorydetails():
    """
     test to create inventory details Instance
    :return:
    """
    include = ["deviceVendor", "deviceRole", "deviceModel", "os_state"]

    device_obj = InventoryDetails(
        include,
    )
    assert isinstance(device_obj, InventoryDetails)
    assert device_obj.include == ["deviceVendor", "deviceRole", "deviceModel", "os_state"]


params1 = ["deviceVendor"]
result1 = {"deviceVendor": [{"deviceId": "1", "vendor": "CISCO"}]}

params2 = ["deviceModel"]
result2 = {"deviceModel": [{"deviceId": "1", "model": "NCS540"}]}

params3 = ["region"]
result3 = {"region": [{"region": "UK", "regionId": "1"}]}

params4 = ["currentState"]
result4 = {"currentState": [{"state": "Decommissioned", "stateId": "1"}]}

params5 = ["deviceRole"]
result5 = {"deviceRole": [{"role": "SUPER CORE", "roleId": "1"}]}

params6 = ["fileType"]
result6 = {"fileType": [{"file": "tar", "fileId": "1"}]}

params7 = ["packageType"]
result7 = {"packageType": [{"package": "XR", "packageId": "1"}]}

case = [
    (params1, [(1, "CISCO")], result1),
    (params2, [(1, "NCS540")], result2),
    (params3, [(1, "UK")], result3),
    (params4, [(1, "Decommissioned")], result4),
    (params5, [(1, "SUPER CORE")], result5),
    (params6, [(1, "tar")], result6),
    (params7, [(1, "XR")], result7),
]


@pytest.mark.parametrize("case", case)
def test_get_inventory_details(case):
    """
    scenario 1: Validate the inventory details function with deviceVendor param
    scenario 2: Validate the inventory details function with deviceModel param
    scenario 3: Validate the inventory details function with region param
    scenario 4: VValidate the inventory details function with currentstate param
    scenario 5: Validate the inventory details function with deviceRole param
    scenario 6: Validate the inventory details function with fieldType param
    scenario 7: Validate the inventory details function with packageType param
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Configure the return value of the session's query method to return the mock result
    mock_session.query.return_value = case[1]  # Wrap the mock_result in a list

    mock_sql_instance.transactional_session.return_value.__enter__.return_value = mock_session
    # Create an instance of InventoryDetails using the mocked SqlDB
    inventory = InventoryDetails(case[0])
    inventory.sql_instance = mock_sql_instance
    # Call the method being tested
    result = inventory.get_inventory_details()

    # Assertions
    assert result == case[2]


def test_get_inventory_details_service_db_exception():
    """
    To test the case of service DB expression
    :return:
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Configure the mocked SqlDB to raise a ServiceDBException when transactional_session is called
    mock_sql_instance.transactional_session.side_effect = AttributeError("Error occurred")

    # Create an instance of InventoryDetails using the mocked SqlDB
    inventory = InventoryDetails(["deviceVendor"])
    inventory.sql_instance = mock_sql_instance

    # Call the method being tested
    result = inventory.get_inventory_details()

    # Assertions
    assert result == {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-0500",
                "message": "Exception occurred while performing get inventory details from tables : AttributeError",
            }
        ],
    }


def test_get_inventory_details_generic_exception():
    """
    To test the case of generic expression
    :return:
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Configure the mocked SqlDB to raise a generic Exception when transactional_session is called
    mock_sql_instance.transactional_session.side_effect = Exception("Error occurred")

    # Create an instance of InventoryDetails using the mocked SqlDB
    inventory = InventoryDetails(["deviceVendor"])
    inventory.sql_instance = mock_sql_instance

    # Call the method being tested
    result = inventory.get_inventory_details()

    # Assertions
    assert result == {
        "status": "failure",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-0500",
                "message": "Generic Exception occurred while performing get inventory details from tables : Exception",
            }
        ],
    }
