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
from unittest.mock import patch

# DNE Library
from connectors.webserver.admin.tasks.read_image_metadata import get_image_details


@patch("connectors.core.services.admin.get_device_os_version.DeviceDetails.get_device_details")
def test_get_image_details(get_device_details_mock):
    mock_response = {
        "status": "success",
        "deviceOsVersionDetails": [
            {
                "deviceOsVersionId": 3,
                "deviceRole": "t_agg",
                "deviceVendor": "Cisco",
                "deviceModel": "NCS-5508",
                "os": "ios-xr",
                "osVersion": "7.0.2",
                "status": "Active",
                "createdBy": "Mike",
                "createdOn": "2020-11-11 13:23:44",
                "modifiedBy": "John",
                "modifiedOn": "2020-12-11 13:20:44",
            }
        ],
    }
    get_device_details_mock.return_value = mock_response

    image_details_obj = get_image_details(
        _include=["deviceVendor", "deviceRole", "deviceModel", "os"],
        limit=10,
        deviceVendor="Cisco",
        deviceRole="m_agg",
        deviceModel="NCS-540",
        os="ios-xr",
        osVersion="7.0.2",
        status="Active",
        createdOn="2020-12-11 13:20:44",
        modifiedOn="2020-10-11 13:20:44",
        deviceOsVersionId=5,
    )
    assert image_details_obj == mock_response
    image_details_obj = get_image_details(limit=10, status="Active", user="test", token_info="test")
    assert image_details_obj == {
        "status": "failure",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-009-0002",
                "message": "Filter criteria may result too much records, Please argument with another filter",
            }
        ],
    }
    image_details_obj = get_image_details(limit=10, user="test", token_info="test")
    assert image_details_obj == {
        "status": "failure",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-009-0002",
                "message": "Filter criteria may result too much records, Please argument with another filter",
            }
        ],
    }
