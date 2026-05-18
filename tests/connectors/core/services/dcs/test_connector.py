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
from unittest import mock
from unittest.mock import call, patch

# Third Party Library
import pytest

# DNE Library
from connectors.core.exceptions import ConnectorsException
from connectors.core.services.dcs.connector import DeviceConfigurationService
from connectors.core.utils.exceptions import ResourceServiceNotAvailable, RestUtilityException

hostname = "ar15-cdn.thlon.isp.sky.com"
username = "abcd"
password = "xyz"
user_model = {
    "hostname": "ar15-cdn.thlon.isp.sky.com",
    "deviceVendor": "cisco",
    "deviceModel": "NCS-5508",
    "os": "ios-xr",
    "osVersion": "7.0.2",
    "adminGroup": "sky",
    "owner": "MD_IPCore",
    "status": "preproduction",
    "tacacsGroup": "IP_OVN_CRS",
    "tacacsSecret": "xfyg23sz6sf3rsah",
    "deviceType": "Cisco",
}

fail_response = (False, "hostname ar15-cdn.thlon.isp.sky.com already exists in DCS")

user_model1 = {
    "hostname": "ar16-cdn.thlon.isp.sky.com",
    "deviceVendor": "cisco",
    "deviceModel": "NCS-5508",
    "os": "ios-xr",
    "osVersion": "7.0.2",
    "adminGroup": "sky",
    "owner": "MD_IPCore",
    "status": "preproduction",
    "tacacsGroup": "IP_OVN_CRS",
    "tacacsSecret": "xfyg23sz6sf3rsah",
    "deviceType": "Cisco",
}

get_user_model = [
    {"param": "vendor", "operator": "eq", "values": ["mrv"], "logicalOperator": "and"},
    {"param": "hostname", "operator": "regex", "values": ["/.*cmbrau.*/"]},
]

get_user_model_2 = [
    {"param": "vendor", "operator": "ne", "values": ["mrv"]},
    {"param": "hostname", "operator": "regex", "values": ["/.*cmbrau.*/"]},
]

pass_response = None

exception_device_fn = (ValueError, TypeError, AttributeError)

sub_exceptions_add_device = [
    (ValueError, ConnectorsException),
    (TypeError, ConnectorsException),
    (AttributeError, ConnectorsException),
    (KeyError, ConnectorsException),
    (RestUtilityException, RestUtilityException),
]


def test_connector_add_device_instance():
    """
     test to create add device to dis Instance
    :return:
    """
    dis_create_obj = DeviceConfigurationService(
        hostname=hostname, username=username, password=password, data=user_model
    )
    assert isinstance(dis_create_obj, DeviceConfigurationService)


def test_add_device():
    """
    test to create add device to dcs
    :return:
    """
    dis_create_obj = DeviceConfigurationService(
        hostname=hostname, username=username, password=password, data=user_model1
    )
    dis_create_obj.rest.post = mock.Mock(return_value=({"hostname": "ar16-cdn.thlon.isp.sky.com"}))
    dis_create_obj.device = resource_side_effect
    assert dis_create_obj.add_device() == {"hostname": "ar16-cdn.thlon.isp.sky.com"}


def resource_side_effect():
    raise ResourceServiceNotAvailable


@mock.patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@pytest.mark.parametrize("exception_type", exception_device_fn)
def test_add_device_connectors_exception(mock_rest_get, exception_type):
    """
    Test to verify if add_device raises ConnectorsException(for ValueError/TypeError/AttributeError)
    """
    dcs = DeviceConfigurationService(hostname=hostname, username=username, password=password, data=user_model)
    mock_rest_get.side_effect = exception_type("dummy error message")
    with pytest.raises(ConnectorsException):
        dcs.add_device()


@mock.patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@mock.patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@pytest.mark.parametrize("exception_type, raised_exception", sub_exceptions_add_device)
def test_add_device_sub_exceptions(mock_rest_get, mock_rest_post, exception_type, raised_exception):
    """
    Test to verify if add_device raises sub-exceptions ConnectorsException(for ValueError/TypeError/AttributeError/
        Keyerror) and RestUtilityException
    """
    dcs = DeviceConfigurationService(hostname=hostname, username=username, password=password, data=user_model)

    class ResponseMock:
        def __init__(self):
            self.status_code = 404

    resp = ResponseMock()
    mock_rest_get.side_effect = (
        exception_type("dummy error message")
        if exception_type != RestUtilityException
        else exception_type("dummy error message", resp)
    )
    mock_rest_post.side_effect = (
        exception_type("dummy error message")
        if exception_type != RestUtilityException
        else exception_type("dummy error message", resp)
    )
    with pytest.raises(raised_exception):
        dcs.add_device()


@mock.patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@pytest.mark.parametrize("exception_type", exception_device_fn)
def test_device_fn_connectors_exception(mock_rest_get, exception_type):
    """
    Test to verify if device() function raises ConnectorsException(for ValueError/TypeError/AttributeError)
    """
    dcs = DeviceConfigurationService(hostname=hostname, username=username, password=password)
    mock_rest_get.side_effect = exception_type("dummy error message")
    with pytest.raises(ConnectorsException):
        dcs.device()


user_model2 = [
    {"op": "replace", "attribute": "status", "value": "production"},
    {"op": "add", "attribute": "owner", "value": "test"},
]


def test_update_device():
    """
    test to update device to dcs
    :return:
    """
    dis_update_obj = DeviceConfigurationService(
        hostname=hostname, username=username, password=password, data=user_model2
    )
    dis_update_obj.rest.patch = mock.Mock(return_value=({"hostname": "ar16-cdn.thlon.isp.sky.com"}))
    dis_update_obj.device = resource_side_effect
    assert dis_update_obj.update_device() == {"status": "SUCCESS"}


@mock.patch("connectors.core.utils.rest_api_utility.RestUtility.patch")
@pytest.mark.parametrize("exception_type", exception_device_fn)
def test_update_device_connectors_exception(mock_rest_patch, exception_type):
    """
    Test to verify if update_device raises ConnectorsException(for ValueError/TypeError/AttributeError)
    """
    dcs = DeviceConfigurationService(hostname=hostname, username=username, password=password, data=user_model2)
    mock_rest_patch.side_effect = exception_type("dummy error message")
    with pytest.raises(ConnectorsException):
        dcs.update_device()


@mock.patch("connectors.core.utils.rest_api_utility.RestUtility.patch")
@mock.patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@pytest.mark.parametrize("exception_type, raised_exception", sub_exceptions_add_device)
def test_update_device_sub_exceptions(mock_rest_get, mock_rest_patch, exception_type, raised_exception):
    """
    Test to verify if update_device raises sub-exceptions ConnectorsException(for ValueError/TypeError/AttributeError/
        Keyerror) and RestUtilityException
    """
    dcs = DeviceConfigurationService(hostname=hostname, username=username, password=password, data=user_model2)

    class ResponseMock:
        def __init__(self):
            self.status_code = 400

    resp = ResponseMock()
    mock_rest_get.side_effect = (
        exception_type("dummy error message")
        if exception_type != RestUtilityException
        else exception_type("dummy error message", resp)
    )
    mock_rest_patch.side_effect = (
        exception_type("dummy error message")
        if exception_type != RestUtilityException
        else exception_type("dummy error message", resp)
    )
    with pytest.raises(raised_exception):
        dcs.update_device()


@mock.patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_all_devices(mock_rest_get):
    """
    Test all_devices()
    """
    dcs = DeviceConfigurationService(hostname=None, username=username, password=password)
    mock_rest_get.return_value = "dummy"
    assert dcs.all_devices() == "dummy"
    mock_rest_get.assert_called_once_with(mock.ANY, log_results=False)


@mock.patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_all_devices_rest_exception(mock_rest_get):
    """
    Test to verify if all_devices() function raises RestUtilityException
    """
    dcs = DeviceConfigurationService(hostname=None, username=username, password=password)
    mock_rest_get.side_effect = RestUtilityException("dummy message")
    with pytest.raises(ConnectorsException):
        dcs.all_devices()


@mock.patch("connectors.core.utils.rest_api_utility.RestUtility.put")
def test_send_dcs_fetch_request(mock_put):
    """
    Tests dcs fetch request for success response.
    """
    dcs = DeviceConfigurationService(hostname=None, username=username, password=password)
    mock_put.return_value = "Success Response"
    assert dcs.send_dcs_fetch_request() == "Success Response"


device_resp = {
    "pageNumber": 1,
    "totalPages": 1,
    "offset": 0,
    "limit": 100,
    "results": [
        {
            "access": None,
            "admin_group": "sky",
            "collection": {
                "collector": "dis-col01.nme.bllon.sns.sky.com",
                "datetime": "2023-05-15T09:13:45Z",
                "detail": [
                    {
                        "descr": "Resolve cm0.cmbrau.isp.sky.com to 90.222.227.117",
                        "error": None,
                        "name": "Resolver",
                        "time": 0,
                    },
                    {"descr": "Sky auth credentials setup", "error": None, "name": "SkyAuthSetup", "time": 0},
                    {
                        "descr": "SNMP community guesser (version 2 community 2)",
                        "error": None,
                        "name": "SnmpCommunityGuesser",
                        "time": 22,
                    },
                    {"descr": "SNMP sys probe mrv lx", "error": None, "name": "SnmpSysDescrProbe", "time": 0},
                    {
                        "descr": "MRV LX multi config fetch (binary 20652 bytes, config length 9037)",
                        "error": None,
                        "name": "MrvLxMultiConfigFetch",
                        "time": 12,
                    },
                    {
                        "descr": "SNMP interfaces probe (found 8 interfaces)",
                        "error": None,
                        "name": "MrvLxPortConfigSet",
                        "time": 0,
                    },
                    {
                        "descr": "Binary config archival: saved 0 copies (20652 total bytes compressed)",
                        "error": None,
                        "name": "ArchiveBinConfig",
                        "time": 0,
                    },
                    {"descr": "Config commit:  committed", "error": None, "name": "UpdateConfig", "time": 7},
                    {"descr": "Config parse processing", "error": None, "name": "ConfigParseProc", "time": 1},
                    {"descr": "Probe status: OK", "error": None, "name": "ProbeStatus", "time": 0},
                ],
                "errors": [],
                "issues": {"error": {}},
            },
            "config": {
                "datetime": "2020-07-10T01:47:58Z",
                "id": "eac93339c0a48818c4c5460f52a29f2eb4d293e3",
                "size": 9037,
            },
            "device_type": "MRV_LX",
            "hostname": "cm0.cmbrau.isp.sky.com",
            "ipaddr": "90.222.227.117",
            "known_issue": None,
            "location": "BRAUNSTON",
            "model": "lx",
            "os": None,
            "os_version": None,
            "owner": "MD_IPAccess",
            "ports": [
                {"descr": "bm0.cmbrau", "enabled": 1, "name": 3},
                {"descr": "free", "enabled": 1, "name": 7},
                {"descr": "wbm0.cmbrau", "enabled": 1, "name": 8},
                {"descr": "ar0.cmbrau", "enabled": 1, "name": 1},
                {"descr": "as100.cmbrau", "enabled": 1, "name": 4},
                {"descr": "vm0.cmbrau.ntb", "enabled": 1, "name": 5},
                {"descr": "vm0.cmbrau.nta", "enabled": 1, "name": 6},
                {"descr": "free", "enabled": 1, "name": 2},
            ],
            "rev": "5024-4a142a732ed75641de7c5efc45b48085",
            "snmp_sysdescr": "LX Console Manager, s/w version=5.3.9",
            "status": "production",
            "tacacs_group": "IP_OVN_MRV",
            "vendor": "mrv",
        }
    ],
}

user_model_list = [get_user_model, get_user_model_2]


@pytest.mark.parametrize("user_data", user_model_list)
def test_get_all_device_details(user_data):
    """
    test to get all device details to dcs
    :return:
    """
    dis_create_obj = DeviceConfigurationService(
        hostname=hostname, username=username, password=password, filters=user_data, page_number=1, offset=0, limit=100
    )
    dis_create_obj.rest.get = mock.Mock(return_value=device_resp["results"])
    assert dis_create_obj.get_all_device_details() == device_resp


def test_get_all_device_details_no_filter():
    """
    test to get all device details to dcs
    :return:
    """
    dis_create_obj = DeviceConfigurationService(
        hostname=hostname, username=username, password=password, filters=[], page_number=1, offset=0, limit=100
    )
    dis_create_obj.rest.get = mock.Mock(return_value=device_resp["results"])
    assert dis_create_obj.get_all_device_details() == device_resp


error_details = {
    "errorCategory": "FAILED",
    "errors": [{"code": "ERR-011-999-1001", "message": "Getting device details from DCS failed:"}],
}

exception_list = [
    {
        "exception_type": RestUtilityException,
        "exception_value": RestUtilityException("dummy message"),
        "error_data": "",
    },
    {
        "exception_type": Exception,
        "exception_value": Exception,
        "error_data": error_details,
    },
]


@mock.patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@pytest.mark.parametrize("exception_data", exception_list)
def test_get_all_device_details_exceptions(mock_rest_get, exception_data):
    """
    Test to verify if get_all_device_details raises Exception
    RestUtilityException
    """
    dcs = DeviceConfigurationService(
        hostname=hostname,
        username=username,
        password=password,
        filters=get_user_model,
        page_number=1,
        offset=0,
        limit=100,
    )
    mock_rest_get.side_effect = exception_data["exception_value"]
    if exception_data["exception_type"] == RestUtilityException:
        with pytest.raises(RestUtilityException):
            dcs.get_all_device_details()
    else:
        response = dcs.get_all_device_details()
        assert response == exception_data["error_data"]


error_data = [
    {
        "device_response": [],
        "final_response": {"pageNumber": 1, "totalPages": 0, "offset": 0, "limit": 100, "results": []},
        "limit": 100,
        "offset": 0,
        "pageNumber": 1,
    },
    {
        "device_response": [
            {
                "access": None,
                "admin_group": "sky",
                "collection": {
                    "collector": "dis-col01.nme.bllon.sns.sky.com",
                    "datetime": "2023-05-15T09:13:45Z",
                    "detail": [
                        {
                            "descr": "Resolve cm0.cmbrau.isp.sky.com to 90.222.227.117",
                            "error": None,
                            "name": "Resolver",
                            "time": 0,
                        },
                        {"descr": "Sky auth credentials setup", "error": None, "name": "SkyAuthSetup", "time": 0},
                        {
                            "descr": "SNMP community guesser (version 2 community 2)",
                            "error": None,
                            "name": "SnmpCommunityGuesser",
                            "time": 22,
                        },
                        {"descr": "SNMP sys probe mrv lx", "error": None, "name": "SnmpSysDescrProbe", "time": 0},
                        {
                            "descr": "MRV LX multi config fetch (binary 20652 bytes, config length 9037)",
                            "error": None,
                            "name": "MrvLxMultiConfigFetch",
                            "time": 12,
                        },
                        {
                            "descr": "SNMP interfaces probe (found 8 interfaces)",
                            "error": None,
                            "name": "MrvLxPortConfigSet",
                            "time": 0,
                        },
                        {
                            "descr": "Binary config archival: saved 0 copies (20652 total bytes compressed)",
                            "error": None,
                            "name": "ArchiveBinConfig",
                            "time": 0,
                        },
                        {"descr": "Config commit:  committed", "error": None, "name": "UpdateConfig", "time": 7},
                        {"descr": "Config parse processing", "error": None, "name": "ConfigParseProc", "time": 1},
                        {"descr": "Probe status: OK", "error": None, "name": "ProbeStatus", "time": 0},
                    ],
                    "errors": [],
                    "issues": {"error": {}},
                },
                "config": {
                    "datetime": "2020-07-10T01:47:58Z",
                    "id": "eac93339c0a48818c4c5460f52a29f2eb4d293e3",
                    "size": 9037,
                },
                "device_type": "MRV_LX",
                "hostname": "cm0.cmbrau.isp.sky.com",
                "ipaddr": "90.222.227.117",
                "known_issue": None,
                "location": "BRAUNSTON",
                "model": "lx",
                "os": None,
                "os_version": None,
                "owner": "MD_IPAccess",
                "ports": [
                    {"descr": "bm0.cmbrau", "enabled": 1, "name": 3},
                    {"descr": "free", "enabled": 1, "name": 7},
                    {"descr": "wbm0.cmbrau", "enabled": 1, "name": 8},
                    {"descr": "ar0.cmbrau", "enabled": 1, "name": 1},
                    {"descr": "as100.cmbrau", "enabled": 1, "name": 4},
                    {"descr": "vm0.cmbrau.ntb", "enabled": 1, "name": 5},
                    {"descr": "vm0.cmbrau.nta", "enabled": 1, "name": 6},
                    {"descr": "free", "enabled": 1, "name": 2},
                ],
                "rev": "5024-4a142a732ed75641de7c5efc45b48085",
                "snmp_sysdescr": "LX Console Manager, s/w version=5.3.9",
                "status": "production",
                "tacacs_group": "IP_OVN_MRV",
                "vendor": "mrv",
            }
        ],
        "final_response": {
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-011-999-1001",
                    "message": "Given offset is exceeding than total response",
                }
            ],
        },
        "limit": 20,
        "offset": 10,
        "pageNumber": 2,
    },
    {
        "device_response": [
            {
                "access": None,
                "admin_group": "sky",
                "collection": {
                    "collector": "dis-col01.nme.bllon.sns.sky.com",
                    "datetime": "2023-05-15T09:13:45Z",
                    "detail": [
                        {
                            "descr": "Resolve cm0.cmbrau.isp.sky.com to 90.222.227.117",
                            "error": None,
                            "name": "Resolver",
                            "time": 0,
                        },
                        {"descr": "Sky auth credentials setup", "error": None, "name": "SkyAuthSetup", "time": 0},
                        {
                            "descr": "SNMP community guesser (version 2 community 2)",
                            "error": None,
                            "name": "SnmpCommunityGuesser",
                            "time": 22,
                        },
                        {"descr": "SNMP sys probe mrv lx", "error": None, "name": "SnmpSysDescrProbe", "time": 0},
                        {
                            "descr": "MRV LX multi config fetch (binary 20652 bytes, config length 9037)",
                            "error": None,
                            "name": "MrvLxMultiConfigFetch",
                            "time": 12,
                        },
                        {
                            "descr": "SNMP interfaces probe (found 8 interfaces)",
                            "error": None,
                            "name": "MrvLxPortConfigSet",
                            "time": 0,
                        },
                        {
                            "descr": "Binary config archival: saved 0 copies (20652 total bytes compressed)",
                            "error": None,
                            "name": "ArchiveBinConfig",
                            "time": 0,
                        },
                        {"descr": "Config commit:  committed", "error": None, "name": "UpdateConfig", "time": 7},
                        {"descr": "Config parse processing", "error": None, "name": "ConfigParseProc", "time": 1},
                        {"descr": "Probe status: OK", "error": None, "name": "ProbeStatus", "time": 0},
                    ],
                    "errors": [],
                    "issues": {"error": {}},
                },
                "config": {
                    "datetime": "2020-07-10T01:47:58Z",
                    "id": "eac93339c0a48818c4c5460f52a29f2eb4d293e3",
                    "size": 9037,
                },
                "device_type": "MRV_LX",
                "hostname": "cm0.cmbrau.isp.sky.com",
                "ipaddr": "90.222.227.117",
                "known_issue": None,
                "location": "BRAUNSTON",
                "model": "lx",
                "os": None,
                "os_version": None,
                "owner": "MD_IPAccess",
                "ports": [
                    {"descr": "bm0.cmbrau", "enabled": 1, "name": 3},
                    {"descr": "free", "enabled": 1, "name": 7},
                    {"descr": "wbm0.cmbrau", "enabled": 1, "name": 8},
                    {"descr": "ar0.cmbrau", "enabled": 1, "name": 1},
                    {"descr": "as100.cmbrau", "enabled": 1, "name": 4},
                    {"descr": "vm0.cmbrau.ntb", "enabled": 1, "name": 5},
                    {"descr": "vm0.cmbrau.nta", "enabled": 1, "name": 6},
                    {"descr": "free", "enabled": 1, "name": 2},
                ],
                "rev": "5024-4a142a732ed75641de7c5efc45b48085",
                "snmp_sysdescr": "LX Console Manager, s/w version=5.3.9",
                "status": "production",
                "tacacs_group": "IP_OVN_MRV",
                "vendor": "mrv",
            }
        ],
        "final_response": {
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-011-999-1001",
                    "message": "Given page number is exceeding than total page",
                }
            ],
        },
        "limit": 10,
        "offset": 0,
        "pageNumber": 2,
    },
]


@pytest.mark.parametrize("params", error_data)
def test_get_directory_details_case(params):
    """
    test to get all device details to dcs with empty and error response
    """
    dis_create_obj = DeviceConfigurationService(
        hostname=hostname,
        username=username,
        password=password,
        filters=get_user_model,
        page_number=params["pageNumber"],
        offset=params["offset"],
        limit=params["limit"],
    )
    dis_create_obj.rest.get = mock.Mock(return_value=params["device_response"])
    assert dis_create_obj.get_all_device_details() == params["final_response"]


@patch.object(DeviceConfigurationService, "_generate_dcs_filter")
@patch.object(DeviceConfigurationService, "_find_all_values_in_dcs_response")
def test_find_all_vendors(mocked_find_all_values_in_dcs_response, mocked_generate_dcs_filter):
    dcs = DeviceConfigurationService(
        hostname=hostname,
        username=username,
        password=password,
        filters=get_user_model,
        page_number=0,
        offset=0,
        limit=0,
    )
    mocked_find_all_values_in_dcs_response.return_value = ["cisco", "nokia", "huawei"]
    response = dcs.find_all_vendors()
    assert response == {"vendors": ["cisco", "nokia", "huawei"]}
    mocked_find_all_values_in_dcs_response.assert_called_once_with("vendor")
    mocked_generate_dcs_filter.assert_not_called()


@patch.object(DeviceConfigurationService, "_generate_dcs_filter")
@patch.object(DeviceConfigurationService, "_find_all_values_in_dcs_response")
def test_find_all_platforms(mocked_find_all_values_in_dcs_response, mocked_generate_dcs_filter):
    dcs = DeviceConfigurationService(
        hostname=hostname,
        username=username,
        password=password,
        filters=get_user_model,
        page_number=0,
        offset=0,
        limit=0,
    )
    mocked_find_all_values_in_dcs_response.return_value = [
        "ADE-OS",
        "Cisco IMC",
        "VMware ESXi",
        "asa",
        "gss",
        "ios",
        "ios-xr",
        "nx",
    ]
    response = dcs.find_all_platforms(vendor="cisco")
    assert response == {"platforms": ["ADE-OS", "Cisco IMC", "VMware ESXi", "asa", "gss", "ios", "ios-xr", "nx"]}
    mocked_find_all_values_in_dcs_response.assert_called_once_with("os")
    mocked_generate_dcs_filter.assert_called_once_with("cisco", "vendor")


@patch.object(DeviceConfigurationService, "_generate_dcs_filter")
@patch.object(DeviceConfigurationService, "_find_all_values_in_dcs_response")
def test_find_all_os_versions(mocked_find_all_values_in_dcs_response, mocked_generate_dcs_filter):
    dcs = DeviceConfigurationService(
        hostname=hostname,
        username=username,
        password=password,
        filters=get_user_model,
        page_number=0,
        offset=0,
        limit=0,
    )
    mocked_find_all_values_in_dcs_response.return_value = [
        "24.1.2",
        "24.2.2",
        "25.1.1.27I",
        "4.3.4",
        "5.2.3",
    ]
    response = dcs.find_all_os_versions(vendor="cisco", platform="ios-xr")
    assert response == {
        "os_versions": [
            "24.1.2",
            "24.2.2",
            "25.1.1.27I",
            "4.3.4",
            "5.2.3",
        ]
    }
    mocked_find_all_values_in_dcs_response.assert_called_once_with("os_version")
    mocked_generate_dcs_filter.assert_has_calls([call("cisco", "vendor"), call("ios-xr", "os")])


@patch.object(DeviceConfigurationService, "_generate_dcs_filter")
@patch.object(DeviceConfigurationService, "_find_all_values_in_dcs_response")
def test_find_all_chassis(mocked_find_all_values_in_dcs_response, mocked_generate_dcs_filter):
    dcs = DeviceConfigurationService(
        hostname=hostname,
        username=username,
        password=password,
        filters=get_user_model,
        page_number=0,
        offset=0,
        limit=0,
    )
    mocked_find_all_values_in_dcs_response.return_value = ["ASR9K"]
    response = dcs.find_all_chassis(vendor="cisco", platform="ios-xr", os_version="7.9.2")
    assert response == {"chassis": ["ASR9K"]}
    mocked_find_all_values_in_dcs_response.assert_called_once_with("model")
    mocked_generate_dcs_filter.assert_has_calls(
        [call("cisco", "vendor"), call("ios-xr", "os"), call("7.9.2", "os_version")]
    )


def test_generate_dcs_filter():
    dcs = DeviceConfigurationService(
        hostname=hostname,
        username=username,
        password=password,
        filters=get_user_model,
        page_number=0,
        offset=0,
        limit=0,
    )
    assert dcs._generate_dcs_filter("cisco", "vendor") == {
        "logicalOperator": "and",
        "operator": "eq",
        "param": "vendor",
        "values": ["CISCO", "Cisco", "cisco"],
    }


dcs_device_response = [
    {
        "access": None,
        "admin_group": "Group_SP",
        "collection": {
            "collector": "dis-col01.nme.bllon.sns.sky.com",
            "datetime": "2025-05-01T03:00:33Z",
            "detail": [
                {
                    "descr": "Resolve ak1-pp.bllab.isp.sky.com to 2.120.0.86",
                    "error": None,
                    "name": "Resolver",
                    "time": 0,
                },
                {"descr": "Group_SP auth credentials setup", "error": None, "name": "GroupSpAuthSetup", "time": 0},
                {
                    "descr": "SNMP community guesser (version 3)",
                    "error": None,
                    "name": "SnmpCommunityGuesser",
                    "time": 110,
                },
                {"descr": "SNMP sys probe cisco", "error": None, "name": "SnmpSysDescrProbe", "time": 1},
                {
                    "descr": "Cisco recogniser PPC_LINUX_IOSD-UNIVERSALK9_NPE-M ios 16.12.8,",
                    "error": None,
                    "name": "CiscoRecognition",
                    "time": 0,
                },
                {"descr": "Ping probe: ok", "error": None, "name": "Ping", "time": 3},
                {
                    "descr": "SNMP interfaces probe (found 36 interfaces)",
                    "error": None,
                    "name": "SnmpInterfacesProbe",
                    "time": 0,
                },
                {"descr": "Cisco model probe: ASR-920-24SZ-M", "error": None, "name": "CiscoSoftwareModel", "time": 31},
                {
                    "descr": "Cisco config (by ssh) fetch (48126 bytes)",
                    "error": None,
                    "name": "CiscoConfig",
                    "time": 32,
                },
                {"descr": "Cisco config parse", "error": None, "name": "CiscoConfigParse", "time": 0},
                {"descr": "Config commit:  committed", "error": None, "name": "UpdateConfig", "time": 26},
                {"descr": "Config parse processing", "error": None, "name": "ConfigParseProc", "time": 0},
                {"descr": "Probe status", "error": None, "name": "ProbeStatus", "time": 0},
            ],
            "errors": [],
            "issues": None,
        },
        "config": {"datetime": "2025-04-24T18:48:56Z", "id": "d2927516439726f8ca03e8e1d7de35cc3df302f7", "size": 48126},
        "device_type": "Cisco",
        "hostname": "ak1-pp.bllab.isp.sky.com",
        "ipaddr": "2.120.0.86",
        "known_issue": None,
        "location": "UK/BRICKLANE/Sky POP/Basement MR/Rack C20",
        "model": "ASR-920-24SZ-M",
        "os": "ios",
        "os_version": "16.12.8,",
        "owner": "MD_TEST",
        "rev": "507-fdffa3e149d1823da4353dead23e930b",
        "snmp_sysdescr": "Cisco IOS Software [Gibraltar], ASR920 Software (PPC_LINUX_IOSD-UNIVERSALK9_NPE-M), "
        "Version 16.12.8, RELEASE SOFTWARE (fc1)\r\nTechnical Support: http://www.cisco.com/techsupport\r\nCopyright "
        "(c) 1986-2022 by Cisco Systems, Inc.\r\nCompiled Thu 15-Sep-22 05:28 ",
        "status": "development",
        "tacacs_group": "TBC",
        "vendor": "cisco",
    },
    {
        "access": None,
        "admin_group": "enterprise",
        "collection": {
            "collector": "dis-col01.nme.enslo.sns.sky.com",
            "datetime": "2025-05-01T12:45:59Z",
            "detail": [
                {
                    "descr": "Resolve aoip-h1-dswt-01.bskyb.com to 10.254.209.27",
                    "error": None,
                    "name": "Resolver",
                    "time": 0,
                },
                {"descr": "Enterprise auth credentials setup", "error": None, "name": "EnterpriseAuthSetup", "time": 0},
                {
                    "descr": "SNMP community guesser (version 2 community 1)",
                    "error": None,
                    "name": "SnmpCommunityGuesser",
                    "time": 0,
                },
                {"descr": "SNMP sys probe cisco", "error": None, "name": "SnmpSysDescrProbe", "time": 0},
                {"descr": "Cisco recogniser nxos nx 7.0(3)I5(2)", "error": None, "name": "CiscoRecognition", "time": 0},
                {
                    "descr": "SNMP interfaces probe (found 77 interfaces)",
                    "error": None,
                    "name": "SnmpInterfacesProbe",
                    "time": 2,
                },
                {
                    "descr": "Cisco model probe: Nexus9000 93180YC-EX",
                    "error": None,
                    "name": "CiscoSoftwareModel",
                    "time": 34,
                },
                {
                    "descr": "Cisco config (by ssh) fetch (33418 bytes)",
                    "error": None,
                    "name": "CiscoConfig",
                    "time": 32,
                },
                {"descr": "Cisco config parse", "error": None, "name": "CiscoConfigParse", "time": 0},
                {"descr": "Config commit:  committed DB updated", "error": None, "name": "UpdateConfig", "time": 1773},
                {"descr": "Config parse processing", "error": None, "name": "ConfigParseProc", "time": 0},
                {"descr": "Probe status: OK", "error": None, "name": "ProbeStatus", "time": 0},
            ],
            "errors": [],
            "issues": {"error": {}},
        },
        "config": {"datetime": "2025-05-01T12:45:54Z", "id": "fa06785aafa0916c402f9b8b5c9a37d45c9773be", "size": 33418},
        "device_type": "Cisco",
        "hostname": "aoip-h1-dswt-01.bskyb.com",
        "ipaddr": "10.254.209.27",
        "known_issue": None,
        "location": "Osterley, Sky Studios, TER21, J11",
        "model": "Nexus9000 93180YC-EX",
        "model_family": "nxos.7.0.3.I5.2.bin",
        "os": "nx",
        "os_version": "7.0(3)I5(2)",
        "owner": "MD_ENTERPRISE",
        "rev": "7535-3358cf48e72efa7419a00a0c169d03b3",
        "snmp_sysdescr": "Cisco NX-OS(tm) nxos.7.0.3.I5.2.bin, Software (nxos), Version 7.0(3)I5(2), RELEASE SOFTWARE "
        "Copyright (c) 2002-2016 by Cisco Systems, Inc. Compiled 2/16/2017 7:00:00",
        "status": "production",
        "tacacs_group": "TBC",
        "vendor": "cisco",
    },
    {
        "access": None,
        "admin_group": "enterprise",
        "collection": {
            "collector": "dis-col01.nme.bllon.sns.sky.com",
            "datetime": "2025-05-01T00:01:51Z",
            "detail": [
                {
                    "descr": "Resolve aoip-h1-dswt-02.bskyb.com to 10.254.210.18",
                    "error": None,
                    "name": "Resolver",
                    "time": 0,
                },
                {"descr": "Enterprise auth credentials setup", "error": None, "name": "EnterpriseAuthSetup", "time": 0},
                {
                    "descr": "SNMP community guesser (version 2 community 1)",
                    "error": None,
                    "name": "SnmpCommunityGuesser",
                    "time": 0,
                },
                {"descr": "SNMP sys probe cisco", "error": None, "name": "SnmpSysDescrProbe", "time": 0},
                {"descr": "Cisco recogniser nxos nx 7.0(3)I5(2)", "error": None, "name": "CiscoRecognition", "time": 0},
                {
                    "descr": "SNMP interfaces probe (found 77 interfaces)",
                    "error": None,
                    "name": "SnmpInterfacesProbe",
                    "time": 1,
                },
                {
                    "descr": "Cisco model probe: Nexus9000 93180YC-EX",
                    "error": None,
                    "name": "CiscoSoftwareModel",
                    "time": 32,
                },
                {
                    "descr": "Cisco config (by ssh) fetch (33282 bytes)",
                    "error": None,
                    "name": "CiscoConfig",
                    "time": 32,
                },
                {"descr": "Cisco config parse", "error": None, "name": "CiscoConfigParse", "time": 0},
                {"descr": "Config commit:  committed DB updated", "error": None, "name": "UpdateConfig", "time": 723},
                {"descr": "Config parse processing", "error": None, "name": "ConfigParseProc", "time": 0},
                {"descr": "Probe status: OK", "error": None, "name": "ProbeStatus", "time": 0},
            ],
            "errors": [],
            "issues": {"error": {}},
        },
        "config": {"datetime": "2025-05-01T00:01:42Z", "id": "86235d56582a6c31b800bcb99b3148c16af7a9e4", "size": 33282},
        "device_type": "Cisco",
        "hostname": "aoip-h1-dswt-02.bskyb.com",
        "ipaddr": "10.254.210.18",
        "known_issue": None,
        "location": "Osterley, Sky Studios, TER31, J01",
        "model": "Nexus9000 93180YC-EX",
        "model_family": "nxos.7.0.3.I5.2.bin",
        "os": "nx",
        "os_version": "7.0(3)I5(2)",
        "owner": "MD_ENTERPRISE",
        "rev": "7523-a36e84bd5d8dbe50ef6038e16ff927bf",
        "snmp_sysdescr": "Cisco NX-OS(tm) nxos.7.0.3.I5.2.bin, Software (nxos), Version 7.0(3)I5(2), RELEASE SOFTWARE "
        "Copyright (c) 2002-2016 by Cisco Systems, Inc. Compiled 2/16/2017 7:00:00",
        "status": "production",
        "tacacs_group": "TBC",
        "vendor": "cisco",
    },
    {
        "access": None,
        "admin_group": "enterprise",
        "collection": {
            "collector": "dis-col01.nme.bllon.sns.sky.com",
            "datetime": "2025-04-30T23:52:14Z",
            "detail": [
                {
                    "descr": "Resolve aoip-h1-sfa01-a.bskyb.com to 10.254.209.28",
                    "error": None,
                    "name": "Resolver",
                    "time": 0,
                },
                {"descr": "Enterprise auth credentials setup", "error": None, "name": "EnterpriseAuthSetup", "time": 0},
                {
                    "descr": "SNMP community guesser (version 2 community 1)",
                    "error": None,
                    "name": "SnmpCommunityGuesser",
                    "time": 0,
                },
                {"descr": "SNMP sys probe cisco", "error": None, "name": "SnmpSysDescrProbe", "time": 0},
                {"descr": "Cisco recogniser nxos nx 7.0(3)I5(2)", "error": None, "name": "CiscoRecognition", "time": 0},
                {
                    "descr": "SNMP interfaces probe (found 58 interfaces)",
                    "error": None,
                    "name": "SnmpInterfacesProbe",
                    "time": 1,
                },
                {
                    "descr": "Cisco model probe: Nexus9000 C93108TC-EX",
                    "error": None,
                    "name": "CiscoSoftwareModel",
                    "time": 32,
                },
                {
                    "descr": "Cisco config (by ssh) fetch (27737 bytes)",
                    "error": None,
                    "name": "CiscoConfig",
                    "time": 32,
                },
                {"descr": "Cisco config parse", "error": None, "name": "CiscoConfigParse", "time": 0},
                {"descr": 'Plugin "CiscoN9KModel"', "error": None, "name": "CiscoN9KModel", "time": 0},
                {
                    "descr": "Config commit",
                    "error": "exceeded timeout (2400 seconds)",
                    "name": "UpdateConfig",
                    "time": 2400,
                },
                {"descr": "Config parse processing", "error": None, "name": "ConfigParseProc", "time": 0},
                {"descr": "Probe status: OK", "error": None, "name": "ProbeStatus", "time": 0},
            ],
            "errors": ["exceeded timeout (2400 seconds)"],
            "issues": {"error": {}},
        },
        "config": {"datetime": "2025-04-29T19:53:29Z", "id": "fa3befebdee165ddaddf4a07ce57e9314efdc74f", "size": 27737},
        "device_type": "Cisco",
        "hostname": "aoip-h1-sfa01-a.bskyb.com",
        "ipaddr": "10.254.209.28",
        "known_issue": None,
        "location": "Osterley, Sky Studios, TER21, G11",
        "model": "N9K-C93108TC-EX",
        "os": "nx",
        "os_version": "7.0(3)I5(2)",
        "owner": "MD_ENTERPRISE",
        "rev": "7521-2c6e82fb806c167000f09aa69e35a180",
        "snmp_sysdescr": "Cisco NX-OS(tm) nxos.7.0.3.I5.2.bin, Software (nxos), Version 7.0(3)I5(2), RELEASE SOFTWARE "
        "Copyright (c) 2002-2016 by Cisco Systems, Inc. Compiled 2/16/2017 7:00:00",
        "status": "production",
        "tacacs_group": "TBC",
        "vendor": "cisco",
    },
    {
        "access": None,
        "admin_group": "enterprise",
        "collection": {
            "collector": "dis-col01.nme.enslo.sns.sky.com",
            "datetime": "2025-05-01T00:52:15Z",
            "detail": [
                {
                    "descr": "Resolve aoip-h1-sfa01-b.bskyb.com to 10.254.209.29",
                    "error": None,
                    "name": "Resolver",
                    "time": 0,
                },
                {"descr": "Enterprise auth credentials setup", "error": None, "name": "EnterpriseAuthSetup", "time": 0},
                {
                    "descr": "SNMP community guesser (version 2 community 1)",
                    "error": None,
                    "name": "SnmpCommunityGuesser",
                    "time": 0,
                },
                {"descr": "SNMP sys probe cisco", "error": None, "name": "SnmpSysDescrProbe", "time": 0},
                {"descr": "Cisco recogniser nxos nx 7.0(3)I5(2)", "error": None, "name": "CiscoRecognition", "time": 0},
                {
                    "descr": "SNMP interfaces probe (found 58 interfaces)",
                    "error": None,
                    "name": "SnmpInterfacesProbe",
                    "time": 2,
                },
                {
                    "descr": "Cisco model probe: Nexus9000 C93108TC-EX",
                    "error": None,
                    "name": "CiscoSoftwareModel",
                    "time": 32,
                },
                {
                    "descr": "Cisco config (by ssh) fetch (26873 bytes)",
                    "error": None,
                    "name": "CiscoConfig",
                    "time": 32,
                },
                {"descr": "Cisco config parse", "error": None, "name": "CiscoConfigParse", "time": 0},
                {"descr": 'Plugin "CiscoN9KModel"', "error": None, "name": "CiscoN9KModel", "time": 0},
                {"descr": "Config commit:  committed DB updated", "error": None, "name": "UpdateConfig", "time": 1042},
                {"descr": "Config parse processing", "error": None, "name": "ConfigParseProc", "time": 0},
                {"descr": "Probe status: OK", "error": None, "name": "ProbeStatus", "time": 0},
            ],
            "errors": [],
            "issues": {"error": {}},
        },
        "config": {"datetime": "2025-05-01T00:52:10Z", "id": "70881f2a4bd9e97148a240e783b307b4edffc041", "size": 26873},
        "device_type": "Cisco",
        "hostname": "aoip-h1-sfa01-b.bskyb.com",
        "ipaddr": "10.254.209.29",
        "known_issue": None,
        "location": "Osterley, Sky Studios, TER21, H01",
        "model": "N9K-C93108TC-EX",
        "model_family": "nxos.7.0.3.I5.2.bin",
        "os": "nx",
        "os_version": "7.0(3)I5(2)",
        "owner": "MD_ENTERPRISE",
        "rev": "6593-84ebcef302786be67b59cbf771422a12",
        "snmp_sysdescr": "Cisco NX-OS(tm) nxos.7.0.3.I5.2.bin, Software (nxos), Version 7.0(3)I5(2), RELEASE SOFTWARE "
        "Copyright (c) 2002-2016 by Cisco Systems, Inc. Compiled 2/16/2017 7:00:00",
        "status": "production",
        "tacacs_group": "TBC",
        "vendor": "cisco",
    },
]


@patch.object(DeviceConfigurationService, "get_all_device_details")
def test_find_all_values_in_dcs_response(mocked_get_all_device_details):
    dcs = DeviceConfigurationService(
        hostname=hostname,
        username=username,
        password=password,
        filters=get_user_model,
        page_number=0,
        offset=0,
        limit=0,
    )
    dcs.device_list = dcs_device_response
    mocked_get_all_device_details.return_value = dcs_device_response

    response = dcs._find_all_values_in_dcs_response("vendor")

    mocked_get_all_device_details.assert_called_once_with(expand=["attribs"])

    assert response == ["cisco"]
