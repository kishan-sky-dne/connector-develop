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
from connectors.core.services.plannet.connector import PlannetService
from connectors.core.utils.helpers import generic_secret

secret = generic_secret()

access_token = secret
kwargs = {"url": "api/circuits/circuit-types"}
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Token {access_token}",
}
kwargs["headers"] = headers
planet_ckt_response = {
    "count": 22,
    "next": "None",
    "previous": "None",
    "results": [
        {"id": 1, "created": "2021-05-20", "last_updated": "2021-05-20T17:56:13.429610Z", "name": "Backhaul"},
        {"id": 2, "created": "2021-05-20", "last_updated": "2021-05-20T17:56:13.519249Z", "name": "BES"},
        {"id": 7, "created": "2021-05-20", "last_updated": "2021-05-20T18:00:06.010228Z", "name": "CableLink"},
        {"id": 12, "created": "2021-05-20", "last_updated": "2021-05-20T20:00:40.012812Z", "name": "DFx"},
        {"id": 18, "created": "2021-05-21", "last_updated": "2021-05-21T15:23:20.777227Z", "name": "DSLAM"},
        {"id": 5, "created": "2021-05-20", "last_updated": "2021-05-20T17:56:15.867957Z", "name": "EAD"},
        {"id": 3, "created": "2021-05-20", "last_updated": "2021-05-20T17:56:13.938071Z", "name": "EBD"},
        {"id": 4, "created": "2021-05-20", "last_updated": "2021-05-20T17:56:15.391363Z", "name": "Fibre"},
        {"id": 14, "created": "2021-05-20", "last_updated": "2021-05-20T23:39:40.895307Z", "name": "GEA cablelink"},
        {"id": 13, "created": "2021-05-20", "last_updated": "2021-05-20T20:07:30.884724Z", "name": "Intra"},
        {"id": 17, "created": "2021-05-21", "last_updated": "2021-05-21T15:22:15.135582Z", "name": "ISAM-B"},
        {"id": 16, "created": "2021-05-21", "last_updated": "2021-05-21T15:22:13.004060Z", "name": "ISAM-V"},
        {"id": 15, "created": "2021-05-21", "last_updated": "2021-05-21T15:22:12.925169Z", "name": "MSAN"},
        {"id": 6, "created": "2021-05-20", "last_updated": "2021-05-20T17:57:13.441750Z", "name": "OSA"},
        {"id": 9, "created": "2021-05-20", "last_updated": "2021-05-20T19:46:44.148515Z", "name": "OSA_10TCE"},
        {"id": 11, "created": "2021-05-20", "last_updated": "2021-05-20T19:50:54.758889Z", "name": "OSA_CC"},
        {"id": 10, "created": "2021-05-20", "last_updated": "2021-05-20T19:48:28.531606Z", "name": "OSA_XG210_RF"},
        {"id": 8, "created": "2021-05-20", "last_updated": "2021-05-20T19:45:19.717793Z", "name": "OSA_XG210_SFW"},
        {"id": 19, "created": "2021-05-21", "last_updated": "2021-05-21T15:23:20.848776Z", "name": "Stinger"},
        {"id": 21, "created": "2021-05-22", "last_updated": "2021-05-22T10:34:36.971803Z", "name": "T1 Optical Bearer"},
        {
            "id": 22,
            "created": "2021-05-22",
            "last_updated": "2021-05-22T10:44:06.637478Z",
            "name": "T1 Optical Wavelength",
        },
        {"id": 20, "created": "2021-05-22", "last_updated": "2021-05-22T07:36:00.781275Z", "name": "Wholesale Access"},
    ],
}

planet_int_response = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [
        {
            "atg": {
                "coordinator": None,
                "date": "2020-06-22",
                "dependencies": [],
                "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                "id": 439,
                "name": "initialize olt0.ag01",
                "name_str": "TG439 initialize olt0.ag01 (22/06/2020)",
                "nis_ref": "TG7296",
            },
            "circuit": {
                "a_site_external_cable_id": None,
                "a_site_external_cable_length": None,
                "b_site_external_cable_id": None,
                "b_site_external_cable_length": None,
                "capacity": None,
                "cct_no": None,
                "cid": "EB/LL/AG01-ME01/10G/AB/002/OF:900000000233",
                "created": "2021-03-18",
                "description": None,
                "id": 352,
                "is_protected": False,
                "last_updated": "2021-03-18T22:05:35.653035Z",
                "length": None,
                "parent_ref": None,
                "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/1",
                "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/3",
                "subtype": None,
                "tenant": None,
                "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/3",
            },
            "created": "2021-03-18",
            "description": None,
            "dtg": {
                "coordinator": None,
                "date": "2099-12-31",
                "dependencies": [],
                "domains": [],
                "id": 9999,
                "name": "Default End Transition",
                "name_str": "TG9999 Default End Transition (31/12/2099)",
                "nis_ref": "TG9999",
            },
            "id": 1119,
            "interface_1": {
                "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/439",
                "card": "https://plannet.cf.paas.bskyb.com/api/dcim/cards/1646",
                "created": "2021-03-18",
                "description": None,
                "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                "fpe": None,
                "id": 19148,
                "lag": None,
                "last_updated": "2021-03-18T22:04:54.645902Z",
                "mac_address": None,
                "name": "olt0.ag01.it.bb.sky.com 10GE0/9/0 | TG439 (22/06/2020) TG9999 (31/12/2099)",
                "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/290",
                "rates": [3],
                "related_interface": None,
                "tagged_vlans": [],
                "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                "untagged_vlan": None,
            },
            "interface_2": {
                "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/95",
                "card": None,
                "created": "2021-03-18",
                "description": None,
                "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                "fpe": None,
                "id": 4975,
                "lag": None,
                "last_updated": "2021-03-18T16:03:47.148812Z",
                "mac_address": None,
                "name": "ma0.me01.it.bb.sky.com TenGigE0/0/0/12 | TG95 (30/10/2019) TG9999 (31/12/2099)",
                "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/113",
                "rates": [3],
                "related_interface": None,
                "tagged_vlans": [],
                "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                "untagged_vlan": None,
            },
            "is_active": None,
            "last_updated": "2021-04-12T16:17:16.450963Z",
            "link_prev": None,
            "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
            "name": "EB_olt0.ag01:10GE0/9/0_ma0.me01:TenGigE0/0/0/12",
            "ne_1": {
                "asn": "https://plannet.cf.paas.bskyb.com/api/dcim/asns/1",
                "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/439",
                "created": "2021-03-18",
                "description": None,
                "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                "face": 0,
                "height": 1,
                "hostname": "olt0.ag01",
                "id": 290,
                "last_updated": "2021-03-18T22:04:43.790723Z",
                "local_context_data": None,
                "logical_site": None,
                "name": "olt0.ag01.it.bb.sky.com",
                "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/9",
                "ne_subrole": None,
                "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/7",
                "parent": None,
                "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/4",
                "position": None,
                "rack": None,
                "room": None,
                "serial": None,
                "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/198",
                "state": "ACTIVE",
                "tenant": None,
            },
            "ne_2": {
                "asn": "https://plannet.cf.paas.bskyb.com/api/dcim/asns/1",
                "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/95",
                "created": "2021-03-18",
                "description": None,
                "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                "face": 0,
                "height": 2,
                "hostname": "ma0.me01",
                "id": 113,
                "last_updated": "2021-03-18T16:03:45.598894Z",
                "local_context_data": None,
                "logical_site": None,
                "name": "ma0.me01.it.bb.sky.com",
                "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/3",
                "ne_subrole": None,
                "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/3",
                "parent": None,
                "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/2",
                "position": None,
                "rack": None,
                "room": None,
                "serial": None,
                "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/31",
                "state": "ACTIVE",
                "tenant": None,
            },
            "parents": [
                {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/439",
                    "circuit": None,
                    "created": "2021-03-18",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "id": 1118,
                    "interface_1": "https://plannet.cf.paas.bskyb.com/api/dcim/interfaces/19200",
                    "interface_2": "https://plannet.cf.paas.bskyb.com/api/dcim/interfaces/19201",
                    "is_active": None,
                    "last_updated": "2021-04-12T16:17:16.462087Z",
                    "link_prev": None,
                    "link_type": 10,
                    "name": "LAG_olt0.ag01:LAG1_ma0.me01:BE1161",
                    "name_str": "LAG_olt0.ag01:LAG1_ma0.me01:Bundle-Ether1161",
                    "ne_1": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/290",
                    "ne_2": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/113",
                    "parents": [],
                    "rate": None,
                    "subrate": None,
                }
            ],
            "rate": {"description": "10G rate", "id": 3, "name": "10G", "unit_id": 3, "value": 10.0},
            "subrate": None,
        }
    ],
}


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth.token_generator")
def test_get_plannet_details(mock_token_generator, get_mocked):
    """
    Test to check the functionality of get_inca_details()
    """
    plannet_inca = PlannetService()
    get_mocked.return_value = planet_ckt_response
    output = plannet_inca.get_plannet_details(**kwargs)
    assert output == planet_ckt_response


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth.token_generator")
def test_get_plannet_details1(mock_token_generator, get_mocked):
    """
    Test to check the functionality of get_plannet_details()
    """
    plannet_conn = PlannetService()
    get_mocked.return_value = planet_int_response
    output = plannet_conn.get_plannet_details(**kwargs)
    assert output == planet_int_response


@patch("connectors.core.utils.rest_api_utility.RestUtility.patch")
def test_patch_plannet_details(patch_mock):
    """
    Test for patch_plannet_details
    """
    plannet = PlannetService()
    patch_mock.return_value = {"dummy_response": True}
    request = {
        "url": "dcim/cards",
        "headers": {"content-type", "application/json"},
        "payload": "{'card_type': 'abc_card'}",
    }
    output = plannet.patch_plannet_details(**request)
    assert output == {"dummy_response": True}
