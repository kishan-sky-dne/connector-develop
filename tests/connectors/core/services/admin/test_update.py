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
from connectors.core.services.admin.update import UpdateDetails

update_phase_list = []
update_custom_list = []
update_custom_list_1 = []
image_list_1 = []
image_list_2 = []

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

update_image_data = [
    [
        {
            "OsVersionDeviceRegionId": 2,
            "device_region_id": 8,
            "file_type": None,
            "url": None,
            "md5": None,
            "file_size": None,
            "comments": "7.3.0-V1 is in deprecated status",
            "os": "IOSXR",
            "os_label": "7.3.0-V1",
            "os_version": "7.3.0",
            "validity_state": "Target",
            "os_validity_id": 5,
            "vendor": "CISCO",
            "model": "NCS5K",
            "region": "DE",
            "image_id": None,
        }
    ],
    [
        {
            "OsVersionDeviceRegionId": 5,
            "device_region_id": 11,
            "file_type": None,
            "url": None,
            "md5": None,
            "file_size": None,
            "comments": "7.3.0-V2 is in deprecated status",
            "os": "IOSXR",
            "os_label": "7.3.0-V2",
            "os_version": "7.3.0",
            "validity_state": "Deprecated",
            "os_validity_id": 5,
            "vendor": "CISCO",
            "model": "NCS5K",
            "region": "DE",
            "image_id": None,
        }
    ],
]
for image_data in update_image_data[0]:
    d_named = namedtuple("image", image_data.keys())(*image_data.values())
    image_list_1.append(d_named)

for image_data in update_image_data[1]:
    d_named = namedtuple("image", image_data.keys())(*image_data.values())
    image_list_2.append(d_named)

update_cases = [
    {
        "count": (0, 0, 0),
        "payload": {
            "upgradeDetails": {
                "targetOs": {"customConfig": [{"deviceRole": ["TA"], "configMode": "XR"}]},
                "intermediateSteps": [
                    {
                        "sequence": 1,
                        "customConfig": [
                            {
                                "deviceRole": ["TA"],
                                "beforeUpgrade": ["intermediate before upgrade"],
                                "afterUpgrade": ["intermediate after upgrade"],
                                "isRollbackRequired": "true",
                                "beforeRollback": ["intermediate before rollback"],
                                "afterRollback": ["intermediate after rollback"],
                                "configMode": "XR",
                            }
                        ],
                    }
                ],
            },
            "Comments": "Upgrade is due to certain reason... ",
        },
        "response": {
            "status": "FAILURE",
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-1001",
                    "message": "Validation Failed: Invalid osVersionUpgradeId to update upgrade details",
                }
            ],
        },
    },
    {
        "count": (1, 0, 1),
        "payload": {
            "upgradeDetails": {
                "targetOs": {"customConfig": [{"deviceRole": ["TA"], "configMode": "XR"}]},
                "intermediateSteps": [
                    {
                        "sequence": 1,
                        "customConfig": [
                            {
                                "deviceRole": ["TA"],
                                "beforeUpgrade": ["intermediate before upgrade"],
                                "afterUpgrade": ["intermediate after upgrade"],
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
        },
        "response": {
            "status": "FAILURE",
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-1002",
                    "message": "Validation Failed: osVersionUpgradeId found in phase upgrade table "
                    "but not available in sequence upgrade table",
                }
            ],
        },
    },
    {
        "count": (1, 1, 1),
        "payload": {
            "upgradeDetails": {
                "targetOs": {
                    "customConfig": [
                        {
                            "deviceRole": ["TA"],
                            "afterUpgrade": ["target after upgrade"],
                            "isRollbackRequired": "true",
                            "beforeRollback": ["target before rollback"],
                            "afterRollback": ["target after rollback"],
                            "configMode": "XR",
                        }
                    ]
                },
                "intermediateSteps": [
                    {
                        "sequence": 1,
                        "customConfig": [
                            {
                                "deviceRole": ["TA"],
                                "afterUpgrade": ["intermediate after upgrade"],
                                "isRollbackRequired": "true",
                                "beforeRollback": ["intermediate before rollback"],
                                "afterRollback": ["intermediate after rollback"],
                                "configMode": "XR",
                            }
                        ],
                    }
                ],
            },
            "Comments": "Upgrade is due to certain reason... ",
        },
        "response": {"comments": "Upgrade is due to certain reason... ", "osVersionUpgradeId": 2, "status": "success"},
    },
    {
        "count": (1, 1, 1),
        "payload": {
            "upgradeDetails": {
                "targetOs": {"customConfig": [{"deviceRole": ["TA"], "beforeUpgrade": ["target before upgrade"]}]},
                "intermediateSteps": [
                    {
                        "sequence": 1,
                        "customConfig": [{"deviceRole": ["TA"], "beforeUpgrade": ["intermediate before upgrade"]}],
                    }
                ],
            },
            "Comments": "Upgrade is due to certain reason... ",
        },
        "response": {"comments": "Upgrade is due to certain reason... ", "osVersionUpgradeId": 2, "status": "success"},
    },
]

m_data = Mock(return_value=None)

update_cases_2 = [
    {
        "count": 1,
        "custom_data": [
            {
                "deviceRole": ["transport-agg"],
                "afterUpgrade": ["target after upgrade"],
                "isRollbackRequired": True,
                "beforeRollback": ["target before rollback"],
                "afterRollback": ["target after rollback"],
                "configMode": "XR",
            }
        ],
        "filter_data": (
            update_phase_list,
            update_custom_list,
            update_custom_list_1,
            {},
            m_data,
            m_data,
            m_data,
            m_data,
            update_phase_list,
            {},
        ),
    },
]

seq_cases = [
    {
        "custom_data": [
            {
                "deviceRole": ["transport-agg"],
                "afterUpgrade": ["target after upgrade"],
                "isRollbackRequired": True,
                "beforeRollback": ["target before rollback"],
                "afterRollback": ["target after rollback"],
                "configMode": "XR",
            }
        ],
        "filter_data": update_phase_list,
        "comments": "Test comments",
        "response": {},
    },
    {
        "custom_data": [
            {
                "deviceRole": ["transport-agg"],
                "afterUpgrade": ["target after upgrade"],
                "isRollbackRequired": True,
                "beforeRollback": ["target before rollback"],
                "afterRollback": ["target after rollback"],
                "configMode": "XR",
            }
        ],
        "filter_data": update_custom_list,
        "comments": None,
        "response": {2: 5},
    },
    {
        "custom_data": [
            {
                "deviceRole": ["transport-agg"],
                "afterUpgrade": ["target after upgrade"],
                "isRollbackRequired": True,
                "beforeRollback": ["target before rollback"],
                "afterRollback": ["target after rollback"],
                "configMode": "XR",
            }
        ],
        "filter_data": update_custom_list_1,
        "comments": None,
        "response": {1: 2},
    },
]

update_cases_3 = [
    {
        "count": 1,
        "payload": {"osStatus": "Deprecated", "comments": "comments on this image data"},
        "filter_data": (
            image_list_1,
            image_list_1,
            image_list_1,
        ),
        "response": {
            "status": "FAILURE",
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-1005",
                    "message": "Validation Failed: This state cannot be changed because there is no "
                    "image detail, Please delete this image and recreate with the image detail",
                }
            ],
        },
    },
    {
        "count": 1,
        "payload": {"osStatus": "Current", "comments": "comments on this image data"},
        "filter_data": (
            image_list_2,
            image_list_2,
            image_list_2,
        ),
        "response": {
            "status": "FAILURE",
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-1005",
                    "message": "Validation Failed: This state cannot be changed because there is no "
                    "image detail, Please delete this image and recreate with the image detail",
                }
            ],
        },
    },
]

error_params = [
    {
        "payload": {},
        "exception": KeyError("Error occurred"),
        "response": {
            "status": "FAILURE",
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-0500",
                    "message": "Exception occurred while performing update upgrade details: KeyError",
                }
            ],
        },
    },
    {
        "payload": {},
        "exception": Exception("Error occurred"),
        "response": {
            "status": "FAILURE",
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-0500",
                    "message": "Generic Exception occurred while performing update "
                    "upgrade details from os device region tables : Exception",
                }
            ],
        },
    },
]


@patch("connectors.core.services.admin.update.query_count")
@pytest.mark.parametrize("params", update_cases)
def test_update_upgrade_details(count_mock, params):
    """
    To test the case of update upgrade details
    1. Id not found scenario
    2. update upgrade success scenario
    3. update upgrade success scenario(only configMode is updated)
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    mock_session.query.return_value.filter.return_value.update.return_value = []
    mock_session.query.return_value.filter.return_value.delete.return_value = []
    mock_session.commit.return_value = {}

    # Configure the mocked SqlDB to raise a Exception when transactional_session is called
    mock_sql_instance.transactional_session.return_value.__enter__.return_value = mock_session
    # Create an instance of DeleteAdminDetails using the mocked SqlDB
    upgrade_details = UpdateDetails(osVersionUpgradeId=2, body=params["payload"])
    upgrade_details.sql_instance = mock_sql_instance
    upgrade_details.update_custom_config_data = MagicMock()
    count_mock.side_effect = params["count"]
    # Call the method being tested
    result = upgrade_details.update_upgrade_details()

    # Assertions
    assert result == params["response"]


@patch("connectors.core.services.admin.update.query_count")
@pytest.mark.parametrize("params", error_params)
def test_update_upgrade_details_exception(count_mock, params):
    """
    To test the case of update upgrade details exception
    1. Generic exception occurred
    2. keyError exception occurred
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Configure the mocked SqlDB to raise a Exception when transactional_session is called
    mock_sql_instance.transactional_session.side_effect = params["exception"]

    # Create an instance of DeleteAdminDetails using the mocked SqlDB
    upgrade_details = UpdateDetails(osVersionDeviceRegionId=2, body=params["payload"])
    upgrade_details.sql_instance = mock_sql_instance
    count_mock.return_value = 2

    # Call the method being tested
    result = upgrade_details.update_upgrade_details()

    # Assertions
    assert result == params["response"]


update_cases_1 = [
    {
        "count": (0, 0),
        "payload": {"osStatus": "Deprecated", "comments": "comments on this image data"},
        "response": {
            "status": "FAILURE",
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-1004",
                    "message": "Validation Failed: Invalid osVersionDeviceRegionId to update image details",
                }
            ],
        },
    },
    {
        "count": (1, 0),
        "payload": {"osStatus": "Deprecated", "comments": "comments on this image data"},
        "response": {
            "status": "FAILURE",
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-1005",
                    "message": "Validation Failed: osVersionDeviceRegionId found in os version device region "
                    "table but not available in image table",
                }
            ],
        },
    },
    {
        "count": (1, 1),
        "payload": {"osStatus": "Deprecated", "comments": "comments on this image data"},
        "response": {"comments": "comments on this image data", "osVersionDeviceRegionId": 2, "status": "success"},
    },
    {
        "count": (1, 1),
        "payload": {"osStatus": "Deprecated"},
        "response": {"comments": None, "osVersionDeviceRegionId": 2, "status": "success"},
    },
]

error_params_1 = [
    {
        "payload": {},
        "exception": KeyError("Error occurred"),
        "response": {
            "status": "FAILURE",
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-0500",
                    "message": "Exception occurred while performing update image details: KeyError",
                }
            ],
        },
    },
    {
        "payload": {},
        "exception": Exception("Error occurred"),
        "response": {
            "status": "FAILURE",
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-0500",
                    "message": "Generic Exception occurred while performing update "
                    "image details from os device region tables : Exception",
                }
            ],
        },
    },
]


@patch("connectors.core.services.admin.update.query_count")
@pytest.mark.parametrize("params", update_cases_1)
def test_update_image_details(count_mock, params):
    """
    To test the case of update image details
    1. Id not found scenario
    2. Image not found scenario
    3. update image success scenario
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    mock_session.query.return_value.filter.return_value.update.return_value = []
    mock_session.commit.return_value = {}

    # Configure the mocked SqlDB to raise a Exception when transactional_session is called
    mock_sql_instance.transactional_session.return_value.__enter__.return_value = mock_session
    # Create an instance of DeleteAdminDetails using the mocked SqlDB
    image_details = UpdateDetails(osVersionDeviceRegionId=2, body=params["payload"])
    image_details.sql_instance = mock_sql_instance
    count_mock.side_effect = params["count"]
    # Call the method being tested
    result = image_details.update_image_details()

    # Assertions
    assert result == params["response"]


@patch("connectors.core.services.admin.update.query_count")
@pytest.mark.parametrize("params", update_cases_3)
def test_update_image_details_failure(count_mock, params):
    """
    To test the case of update image details
    1. Deprecated state failure
    2. Target state failure
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    mock_session.query.return_value.filter.side_effect = params["filter_data"]
    mock_session.query.return_value.filter.return_value.update.return_value = []
    mock_session.commit.return_value = {}

    # Configure the mocked SqlDB to raise a Exception when transactional_session is called
    mock_sql_instance.transactional_session.return_value.__enter__.return_value = mock_session
    # Create an instance of DeleteAdminDetails using the mocked SqlDB
    image_details = UpdateDetails(osVersionDeviceRegionId=2, body=params["payload"])
    image_details.sql_instance = mock_sql_instance
    count_mock.side_effect = params["count"]
    # Call the method being tested
    result = image_details.update_image_details()

    # Assertions
    assert result == params["response"]


@patch("connectors.core.services.admin.update.query_count")
@pytest.mark.parametrize("params", error_params_1)
def test_update_image_details_exception(count_mock, params):
    """
    To test the case of update image details exception
    1. Generic exception occurred
    2. keyError exception occurred
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Configure the mocked SqlDB to raise a Exception when transactional_session is called
    mock_sql_instance.transactional_session.side_effect = params["exception"]

    # Create an instance of DeleteAdminDetails using the mocked SqlDB
    image_details = UpdateDetails(osVersionDeviceRegionId=2, body=params["payload"])
    image_details.sql_instance = mock_sql_instance
    count_mock.return_value = 2

    # Call the method being tested
    result = image_details.update_image_details()

    # Assertions
    assert result == params["response"]


@pytest.mark.parametrize("params", update_cases_2)
def test_update_custom_config_data(params):
    """
    To test the case of update upgrade details for custom config
    1. update upgrade success scenario - custom config
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    mock_session.query.return_value.filter.side_effect = params["filter_data"]
    mock_session.query.return_value.filter.return_value.update.return_value = []
    mock_session.query.return_value.filter.return_value.delete.return_value = []
    mock_session.add.return_value = {}
    mock_session.commit.return_value = {}

    # Configure the mocked SqlDB to raise a Exception when transactional_session is called
    mock_sql_instance.transactional_session.return_value.__enter__.return_value = mock_session
    # Create an instance of DeleteAdminDetails using the mocked SqlDB
    upgrade_details = UpdateDetails(osVersionUpgradeId=2, body=params["custom_data"])
    upgrade_details.sql_instance = mock_sql_instance
    # Call the method being tested
    result = upgrade_details.update_custom_config_data(mock_session, params["custom_data"], 3)

    # Assertions
    assert result is None


@pytest.mark.parametrize("params", seq_cases)
def test_get_sequence_upgrade_details(params):
    """
    To test the case of sequence upgrade details
    1. update upgrade success scenario - custom config
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    mock_session.query.return_value.filter.return_value = params["filter_data"]

    # Configure the mocked SqlDB to raise a Exception when transactional_session is called
    mock_sql_instance.transactional_session.return_value.__enter__.return_value = mock_session
    # Create an instance of DeleteAdminDetails using the mocked SqlDB
    upgrade_details = UpdateDetails(osVersionUpgradeId=2, body=params["custom_data"])
    upgrade_details.sql_instance = mock_sql_instance
    # Call the method being tested
    result = upgrade_details.get_sequence_upgrade_details(mock_session, params["comments"], params["custom_data"])

    # Assertions
    assert result == params["response"]


@patch("connectors.core.services.admin.update.query_count")
def test_update_upgrade_details_1(count_mock):
    """
    To test the case of update upgrade details - failure case
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    mock_session.query.return_value.filter.return_value.update.return_value = []
    mock_session.query.return_value.filter.return_value.delete.return_value = []
    mock_session.commit.return_value = {}

    # Configure the mocked SqlDB to raise a Exception when transactional_session is called
    mock_sql_instance.transactional_session.return_value.__enter__.return_value = mock_session
    # Create an instance of DeleteAdminDetails using the mocked SqlDB
    upgrade_details = UpdateDetails(
        osVersionUpgradeId=2,
        body={
            "upgradeDetails": {
                "targetOs": {"customConfig": [{"deviceRole": ["TA"], "beforeUpgrade": ["target before upgrade"]}]},
                "intermediateSteps": [
                    {
                        "sequence": 1,
                        "customConfig": [{"deviceRole": ["TA"], "beforeUpgrade": ["intermediate before upgrade"]}],
                    }
                ],
            },
            "Comments": "Upgrade is due to certain reason... ",
        },
    )
    upgrade_details.sql_instance = mock_sql_instance
    upgrade_details.update_custom_config_data = MagicMock()
    upgrade_details.get_sequence_upgrade_details = MagicMock(return_value=[])
    count_mock.return_value = 1
    # Call the method being tested
    result = upgrade_details.update_upgrade_details()

    # Assertions
    assert result == {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-1003",
                "message": "Validation Failed: Cannot update single step details with "
                "multi step details given in payload",
            }
        ],
    }
