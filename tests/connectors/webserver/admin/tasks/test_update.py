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
from connectors.core.services.admin.update import UpdateDetails
from connectors.core.utils.exceptions import GenericConnectorsException
from connectors.webserver.admin.tasks.update import update_image_details, update_upgrade_details

update_details = {"comments": "Upgrade is due to certain reason... ", "osVersionUpgradeId": 4, "status": "success"}

update_details_1 = {"comments": "comments on this image data", "osVersionDeviceRegionId": 4, "status": "success"}

kwargs = {
    "osVersionUpgradeId": 5,
    "body": {
        "upgradeDetails": {
            "targetOs": {
                "customConfig": [
                    {
                        "deviceRole": ["TA"],
                        "beforeUpgrade": ["target before upgrade"],
                        "afterUpgrade": ["target after upgrade"],
                        "isRollbackRequired": True,
                        "beforeRollback": ["target before rollback1"],
                        "afterRollback": ["target after rollback1"],
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
}

kwargs1 = {
    "osVersionDeviceRegionId": 4,
    "body": {"osStatus": "Deprecated", "comments": "comments on this image data"},
}

exception = [
    (
        Exception,
        {
            "status": "failure",
            "errorCategory": "FAILED",
            "errors": [{"code": "ERR-000-097-0500", "message": "Database Operation Failed : dummy error message"}],
        },
    ),
]


@patch("connectors.core.services.admin.update.UpdateDetails.update_upgrade_details")
def test_update_upgrade_details_try_block(update_upgrade_details_mock):
    """
    To test update upgrade details success scenario
    """
    # Mock the necessary dependencies
    mock_upgrade_details = update_details
    mock_upgrade_details_obj = MagicMock()
    mock_upgrade_details_obj.image_upgrade_details.return_value = mock_upgrade_details
    UpdateDetails.return_value = mock_upgrade_details_obj

    update_upgrade_details_mock.return_value = update_details
    # Call the function
    result = update_upgrade_details(**kwargs)
    # Assert the result
    assert result == mock_upgrade_details


@patch("connectors.core.services.admin.update.UpdateDetails.update_upgrade_details")
@pytest.mark.parametrize("exception_type, error_resp", exception)
def test_update_upgrade_details_except_block(update_upgrade_details_mock, exception_type, error_resp):
    """
    To test the exception block of update upgrade details
    1. Generic excecption occurred
    """
    update_upgrade_details_mock.side_effect = exception_type("dummy error message")
    response = update_upgrade_details(**kwargs)
    assert response == error_resp


@patch("connectors.core.services.admin.update.UpdateDetails.update_upgrade_details")
def test_update_upgrade_details_except_block_1(update_upgrade_details_mock):
    """
    To test the GenericConnectorsException block of get upgrade details
    """
    update_upgrade_details_mock.side_effect = GenericConnectorsException
    response = update_upgrade_details(**kwargs)
    assert response


@patch("connectors.core.services.admin.update.UpdateDetails.update_image_details")
def test_update_image_details_try_block(update_image_details_mock):
    """
    To test update image details success scenario
    """
    # Mock the necessary dependencies
    mock_image_details = update_details_1
    mock_image_details_obj = MagicMock()
    mock_image_details_obj.image_upgrade_details.return_value = mock_image_details
    UpdateDetails.return_value = mock_image_details_obj

    update_image_details_mock.return_value = update_details_1
    # Call the function
    result = update_image_details(**kwargs1)
    # Assert the result
    assert result == mock_image_details


@patch("connectors.core.services.admin.update.UpdateDetails.update_image_details")
@pytest.mark.parametrize("exception_type, error_resp", exception)
def test_update_image_details_except_block(update_image_details_mock, exception_type, error_resp):
    """
    To test the exception block of update image details
    1. Generic exception occurred
    """
    update_image_details_mock.side_effect = exception_type("dummy error message")
    response = update_image_details(**kwargs)
    assert response == error_resp


@patch("connectors.core.services.admin.update.UpdateDetails.update_image_details")
def test_update_image_details_except_block_1(update_image_details_mock):
    """
    To test the GenericConnectorsException block of get image details
    """
    update_image_details_mock.side_effect = GenericConnectorsException
    response = update_image_details(**kwargs)
    assert response


body = {
    "upgradeDetails": {
        "targetOs": {
            "customConfig": [
                {
                    "deviceRole": ["TA", "MA", "SuperCore"],
                    "beforeUpgrade": ["update before upgrade target"],
                    "afterUpgrade": ["update after upgrade target"],
                    "isRollbackRequired": True,
                    "configMode": "XR",
                }
            ]
        },
        "intermediateSteps": [
            {
                "sequence": 1,
                "customConfig": [
                    {
                        "deviceRole": ["TA", "MA", "SuperCore"],
                        "beforeUpgrade": ["update before upgrade 1st intermediate"],
                        "afterUpgrade": ["update after upgrade 1st intermediate"],
                        "isRollbackRequired": True,
                        "configMode": "XR",
                    }
                ],
            }
        ],
    },
    "Comments": "Update comments for given upgrade details... ",
}


def test_update_upgrade_details():
    """
    Request body validation Test case for update_upgrade_details
    """
    assert update_upgrade_details(body=body) == {
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-097-1007",
                "message": "'beforeRollback' and 'afterRollback' is a required property when 'isRollbackRequired' is "
                "true in upgradeDetails.targetOs.customConfig.0",
            },
            {
                "code": "ERR-000-097-1007",
                "message": "'beforeRollback' and 'afterRollback' is a required property when 'isRollbackRequired' is "
                "true in upgradeDetails.intermediateSteps.0.customConfig.0",
            },
        ],
        "status": "failure",
    }
