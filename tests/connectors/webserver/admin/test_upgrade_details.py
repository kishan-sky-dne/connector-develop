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
from connectors.core.services.admin.image_upgrade_details import ImageUpgradeDetails
from connectors.core.utils.exceptions import GenericConnectorsException
from connectors.webserver.admin.tasks.upgrade_details import image_upgrade_details

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
                    "currentOsLabel": "7.1.0-V1",
                    "currentOsVersion": "7.1.0",
                    "deviceModel": "NCS5K",
                    "deviceVendor": "CISCO",
                    "region": "UK",
                    "targetOsLabel": "7.5.1-V1",
                    "targetOsVersion": "7.5.1",
                },
                "osVersionUpgradeId": 20,
            }
        ],
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
        ],
    },
}

body = [
    {
        "deviceVendor": "Cisco",
        "deviceModel": "NCS5K",
        "region": "UK",
        "currentOsVersion": "7.1.0",
        "currentOsLabel": "7.1.0-V1",
        "upgrade": {
            "upgradeSteps": "2",
            "targetOs": {
                "osVersion": "7.5.1",
                "osLabel": "7.5.1-V1",
                "customConfig": [
                    {
                        "deviceRole": ["TA", "MA", "SuperCore"],
                        "beforeUpgrade": ["command in text format"],
                        "afterUpgrade": ["command in text format"],
                        "isRollbackRequired": False,
                    }
                ],
            },
            "intermediateSteps": [
                {
                    "osVersion": "7.3.0",
                    "osLabel": "7.3.0-V1",
                    "sequence": "1",
                    "customConfig": [
                        {
                            "deviceRole": ["TA", "MA", "SuperCore"],
                            "beforeUpgrade": ["command in text format"],
                            "afterUpgrade": ["command in text format"],
                            "isRollbackRequired": False,
                        }
                    ],
                }
            ],
        },
        "Comments": "Upgrade is due to certain reason... ",
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


@patch("connectors.core.services.admin.image_upgrade_details.ImageUpgradeDetails.image_upgrade_details")
def test_upgrade_details_try_block(get_image_details_mock):
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
    mock_image_details_obj.image_upgrade_details.return_value = mock_image_details
    ImageUpgradeDetails.return_value = mock_image_details_obj

    get_image_details_mock.return_value = image_details
    # Call the function
    result = image_upgrade_details(body=mock_body)

    # Assert the result
    assert result == mock_image_details


@patch("connectors.core.services.admin.image_upgrade_details.ImageUpgradeDetails.image_upgrade_details")
@pytest.mark.parametrize("exception_type, error_resp", exception_add_device)
def test_upgrade_details_except_block(get_images_details_mock, exception_type, error_resp):
    """
    To test the exception block of add image details
    :param get_images_details_mock:
    :return:
    """
    get_images_details_mock.side_effect = exception_type("dummy error message")
    response = image_upgrade_details(body=body)
    assert response == error_resp


@patch("connectors.core.services.admin.image_upgrade_details.ImageUpgradeDetails.image_upgrade_details")
def test_upgrade_details_except_block_1(get_images_details_mock):
    """
    To test the GenericConnectorsException block of add image details
    :param get_images_details_mock:
    :return:
    """
    get_images_details_mock.side_effect = GenericConnectorsException
    response = image_upgrade_details(body=body)
    assert response


body_1 = [
    {
        "deviceVendor": "CISCO",
        "deviceModel": "NCS5K",
        "region": "UK",
        "currentOsVersion": "7.3.2",
        "currentOsLabel": "7.3.2-v7",
        "upgrade": {
            "upgradeSteps": 2,
            "targetOs": {
                "osVersion": "7.3.2",
                "osLabel": "7.3.2-v9",
                "customConfig": [
                    {
                        "deviceRole": ["TA"],
                        "isRollbackRequired": True,
                        "configMode": "XR",
                    }
                ],
            },
            "intermediateSteps": [
                {
                    "osVersion": "7.3.2",
                    "osLabel": "7.3.2-v8",
                    "sequence": 1,
                    "customConfig": [
                        {
                            "deviceRole": ["TA"],
                            "isRollbackRequired": True,
                            "configMode": "XR",
                        }
                    ],
                }
            ],
        },
        "Comments": "Upgrade is due to certain reason... ",
    }
]


def test_image_upgrade_details():
    """
    Request body validation Test case for image_upgrade_details
    """
    assert image_upgrade_details(body=body_1) == {
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-1007",
                "message": "'beforeUpgrade' or 'afterUpgrade' or 'beforeRollback' or 'afterRollback' is a required "
                "property when custom config in upgrade.0.targetOs.customConfig.0",
            },
            {
                "code": "ERR-000-097-1007",
                "message": "'beforeUpgrade' or 'afterUpgrade' or 'beforeRollback' or 'afterRollback' is a required "
                "property when custom config  in upgrade.0.intermediateSteps.0.customConfig.0",
            },
        ],
        "status": "failure",
    }
