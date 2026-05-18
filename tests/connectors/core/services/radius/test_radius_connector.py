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
from connectors.core.services.radius.connector import RadiusService


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.services.radius.connector.oauth.token_generator", Mock(return_value="abcd"))
def test_generate_token_success1(rest_mock):
    radius_service = RadiusService()
    assert radius_service.generate_token() == "abcd"


create_response = {"message": "created", "seqid": 14190, "status_code": 200}

payload = {
    "ruleIpv6Prefix": "2a0e:418::/32",
    "ruleIpv4Prefix": "101.56.0.0/20",
    "psidLength": 3,
    "psidOffset": 6,
    "eaLength": 16,
}


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_add_bmr_details(rest_mock):
    radius_service = RadiusService()
    radius_service.rest.post = Mock(return_value=create_response)
    assert radius_service.add_bmr_details(**{"url": "v1/bmr", "body": payload}) == create_response


get_response = {
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


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_get_bmr_details(rest_mock):
    radius_service = RadiusService()
    radius_service.rest.get = Mock(return_value=get_response)
    assert radius_service.get_bmr_details(**{"url": "v1/bmr"}) == get_response


delete_response = {"message": "2a0e:418::/32 BMR deleted", "seqid": 14193, "status_code": 200}


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_delete_bmr_details(rest_mock):
    radius_service = RadiusService()
    radius_service.rest.delete = Mock(return_value=delete_response)
    assert radius_service.delete_bmr_details(**{"url": "v1/bmr"}) == delete_response
