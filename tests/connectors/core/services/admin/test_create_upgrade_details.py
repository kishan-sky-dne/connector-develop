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
from connectors.core.services.admin.image_upgrade_details import ImageUpgradeDetails

body_payload = [
    {
        "deviceVendor": "CISCO",
        "deviceModel": "NCS5K",
        "region": "UK",
        "currentOsVersion": "7.1.0",
        "currentOsLabel": "7.1.0-V1",
        "upgrade": {
            "upgradeSteps": 2,
            "targetOs": {
                "osVersion": "7.5.1",
                "osLabel": "7.5.1-V1",
                "customConfig": [
                    {
                        "deviceRole": ["TA", "MA", "SuperCore"],
                        "beforeUpgrade": ["command in text format"],
                        "afterUpgrade": ["command in text format"],
                        "isRollbackRequired": True,
                        "beforeRollback": ["target before rollback"],
                        "afterRollback": ["target after rollback"],
                        "configMode": "XR",
                    }
                ],
            },
            "intermediateSteps": [
                {
                    "osVersion": "7.3.0",
                    "osLabel": "7.3.0-V1",
                    "sequence": 1,
                    "customConfig": [
                        {
                            "deviceRole": ["TA", "MA", "SuperCore"],
                            "beforeUpgrade": ["command in text format"],
                            "afterUpgrade": ["command in text format"],
                            "isRollbackRequired": True,
                            "beforeRollback": ["intermediate before rollback"],
                            "afterRollback": ["intermediate after rollback"],
                            "configMode": "XR",
                        }
                    ],
                }
            ],
        },
        "Comments": "Upgrade is due to certain reason... ",
    }
]

image_details_resp = {
    "metadata": {
        "failure": [
            {
                "image": {
                    "currentOsLabel": "7.1.0-V1",
                    "currentOsVersion": "7.1.0",
                    "deviceModel": "NCS5K",
                    "deviceVendor": "CISCO",
                    "region": "UK",
                    "targetOsLabel": "7.5.1-V1",
                    "targetOsVersion": "7.5.1",
                },
            }
        ]
    },
    "errorCategory": "FAILED",
    "errors": [
        {
            "code": "ERR-000-097-0500",
            "message": "Database Operation Failed : Partial operation failure",
            "serviceReference": {"$ref": "#/metadata/failure/0"},
        }
    ],
    "status": "FAILURE",
}


def test_upgradedetails():
    """
     test to upgrade details Instance
    :return:
    """
    body = body_payload

    device_obj = ImageUpgradeDetails(
        body,
    )
    assert isinstance(device_obj, ImageUpgradeDetails)
    assert device_obj.body == body_payload


success_resp = {
    "metadata": {
        "success": [
            {
                "image": {
                    "currentOsLabel": "7.1.0-V1",
                    "currentOsVersion": "7.1.0",
                    "deviceModel": "NCS5K",
                    "deviceVendor": "CISCO",
                    "region": "UK",
                    "targetOsLabel": "7.5.1-V1",
                    "targetOsVersion": "7.5.1",
                },
                "osVersionUpgradeId": None,
            }
        ]
    },
    "status": "SUCCESS",
}

payload = [
    {
        "deviceVendor": "CISCO",
        "deviceModel": "NCS5K",
        "region": "UK",
        "currentOsVersion": "7.1.0",
        "currentOsLabel": "7.1.0-V1",
        "upgrade": {
            "upgradeSteps": "1",
            "targetOs": {
                "osVersion": "7.5.1",
                "osLabel": "7.5.1-V1",
                "customConfig": [
                    {
                        "deviceRole": ["TA", "MA", "SuperCore"],
                        "beforeUpgrade": ["command in text format"],
                        "afterUpgrade": ["command in text format"],
                    }
                ],
            },
        },
        "Comments": "Upgrade is due to certain reason... ",
    }
]

case1 = [
    (body_payload, (1, "CISCO", "NCS540"), success_resp),
    (payload, (1, "CISCO", "NCS540"), success_resp),
]


@patch("connectors.core.services.admin.image_upgrade_details.query_count")
@pytest.mark.parametrize("case", case1)
def test_image_upgrade_details(count_mock, case):
    """
    Validate the upgrade details function with request payload
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Configure the return value of the session's query method to return the mock result
    mock_session.query.return_value.join.return_value.filter.return_value.filter.return_value = case[1]
    mock_session.commit.return_value = {}
    mock_sql_instance.transactional_session.return_value.__enter__.return_value = mock_session
    # Create an instance of ImageDetails using the mocked SqlDB
    image_details = ImageUpgradeDetails(case[0])
    image_details.sql_instance = mock_sql_instance
    count_mock.return_value = 0
    image_details.phase_query = MagicMock()
    image_details.phase_query.return_value.filter.return_value.filter.return_value = case[1]
    image_details.valid_query_check = Mock(return_value=True)
    # Call the method being tested
    result = image_details.image_upgrade_details()

    # Assertions
    assert result == case[2]


def test_upgrade_details_service_db_exception():
    """
    To test the case of service DB expression
    :return:
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Configure the mocked SqlDB to raise a ServiceDBException when transactional_session is called
    mock_sql_instance.transactional_session.side_effect = AttributeError("Error occurred")

    # Create an instance of ImageDetails using the mocked SqlDB
    image_details = ImageUpgradeDetails(body_payload)
    image_details.sql_instance = mock_sql_instance

    # Call the method being tested
    result = image_details.image_upgrade_details()

    # Assertions
    assert result == {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-0500",
                "message": "Generic Exception occurred while performing update "
                "image upgrade details to image and upgrade tables AttributeError : Error occurred",
            }
        ],
    }


def test_add_image_details_generic_exception():
    """
    To test the case of generic expression
    :return:
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Configure the mocked SqlDB to raise a generic Exception when transactional_session is called
    mock_sql_instance.transactional_session.side_effect = Exception("Error occurred")

    # Create an instance of ImageDetails using the mocked SqlDB
    add_device_image = ImageUpgradeDetails(body_payload)
    add_device_image.sql_instance = mock_sql_instance

    # Call the method being tested
    result = add_device_image.image_upgrade_details()

    # Assertions
    assert result == {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-0500",
                "message": "Generic Exception occurred while performing update image upgrade details"
                " to image and upgrade tables Exception : Error occurred",
            }
        ],
    }


def test_device_region_details():
    """
    Validate the device region details function with request payload
    """
    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Create a MagicMock instance for the query result
    mock_query_result = MagicMock()
    mock_query_result.deviceRegionID = 3

    # Configure the session's query method to return the mock query result
    mock_session.query.return_value.join.return_value.join.return_value.filter.return_value.first.return_value = (
        mock_query_result
    )

    image_details = ImageUpgradeDetails(body_payload)
    image_details.device_region_details(mock_session, "CISCO", "NCS5K", "UK")

    mock_session.query.assert_called_once()
    mock_session.query().join.assert_called_once()
    mock_session.query().join().join.assert_called_once()
    mock_session.query().join().join().filter.assert_called_once()


def test_device_region_details_exception():
    """
    Test the exception block of device_region_details method
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Configure the session's query method to raise an exception
    mock_session.query.side_effect = Exception("Database operation failed")

    image_details = ImageUpgradeDetails(body_payload)
    image_details.sql_instance = mock_sql_instance

    # Call the method being tested
    result = image_details.device_region_details(mock_session, "CISCO", "NCS5K", "UK")

    # Define the expected result
    expected_result = {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-0500",
                "message": "Generic Exception occurred while querying data from device region table : Exception",
            }
        ],
    }

    # Assertions
    assert result == expected_result


def test_device_region_details_exception_1():
    """
    Test the exception block of device_region_details method
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Configure the session's query method to raise an exception
    mock_session.query.side_effect = AttributeError("Database operation failed")

    image_details = ImageUpgradeDetails(body_payload)
    image_details.sql_instance = mock_sql_instance

    # Call the method being tested
    result = image_details.device_region_details(mock_session, "CISCO", "NCS5K", "UK")

    # Define the expected result
    expected_result = {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-0500",
                "message": "Exception occurred while querying data from device region table : AttributeError",
            }
        ],
    }

    # Assertions
    assert result == expected_result


def test_os_version_details():
    """
    Test the os_version_details method
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Configure the session's query method to return the mock query result
    mock_query_result = MagicMock()
    mock_query_result.id = 1
    mock_query_result.os = "IOSXR"
    mock_query_result.os_version = "7.1.0"
    mock_query_result.os_label = "7.1.0-V1"
    mock_query_result.osValidityID = 2
    mock_query_result.validity_state = "Current"
    mock_session.query.return_value.filter.return_value = [mock_query_result]

    image_details = ImageUpgradeDetails(body_payload)
    image_details.sql_instance = mock_sql_instance

    result = image_details.os_version_details(
        mock_session,
        total_steps=1,
        current_os="7.1.0",
        current_label="7.1.0-V1",
        target_os="7.5.1",
        target_label="7.5.1-V1",
        intermediate_os=["7.3.0"],
        intermediate_label=["7.3.0-V1"],
    )

    expected_result = [
        {
            "id": 1,
            "os": "IOSXR",
            "os_version": "7.1.0",
            "os_label": "7.1.0-V1",
            "osValidityID": 2,
            "validity_state": "Current",
        }
    ]

    assert result[0][0].id == expected_result[0]["id"]
    assert result[0][0].os == expected_result[0]["os"]
    assert result[0][0].os_version == expected_result[0]["os_version"]
    assert result[0][0].os_label == expected_result[0]["os_label"]
    assert result[0][0].osValidityID == expected_result[0]["osValidityID"]
    assert result[0][0].validity_state == expected_result[0]["validity_state"]


def test_os_version_details_exception():
    """
    Test the exception block of the os_version_details method
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Configure the session's query method to raise an exception
    mock_session.query.side_effect = Exception("Database Operation Failed")

    image_details = ImageUpgradeDetails(body_payload)
    image_details.sql_instance = mock_sql_instance

    result = image_details.os_version_details(
        mock_session,
        total_steps=1,
        current_os="7.1.0",
        current_label="7.1.0-V1",
        target_os="7.5.1",
        target_label="7.5.1-V1",
        intermediate_os=["7.3.0"],
        intermediate_label=["7.3.0-V1"],
    )

    expected_result = {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-0500",
                "message": "Exception occurred while querying data from os version table : Exception",
            }
        ],
    }

    assert result == expected_result


def test_os_version_device_region_details_success():
    """
    Test the os_version_device_region_details method for success scenario
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Create a MagicMock instance for the query result
    mock_query_result = MagicMock(id=1, device_region_id=3, os_version_id=2, os_validity_id=1)
    mock_session.query.return_value.filter.return_value = [mock_query_result]

    image_details = ImageUpgradeDetails(body_payload)
    image_details.sql_instance = mock_sql_instance

    # Create mock arguments for the method
    device_version_details = [MagicMock(deviceRegionID=3)]
    source_os_details = [MagicMock(id=2, osValidityID=1)]
    target_os_details = []
    intermediate_os_details = []

    result = image_details.os_version_device_region_details(
        mock_session,
        device_version_details=device_version_details,
        source_os_details=source_os_details,
        target_os_details=target_os_details,
        intermediate_os_details=intermediate_os_details,
        total_steps=1,
    )

    expected_result = {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-0500",
                "message": "Exception occurred while querying data from os version device region table : IndexError",
            }
        ],
    }

    # Assertions
    assert result == expected_result


def test_os_version_device_region_details_exception():
    """
    Test the os_version_device_region_details method for exception scenario
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Configure the session to raise an exception when the query is executed
    mock_session.query.side_effect = Exception("Error occurred")

    image_details = ImageUpgradeDetails(body_payload)
    image_details.sql_instance = mock_sql_instance

    # Create mock arguments for the method
    device_version_details = [MagicMock(deviceRegionID=3)]
    source_os_details = [MagicMock(id=2, osValidityID=1)]
    target_os_details = []
    intermediate_os_details = []

    result = image_details.os_version_device_region_details(
        mock_session,
        device_version_details=device_version_details,
        source_os_details=source_os_details,
        target_os_details=target_os_details,
        intermediate_os_details=intermediate_os_details,
        total_steps=1,
    )

    expected_result = {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-0500",
                "message": "Generic Exception occurred while querying data "
                "from os version device region table : Exception",
            }
        ],
    }

    assert result == expected_result


source_os_region_data = [
    {"id": 1, "device_region_id": 3, "os_version_id": 2, "os_validity_id": 1},
]
source_os_device_region_details = [
    namedtuple("source_os_device_region_details", source.keys())(*source.values()) for source in source_os_region_data
]

intermediate_os_region_data = [
    {"id": 2, "device_region_id": 4, "os_version_id": 3, "os_validity_id": 2},
    {"id": 3, "device_region_id": 5, "os_version_id": 4, "os_validity_id": 3},
]
intermediate_os_device_region_details = [
    [namedtuple("intermediate_os_device_region_details", source.keys())(*source.values())]
    for source in intermediate_os_region_data
]

target_os_region_data = [
    {"id": 4, "device_region_id": 6, "os_version_id": 5, "os_validity_id": 4},
]
target_os_device_region_details = [
    namedtuple("target_os_device_region_details", source.keys())(*source.values()) for source in target_os_region_data
]

phase_upgrade_data_single_step = [
    {
        "id": 2,
        "source_osv_dr_id": 8,
        "target_osv_dr_id": 11,
        "steps": 3,
        "sequence_no": 1,
        "deviceregion_id": 14,
        "filter": Mock(return_value=2),
    },
]
single_step_phase_upgrade_query = [
    namedtuple("phase_upgrade_query", source.keys())(*source.values()) for source in phase_upgrade_data_single_step
]

phase_upgrade_data_multi_step = [
    {
        "id": 2,
        "source_osv_dr_id": 8,
        "target_osv_dr_id": 11,
        "steps": 3,
        "sequence_no": 1,
        "deviceregion_id": 14,
        "filter": Mock(return_value=2),
    },
    {
        "id": 5,
        "source_osv_dr_id": 11,
        "target_osv_dr_id": 14,
        "steps": 3,
        "sequence_no": 2,
        "deviceregion_id": 14,
        "filter": Mock(return_value=2),
    },
    {
        "id": 7,
        "source_osv_dr_id": 14,
        "target_osv_dr_id": 17,
        "steps": 3,
        "sequence_no": 3,
        "deviceregion_id": 14,
        "filter": Mock(return_value=2),
    },
]
multi_step_phase_upgrade_query = [
    namedtuple("phase_upgrade_query", source.keys())(*source.values()) for source in phase_upgrade_data_multi_step
]

test_cases_phase_upgrade_insert_success = [
    {
        "total_steps": "1",
        "intermediate_os": [],
        "source_os_device_region_details": source_os_device_region_details,
        "intermediate_os_device_region_details": intermediate_os_device_region_details,
        "target_os_device_region_details": target_os_device_region_details,
        "deviceregion_id": 14,
        "phase_upgrade_query": single_step_phase_upgrade_query,
        "filter_queries": [
            namedtuple("phase_upgrade_query", phase_upgrade_data_single_step[0].keys())(
                *phase_upgrade_data_single_step[0].values()
            ),
        ],
        "intermediate_custom": [],
        "target_custom": [
            {
                "deviceRole": [
                    "transport-agg",
                ],
                "beforeUpgrade": ["target before upgrade"],
                "afterUpgrade": ["target after upgrade"],
                "isRollbackRequired": True,
                "beforeRollback": ["target before rollback"],
                "afterRollback": ["target after rollback"],
                "configMode": "XR",
            },
        ],
    },
    {
        "total_steps": "3",
        "intermediate_os": [
            "7.3.0",
            "7.3.2",
        ],
        "source_os_device_region_details": source_os_device_region_details,
        "intermediate_os_device_region_details": intermediate_os_device_region_details,
        "target_os_device_region_details": target_os_device_region_details,
        "deviceregion_id": 14,
        "phase_upgrade_query": multi_step_phase_upgrade_query,
        "filter_queries": [
            namedtuple("phase_upgrade_query", phase_upgrade_data_multi_step[0].keys())(
                *phase_upgrade_data_multi_step[0].values()
            ),
            namedtuple("phase_upgrade_query", phase_upgrade_data_multi_step[1].keys())(
                *phase_upgrade_data_multi_step[1].values()
            ),
            namedtuple("phase_upgrade_query", phase_upgrade_data_multi_step[2].keys())(
                *phase_upgrade_data_multi_step[2].values()
            ),
        ],
        "intermediate_custom": [
            [
                {
                    "deviceRole": [
                        "transport-agg",
                    ],
                    "beforeUpgrade": ["1st intermediate before upgrade"],
                    "afterUpgrade": ["1st intermediate after upgrade"],
                    "isRollbackRequired": True,
                    "beforeRollback": ["1st intermediate before rollback"],
                    "afterRollback": ["1st intermediate after rollback"],
                    "configMode": "XR",
                }
            ],
            [
                {
                    "deviceRole": [
                        "transport-agg",
                    ],
                    "beforeUpgrade": ["2nd intermediate before upgrade"],
                    "afterUpgrade": ["2nd intermediate after upgrade"],
                    "isRollbackRequired": True,
                    "beforeRollback": ["2nd intermediate before rollback"],
                    "afterRollback": ["2nd intermediate after rollback"],
                    "configMode": "XR",
                }
            ],
        ],
        "target_custom": [
            {
                "deviceRole": [
                    "transport-agg",
                ],
                "beforeUpgrade": ["target before upgrade"],
                "afterUpgrade": ["target after upgrade"],
                "isRollbackRequired": True,
                "beforeRollback": ["target before rollback"],
                "afterRollback": ["target after rollback"],
                "configMode": "XR",
            },
        ],
    },
]


@pytest.mark.parametrize("params", test_cases_phase_upgrade_insert_success)
@patch("connectors.core.services.admin.image_upgrade_details.query_count")
def test_phase_upgrade_insert_success(count_mock, params):
    """
    Success test cases for phase_upgrade_insert method
    1) Success case for single step upgrade details
    1) Success case for multiple step upgrade details
    """
    # Create a mock session
    session_mock = MagicMock()

    service = ImageUpgradeDetails(body_payload)
    count_mock.return_value = False
    # session_mock.query.return_value.join.return_value = params["phase_upgrade_query"]
    session_mock.query.return_value.join.return_value.filter.side_effect = params["filter_queries"]
    session_mock.query.return_value.join.return_value.filter.return_value.filter.return_value = 1
    result = service.phase_upgrade_insert(session_mock, **params)

    # Assertions
    assert isinstance(result, list)


def test_phase_upgrade_insert_failure():
    """
    Failure test cases for phase_upgrade_insert method
    """
    # Create a mock session
    session_mock = MagicMock()

    # Create the input kwargs for the method
    kwargs = {
        "total_steps": 1,
        "intermediate_os": [],
        "source_os_device_region_details": [
            {
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-000-097-0500",
                        "message": "Generic Exception occurred while inserting data "
                        "into phase upgrade table : AttributeError",
                    }
                ],
                "status": "FAILURE",
            }
        ],
        "target_os_device_region_details": [],
        "intermediate_os_device_region_details": [],
        "pre_target_config": "pre_target_config",
        "pre_intermediate_config": [],
        "post_target_config": "post_target_config",
        "target_rollback_required": True,
        "target_before_rollback_config": ["pre rollback"],
        "target_after_rollback_config": ["post rollback"],
        "target_config_mode": "XR",
        "target_custom": [
            {
                "deviceRole": ["transport-agg", "metro-agg"],
                "beforeUpgrade": ["target before upgrade"],
                "afterUpgrade": ["target after upgrade"],
                "isRollbackRequired": True,
                "beforeRollback": ["target before rollback"],
                "afterRollback": ["target after rollback"],
                "configMode": "XR",
            }
        ],
    }

    service = ImageUpgradeDetails(body_payload)
    result = service.phase_upgrade_insert(session_mock, **kwargs)

    # Assertions
    assert isinstance(result, dict)
    assert result["status"] == "FAILURE"
    assert result["errorCategory"] == "FAILED"
    assert len(result["errors"]) == 1
    assert result["errors"][0]["code"] == "ERR-000-097-0500"
    assert (
        result["errors"][0]["message"]
        == "Generic Exception occurred while inserting data into phase upgrade table AttributeError : "
        "'dict' object has no attribute 'id'"
    )


@patch("connectors.core.services.admin.image_upgrade_details.query_count")
def test_valid_query_check(count_mock):
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Create a MagicMock instance for the query result
    mock_query_result = MagicMock(id=1, device_region_id=3, os_version_id=2, os_validity_id=1)
    mock_session.query.return_value.filter.return_value = [mock_query_result]

    image_details = ImageUpgradeDetails(body_payload)
    image_details.sql_instance = mock_sql_instance

    device_version_details = MagicMock(deviceRegionID=3)
    # Create mock arguments for the method
    result = image_details.valid_query_check(device_version_details=device_version_details)
    assert not result

    # Create mock arguments for the method
    source_os_details = MagicMock(id=2, osValidityID=1)
    target_os_details = MagicMock(id=2, osValidityID=1)
    intermediate_os_details = MagicMock(id=2, osValidityID=1)

    result = image_details.valid_query_check(
        source_os_details=source_os_details,
        total_steps=1,
        intermediate_os_details=intermediate_os_details,
        target_os_details=target_os_details,
    )
    assert not result
    count_mock.return_value = 1
    # Create mock arguments for the method
    source_os_device_region_details = MagicMock(id=2, osValidityID=1)
    target_os_device_region_details = MagicMock(id=2, osValidityID=1)
    intermediate_os_device_region_details = MagicMock(id=2, osValidityID=1)

    result = image_details.valid_query_check(
        source_os_device_region_details=source_os_device_region_details,
        target_os_device_region_details=target_os_device_region_details,
        intermediate_os_device_region_details=intermediate_os_device_region_details,
        total_steps=1,
    )
    assert result


payload = [
    {
        "deviceVendor": "CISCO",
        "deviceModel": "NCS5K",
        "region": "UK",
        "currentOsVersion": "7.1.0",
        "currentOsLabel": "7.1.0-V1",
        "upgrade": {
            "upgradeSteps": 1,
            "targetOs": {
                "osVersion": "7.5.1",
                "osLabel": "7.5.1-V1",
                "customConfig": [
                    {
                        "deviceRole": ["TA", "MA", "SuperCore"],
                        "beforeUpgrade": ["command in text format"],
                        "afterUpgrade": ["command in text format"],
                    }
                ],
            },
        },
        "Comments": "Upgrade is due to certain reason... ",
    }
]


fail_resp = {
    "metadata": {
        "failure": [
            {
                "image": {
                    "deviceVendor": "CISCO",
                    "deviceModel": "NCS5K",
                    "region": "UK",
                    "currentOsVersion": "7.1.0",
                    "currentOsLabel": "7.1.0-V1",
                    "targetOsVersion": "7.5.1",
                    "targetOsLabel": "7.5.1-V1",
                }
            }
        ]
    },
    "errorCategory": "FAILED",
    "errors": [
        {
            "code": "ERR-000-097-0500",
            "message": "Database Operation Failed : Insertion into Sequence Table Failed",
            "serviceReference": {"$ref": "#/metadata/failure/0"},
        }
    ],
    "status": "FAILURE",
}


payload_case_2 = [
    {
        "deviceVendor": "CISCO",
        "deviceModel": "NCS5K",
        "region": "UK",
        "currentOsVersion": "7.1.0",
        "currentOsLabel": "7.1.0-v1",
        "upgrade": {
            "upgradeSteps": 1,
            "targetOs": {
                "osVersion": "7.5.1",
                "osLabel": "7.5.1-v1",
                "customConfig": [
                    {
                        "deviceRole": ["TA", "MA", "SuperCore"],
                        "beforeUpgrade": ["command in text format"],
                        "afterUpgrade": ["command in text format"],
                        "isRollbackRequired": True,
                        "beforeRollback": ["command in text format"],
                        "afterRollback": ["command in text format"],
                        "configMode": "XR",
                    }
                ],
            },
            "intermediateSteps": [
                {
                    "osVersion": "7.3.2",
                    "osLabel": "7.3.2-v4",
                    "sequence": 1,
                    "customConfig": [
                        {
                            "deviceRole": ["TA", "MA", "SuperCore"],
                            "beforeUpgrade": ["command in text format"],
                            "afterUpgrade": ["command in text format"],
                            "isRollbackRequired": True,
                            "beforeRollback": ["command in text format"],
                            "afterRollback": ["command in text format"],
                            "configMode": "XR",
                        }
                    ],
                },
                {
                    "osVersion": "7.3.2",
                    "osLabel": "7.3.2-v5",
                    "sequence": 2,
                    "customConfig": [
                        {
                            "deviceRole": ["TA", "MA", "SuperCore"],
                            "beforeUpgrade": ["command in text format"],
                            "afterUpgrade": ["command in text format"],
                            "isRollbackRequired": True,
                            "beforeRollback": ["command in text format"],
                            "afterRollback": ["command in text format"],
                            "configMode": "XR",
                        }
                    ],
                },
            ],
        },
        "Comments": "Upgrade is due to certain reason... ",
    }
]


fail_resp_case_2 = {
    "metadata": {
        "failure": [
            {
                "image": {
                    "deviceVendor": "CISCO",
                    "deviceModel": "NCS5K",
                    "region": "UK",
                    "currentOsVersion": "7.1.0",
                    "currentOsLabel": "7.1.0-v1",
                    "targetOsVersion": "7.5.1",
                    "targetOsLabel": "7.5.1-v1",
                }
            }
        ]
    },
    "errorCategory": "FAILED",
    "errors": [
        {
            "code": "ERR-000-097-1001",
            "message": (
                "Validation Failed: UpgradeSteps steps is 1 but provided intermediate details length is 2."
                "Intermediate details length should one less than UpgradeSteps."
            ),
            "serviceReference": {"$ref": "#/metadata/failure/0"},
        }
    ],
    "status": "FAILURE",
}

payload_case_3 = [
    {
        "deviceVendor": "CISCO",
        "deviceModel": "NCS5K",
        "region": "UK",
        "currentOsVersion": "7.1.0",
        "currentOsLabel": "7.1.0-v1",
        "upgrade": {
            "upgradeSteps": 1,
            "targetOs": {
                "osVersion": "7.5.1",
                "osLabel": "7.5.1-v1",
                "customConfig": [
                    {
                        "deviceRole": ["TA", "MA", "SuperCore"],
                        "beforeUpgrade": ["command in text format"],
                        "afterUpgrade": ["command in text format"],
                        "isRollbackRequired": True,
                        "beforeRollback": ["command in text format"],
                        "afterRollback": ["command in text format"],
                        "configMode": "XR",
                    }
                ],
            },
        },
        "Comments": "Upgrade is due to certain reason... ",
    }
]


fail_resp_case_3 = {
    "metadata": {
        "failure": [
            {
                "image": {
                    "deviceVendor": "CISCO",
                    "deviceModel": "NCS5K",
                    "region": "UK",
                    "currentOsVersion": "7.1.0",
                    "currentOsLabel": "7.1.0-v1",
                    "targetOsVersion": "7.5.1",
                    "targetOsLabel": "7.5.1-v1",
                }
            }
        ]
    },
    "errorCategory": "FAILED",
    "errors": [
        {
            "code": "ERR-000-097-1002",
            "message": (
                "Validation Failed: Device Region ID for given vendor CISCO, model " "NCS5K and region UK is not in DB"
            ),
            "serviceReference": {"$ref": "#/metadata/failure/0"},
        }
    ],
    "status": "FAILURE",
}

fail_resp_case_4 = {
    "metadata": {
        "failure": [
            {
                "image": {
                    "deviceVendor": "CISCO",
                    "deviceModel": "NCS5K",
                    "region": "UK",
                    "currentOsVersion": "7.1.0",
                    "currentOsLabel": "7.1.0-v1",
                    "targetOsVersion": "7.5.1",
                    "targetOsLabel": "7.5.1-v1",
                }
            }
        ]
    },
    "errorCategory": "FAILED",
    "errors": [
        {
            "code": "ERR-000-097-1003",
            "message": (
                "Validation Failed: OS Version Details corresponding to current version 7.1.0-v1 "
                "or target version 7.5.1-v1 not in DB"
            ),
            "serviceReference": {"$ref": "#/metadata/failure/0"},
        }
    ],
    "status": "FAILURE",
}

fail_resp_case_5 = {
    "metadata": {
        "failure": [
            {
                "image": {
                    "deviceVendor": "CISCO",
                    "deviceModel": "NCS5K",
                    "region": "UK",
                    "currentOsVersion": "7.1.0",
                    "currentOsLabel": "7.1.0-v1",
                    "targetOsVersion": "7.5.1",
                    "targetOsLabel": "7.5.1-v1",
                }
            }
        ]
    },
    "errorCategory": "FAILED",
    "errors": [
        {
            "code": "ERR-000-097-1004",
            "message": (
                "Validation Failed: OS Version Device Region Details corresponding to current version "
                "7.1.0-v1 or target version 7.5.1-v1 and for  given vendor CISCO, model NCS5K and region UK is"
                " not found in DB"
            ),
            "serviceReference": {"$ref": "#/metadata/failure/0"},
        }
    ],
    "status": "FAILURE",
}

test_scenario_image_update_failure = [
    [(1, "CISCO", "NCS540"), payload_case_2, [True], fail_resp_case_2],
    [(1, "CISCO", "NCS540"), payload_case_3, [False], fail_resp_case_3],
    [(1, "CISCO", "NCS540"), payload_case_3, [True, False], fail_resp_case_4],
    [(1, "CISCO", "NCS540"), payload_case_3, [True, True, False], fail_resp_case_5],
]


@patch("connectors.core.services.admin.image_upgrade_details.SequenceUpgrade")
@patch("connectors.core.services.admin.image_upgrade_details.query_count")
def test_image_upgrade_details_failure(count_mock, seq_mock):
    """
    Validate the upgrade details function with request payload
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Configure the return value of the session's query method to return the mock result
    mock_session.query.return_value.join.return_value.filter.return_value.filter.return_value = (1, "CISCO", "NCS540")
    mock_session.commit.return_value = {}
    mock_sql_instance.transactional_session.return_value.__enter__.return_value = mock_session
    # Create an instance of ImageDetails using the mocked SqlDB
    image_details = ImageUpgradeDetails(payload)
    image_details.sql_instance = mock_sql_instance
    count_mock.return_value = 0
    seq_mock.return_value = False
    image_details.phase_upgrade_insert = Mock(return_value=[None])
    image_details.valid_query_check = Mock(return_value=True)
    # Call the method being tested
    result = image_details.image_upgrade_details()

    # Assertions
    assert result == fail_resp


@patch("connectors.core.services.admin.image_upgrade_details.query_count")
@pytest.mark.parametrize("case", test_scenario_image_update_failure)
def test_image_upgrade_details_failure3(count_mock, case):
    """
    Validate the upgrade details function with request payload
    1) Faliure case when sequence table insertion failed
    2) Failure case when total steps is not matched with intermediate steps
    3) Failure case when region, vendor and device model is not found in DB
    4) Failure case when os version detials not found in DB
    5) Failure case when current and target os version details are not matched with device found in DB
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Configure the return value of the session's query method to return the mock result
    mock_session.query.return_value.join.return_value.filter.return_value.filter.return_value = case[0]
    mock_session.commit.return_value = {}
    mock_sql_instance.transactional_session.return_value.__enter__.return_value = mock_session
    # Create an instance of ImageDetails using the mocked SqlDB
    image_details = ImageUpgradeDetails(case[1])
    count_mock.return_value = 0
    image_details.sql_instance = mock_sql_instance
    image_details.phase_query = MagicMock()
    image_details.phase_query.return_value.filter.return_value.filter.return_value = case[0]
    image_details.valid_query_check = Mock(side_effect=case[2])
    # Call the method being tested
    result = image_details.image_upgrade_details()

    # Assertions
    assert result == case[3]


error1 = {
    "metadata": {
        "failure": [
            {
                "image": {
                    "deviceVendor": "CISCO",
                    "deviceModel": "NCS5K",
                    "region": "UK",
                    "currentOsVersion": "7.1.0",
                    "currentOsLabel": "7.1.0-V1",
                    "targetOsVersion": "7.5.1",
                    "targetOsLabel": "7.5.1-V1",
                }
            }
        ]
    },
    "errorCategory": "FAILED",
    "errors": [
        {
            "code": "ERR-000-097-1006",
            "message": "Validation Failed: Please delete single step upgrade with current version 7.1.0-V1, and "
            "target version ['7.3.0-V1'] or 7.5.1-V1 before multi step image upgrade",
            "serviceReference": {"$ref": "#/metadata/failure/0"},
        }
    ],
    "status": "FAILURE",
}

error2 = {
    "metadata": {
        "failure": [
            {
                "image": {
                    "deviceVendor": "CISCO",
                    "deviceModel": "NCS5K",
                    "region": "UK",
                    "currentOsVersion": "7.1.0",
                    "currentOsLabel": "7.1.0-V1",
                    "targetOsVersion": "7.5.1",
                    "targetOsLabel": "7.5.1-V1",
                }
            }
        ]
    },
    "errorCategory": "FAILED",
    "errors": [
        {
            "code": "ERR-000-097-1005",
            "message": "Validation Failed: Duplication of single step upgrade details with current version 7.1.0-V1 "
            "and target version 7.5.1-V1 is not allowed",
            "serviceReference": {"$ref": "#/metadata/failure/0"},
        }
    ],
    "status": "FAILURE",
}

error3 = {
    "metadata": {
        "failure": [
            {
                "image": {
                    "deviceVendor": "CISCO",
                    "deviceModel": "NCS5K",
                    "region": "UK",
                    "currentOsVersion": "7.1.0",
                    "currentOsLabel": "7.1.0-V1",
                    "targetOsVersion": "7.5.1",
                    "targetOsLabel": "7.5.1-V1",
                }
            }
        ]
    },
    "errorCategory": "FAILED",
    "errors": [
        {
            "code": "ERR-000-097-1006",
            "message": "Validation Failed: Please delete multi step upgrade with current version 7.1.0-V1, and target "
            "or intermediate version 7.5.1-V1 before single step image upgrade",
            "serviceReference": {"$ref": "#/metadata/failure/0"},
        }
    ],
    "status": "FAILURE",
}

error4 = {
    "metadata": {
        "failure": [
            {
                "image": {
                    "deviceVendor": "CISCO",
                    "deviceModel": "NCS5K",
                    "region": "UK",
                    "currentOsVersion": "7.1.0",
                    "currentOsLabel": "7.1.0-V1",
                    "targetOsVersion": "7.5.1",
                    "targetOsLabel": "7.5.1-V1",
                }
            }
        ]
    },
    "errorCategory": "FAILED",
    "errors": [
        {
            "code": "ERR-000-097-1005",
            "message": "Validation Failed: Duplication of multi step upgrade details with current version 7.1.0-V1, "
            "intermediate ['7.3.0-V1'] and target version 7.5.1-V1 is not allowed",
            "serviceReference": {"$ref": "#/metadata/failure/0"},
        }
    ],
    "status": "FAILURE",
}

case2 = [
    (body_payload, (1, "CISCO", "NCS540"), error1, (1, 0)),
    (body_payload, (1, "CISCO", "NCS540"), error4, (0, 1)),
    (payload, (1, "CISCO", "NCS540"), error2, (1, 0)),
    (payload, (1, "CISCO", "NCS540"), error3, (0, 1)),
]


@patch("connectors.core.services.admin.image_upgrade_details.query_count")
@pytest.mark.parametrize("case", case2)
def test_image_upgrade_details_failure2(count_mock, case):
    """
    Validate the upgrade details function with request payload
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Configure the return value of the session's query method to return the mock result
    mock_session.query.return_value.join.return_value.filter.return_value.filter.return_value = case[1]
    mock_session.commit.return_value = {}
    mock_sql_instance.transactional_session.return_value.__enter__.return_value = mock_session
    # Create an instance of ImageDetails using the mocked SqlDB
    image_details = ImageUpgradeDetails(case[0])
    image_details.sql_instance = mock_sql_instance
    count_mock.side_effect = case[3]
    image_details.phase_query = MagicMock()
    image_details.phase_query.return_value.filter.return_value.filter.return_value = case[1]
    image_details.valid_query_check = Mock(return_value=True)
    # Call the method being tested
    result = image_details.image_upgrade_details()

    # Assertions
    assert result == case[2]
