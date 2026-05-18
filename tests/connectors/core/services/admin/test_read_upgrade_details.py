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
from unittest.mock import MagicMock, Mock, patch

# Third Party Library
import pytest
from test_read_upgrade_details_input import (  # sourcery skip
    error_params,
    filter_error_params,
    image_detail_case,
    os_error_params,
    read_cases,
    service_check_case,
    service_error_params,
    source_error_params,
    target_error_params,
    test_cases_get_custom_config,
    traffic_error_params,
)

# DNE Library
from connectors.core.services.admin.read_upgrade_details import UpgradeDetails


@patch("connectors.core.services.admin.read_upgrade_details.query_count")
@pytest.mark.parametrize("params", read_cases)
def test_get_upgrade_details_case(count_mock, params):
    """
    Verify get_directory_details
    Case1: verify directory details when filePath parameter alone given
    Case2: verify directory details when filePath and location parameters are given
    Case3: Verify Failure Exception case
    """
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Configure the return value of the session's query method to return the mock result
    mock_sql_instance.transactional_session.return_value.__enter__.return_value = mock_session
    # Create an instance of InventoryDetails using the mocked SqlDB
    update = UpgradeDetails(**params["kwargs"])
    update.sql_instance = mock_sql_instance
    update.source_query = MagicMock()
    update.target_query = MagicMock()
    update.os_details_query = MagicMock()
    update.package_query = MagicMock()
    update.traffic_diversion_query = MagicMock()
    update.get_custom_config = MagicMock()
    update.file_query = Mock(return_value="iso")
    mock_session.query.return_value.get.return_value = params.get("role", "")
    count_mock.return_value = params["count"]
    update.source_query.return_value.filter.return_value.filter.return_value.filter.return_value = params.get(
        "source_data"
    )
    update.target_query.return_value.filter.return_value.filter.return_value.filter.return_value = params.get(
        "target_data"
    )
    update.get_custom_config.return_value = params.get("custom_config_data")
    if params.get("kwargs").get("osVersionUpgradeId"):
        update.source_query.return_value.filter.return_value = params.get("source_data")
        update.target_query.return_value = params.get("target_data")

    update.os_details_query.return_value.filter.return_value = params.get("image_data")
    update.package_query.return_value = params.get("package_data")
    update.traffic_diversion_query.return_value = params.get("traffic_data")
    # Call the method being tested
    result = update.get_upgrade_details()

    # Assertions
    assert result == params["final_response"]


@patch("connectors.core.services.admin.read_upgrade_details.query_count")
def test_get_upgrade_details_case_2(count_mock):
    """
    Verify get_upgrade_details for image case
    Case1: _include = imageDetail fetch all image details from table
    """
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Configure the return value of the session's query method to return the mock result
    mock_sql_instance.transactional_session.return_value.__enter__.return_value = mock_session
    # Create an instance of InventoryDetails using the mocked SqlDB
    update = UpgradeDetails(**image_detail_case["kwargs"])
    update.sql_instance = mock_sql_instance
    update.source_query = MagicMock()
    update.target_query = MagicMock()
    update.os_details_query = MagicMock()
    update.package_query = MagicMock()
    update.traffic_diversion_query = MagicMock()
    update.file_query = Mock(return_value="iso")
    count_mock.return_value = image_detail_case["count"]
    update.os_details_query.return_value = image_detail_case["image_data"]
    update.package_query.return_value = image_detail_case["package_data"]
    # Call the method being tested
    result = update.get_upgrade_details()

    # Assertions
    assert result == image_detail_case["final_response"]


@pytest.mark.parametrize("params", error_params)
def test_get_upgrade_details_exception(params):
    """
    To test the case of get upgrade details exception
    :return:
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Configure the mocked SqlDB to raise a Exception when transactional_session is called
    mock_sql_instance.transactional_session.side_effect = params["exception"]

    # Create an instance of ImageDetails using the mocked SqlDB
    update = UpgradeDetails(**params)
    update.sql_instance = mock_sql_instance
    update.source_query = MagicMock()
    update.target_query = MagicMock()
    # Call the method being tested
    result = update.get_upgrade_details()

    # Assertions
    assert result == {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-0500",
                "message": f"{params['message']} : {params['value']}",
            }
        ],
    }


test_data = {
    "_include": "brief",
    "limit": 3,
    "offset": 0,
    "region": "UK",
    "deviceVendor": "CISCO",
    "deviceModel": "NCS5K",
}


@pytest.mark.parametrize("params", source_error_params)
def test_source_query_exception(params):
    """
    Test the exception block of source_query method
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Configure the mocked SqlDB to raise Exception when transactional_session is called
    mock_session.query.side_effect = params["exception"]

    # Create an instance of ImageDetails using the mocked SqlDB
    update = UpgradeDetails(**test_data)
    update.sql_instance = mock_sql_instance

    # Call the method being tested
    result = update.source_query(mock_session)

    # Define the expected result
    expected_result = {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-0500",
                "message": f"{params['message']} : {params['value']}",
            }
        ],
    }

    # Assertions
    assert result == expected_result


@pytest.mark.parametrize("params", target_error_params)
def test_target_query_exception(params):
    """
    Test the exception block of target_query method
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Configure the mocked SqlDB to raise Exception when transactional_session is called
    mock_session.query.side_effect = params["exception"]

    # Create an instance of ImageDetails using the mocked SqlDB
    update = UpgradeDetails(**test_data)
    update.sql_instance = mock_sql_instance

    # Call the method being tested
    result = update.target_query(mock_session)

    # Define the expected result
    expected_result = {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-0500",
                "message": f"{params['message']} : {params['value']}",
            }
        ],
    }

    # Assertions
    assert result == expected_result


@pytest.mark.parametrize("params", os_error_params)
def test_os_details_query_exception(params):
    """
    Test the exception block of os_details_query method
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Configure the mocked SqlDB to raise Exception when transactional_session is called
    mock_session.query.side_effect = params["exception"]

    # Create an instance of ImageDetails using the mocked SqlDB
    update = UpgradeDetails(**test_data)
    update.sql_instance = mock_sql_instance

    # Call the method being tested
    result = update.os_details_query(mock_session)

    # Define the expected result
    expected_result = {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-0500",
                "message": f"{params['message']} : {params['value']}",
            }
        ],
    }

    # Assertions
    assert result == expected_result


@pytest.mark.parametrize("params", traffic_error_params)
def test_traffic_diversion_query_exception(params):
    """
    Test the exception block of traffic_diversion_query method
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Configure the mocked SqlDB to raise Exception when transactional_session is called
    mock_session.query.side_effect = params["exception"]

    # Create an instance of ImageDetails using the mocked SqlDB
    update = UpgradeDetails(**test_data)
    update.sql_instance = mock_sql_instance

    # Call the method being tested
    result = update.traffic_diversion_query(mock_session)

    # Define the expected result
    expected_result = {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-0500",
                "message": f"{params['message']} : {params['value']}",
            }
        ],
    }

    # Assertions
    assert result == expected_result


@pytest.mark.parametrize("params", filter_error_params)
def test_filter_traffic_diversion_details_exception(params):
    """
    Test the exception block of filter_traffic_diversion_details method
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Configure the mocked SqlDB to raise Exception when transactional_session is called
    mock_session.query.side_effect = params["exception"]

    # Create an instance of ImageDetails using the mocked SqlDB
    update = UpgradeDetails(**test_data)
    update.sql_instance = mock_sql_instance

    # Call the method being tested
    update.traffic_diversion_query = MagicMock(side_effect=params["exception"])
    result = update.filter_traffic_diversion_details(mock_session)

    # Define the expected result
    expected_result = {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-0500",
                "message": f"{params['message']} : {params['value']}",
            }
        ],
    }

    # Assertions
    assert result == expected_result


test_data_1 = {
    "_include": "serviceChecks",
    "region": "UK",
    "deviceVendor": "CISCO",
    "deviceModel": "NCS5K",
}


@pytest.mark.parametrize("params", service_error_params)
def test_service_check_query_exception(params):
    """
    Test the exception block of service_check_query method
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Configure the mocked SqlDB to raise Exception when transactional_session is called
    mock_session.query.side_effect = params["exception"]

    # Create an instance of ImageDetails using the mocked SqlDB
    update = UpgradeDetails(**test_data_1)
    update.sql_instance = mock_sql_instance

    # Call the method being tested
    result = update.service_check_query(mock_session)

    # Define the expected result
    expected_result = {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-0500",
                "message": f"{params['message']} : {params['value']}",
            }
        ],
    }

    # Assertions
    assert result == expected_result


@patch("connectors.core.services.admin.read_upgrade_details.query_count")
def test_get_upgrade_details_service_check(count_mock):
    """
    Verify get_upgrade_details for image case
    Case1: _include = serviceChecks fetch all service_check details from table
    """
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()
    # Configure the return value of the session's query method to return the mock result
    mock_sql_instance.transactional_session.return_value.__enter__.return_value = mock_session
    # Create an instance of InventoryDetails using the mocked SqlDB
    update = UpgradeDetails(**service_check_case["kwargs"])
    update.sql_instance = mock_sql_instance
    update.source_query = MagicMock()
    update.target_query = MagicMock()
    update.filter_parameter = MagicMock()
    update.service_check_query = MagicMock()
    update.traffic_diversion_query = MagicMock()
    count_mock.return_value = service_check_case["count"]
    update.filter_parameter.return_value = (service_check_case["service_data"], None)
    update.service_check_query.return_value = service_check_case["service_data"]
    # Call the method being tested
    result = update.get_upgrade_details()

    # Assertions
    assert result == service_check_case["final_response"]


@pytest.mark.parametrize("params", test_cases_get_custom_config)
def test_get_custom_config(params):
    """
    Test cases for get_custom_config mehtod for multiple steps
    """
    mock_session = Mock()

    update = UpgradeDetails(**params["kwargs"])
    mock_session.query.return_value.join.return_value.filter.side_effect = params["custom_config_data"]

    result = update.get_custom_config(mock_session, params["config_id"])
    assert len(list(result)) == params["count"]
