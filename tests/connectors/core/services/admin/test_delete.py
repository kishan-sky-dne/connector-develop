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
from collections import namedtuple
from unittest.mock import MagicMock, Mock, patch

# Third Party Library
import pytest

# DNE Library
from connectors.core.services.admin.delete import DeleteAdminDetails

update_phase_list = []
update_custom_list = []
update_custom_list_1 = []

update_phase_data = [
    {
        "custom_config_id": 2,
        "id": 1,
        "source_osv_dr_id": 5,
        "target_osv_dr_id": 5,
        "sequence_no": 1,
        "steps": 1,
        "next_sequence_id": 2,
        "phase_upgrade_id": 5,
    }
]
for phase_data in update_phase_data:
    d_named = namedtuple("phase", phase_data.keys())(*phase_data.values())
    update_phase_list.append(d_named)

update_custom_data = [
    {
        "role_list_id": 2,
        "id": 1,
        "next_config_id": 2,
        "sequence_no": 2,
        "steps": 2,
        "next_sequence_id": 2,
        "phase_upgrade_id": 5,
    }
]
for cust_data in update_custom_data:
    d_named = namedtuple("custom", cust_data.keys())(*cust_data.values())
    update_custom_list.append(d_named)

update_custom_data_1 = [
    {
        "role_list_id": 5,
        "id": 2,
        "next_config_id": None,
        "sequence_no": 1,
        "steps": 2,
        "next_sequence_id": 0,
        "phase_upgrade_id": 5,
    }
]
for cust_data in update_custom_data_1:
    d_named = namedtuple("custom", cust_data.keys())(*cust_data.values())
    update_custom_list_1.append(d_named)

m_data = Mock(return_value=None)

delete_upgrade_params = [
    {
        "count": 0,
        "filter_data": (
            update_phase_list,
            update_custom_list,
            update_custom_list_1,
            update_custom_list,
            update_custom_list_1,
            m_data,
            m_data,
            m_data,
            m_data,
            m_data,
            m_data,
            m_data,
            m_data,
        ),
        "response": {
            "status": "FAILURE",
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-1004",
                    "message": "Validation Failed: Invalid osVersionUpgradeId to delete upgrade details",
                }
            ],
        },
    },
    {
        "count": 1,
        "filter_data": (
            update_phase_list,
            update_custom_list,
            update_custom_list_1,
            update_custom_list,
            update_custom_list_1,
            update_phase_list,
            update_custom_list,
            update_custom_list_1,
            m_data,
            m_data,
            m_data,
            m_data,
            m_data,
            m_data,
            m_data,
            m_data,
            m_data,
            m_data,
            m_data,
            m_data,
        ),
        "response": {"status": "success"},
    },
]

error_params = [
    {
        "exception": Exception("Error occurred"),
        "value": "Exception",
        "message": "Generic Exception occurred while performing delete image details to image and package tables",
    },
    {
        "exception": KeyError("Error occurred"),
        "value": "KeyError",
        "message": "Exception occurred while performing delete image details from image and package tables",
    },
]


@patch("connectors.core.services.admin.delete.query_count")
@pytest.mark.parametrize("params", error_params)
def test_delete_device_image_exception(count_mock, params):
    """
    To test the case of delete device image exception
    1. Generic Exception occurred
    2. KeyError Exception occurred
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Configure the mocked SqlDB to raise a Exception when transactional_session is called
    mock_sql_instance.transactional_session.side_effect = params["exception"]

    # Create an instance of ImageDetails using the mocked SqlDB
    image_details = DeleteAdminDetails(osVersionDeviceRegionId=2)
    count_mock.return_value = 2
    image_details.sql_instance = mock_sql_instance
    # Call the method being tested
    result = image_details.delete_device_image()

    # Assertions
    assert result == {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-0500",
                "message": f"{params['message']} : {params['value']} due to {params['exception']}",
            }
        ],
    }


error_params_1 = [
    {
        "exception": KeyError("Error occurred"),
        "value": "KeyError",
        "message": "Exception occurred while performing delete upgrade details from phase and sequence tables",
    },
    {
        "exception": Exception("Error occurred"),
        "value": "Exception",
        "message": "Generic Exception occurred while performing delete upgrade details from phase and sequence tables",
    },
]


@patch("connectors.core.services.admin.delete.query_count")
@pytest.mark.parametrize("params", error_params_1)
def test_delete_upgrade_details_exception(count_mock, params):
    """
    To test the case of delete upgrade details exception
    1. Generic exception occurred
    2. keyError exception occurred
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Configure the mocked SqlDB to raise a Exception when transactional_session is called
    mock_sql_instance.transactional_session.side_effect = params["exception"]

    # Create an instance of ImageDetails using the mocked SqlDB
    image_details = DeleteAdminDetails(osVersionDeviceRegionId=2)
    image_details.sql_instance = mock_sql_instance
    count_mock.return_value = 2
    # Call the method being tested
    result = image_details.delete_upgrade_details()

    # Assertions
    assert result == {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-0500",
                "message": f"{params['message']} : {params['value']} due to {params['exception']}",
            }
        ],
    }


delete_image_params = [
    {
        "count": (0, 0, 0, 0),
        "response": {
            "status": "FAILURE",
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-1001",
                    "message": "Validation Failed: Invalid osVersionDeviceRegionId to delete image details",
                }
            ],
        },
    },
    {
        "count": (1, 1, 1, 1),
        "response": {
            "status": "FAILURE",
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-1002",
                    "message": "Selected image is being used to upgrade "
                    "already. Please delete the upgrade entry before deleting the image",
                }
            ],
        },
    },
    {
        "count": (1, 0, 0, 0),
        "response": {
            "status": "FAILURE",
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-1003",
                    "message": "For requested os version device region id " "2 - image detail is not found",
                }
            ],
        },
    },
    {"count": (1, 0, 0, 1, 1), "response": {"status": "success"}},
]


@patch("connectors.core.services.admin.delete.query_count")
@pytest.mark.parametrize("params", delete_upgrade_params)
def test_delete_upgrade_details(count_mock, params):
    """
    To test the case of delete upgrade details
    1. Id not found scenario
    2. delete upgrade success scenario
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    mock_session.query.return_value.filter.side_effect = params["filter_data"]
    mock_session.query.return_value.filter.return_value.delete.return_value = []
    mock_session.commit.return_value = {}

    # Configure the mocked SqlDB to raise a Exception when transactional_session is called
    mock_sql_instance.transactional_session.return_value.__enter__.return_value = mock_session
    # Create an instance of DeleteAdminDetails using the mocked SqlDB
    image_details = DeleteAdminDetails(osVersionUpgradeId=2)
    image_details.sql_instance = mock_sql_instance
    count_mock.return_value = params["count"]
    # Call the method being tested
    result = image_details.delete_upgrade_details()

    # Assertions
    assert result == params["response"]


@patch("connectors.core.services.admin.delete.query_count")
@pytest.mark.parametrize("params", delete_image_params)
def test_delete_device_image(count_mock, params):
    """
    To test the case of delete upgrade details
    1. Id not found scenario
    2. upgrade image already used failure
    3. delete image success scenario
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()
    mock_session.commit.return_value = {}
    mock_session.query.return_value.filter.return_value.delete.return_value = []

    # Configure the mocked SqlDB to raise a Exception when transactional_session is called
    mock_sql_instance.transactional_session.return_value.__enter__.return_value = mock_session
    # Create an instance of DeleteAdminDetails using the mocked SqlDB
    image_details = DeleteAdminDetails(osVersionDeviceRegionId=2)
    image_details.sql_instance = mock_sql_instance
    count_mock.side_effect = params["count"]
    # Call the method being tested
    result = image_details.delete_device_image()

    # Assertions
    assert result == params["response"]
