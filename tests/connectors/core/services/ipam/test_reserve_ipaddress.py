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
from connectors.core.services.ipam import connector
from connectors.core.services.ipam.connector import ReserveIpAddress

netbox_tenant_url = "dummy_url"
ipaddress_kwargs = {
    "address": "11.0.0.4/28",
    "prefix": "11.0.0.0/28",
    "network": "UK",
    "domain": "Core",
    "vrf": "test_vrf",
    "routeDistinguisher": "11:11",
    "status": 1,
    "description": "Tset 2",
    "tags": ["Loopback"],
    "custom_fields": {},
    "getFreeIPs": True,
}


def test_reserve_ipaddress_instance():
    connector.status = 1
    reserve_ipaddress_obj = ReserveIpAddress(ipaddress_kwargs)
    assert isinstance(reserve_ipaddress_obj, ReserveIpAddress)
    assert reserve_ipaddress_obj.address == ipaddress_kwargs["address"]
    assert reserve_ipaddress_obj.prefix == ipaddress_kwargs["prefix"]
    assert reserve_ipaddress_obj.network == ipaddress_kwargs["network"]
    assert reserve_ipaddress_obj.domain == ipaddress_kwargs["domain"]
    assert reserve_ipaddress_obj.vrf == ipaddress_kwargs["vrf"]
    assert reserve_ipaddress_obj.route_distinguisher == ipaddress_kwargs["routeDistinguisher"]
    assert reserve_ipaddress_obj.status == ipaddress_kwargs["status"]
    assert reserve_ipaddress_obj.description == ipaddress_kwargs["description"]
    assert reserve_ipaddress_obj.tags == ipaddress_kwargs["tags"]
    assert reserve_ipaddress_obj.custom_fields == ipaddress_kwargs["custom_fields"]


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_validate_tenant(get_mock):
    reserve_ipaddress_obj = ReserveIpAddress(ipaddress_kwargs)
    get_mock.return_value = {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [
            {
                "id": 2,
                "name": "UK-Core",
                "slug": "uk-core",
                "group": {
                    "id": 1,
                    "url": "https://netbox-lab.cf.dev-paas.bskyb.com/api/tenancy/tenant-groups/1/",
                    "name": "UK",
                    "slug": "uk",
                },
                "description": "",
                "comments": "",
                "tags": [],
                "custom_fields": {},
                "created": "2019-07-09",
                "last_updated": "2020-10-08T15:27:29.039612Z",
            }
        ],
    }
    tenant_id = reserve_ipaddress_obj.validate_tenant()
    assert tenant_id == 2


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_validate_vrf(get_mock):
    reserve_ipaddress_obj = ReserveIpAddress(ipaddress_kwargs)
    get_mock.return_value = {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [
            {
                "id": 1,
                "name": "test_vrf",
                "rd": "11:11",
                "tenant": None,
                "enforce_unique": True,
                "description": "",
                "tags": [],
                "display_name": "test_vrf (11:11)",
                "custom_fields": {},
                "created": "2020-10-22",
                "last_updated": "2020-10-22T02:16:54.332134Z",
            }
        ],
    }
    vrf_id = reserve_ipaddress_obj.validate_vrf()
    assert vrf_id == 1


@patch("connectors.core.services.ipam.connector.ReserveIpAddress.validate_vrf")
@patch("connectors.core.services.ipam.connector.ReserveIpAddress.validate_tenant")
@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
def test_reserve_ip(post_mock, tenant_mock, vrf_mock):
    reserve_ipaddress_obj = ReserveIpAddress(ipaddress_kwargs)
    post_mock.return_value = {
        "id": 59,
        "family": {"value": 4, "label": "IPv4"},
        "address": "11.0.0.4/28",
        "vrf": {
            "id": 1,
            "url": "https://netbox-lab.cf.dev-paas.bskyb.com/api/ipam/vrfs/1/",
            "name": "test_vrf",
            "rd": "11:11",
        },
        "tenant": {
            "id": 2,
            "url": "https://netbox-lab.cf.dev-paas.bskyb.com/api/tenancy/tenants/2/",
            "name": "UK-Core",
            "slug": "uk-core",
        },
        "status": {"value": 1, "label": "Active"},
        "interface": "None",
        "description": "Tset 2",
        "nat_inside": "None",
        "nat_outside": "None",
        "tags": ["Loopback"],
        "created": "2020-11-03",
        "last_updated": "2020-11-03T09:16:51.918897Z",
    }
    tenant_mock.return_value = 2
    vrf_mock.return_value = 1
    actual = reserve_ipaddress_obj.reserve_ip()
    expected = {
        "id": 59,
        "status": "success",
    }
    assert actual == expected


# Negative cases
@patch("connectors.core.services.ipam.connector.ReserveIpAddress.validate_vrf")
@patch("connectors.core.services.ipam.connector.ReserveIpAddress.validate_tenant")
@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
def test_reserve_ip_not_available(post_mock, tenant_mock, vrf_mock):
    reserve_ipaddress_obj = ReserveIpAddress(ipaddress_kwargs)
    post_mock.return_value = {}
    tenant_mock.return_value = 2
    vrf_mock.return_value = 1
    actual = reserve_ipaddress_obj.reserve_ip()
    expected = {
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-006-999-0005",
                "message": "IP Reservation for Interface failed. Provided IP is already reserved",
            }
        ],
        "metadata": {
            "vrf": "test_vrf",
        },
        "status": "failure",
    }
    assert actual == expected


@patch("connectors.core.services.ipam.connector.ReserveIpAddress.validate_vrf")
@patch("connectors.core.services.ipam.connector.ReserveIpAddress.validate_tenant")
@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
def test_reserve_ip_not_available_no_prefix(
    post_mock,
    tenant_mock,
    vrf_mock,
):
    ipaddress_kwargs_no_prefix = {"address": "89.200.101.88/31", "network": "UK", "domain": "Core"}
    reserve_ipaddress_obj = ReserveIpAddress(ipaddress_kwargs_no_prefix)
    post_mock.return_value = {}
    tenant_mock.return_value = 2
    vrf_mock.return_value = 1
    actual = reserve_ipaddress_obj.reserve_ip()
    expected = {
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-006-999-0005",
                "message": "IP Reservation for Interface failed. Provided IP is already reserved",
            }
        ],
        "metadata": {
            "vrf": "Global",
        },
        "status": "failure",
    }
    assert actual == expected


@patch("connectors.core.services.ipam.connector.ReserveIpAddress.validate_vrf")
@patch("connectors.core.services.ipam.connector.ReserveIpAddress.validate_tenant")
@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
def test_reserve_ip_not_available_free_ips_false(post_mock, tenant_mock, vrf_mock):
    ipaddress_kwargs["getFreeIPs"] = False
    reserve_ipaddress_obj = ReserveIpAddress(ipaddress_kwargs)
    post_mock.return_value = {}
    tenant_mock.return_value = 2
    vrf_mock.return_value = 1
    actual = reserve_ipaddress_obj.reserve_ip()
    expected = {
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-006-999-0005",
                "message": "IP Reservation for Interface failed. Provided IP is " "already reserved",
            }
        ],
        "metadata": {
            "vrf": "test_vrf",
        },
        "status": "failure",
    }
    assert actual == expected
