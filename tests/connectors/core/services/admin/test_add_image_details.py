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
from copy import deepcopy
from unittest.mock import MagicMock, Mock, patch

# Third Party Library
import pytest

# DNE Library
from connectors.core.services.admin.add_image_details import AddImageDetails

body_payload = [
    {
        "deviceVendor": "Cisco",
        "deviceModel": "NCS5K",
        "region": "DE",
        "osVersion": "7.3.0",
        "osLabel": "7.3.0-V1",
        "osStatus": "Deprecated",
        "comments": "7.3.0-V1 is in deprecated status",
        "osDetails": {
            "imageFiles": [
                {
                    "imageType": "iso",
                    "fileName": "/bluebird/ios-xr/7.3.0/NCS540/install-image.iso",
                    "md5Value": "cb915e5704a0b30cfba48056567f625b",
                    "fileSize": "2742723234",
                }
            ],
            "packageDetails": [
                {
                    "type": "XR",
                    "packages": ["ncs540-li-1.0.0.0-r732", "ncs540-eigrp-1.0.0.0-r732", "ncs540-isis-1.0.0.0-r732"],
                },
                {
                    "type": "SYSADMIN-FIX",
                    "packages": [
                        "ncs540-sysadmin-shared-7.3.0.1-r732.CSCvx53252",
                        "ncs540-sysadmin-system-7.3.0.2-r732.CSCvy03814",
                        "ncs540-sysadmin-ncs540-7.3.0.5-r732.CSCvz54957",
                    ],
                },
                {
                    "type": "SYSADMIN-MOD",
                    "packages": [
                        "ncs540-sysadmin-shared-7.3.0.1-r732.CSCvx53252",
                        "ncs540-sysadmin-system-7.3.0.2-r732.CSCvy03814",
                        "ncs540-sysadmin-ncs540-7.3.0.5-r732.CSCvz54957",
                    ],
                },
            ],
        },
    }
]

device_list = []
device_region_data = [
    {
        "id": None,
        "region": None,
    }
]

for dev_data in device_region_data:
    d_named = namedtuple("device", dev_data.keys())(*dev_data.values())
    device_list.append(d_named)

img_list = []
img_data = [
    {
        "id": 3,
    }
]

for img in img_data:
    d_named = namedtuple("img", img.keys())(*img.values())
    img_list.append(d_named)

image_details_resp = {
    "metadata": {
        "failure": [
            {
                "deviceVendor": "Cisco",
                "deviceModel": "NCS5K",
                "region": "DE",
                "osVersion": "7.3.0",
                "osLabel": "7.3.0-V1",
                "osStatus": "Deprecated",
            }
        ]
    },
    "errorCategory": "FAILED",
    "errors": [
        {
            "code": "ERR-000-097-0500",
            "message": "Operation Failed : osVersionDeviceRegionId not found",
            "serviceReference": {"$ref": "#/metadata/failure/0"},
        }
    ],
    "status": "FAILURE",
}

image_details_resp_1 = {
    "metadata": {
        "success": [
            {
                "image": {
                    "deviceVendor": "Cisco",
                    "deviceModel": "NCS5K",
                    "region": "DE",
                    "osVersion": "7.3.0",
                    "osLabel": "7.3.0-V1",
                    "osStatus": "Deprecated",
                },
                "osVersionDeviceRegionId": 3,
            }
        ]
    },
    "status": "SUCCESS",
}


def test_addimagedetails():
    """
     test to add image details Instance
    :return:
    """
    body = body_payload

    device_obj = AddImageDetails(
        body,
    )
    assert isinstance(device_obj, AddImageDetails)
    assert device_obj.body == body_payload


case1 = [
    (body_payload, (1, "CISCO", "NCS540"), False, image_details_resp),
    (body_payload, (1, "CISCO", "NCS540"), 3, image_details_resp_1),
]

case2 = [
    {
        "type": "md5Value",
        "value": "c05e19b77f977c2f3afe0b98f0b77aa",
        "count": 0,
        "os_status_id": 1,
        "file_type": 1,
        "response": {
            "metadata": {
                "failure": [
                    {
                        "deviceVendor": "Cisco",
                        "deviceModel": "NCS5K",
                        "region": "DE",
                        "osVersion": "7.3.0",
                        "osLabel": "7.3.0-V1",
                        "osStatus": "Deprecated",
                    }
                ]
            },
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-1004",
                    "message": "Validation Failed: MD5 checksum is not matching with expected bytes size in DB",
                    "serviceReference": {"$ref": "#/metadata/failure/0"},
                }
            ],
            "status": "FAILURE",
        },
    },
    {
        "type": "md5Value",
        "value": "b095045a1231c9328d2892a58a5b6399",
        "count": 0,
        "os_status_id": 1,
        "file_type": 1,
        "response": {
            "metadata": {
                "failure": [
                    {
                        "deviceVendor": "Cisco",
                        "deviceModel": "NCS5K",
                        "region": "DE",
                        "osVersion": "7.3.0",
                        "osLabel": "7.3.0-V1",
                        "osStatus": "Deprecated",
                    }
                ]
            },
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-1005",
                    "message": "Validation Failed: Package type is not matched with DB entry",
                    "serviceReference": {"$ref": "#/metadata/failure/0"},
                }
            ],
            "status": "FAILURE",
        },
    },
    {
        "type": "fileSize",
        "value": "4742723234",
        "count": 0,
        "os_status_id": 1,
        "file_type": 1,
        "response": {
            "metadata": {
                "failure": [
                    {
                        "deviceVendor": "Cisco",
                        "deviceModel": "NCS5K",
                        "region": "DE",
                        "osVersion": "7.3.0",
                        "osLabel": "7.3.0-V1",
                        "osStatus": "Deprecated",
                    }
                ]
            },
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-1003",
                    "message": "Validation Failed: Image size is greater than expected size in DB",
                    "serviceReference": {"$ref": "#/metadata/failure/0"},
                }
            ],
            "status": "FAILURE",
        },
    },
    {
        "type": "md5Value",
        "value": "cb915e5704a0b30cfba48056567f625b",
        "count": 2,
        "os_status_id": 1,
        "file_type": 1,
        "response": {
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-1006",
                    "message": "Validation Failed: Duplication of os version device region details is not allowed",
                    "serviceReference": {"$ref": "#/metadata/failure/0"},
                }
            ],
            "metadata": {
                "failure": [
                    {
                        "deviceModel": "NCS5K",
                        "deviceVendor": "Cisco",
                        "osLabel": "7.3.0-V1",
                        "osStatus": "Deprecated",
                        "osVersion": "7.3.0",
                        "region": "DE",
                    }
                ]
            },
            "status": "FAILURE",
        },
    },
    {
        "type": "md5Value",
        "value": "cb915e5704a0b30cfba48056567f625b",
        "count": 0,
        "os_status_id": 0,
        "file_type": 1,
        "response": {
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-1001",
                    "message": "Validation Failed: OS Status is not matched with DB entry",
                    "serviceReference": {"$ref": "#/metadata/failure/0"},
                }
            ],
            "metadata": {
                "failure": [
                    {
                        "deviceModel": "NCS5K",
                        "deviceVendor": "Cisco",
                        "osLabel": "7.3.0-V1",
                        "osStatus": "Deprecated",
                        "osVersion": "7.3.0",
                        "region": "DE",
                    }
                ]
            },
            "status": "FAILURE",
        },
    },
    {
        "type": "md5Value",
        "value": "cb915e5704a0b30cfba48056567f625b",
        "count": 0,
        "os_status_id": 1,
        "file_type": 0,
        "response": {
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-000-097-1002",
                    "message": "Validation Failed: Image type is not matched with DB entry",
                    "serviceReference": {"$ref": "#/metadata/failure/0"},
                }
            ],
            "metadata": {
                "failure": [
                    {
                        "deviceModel": "NCS5K",
                        "deviceVendor": "Cisco",
                        "osLabel": "7.3.0-V1",
                        "osStatus": "Deprecated",
                        "osVersion": "7.3.0",
                        "region": "DE",
                    }
                ]
            },
            "status": "FAILURE",
        },
    },
]


@patch("connectors.core.services.admin.add_image_details.query_count")
@pytest.mark.parametrize("case", case1)
def test_add_device_image(count_mock, case):
    """
    Validate the image details function with request payload
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Configure the return value of the session's query method to return the mock result
    mock_session.query.return_value.join.return_value.filter.return_value = case[1]  # Wrap the mock_result in a list
    mock_session.commit.return_value = {}
    mock_sql_instance.transactional_session.return_value.__enter__.return_value = mock_session
    count_mock.return_value = 0
    # Create an instance of ImageDetails using the mocked SqlDB
    image_details = AddImageDetails(case[0])
    image_details.insert_os_version_device_region = MagicMock()
    image_details.insert_os_version_device_region.return_value = case[2]
    image_details.query_os_version_details = MagicMock()
    image_details.query_os_version_details.return_value = {}
    image_details.sql_instance = mock_sql_instance
    # Call the method being tested
    result = image_details.add_device_image()

    # Assertions
    assert result == case[3]


@patch("connectors.core.services.admin.add_image_details.query_count")
@pytest.mark.parametrize("case", case2)
def test_add_device_image_error(count_mock, case):
    """
    Validate the image details function with request payload
    """
    error_body_payload = deepcopy(body_payload)
    error_body_payload[0]["osDetails"]["imageFiles"][0][case["type"]] = case["value"]
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session

    mock_session = MagicMock()

    # Configure the return value of the session's query method to return the mock result
    mock_session.query.return_value.join.return_value.filter.return_value = (1, "CISCO", "NCS540")
    mock_session.commit.return_value = {}
    mock_sql_instance.transactional_session.return_value.__enter__.return_value = mock_session
    count_mock.return_value = case["count"]
    # Create an instance of ImageDetails using the mocked SqlDB
    image_details = AddImageDetails(error_body_payload)
    image_details.query_os_version_details = MagicMock()
    image_details.query_os_version_details.return_value = {}
    image_details.os_version_details = MagicMock()
    image_details.os_version_details.return_value = case["os_status_id"]
    image_details.image_type_details = MagicMock()
    image_details.image_type_details.return_value = case["file_type"]
    image_details.package_type = Mock(return_value=device_list)
    image_details.sql_instance = mock_sql_instance
    # Call the method being tested
    result = image_details.add_device_image()

    # Assertions
    assert result == case["response"]


def test_add_image_details_service_db_exception():
    """
    To test the case of service DB expression
    :return:
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Configure the mocked SqlDB to raise a ServiceDBException when transactional_session is called
    mock_sql_instance.transactional_session.side_effect = AttributeError("Error occurred")

    # Create an instance of ImageDetails using the mocked SqlDB
    image_details = AddImageDetails(body_payload)
    image_details.sql_instance = mock_sql_instance

    # Call the method being tested
    result = image_details.add_device_image()

    # Assertions
    assert result == {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-0500",
                "message": "Exception occurred while performing add image details "
                "to image and package tables : AttributeError",
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
    image_details = AddImageDetails(body_payload)
    image_details.sql_instance = mock_sql_instance

    # Call the method being tested
    result = image_details.add_device_image()

    # Assertions
    assert result == {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-0500",
                "message": "Generic Exception occurred while performing add image details"
                " to image and package tables : Exception",
            }
        ],
    }


os_case = [
    {"count": 0, "filter": [], "response": None},
    {"count": 1, "filter": img_list, "response": 3},
]


@patch("connectors.core.services.admin.add_image_details.query_count")
@patch("connectors.core.utils.sqldb.swlifecycle_model.OSVersion")
@pytest.mark.parametrize("case", os_case)
def test_insert_os_version(ver_mock, count_mock, case):
    """
    Validate the insert os version function with request payload
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Configure the return value of the session's query method to return the mock result
    mock_session.query.return_value.filter.return_value = case["filter"]
    mock_session.add.return_value = {}
    mock_session.commit.return_value = {}
    count_mock.return_value = case["count"]
    ver_mock.return_value = [{"id": 6}]
    mock_sql_instance.transactional_session.return_value.__enter__.return_value = mock_session
    # Create an instance of ImageDetails using the mocked SqlDB
    image_details = AddImageDetails(body_payload)
    # Call the method being tested
    result = image_details.insert_os_version(
        mock_session, os="iosxr", os_label="7.3.2-v6", os_version="7.3.2", createdBy="", modifiedBy=""
    )

    # Assertions
    assert result is case["response"]


@patch("connectors.core.services.admin.add_image_details.query_count")
@patch("connectors.core.utils.sqldb.swlifecycle_model.OSVersion")
def test_insert_os_version_device_region(ver_mock, count_mock):
    """
    Validate the insert os version device region function with payload
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Configure the return value of the session's query method to return the mock result
    mock_session.query.return_value.filter.return_value = []
    mock_session.add.return_value = {}
    mock_session.commit.return_value = {}
    count_mock.return_value = 0
    ver_mock.return_value = [{"id": 6}]
    mock_sql_instance.transactional_session.return_value.__enter__.return_value = mock_session
    # Create an instance of ImageDetails using the mocked SqlDB
    image_details = AddImageDetails(body_payload)
    # Call the method being tested
    result = image_details.insert_os_version_device_region(
        mock_session, device_region_id=4, os_version_id=2, os_validity_id=7, createdBy="", modifiedBy=""
    )

    # Assertions
    assert result is None


@patch("connectors.core.services.admin.add_image_details.query_count")
@patch("connectors.core.utils.sqldb.swlifecycle_model.FileType")
def test_image_type_details(ver_mock, count_mock):
    """
    Validate the insert os version device region function with payload
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Configure the return value of the session's query method to return the mock result
    mock_sql_instance.transactional_session.return_value.__enter__.return_value = mock_session
    # Create an instance of ImageDetails using the mocked SqlDB
    image_details = AddImageDetails(body_payload)
    # Call the method being tested
    result = image_details.image_type_details(mock_session, None)
    # Assertions
    assert result is None


@patch("connectors.core.services.admin.add_image_details.query_count")
@patch("connectors.core.utils.sqldb.swlifecycle_model.OSVersion")
def test_validation_check(ver_mock, count_mock):
    """
    Validate the insert os version device region function with payload
    """
    # Create a MagicMock instance for SqlDB
    mock_sql_instance = MagicMock()

    # Create a MagicMock instance for the session
    mock_session = MagicMock()

    # Configure the return value of the session's query method to return the mock result
    mock_session.query.return_value.filter.return_value = []
    mock_session.add.return_value = {}
    mock_session.commit.return_value = {}
    count_mock.return_value = 0
    ver_mock.return_value = [{"id": 6}]
    mock_sql_instance.transactional_session.return_value.__enter__.return_value = mock_session
    # Create an instance of ImageDetails using the mocked SqlDB
    image_details = AddImageDetails(body_payload)
    image_details.query_os_version_details = Mock()
    image_details.device_region_details = Mock(return_value=device_list)
    # Call the method being tested
    result = image_details.validation_check(
        mock_session,
        body_payload[0],
        {"metadata": {}},
        {"failure": []},
        status=[],
        errors=[],
        response_dict={
            "deviceVendor": "Cisco",
            "deviceModel": "NCS5K",
            "region": "DE",
            "osVersion": "7.3.0",
            "osLabel": "7.3.0-V1",
            "osStatus": "Deprecated",
        },
    )
    # Assertions
    assert result == ("", "", [], [])
