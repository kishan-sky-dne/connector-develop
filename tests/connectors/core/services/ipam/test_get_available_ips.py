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
from unittest.mock import Mock, patch

# DNE Library
from connectors.core.services.ipam.connector import PrefixAvailableIps
from connectors.core.utils.exceptions import ConnectorException


def test_prefix_available_ips_instance():
    """
     test to create prefix available Instance
    :return:
    """
    request_body = {"prefix": "10.0.0.0/8", "quantity": 5, "domain": "Core"}
    prefix_available_ips_instance_obj = PrefixAvailableIps(request_body)
    assert isinstance(prefix_available_ips_instance_obj, PrefixAvailableIps)
    assert prefix_available_ips_instance_obj.prefix == "10.0.0.0/8"
    assert prefix_available_ips_instance_obj.limit == 5
    assert prefix_available_ips_instance_obj.domain == "Core"
    assert prefix_available_ips_instance_obj.err_msg == "Unknown"


mocked_response_prefix = {
    "count": 1,
    "next": "None",
    "previous": "None",
    "results": [
        {
            "id": 559,
            "family": {"value": 4, "label": "IPv4"},
            "prefix": "89.200.128.0/24",
            "site": None,
            "vrf": None,
            "vlan": "None",
            "status": {"value": 1, "label": "Active"},
            "role": {
                "id": 6,
                "url": "https://netbox.sns.sky.com/api/ipam/roles/6/",
                "name": "Core-Loopback",
                "slug": "core-loopback",
            },
            "is_pool": True,
            "description": "Loopback0",
            "tags": ["Loopback"],
            "custom_fields": {"map_json": "None", "text_field": "None"},
            "created": "2019-05-21",
            "last_updated": "2020-01-22T14:22:01.361627Z",
        }
    ],
}
mocked_response_available_ips = [
    {"family": 4, "address": "89.200.128.0/24", "vrf": None},
    {"family": 4, "address": "89.200.128.233/24", "vrf": None},
    {"family": 4, "address": "89.200.128.237/24", "vrf": None},
    {"family": 4, "address": "89.200.128.241/24", "vrf": None},
    {"family": 4, "address": "89.200.128.252/24", "vrf": None},
    {"family": 4, "address": "89.200.128.255/24", "vrf": None},
]


def test_get_ipam_prefixes():
    """
     test for ipam prefixes
    :return:
    """
    request_body = {"prefix": "10.0.0.0/8", "quantity": 5, "domain": "Core"}
    prefix_available_obj = PrefixAvailableIps(request_body)
    prefix_available_obj.rest.get = Mock(return_value=mocked_response_prefix)
    result = prefix_available_obj.get_ipam_prefixes()
    assert result == mocked_response_prefix


def test_get_ipam_prefix_available_ips():
    """
     unit test for get_ipam_prefix_available_ips
    :return:
    """
    request_body = {"prefix": "10.0.0.0/8", "quantity": 5, "domain": "Core"}
    prefix_available_obj = PrefixAvailableIps(request_body)
    prefix_available_obj.rest.get = Mock(return_value=mocked_response_available_ips)
    result = prefix_available_obj.get_ipam_prefix_available_ips(10)
    assert result == mocked_response_available_ips


@patch("connectors.core.services.ipam.connector.PrefixAvailableIps.get_ipam_prefixes")
@patch("connectors.core.services.ipam.connector.PrefixAvailableIps.get_ipam_prefix_available_ips")
def test_get_prefix_available_ips(get_ipam_prefix_available_ips_mock, get_ipam_prefixes_mock):
    request_body = {"prefix": "10.0.0.0/8", "quantity": 5, "domain": "Core", "network": "UK"}
    prefix_available_obj = PrefixAvailableIps(request_body)
    get_ipam_prefixes_mock.return_value = mocked_response_prefix
    get_ipam_prefix_available_ips_mock.return_value = mocked_response_available_ips
    result = prefix_available_obj.get_prefix_available_ips()
    assert result == {
        "status": "success",
        "metadata": {
            "vrf": "Global",
            "avlIpAddressList": [
                "89.200.128.0/24",
                "89.200.128.233/24",
                "89.200.128.237/24",
                "89.200.128.241/24",
                "89.200.128.252/24",
                "89.200.128.255/24",
            ],
        },
    }

    request_body = {"prefix": "10.0.0.0/8", "quantity": 5, "domain": "Core"}
    prefix_available_obj = PrefixAvailableIps(request_body)
    get_ipam_prefixes_mock.side_effect = ConnectorException(msg="Connectors Exception")
    get_ipam_prefix_available_ips_mock.side_effect = ConnectorException(msg="Connectors Exception")
    result = prefix_available_obj.get_prefix_available_ips()
    assert (
        result == "Getting the available ips for the given prefix operation failed due to Exception: "
        "ConnectorException Connectors Exception"
    )


# Negative use case for exhausted prefix and there is no avialable ips
@patch("connectors.core.services.ipam.connector.PrefixAvailableIps.get_ipam_prefixes")
@patch("connectors.core.services.ipam.connector.PrefixAvailableIps.get_ipam_prefix_available_ips")
def test_get_prefix_available_ips_negative(get_ipam_prefix_available_ips_mock, get_ipam_prefixes_mock):
    mocked_available_ip = [{"family": 4, "address": "89.200.128.0/24", "vrf": None}]
    request_body = {"prefix": "89.200.128.0/24", "quantity": 5, "domain": "Core"}
    prefix_available_obj = PrefixAvailableIps(request_body)
    get_ipam_prefixes_mock.return_value = mocked_response_prefix
    get_ipam_prefix_available_ips_mock.return_value = mocked_available_ip
    result = prefix_available_obj.get_prefix_available_ips()
    assert result == {
        "status": "failure",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-006-999-1003",
                "message": "Prefix has been exhausted and There is No Available IPs." " Please validate the Prefix",
            }
        ],
    }
