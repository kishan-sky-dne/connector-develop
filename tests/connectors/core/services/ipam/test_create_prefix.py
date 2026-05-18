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
import sys
from unittest.mock import patch

# Sky Library
from isp_config import ConfigManagerException

# DNE Library
from connectors.core.config import connectors_config
from connectors.core.services.ipam.connector import CreatePrefix

try:
    config = connectors_config.ConnectorsConfigManager()
    config.load_config()
except ConfigManagerException:
    sys.exit(1)

netbox_url = "dummy_url"
prefix_kwargs = {
    "prefix": "2.120.12.2/31",
    "site": "BLLON",
    "vrf": "Global",
    "tenant": "UK-Core",
    "role": "Core-Interconnect",
    "is_pool": True,
    "description": "ta0.bllon Bundle-Ether403 <-> sr0.bllon base_ma0.bllon_1",
    "tags": ["interconnect"],
    "custom_fields": {},
}


def test_create_prefix_instance():
    create_prefix_obj = CreatePrefix(prefix_kwargs)
    assert isinstance(create_prefix_obj, CreatePrefix)
    assert create_prefix_obj.prefix == prefix_kwargs["prefix"]
    assert create_prefix_obj.site == prefix_kwargs["site"]
    assert create_prefix_obj.tenant == prefix_kwargs["tenant"]
    assert create_prefix_obj.vrf == prefix_kwargs["vrf"]
    assert create_prefix_obj.is_pool == prefix_kwargs["is_pool"]
    assert create_prefix_obj.role == prefix_kwargs["role"]
    assert create_prefix_obj.description == prefix_kwargs["description"]
    assert create_prefix_obj.tags == prefix_kwargs["tags"]
    assert create_prefix_obj.custom_fields == prefix_kwargs["custom_fields"]


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_create_prefix(get_mock, post_mock):
    create_prefix_obj = CreatePrefix(prefix_kwargs)
    get_mock.side_effect = iter(
        [
            (
                {
                    "count": 1,
                    "next": None,
                    "previous": None,
                    "results": [{"id": 3, "name": "Core-Interconnect", "slug": "Core-Interconnect", "weight": 1000}],
                }
            ),
            (
                {
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
                                "url": "https://netbox-lab.cf.dev-paas.bskyb.com/api" "/tenancy/tenant-groups/1/",
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
            ),
            (
                {
                    "count": 1,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "id": 2,
                            "name": "Global",
                            "rd": None,
                            "tenant": None,
                            "enforce_unique": True,
                            "description": "",
                            "tags": [],
                            "display_name": "Global",
                            "custom_fields": {},
                            "created": "2021-01-06",
                            "last_updated": "2021-01-06T18:11:23.991024Z",
                        }
                    ],
                }
            ),
            (
                {
                    "count": 1,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "id": 11,
                            "name": "BLLON",
                            "slug": "bllon",
                            "status": {"value": 1, "label": "Active"},
                            "region": {
                                "id": 11,
                                "url": "https://netbox-lab.cf.dev-paas.bskyb.com/api/dcim/regions/11/",
                                "name": "London",
                                "slug": "london",
                            },
                            "tenant": None,
                            "facility": "Sky",
                            "asn": None,
                            "time_zone": None,
                            "description": "Brick Lane",
                            "physical_address": "",
                            "shipping_address": "",
                            "latitude": None,
                            "longitude": None,
                            "contact_name": "",
                            "contact_phone": "",
                            "contact_email": "",
                            "comments": "",
                            "tags": [],
                            "custom_fields": {"Community": None},
                            "created": "2019-09-06",
                            "last_updated": "2019-09-06T10:21:02.973483Z",
                            "count_prefixes": 0,
                            "count_vlans": 0,
                            "count_racks": 0,
                            "count_devices": 0,
                            "count_circuits": 0,
                        }
                    ],
                }
            ),
        ]
    )
    post_mock.return_value = {
        "id": 288,
        "family": {"value": 4, "label": "IPv4"},
        "prefix": "2.120.12.2/31",
        "site": {
            "id": 11,
            "url": "https://netbox-lab.cf.dev-paas.bskyb.com/api/dcim/sites/11/",
            "name": "BLLON",
            "slug": "bllon",
        },
        "vrf": {
            "id": 2,
            "url": "https://netbox-lab.cf.dev-paas.bskyb.com/api/ipam/vrfs/2/",
            "name": "Global",
            "rd": None,
        },
        "tenant": {
            "id": 2,
            "url": "https://netbox-lab.cf.dev-paas.bskyb.com/api/tenancy/tenants/2/",
            "name": "UK-Core",
            "slug": "uk-core",
        },
        "vlan": None,
        "status": {"value": 1, "label": "Active"},
        "role": {
            "id": 3,
            "url": "https://netbox-lab.cf.dev-paas.bskyb.com/api/ipam/roles/3/",
            "name": "Core-Interconnect",
            "slug": "Core-Interconnect",
        },
        "is_pool": True,
        "description": "ta0.bllon Bundle-Ether403 <-> sr0.bllon base_ma0.bllon_1",
        "tags": ["interconnect"],
        "created": "2021-01-20",
        "last_updated": "2021-01-20T08:01:32.168620Z",
    }
    expected_prefix_status = {"id": 288, "status": "success"}
    actual_prefix_status = create_prefix_obj.create_prefix()
    assert actual_prefix_status == expected_prefix_status


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_create_prefix_negative(get_mock, post_mock):
    create_prefix_obj = CreatePrefix(prefix_kwargs)
    get_mock.side_effect = iter(
        [
            (
                {
                    "count": 1,
                    "next": None,
                    "previous": None,
                    "results": [{"id": 3, "name": "Core-Interconnect", "slug": "Core-Interconnect", "weight": 1000}],
                }
            ),
            (
                {
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
                                "url": "https://netbox-lab.cf.dev-paas.bskyb.com/api/tenancy/tenant" "-groups/1/",
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
            ),
            (
                {
                    "count": 1,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "id": 2,
                            "name": "Global",
                            "rd": None,
                            "tenant": None,
                            "enforce_unique": True,
                            "description": "",
                            "tags": [],
                            "display_name": "Global",
                            "custom_fields": {},
                            "created": "2021-01-06",
                            "last_updated": "2021-01-06T18:11:23.991024Z",
                        }
                    ],
                }
            ),
            (
                {
                    "count": 1,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "id": 11,
                            "name": "BLLON",
                            "slug": "bllon",
                            "status": {"value": 1, "label": "Active"},
                            "region": {
                                "id": 11,
                                "url": "https://netbox-lab.cf.dev-paas.bskyb.com/api/dcim/regions/11/",
                                "name": "London",
                                "slug": "london",
                            },
                            "tenant": None,
                            "facility": "Sky",
                            "asn": None,
                            "time_zone": None,
                            "description": "Brick Lane",
                            "physical_address": "",
                            "shipping_address": "",
                            "latitude": None,
                            "longitude": None,
                            "contact_name": "",
                            "contact_phone": "",
                            "contact_email": "",
                            "comments": "",
                            "tags": [],
                            "custom_fields": {"Community": None},
                            "created": "2019-09-06",
                            "last_updated": "2019-09-06T10:21:02.973483Z",
                            "count_prefixes": 0,
                            "count_vlans": 0,
                            "count_racks": 0,
                            "count_devices": 0,
                            "count_circuits": 0,
                        }
                    ],
                }
            ),
        ]
    )
    post_mock.return_value = {}
    expected_prefix_status = {
        "errorCategory": "FAILED",
        "errors": [
            {"code": "ERR-006-999-0008", "message": "Prefix creation Interface failed. Provided prefix already exists"}
        ],
        "status": "failure",
    }
    actual_prefix_status = create_prefix_obj.create_prefix()
    assert actual_prefix_status == expected_prefix_status
