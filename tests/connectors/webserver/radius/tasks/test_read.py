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
from copy import deepcopy
from unittest.mock import Mock, patch

# DNE Library
from connectors.core.utils.exceptions import GenericConnectorsException, RestUtilityException
from connectors.webserver.radius.tasks import read

kwargs = {"ipv6Prefix": "2a0e:418::/32"}

bmr_details1 = {
    "status_code": 200,
    "message": {
        "ruleipv6prefix": "2a0e:418::/32",
        "ruleipv4prefix": "101.56.0.0/20",
        "psid_length": 3,
        "psid_offset": 6,
        "ea_length": 16,
        "seqid": 14187,
        "timestamp": 1694502737077211424,
        "objtype": "bmr",
    },
}

response1 = {
    "bmrRecord": {
        "rule_ipv6_prefix": "2a0e:418::/32",
        "rule_ipv4_prefix": "101.56.0.0/20",
        "psid_length": 3,
        "psid_offset": 6,
        "ea_length": 16,
        "seqid": 14187,
        "timestamp": 1694502737077211424,
        "objtype": "bmr",
    }
}


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.services.radius.connector.RadiusService.generate_token", Mock(return_value="abcd"))
@patch("connectors.core.services.radius.connector.RadiusService.get_bmr_details", Mock(return_value=bmr_details1))
def test_get_bmr_by_ip_success1(rest_utility_mock):
    output = read.get_bmr_by_ip(**kwargs)
    assert output == (response1, 200)


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.services.radius.connector.RadiusService.generate_token", Mock(return_value="abcd"))
@patch("connectors.core.services.radius.connector.RadiusService.get_bmr_details")
def test_get_bmr_by_ip_success2(bmr_mock, rest_utility_mock):
    output = read.get_bmr_by_ip(**kwargs)
    assert output == (
        {
            "status": "FAILURE",
            "errorCategory": "FAILED",
            "errors": [{"code": "ERR-015-999-0200", "message": "Failed to fetch BMR records: "}],
        },
        200,
    )


response_failure1 = {
    "status": "FAILURE",
    "errorCategory": "FAILED",
    "errors": [{"code": "ERR-015-999-0001", "message": "Failed to fetch BMR records: URL not found"}],
}


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.services.radius.connector.RadiusService.generate_token")
@patch("connectors.core.services.radius.connector.RadiusService.get_bmr_details", Mock(return_value=None))
def test_get_bmr_by_ip_token_failure1(generate_token_mock, rest_utility_mock):
    generate_token_mock.side_effect = RestUtilityException("URL not found")
    output = read.get_bmr_by_ip(**kwargs)
    assert output == (response_failure1, 200)


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.services.radius.connector.RadiusService.generate_token")
@patch("connectors.core.services.radius.connector.RadiusService.get_bmr_details", Mock(return_value=None))
def test_get_bmr_by_ip_token_failure2(generate_token_mock, rest_utility_mock):
    generate_token_mock.side_effect = GenericConnectorsException("URL not found")
    output = read.get_bmr_by_ip(**kwargs)
    assert output == (response_failure1, 200)


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.services.radius.connector.RadiusService.generate_token", Mock(return_value="abcd"))
@patch("connectors.core.services.radius.connector.RadiusService.get_bmr_details")
def test_get_bmr_by_ip_url_failure1(get_bmr_mock, rest_utility_mock):
    get_bmr_mock.side_effect = RestUtilityException("URL not found")
    output = read.get_bmr_by_ip(**kwargs)
    assert output == (response_failure1, 200)


# # Sync status start

sync_kwargs = {"seqid": 14187}

sync_details1 = {
    "status_code": 200,
    "message": {
        "BMRStatus": {
            "synchronised": True,
            "sync_seqid": 14187,
            "bmr_status_detail": [
                {
                    "owner": "aaa-api",
                    "seqid": 14187,
                    "bmrset": [12577, 14152, 14155, 14156, 14168, 14175, 14176, 14187],
                    "timestamp": 1694502737077211424,
                    "objtype": "bmrstatus",
                },
                {
                    "owner": "https://be0.lab-radproxy1.ts1.bllon.isp.sky.com/api/v1/bmr/127.0.0.1",
                    "seqid": 14187,
                    "bmrset": [12577, 14152, 14155, 14156, 14168, 14175, 14176, 14187],
                    "timestamp": 1694502737077211424,
                    "objtype": "bmrstatus",
                },
                {
                    "owner": "https://be0.lab-radproxy2.ts1.bllon.isp.sky.com/api/v1/bmr/127.0.0.1",
                    "seqid": 14187,
                    "bmrset": [12577, 14152, 14155, 14156, 14168, 14175, 14176, 14187],
                    "timestamp": 1694502737077211424,
                    "objtype": "bmrstatus",
                },
            ],
        }
    },
}

sync_response1 = {
    "current_sync_seqid": 14187,
    "requested_sync_seqid": 14187,
    "synchronised": True,
    "timestamp": 1694502737077211424,
}


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.services.radius.connector.RadiusService.generate_token", Mock(return_value="abcd"))
@patch("connectors.core.services.radius.connector.RadiusService.sync_bmr_details", Mock(return_value=sync_details1))
def test_sync_bmr_by_seq_id_success1(rest_utility_mock):
    output = read.sync_bmr_by_seq_id(**sync_kwargs)
    assert output == (sync_response1, 200)


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.services.radius.connector.RadiusService.generate_token", Mock(return_value="abcd"))
@patch("connectors.core.services.radius.connector.RadiusService.sync_bmr_details", Mock(return_value=sync_details1))
def test_sync_bmr_by_seq_id_success3(rest_utility_mock):
    sync_response2 = deepcopy(sync_response1)
    sync_response2["synchronised"] = False
    sync_response2["requested_sync_seqid"] = 14188
    sync_kwargs2 = deepcopy(sync_kwargs)
    sync_kwargs2["seqid"] = 14188
    output = read.sync_bmr_by_seq_id(**sync_kwargs2)
    assert output == (sync_response2, 200)


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.services.radius.connector.RadiusService.generate_token", Mock(return_value="abcd"))
@patch("connectors.core.services.radius.connector.RadiusService.sync_bmr_details", Mock(return_value=None))
def test_sync_bmr_by_seq_id_success2(rest_utility_mock):
    output = read.sync_bmr_by_seq_id(**sync_kwargs)
    # sync_response2 = deepcopy(sync_response1)
    # sync_response2.update(
    #     {"current_sync_seqid": None, "requested_sync_seqid": 14187, "synchronised": False, "timestamp": None}
    # )
    sync_response2 = {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [{"code": "ERR-015-999-0001", "message": "Failed to fetch BMR status: "}],
    }
    assert output == (sync_response2, 200)


sync_response_failure1 = {
    "status": "FAILURE",
    "errorCategory": "FAILED",
    "errors": [{"code": "ERR-015-999-0001", "message": "Failed to fetch BMR status: URL not found"}],
}

sync_response_failure2 = (
    {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [{"code": "ERR-015-999-0001", "message": "Failed to fetch BMR status: "}],
    },
    200,
)


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.services.radius.connector.RadiusService.generate_token")
@patch("connectors.core.services.radius.connector.RadiusService.sync_bmr_details", Mock(return_value=None))
def test_sync_bmr_by_seq_id_token_failure1(generate_token_mock, rest_utility_mock):
    generate_token_mock.side_effect = RestUtilityException("URL not found")
    output = read.sync_bmr_by_seq_id(**sync_kwargs)
    assert output == (sync_response_failure1, 200)


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.services.radius.connector.RadiusService.generate_token")
@patch("connectors.core.services.radius.connector.RadiusService.sync_bmr_details", Mock(return_value=None))
def test_sync_bmr_by_seq_id_token_failure2(generate_token_mock, rest_utility_mock):
    generate_token_mock.side_effect = GenericConnectorsException("URL not found")
    output = read.sync_bmr_by_seq_id(**sync_kwargs)
    assert output == (sync_response_failure1, 200)


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.services.radius.connector.RadiusService.generate_token", Mock(return_value="abcd"))
@patch("connectors.core.services.radius.connector.RadiusService.sync_bmr_details")
def test_sync_bmr_by_seq_id_url_failure1(get_bmr_mock, rest_utility_mock):
    get_bmr_mock.side_effect = RestUtilityException("URL not found")
    output = read.sync_bmr_by_seq_id(**sync_kwargs)
    assert output == (
        {
            "status": "FAILURE",
            "errorCategory": "FAILED",
            "errors": [{"code": "ERR-015-999-0001", "message": "Failed to fetch BMR status: URL not found"}],
        },
        200,
    )
