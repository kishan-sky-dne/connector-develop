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
from connectors.webserver.admin.tasks.addImage import add_image_details


@patch("connectors.core.services.admin.add_image_operations.AddImageOperations.add_device_image")
def test_get_image_details(add_device_image_mock):
    mocked_device_os_version_id = 3
    kwargs = {
        "body": {
            "deviceRole": "t_agg",
            "deviceVendor": "Cisco",
            "deviceModel": "NCS-5508",
            "os": "ios-xr",
            "osVersion": "7.0.2",
            "bootableFileDetails": [
                {
                    "fileName": "boot/install-image.iso",
                    "md5Value": "7c40343bdad67a6cda6f89153c66b3717c40343bdad67a6cda6f89153c66b3717c40343bdad67a6cda6f"
                    "89153c66b3717c40343bdad67a6cda6f89153c66b371",
                },
                {
                    "fileName": "EFI/boot/bootx64.efi",
                    "md5Value": "7c40343bdad67a6cda6f89153c66b3717c40343bdad67a6cda6f89153c66b3717c40343bdad67a6cda6f89"
                    "153c66b3717c40343bdad67a6cda6f89153c66b371",
                },
            ],
            "rpmPackageDetails": [
                {"fileName": "ncs5500-mpls64.rpm", "fileType": "XR"},
                {"fileName": "ncsr7C3.x86_64.rpm", "fileType": "CALVADOS"},
            ],
        },
        "user": "ipnd_dne_ops_dev",
    }
    add_device_image_mock.return_value = mocked_device_os_version_id
    expected_result = add_image_details(**kwargs)
    assert expected_result == {"status": "success", "deviceOsVersionId": 3}
    kwargs = {
        "body": {
            "deviceRole": "t_agg",
            "deviceVendor": "Cisco",
            "deviceModel": "NCS-5508",
            "os": "ios-xr",
            "osVersion": "7.0.2",
            "bootableFileDetails": [
                {"fileName": "boot/install-image.iso", "md5Value": "c05e19b77f977c2f3afe0b98f0b77aaa"},
                {
                    "fileName": "EFI/boot/bootx64.efi",
                    "md5Value": "7c40343bdad67a6cda6f89153c66b3717c40343bdad67a6cda6"
                    "f89153c66b3717c40343bdad67a6cda6f8915"
                    "3c66b3717c40343bdad67a6cda6f89153c66b371",
                },
            ],
            "rpmPackageDetails": [
                {"fileName": "ncs5500-mpls64.rpm", "fileType": "XR"},
                {"fileName": "ncsr7C3.x86_64.rpm", "fileType": "CALVADOS"},
            ],
        },
        "user": "ipnd_dne_ops_dev",
    }
    expected_result = add_image_details(**kwargs)
    assert expected_result == {
        "status": "failure",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-000-009-0001",
                "message": "Database Operation Failed. md5Value must be equal to 128 characters",
            }
        ],
    }
