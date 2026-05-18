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
from connectors.core.services.admin.get_device_os_version import DeviceDetails


def test_device_instance():
    """
     test to create device available Instance
    :return:
    """
    include = ["deviceVendor", "deviceRole", "deviceModel", "os"]
    limit = 10
    device_vendor = "Cisco"
    device_role = "m_agg"
    device_model = "NCS-540"
    os = "ios-xr"
    os_version = "7.0.2"
    status = "Active"
    created_on = "2020-12-11 13:20:44"
    modified_on = "2020-10-11 13:20:44"
    device_os_version_id = 5

    device_obj = DeviceDetails(
        include,
        limit,
        device_vendor,
        device_role,
        device_model,
        os,
        os_version,
        status,
        created_on,
        modified_on,
        device_os_version_id,
    )
    assert isinstance(device_obj, DeviceDetails)
    assert device_obj.include == ["deviceVendor", "deviceRole", "deviceModel", "os"]
    assert device_obj.limit == 10
    assert device_obj.device_role == "m_agg"
    assert device_obj.device_model == "NCS-540"
    assert device_obj.os == "ios-xr"
    assert device_obj.os_version == "7.0.2"
    assert device_obj.status == "Active"
    assert device_obj.created_on == "2020-12-11 13:20:44"
    assert device_obj.modified_on == "2020-10-11 13:20:44"
    assert device_os_version_id == 5


@patch("connectors.core.services.admin.read_image_operations.DeviceversionDetailsInfo.get_device_version_include")
@patch("connectors.core.services.admin.read_image_operations.DeviceversionDetailsInfo.get_device_version")
def test_get_device_details(get_device_version_mock, get_device_version_include_mock):
    """
    Unit test for get_device_details
    Returns:

    """
    include = ["deviceVendor", "deviceRole", "deviceModel", "os"]
    limit = 10
    device_vendor = "Cisco"
    device_role = "m_agg"
    device_model = "NCS-540"
    os = "ios-xr"
    os_version = "7.0.2"
    status = "Active"
    created_on = "2020-12-11 13:20:44"
    modified_on = "2020-10-11 13:20:44"
    device_os_version_id = 5
    device_obj = DeviceDetails(
        include,
        limit,
        device_vendor,
        device_role,
        device_model,
        os,
        os_version,
        status,
        created_on,
        modified_on,
        device_os_version_id,
    )
    mocked_device_os_version = [
        {
            "device_os_version_id": 3,
            "device_role": "t_agg",
            "device_vendor": "Cisco",
            "device_model": "NCS-5508",
            "os": "ios-xr",
            "os_version": "7.0.2",
            "status": "Active",
            "createdBy": "Mike",
            "created_on": "2020-11-11 13:23:44",
            "modifiedBy": "John",
            "modified_on": "2020-12-11 13:20:44",
        }
    ]
    get_device_version_include_mock.return_value = mocked_device_os_version
    result = device_obj.get_device_details()
    assert result == {
        "status": "success",
        "deviceOsVersionDetails": [
            {
                "device_os_version_id": 3,
                "device_role": "t_agg",
                "device_vendor": "Cisco",
                "device_model": "NCS-5508",
                "os": "ios-xr",
                "os_version": "7.0.2",
                "status": "Active",
                "createdBy": "Mike",
                "created_on": "2020-11-11 13:23:44",
                "modifiedBy": "John",
                "modified_on": "2020-12-11 13:20:44",
            }
        ],
    }
    include = None
    device_obj = DeviceDetails(
        include,
        limit,
        device_vendor,
        device_role,
        device_model,
        os,
        os_version,
        status,
        created_on,
        modified_on,
        device_os_version_id,
    )
    mocked_device_os_version = {
        "deviceOsVersionDetails": [
            {
                "device_os_version_id": 3,
                "device_role": "t_agg",
                "device_vendor": "Cisco",
                "device_model": "NCS-5508",
                "os": "ios-xr",
                "os_version": "7.0.2",
                "status": "Active",
                "bootableFileDetails": [
                    {"fileId": 3, "fileName": "boot/install-image.iso", "md5Value": "c05e19b77f977c2f3afe0b98f0b77aaa"},
                    {"fileId": 4, "fileName": "EFI/boot/bootx64.efi", "md5Value": "7c40343bdad67a6cda6f89153c66b371"},
                ],
                "rpmPackageDetails": [
                    {"packageId": 11, "fileName": "ncs5500-mpls-te-rsvp-3.1.0.0-r702.x86_64.rpm", "fileType": "XR"},
                    {
                        "packageId": 12,
                        "fileName": "ncs5500-sysadmin-fabric-7.0.2.1-r702.CSCvt64193.x86_64.rpm",
                        "fileType": "CALVADOS",
                    },
                ],
                "createdBy": "Mike",
                "created_on": "2020-11-11 13:23:44",
                "modifiedBy": "John",
                "modified_on": "2020-12-11 13:20:44",
            }
        ]
    }
    get_device_version_mock.return_value = mocked_device_os_version
    result = device_obj.get_device_details()
    assert result == {
        "status": "success",
        "deviceOsVersionDetails": {
            "deviceOsVersionDetails": [
                {
                    "device_os_version_id": 3,
                    "device_role": "t_agg",
                    "device_vendor": "Cisco",
                    "device_model": "NCS-5508",
                    "os": "ios-xr",
                    "os_version": "7.0.2",
                    "status": "Active",
                    "bootableFileDetails": [
                        {
                            "fileId": 3,
                            "fileName": "boot/install-image.iso",
                            "md5Value": "c05e19b77f977c2f3afe0b98f0b77aaa",
                        },
                        {
                            "fileId": 4,
                            "fileName": "EFI/boot/bootx64.efi",
                            "md5Value": "7c40343bdad67a6cda6f89153c66b371",
                        },
                    ],
                    "rpmPackageDetails": [
                        {"packageId": 11, "fileName": "ncs5500-mpls-te-rsvp-3.1.0.0-r702.x86_64.rpm", "fileType": "XR"},
                        {
                            "packageId": 12,
                            "fileName": "ncs5500-sysadmin-fabric-7.0.2.1-r702.CSCvt64193.x86_64.rpm",
                            "fileType": "CALVADOS",
                        },
                    ],
                    "createdBy": "Mike",
                    "created_on": "2020-11-11 13:23:44",
                    "modifiedBy": "John",
                    "modified_on": "2020-12-11 13:20:44",
                }
            ]
        },
    }
