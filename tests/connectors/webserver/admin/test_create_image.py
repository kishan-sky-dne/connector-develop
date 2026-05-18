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
from connectors.core.services.admin.add_image_details import AddImageDetails
from connectors.core.utils.exceptions import GenericConnectorsException
from connectors.webserver.admin.tasks.createImage import create_image_details

image_details = {
    "status": "PARTIAL-SUCCESS",
    "errorCategory": "FAILED",
    "errors": [
        {
            "code": "ERR-000-097-0500",
            "message": "Database Operation Failed. <<error message>>",
            "serviceReference": {"$ref": "#/metadata/failure/0"},
        }
    ],
    "metadata": {
        "success": [
            {
                "image": {
                    "deviceVendor": "Cisco",
                    "deviceModel": "NCS5K",
                    "region": "IT",
                    "osVersion": "7.1.0",
                    "osLabel": "7.1.0-V1",
                    "osStatus": "Deprecated",
                },
                "osVersionDeviceRegionId": "2",
            }
        ],
        "failure": [
            {
                "deviceVendor": "Cisco",
                "deviceModel": "NCS5K",
                "region": "UK",
                "osVersion": "7.1.0",
                "osLabel": "7.1.0-V1",
                "osStatus": "Deprecated",
            }
        ],
    },
}

body = [
    {
        "deviceVendor": "Cisco",
        "deviceModel": "NCS5K",
        "region": "DE",
        "osVersion": "7.3.0",
        "osLabel": "7.3.0-V1",
        "osStatus": "Deprecated",
        "osDetails": {
            "imageFile": [
                {
                    "imageType": "iso",
                    "fileName": "/bluebird/ios-xr/7.3.0/NCS540/install-image.iso",
                    "md5Value": "cb915e5704a0b30cfba48056567f625b",
                    "fileSize": "2742723234",
                }
            ],
            "package": [
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

body2 = [
    {
        "deviceVendor": "Cisco",
        "deviceModel": "NCS5K",
        "region": "DE",
        "osVersion": "7.3.0",
        "osLabel": "7.3.0-V1",
        "osStatus": "Current",
    }
]

exception_add_device = [
    (
        Exception,
        {
            "status": "failure",
            "errorCategory": "FAILED",
            "errors": [{"code": "ERR-000-097-0500", "message": "Database Operation Failed : dummy error message"}],
        },
    ),
]


@patch("connectors.core.services.admin.add_image_details.AddImageDetails.add_device_image")
def test_create_image_details_try_block(get_image_details_mock):
    """
    To test get image details
    :param get_image_details_mock:
    :return:
    """
    # Mock the necessary dependencies
    mock_body = body
    mock_image_details = image_details
    # AddImageOperations = MagicMock()
    mock_image_details_obj = MagicMock()
    mock_image_details_obj.add_device_image.return_value = mock_image_details
    AddImageDetails.return_value = mock_image_details_obj

    get_image_details_mock.return_value = image_details
    # Call the function
    result = create_image_details(body=mock_body)

    # Assert the result
    assert result == mock_image_details


@patch("connectors.core.services.admin.add_image_details.AddImageDetails.add_device_image")
@pytest.mark.parametrize("exception_type, error_resp", exception_add_device)
def test_create_image_details_except_block(get_images_details_mock, exception_type, error_resp):
    """
    To test the exception block of add image details
    :param get_images_details_mock:
    :return:
    """
    get_images_details_mock.side_effect = exception_type("dummy error message")
    response = create_image_details(body=body)
    assert response == error_resp


@patch("connectors.core.services.admin.add_image_details.AddImageDetails.add_device_image")
def test_create_image_details_except_block_1(get_images_details_mock):
    """
    To test the GenericConnectorsException block of add image details
    :param get_images_details_mock:
    :return:
    """
    get_images_details_mock.side_effect = GenericConnectorsException
    response = create_image_details(body=body)
    assert response


@patch("connectors.core.services.admin.add_image_details.AddImageDetails.add_device_image")
def test_create_image_details_try_block2(get_image_details_mock):
    """
    To test get image details
    :param get_image_details_mock:
    :return:
    """
    # Mock the necessary dependencies
    mock_body = body2
    mock_image_details = image_details
    # AddImageOperations = MagicMock()
    mock_image_details_obj = MagicMock()
    mock_image_details_obj.add_device_image.return_value = mock_image_details
    AddImageDetails.return_value = mock_image_details_obj

    get_image_details_mock.return_value = image_details
    # Call the function
    result = create_image_details(body=mock_body)

    # Assert the result
    assert result == {
        "status": "failure",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-1001",
                "message": "Validation Failed: Create image details osDetails is mandatory "
                "when os status is in Current or Under_test",
            }
        ],
    }
