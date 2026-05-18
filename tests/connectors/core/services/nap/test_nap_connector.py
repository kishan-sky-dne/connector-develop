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
from connectors.core.services.nap.connector import NapService
from connectors.core.utils.exceptions import RestUtilityException

input_kwargs = {
    "headers": {
        "Content-Type": "application/json",
        "Authorization": "Token xyz",
    },
    "url": "dummy",
    "request_ids": [1, 2],
    "region": "Ireland",
    "mapped_region": "roi",
}


@patch("connectors.core.utils.rest_api_utility.RestUtility")
def instantiate_class(rest_mock):
    inst = NapService()
    assert inst.rest == rest_mock


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
def test_update_nap_details(post_mock):
    inst = NapService()
    post_mock.return_value = (202, "success")
    assert inst.update_nap_details(**input_kwargs) == (
        True,
        [{1: {"status": "SUCCESS", "errorMessage": ""}}, {2: {"status": "SUCCESS", "errorMessage": ""}}],
    )


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
def test_update_nap_details_case2(post_mock):
    inst = NapService()
    post_mock.return_value = (301, "Invalid Credential")
    assert inst.update_nap_details(**input_kwargs) == (
        True,
        [
            {
                1: {
                    "errorMessage": "Failed to reSubmit failed voip circuit with requestid 1, Invalid Credential",
                    "status": "FAIL",
                }
            },
            {
                2: {
                    "errorMessage": "Failed to reSubmit failed voip circuit with requestid 2, Invalid Credential",
                    "status": "FAIL",
                }
            },
        ],
    )


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
def test_update_nap_details_exception(post_mock):
    inst = NapService()
    post_mock.side_effect = RestUtilityException("Invalid url")
    assert inst.update_nap_details(**input_kwargs) == (
        False,
        [
            {
                1: {
                    "errorMessage": (
                        "Exception raised while accessing nexus url for region Ireland with error: Invalid url"
                    ),
                    "status": "FAIL",
                }
            }
        ],
    )


in_flight_orders = {
    "status": "Success",
    "orders": [
        {
            "request": {
                "directoryNumber": {"existingNumber": "+3539650100"},
                "orderReference": "171684529",
                "type": "NETWORK_PROVISION",
                "originalTimestamp": "2024-09-03T09:53:33.261996Z",
            },
            "failure": {
                "failureTimestamp": "2024-09-03T09:53:39.491026Z",
                "rawFailureContext": (
                    "Nap service order '5f6aa5b2-e10e-4aa9-8a83-d18d7eb1cec9' failed: Code [112001], Reason "
                    "[Unrecognised error]"
                ),
            },
        }
    ],
}


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_get_nap_details_success(get_mock):
    inst = NapService()
    get_mock.return_value = in_flight_orders
    assert inst.get_nap_details(**input_kwargs) == (True, in_flight_orders["orders"], "")


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_get_nap_details_fail(get_mock):
    inst = NapService()
    get_mock.return_value = {}
    assert inst.get_nap_details(**input_kwargs) == (False, [], "Error response received from nexus: {}")


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_get_nap_details_exception(get_mock):
    inst = NapService()
    get_mock.side_effect = RestUtilityException("Invalid url")
    assert inst.get_nap_details(**input_kwargs) == (
        False,
        [],
        "Exception raised while accessing nexus url for region Ireland with error: Invalid url",
    )
