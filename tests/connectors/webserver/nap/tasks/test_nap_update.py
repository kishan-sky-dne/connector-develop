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
from connectors.webserver.nap.tasks import update

fail_resp = (False, [], "Error response received from nexus: {}")
success_resp = (
    True,
    [
        {
            "1792342": {
                "errorMessage": "",
                "status": "SUCCESS",
            }
        },
        {
            "1792343": {
                "errorMessage": "",
                "status": "SUCCESS",
            }
        },
    ],
)
partial_resp = (
    True,
    [
        {
            "1792342": {
                "errorMessage": "",
                "status": "SUCCESS",
            }
        },
        {
            "1792343": {
                "errorMessage": "Failed to reSubmit failed voip circuit with requestid 2, Invalid Credential",
                "status": "FAIL",
            }
        },
    ],
)
all_fail_resp = (
    True,
    [
        {
            "1792342": {
                "errorMessage": "Failed to reSubmit failed voip circuit with requestid 1, Invalid Credential",
                "status": "FAIL",
            }
        },
        {
            "1792343": {
                "errorMessage": "Failed to reSubmit failed voip circuit with requestid 2, Invalid Credential",
                "status": "FAIL",
            }
        },
    ],
)


@patch("connectors.core.services.nap.connector.NapService.update_nap_details")
def test_update_nap_details(update_nap):
    update_nap.return_value = success_resp
    assert update.update_nap_details(**{"body": {"region": "Ireland", "requestId": ["1792342", "1792343"]}}) == {
        "status": "SUCCESS",
        "orders": success_resp[1],
    }


@patch("connectors.core.services.nap.connector.NapService.update_nap_details")
def test_update_nap_details_partial(update_nap):
    update_nap.return_value = partial_resp
    assert update.update_nap_details(**{"body": {"region": "Ireland", "requestId": ["1792342", "1792343"]}}) == {
        "status": "PARTIAL-SUCCESS",
        "orders": partial_resp[1],
    }


@patch("connectors.core.services.nap.connector.NapService.update_nap_details")
def test_update_nap_details_fail(update_nap):
    update_nap.return_value = all_fail_resp
    assert update.update_nap_details(**{"body": {"region": "Ireland", "requestId": ["1792342", "1792343"]}}) == {
        "status": "FAIL",
        "orders": all_fail_resp[1],
    }
