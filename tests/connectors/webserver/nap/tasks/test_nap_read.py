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
from connectors.webserver.nap.tasks import read

fail_resp = (False, [], "Error response received from nexus: {}")
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
success_resp = (True, in_flight_orders["orders"], "")


@patch("connectors.core.services.nap.connector.NapService.get_nap_details")
def test_get_nap_details(get_nap):
    get_nap.return_value = success_resp
    assert read.get_nap_details(**{"body": {"region": "Ireland"}}) == {"status": "SUCCESS", "orders": success_resp[1]}


@patch("connectors.core.services.nap.connector.NapService.get_nap_details")
def test_get_nap_details_fail(get_nap):
    get_nap.return_value = fail_resp
    assert read.get_nap_details(**{"body": {"region": "Ireland"}}) == {
        "status": "FAIL",
        "orders": None,
        "errorMessage": fail_resp[2],
    }
