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

# Third Party Library
import pytest

# DNE Library
from connectors.core.utils.exceptions import ResourceServiceNotAvailable, RestUtilityException
from connectors.webserver.dcs.tasks import read

device_details = {
    "admin_group": "Italia_SP",
    "collection": {
        "datetime": "2019-12-10T09:05:35Z",
        "errors": ["no response to ping"],
        "issues": "",
    },
    "device_type": "HuaweiOLT",
    "hostname": "xyz.test.bllab",
    "ipaddr": "10.11.25.162",
    "location": "MC3_brick_lane",
    "model": "",
    "model_family": "",
    "os": "",
    "os_version": "",
    "owner": "MD_IPAccess",
    "ports": "",
    "rev": "240-b8c9978a45c2203830dc29223de184c7",
    "snmp_sysdescr": "Huawei Integrated Access Software",
    "status": "development",
    "vendor": "huawei",
}

device_details_with_tacacs_secret = {
    "admin_group": "sky",
    "collection": {
        "datetime": "2022-02-22T14:45:28Z",
        "errors": [],
        "issues": "",
    },
    "device_type": "CiscoNCS",
    "hostname": "xyz.test.bllab",
    "ipaddr": "2.120.0.21",
    "location": "BLLAB",
    "model": "",
    "model_family": "",
    "os": "",
    "os_version": "7.1.2",
    "tacacs_secret": "fdskfslfkslad",
    "owner": "MD_TEST",
    "ports": "",
    "rev": "1935-b1654082a6ce16e9a301cc3f2e1a9b60",
    "snmp_sysdescr": "Cisco IOS XR Software (NCS-540)",
    "status": "development",
    "vendor": "cisco",
}

all_devices = [
    {"hostname": "8e02.mimnc.isp.sky.com"},
    {"hostname": "A2-AMServiceAddr.isp.sky.com"},
    {"hostname": "ap2.bllon.isp.sky.com"},
]

expected_devices = [{"hostname": "ap2.bllon.isp.sky.com"}]

exception_get_device = [(RestUtilityException, 403), (ResourceServiceNotAvailable, 404), (Exception, 500)]


@patch("connectors.core.services.dcs.connector.DeviceConfigurationService.device")
def test_get_device_details(mock_core_device_fn):
    """
    Test to check the functionality of getDeviceDetails()
    """
    mock_core_device_fn.return_value = device_details
    output = read.getDeviceDetails(hostname="xyz.test.bllab")
    assert output == device_details


@patch("connectors.core.services.dcs.connector.DeviceConfigurationService.device")
@pytest.mark.parametrize("exception_type, error_code", exception_get_device)
def test_get_device_details_raises_exception(mock_core_device_fn, exception_type, error_code):
    """
    Test to check if getDeviceDetails raises different exceptions.
    """
    mock_core_device_fn.side_effect = exception_type("dummy error message")
    response = read.getDeviceDetails(hostname="xyz.test.bllab")
    assert response.status_code == error_code


@patch("connectors.webserver.dcs.tasks.read.encrypt_sensitive_data")
@patch("connectors.webserver.dcs.tasks.read.connexion")
@patch("connectors.webserver.dcs.tasks.read.DeviceConfigurationService")
def test_get_device_details2(device_config_mock, connexion_mock, encrypt_sensitive_data_mock):
    """
    Test to check the functionality of getDeviceDetails()
    """
    encrypt_sensitive_data_mock.return_value = device_details_with_tacacs_secret
    output = read.getDeviceDetails(hostname="xyz.test.bllab")
    assert output == device_details_with_tacacs_secret


@patch("connectors.webserver.dcs.tasks.read.CacheController")
def test_get_all_devices(mock_cache_controller):
    """
    Test get_all_devices()
    """
    mock_cache_controller().get_filtered_devices.return_value = all_devices
    output = read.get_all_devices()
    assert output == all_devices


@patch("connectors.webserver.dcs.tasks.read.DeviceConfigurationService")
def test_get_all_device_vendors(mock_dcs):
    """
    Test get_all_devices()
    """
    mock_dcs().find_all_vendors.return_value = {"vendors": ["cisco", "nokia", "huawei"]}
    output = read.get_all_device_vendors()
    assert output == {"vendors": ["cisco", "nokia", "huawei"]}
    mock_dcs().find_all_vendors.assert_called_once_with()


@patch("connectors.webserver.dcs.tasks.read.DeviceConfigurationService")
def test_get_all_device_platforms(mock_dcs):
    """
    Test get_all_devices()
    """
    mock_dcs().find_all_platforms.return_value = {
        "platforms": ["ADE-OS", "Cisco IMC", "VMware ESXi", "asa", "gss", "ios", "ios-xr", "nx"]
    }
    output = read.get_all_device_platforms(vendor="cisco")
    assert output == {"platforms": ["ADE-OS", "Cisco IMC", "VMware ESXi", "asa", "gss", "ios", "ios-xr", "nx"]}
    mock_dcs().find_all_platforms.assert_called_once_with(vendor="cisco")


@patch("connectors.webserver.dcs.tasks.read.DeviceConfigurationService")
def test_get_all_device_os_versions(mock_dcs):
    """
    Test get_all_devices()
    """
    mock_dcs().find_all_os_versions.return_value = {
        "os_versions": [
            "24.1.2",
            "24.2.2",
            "25.1.1.27I",
        ]
    }
    output = read.get_all_device_os_versions(vendor="cisco", platform="ios-xr")
    assert output == {
        "os_versions": [
            "24.1.2",
            "24.2.2",
            "25.1.1.27I",
        ]
    }
    mock_dcs().find_all_os_versions.assert_called_once_with(vendor="cisco", platform="ios-xr")


@patch("connectors.webserver.dcs.tasks.read.DeviceConfigurationService")
def test_get_all_device_chassis(mock_dcs):
    """
    Test get_all_devices()
    """
    mock_dcs().find_all_chassis.return_value = {"chassis": ["ASR9K"]}
    output = read.get_all_device_chassis(vendor="cisco", platform="ios-xr", os_version="6.5.3")
    assert output == {"chassis": ["ASR9K"]}
    mock_dcs().find_all_chassis.assert_called_once_with(vendor="cisco", platform="ios-xr", os_version="6.5.3")
