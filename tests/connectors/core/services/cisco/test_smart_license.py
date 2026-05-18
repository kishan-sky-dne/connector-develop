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
import datetime
from unittest.mock import patch

# DNE Library
from connectors.core.services.cisco.smart_license_services import CiscoSmartLicense
from connectors.core.utils.helpers import generic_secret

secret = generic_secret()


@patch("connectors.core.services.cisco.smart_license_services.CiscoSmartLicense.fetch_smart_license_from_cisco")
@patch("connectors.core.services.cisco.smart_license_services.CiscoSmartLicense.fetch_authorization_token")
@patch("connectors.core.services.cisco.cisco_smart_license_operations.CiscoSmartOperations.add_token_operations")
@patch("connectors.core.services.cisco.cisco_smart_license_operations.CiscoSmartOperations.get_smart_token_operations")
def test_fetch_authorization_token(
    mocked_get_smart_token_operations,
    mocked_add_token_operations,
    mocked_fetch_authorization_token,
    mocked_fetch_smart_license_from_cisco,
):
    """
    Unit Test case for Cisco Smart license services
    """
    mocked_fetch_smart_license_from_cisco.return_value = {
        "status": "SUCCESS",
        "statusMessage": "A valid, active token was generated.",
        "tokenInfo": {
            "createdBy": "test_user",
            "exportControl": "Allowed",
            "description": "this is test from DNE",
            "token": secret,
            "expirationDate": "2021-09-23 12:46:23",
        },
    }
    mocked_get_smart_token_operations.return_value = (
        secret,
        datetime.datetime.now(datetime.timezone.utc),
    )
    mocked_add_token_operations.return_value = secret
    mocked_fetch_authorization_token.return_value = secret
    csml_obj = CiscoSmartLicense()
    result = csml_obj.get_smart_token()
    assert result == {"status": "SUCCESS", "token": secret}
    mocked_get_smart_token_operations.return_value = secret, datetime.datetime(
        2050, 12, 30, 00, 00, 00, 310046, datetime.timezone.utc
    )
    csml_obj_1 = CiscoSmartLicense()
    result_1 = csml_obj_1.get_smart_token()
    assert result_1 == {"status": "SUCCESS", "token": secret}

    mocked_get_smart_token_operations.return_value = None
    csml_obj_2 = CiscoSmartLicense()
    result_2 = csml_obj_2.get_smart_token()
    assert result_2 == {"status": "SUCCESS", "token": secret}


@patch("connectors.core.services.cisco.cisco_smart_license_operations.CiscoSmartOperations.get_smart_token_operations")
def test_negative_scenario(mocked_get_smart_token_operations):
    """
    Unit Test case for Cisco Smart license services
    """
    mocked_get_smart_token_operations.return_value = 403
    csml_obj = CiscoSmartLicense()
    result = csml_obj.get_smart_token()
    assert result == {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [{"code": "ERR-008-012-1001", "message": "Failed to generate token403"}],
    }


@patch("connectors.core.services.cisco.smart_license_services.CiscoSmartLicense.fetch_smart_license_from_cisco")
@patch("connectors.core.services.cisco.smart_license_services.CiscoSmartLicense.fetch_authorization_token")
@patch("connectors.core.services.cisco.cisco_smart_license_operations.CiscoSmartOperations.add_token_operations")
@patch("connectors.core.services.cisco.cisco_smart_license_operations.CiscoSmartOperations.get_smart_token_operations")
def test_smart_token(
    mocked_get_smart_token_operations,
    mocked_add_token_operations,
    mocked_fetch_authorization_token,
    mocked_fetch_smart_license_from_cisco,
):
    """
    Unit Test case for Cisco Smart license services
    """
    mocked_fetch_smart_license_from_cisco.return_value = {
        "status": "SUCCESS",
        "statusMessage": "A valid, active token was generated.",
        "tokenInfo": {
            "createdBy": "test_user",
            "exportControl": "Allowed",
            "description": "this is test from DNE",
            "token": secret,
            "expirationDate": "2021-09-23 12:46:23",
        },
    }
    mocked_add_token_operations.return_value = secret
    mocked_fetch_authorization_token.return_value = secret
    mocked_get_smart_token_operations.return_value = None
    csml_obj_2 = CiscoSmartLicense()
    result_2 = csml_obj_2.get_smart_token()
    assert result_2 == {"status": "SUCCESS", "token": secret}
