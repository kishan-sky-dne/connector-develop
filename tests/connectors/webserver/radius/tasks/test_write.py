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
from connectors.core.utils.exceptions import GenericConnectorsException, RestUtilityException
from connectors.webserver.radius.tasks import write

kwargs = {
    "body": {
        "ruleIpv6Prefix": "2a0e:418::/32",
        "ruleIpv4Prefix": "101.56.0.0/20",
        "psidLength": 3,
        "psidOffset": 6,
        "eaLength": 16,
    }
}

bmr_details1 = {"message": "created", "seqid": 14190, "status_code": 200}

response1 = {"status": "SUCCESS", "seqid": 14190}


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.services.radius.connector.RadiusService.generate_token", Mock(return_value="abcd"))
@patch("connectors.core.services.radius.connector.RadiusService.add_bmr_details", Mock(return_value=bmr_details1))
def test_create_bmr_success1(rest_utility_mock):
    output = write.create_bmr(**kwargs)
    assert output == (response1, 200)


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.services.radius.connector.RadiusService.generate_token", Mock(return_value="abcd"))
@patch("connectors.core.services.radius.connector.RadiusService.add_bmr_details", Mock(return_value=None))
def test_create_bmr_success2(rest_utility_mock):
    output = write.create_bmr(**kwargs)
    assert output == (
        {
            "status": "FAILURE",
            "errorCategory": "FAILED",
            "errors": [{"code": "ERR-015-999-0200", "message": "Failed to Create BMR record: "}],
        },
        200,
    )


response_failure1 = {
    "status": "FAILURE",
    "errorCategory": "FAILED",
    "errors": [{"code": "ERR-015-999-0001", "message": "Failed to Create BMR record: URL not found"}],
}


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.services.radius.connector.RadiusService.generate_token")
@patch("connectors.core.services.radius.connector.RadiusService.add_bmr_details", Mock(return_value=None))
def test_create_bmr_token_failure1(generate_token_mock, rest_utility_mock):
    generate_token_mock.side_effect = RestUtilityException("URL not found")
    output = write.create_bmr(**kwargs)
    assert output == (response_failure1, 200)


response_failure2 = (
    {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [{"code": "ERR-015-999-0400", "message": "Failed to Create BMR record: 400 URL not found"}],
    },
    200,
)


# @patch("connectors.core.utils.rest_api_utility.RestUtility.post")
# @patch("connectors.core.services.radius.connector.RadiusService.generate_token", Mock(return_value="abcd"))
# def test_create_bmr_token_failure2(rest_utility_mock):
#     rest_utility_mock.side_effect = GenericConnectorsException("400 URL not found")
#     rest_utility_mock.response = Mock()
#     rest_utility_mock.response.status_code = 400
#     rest_utility_mock.side_effect = rest_utility_mock
#     output = write.create_bmr(**kwargs)
#     assert output == response_failure2


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.services.radius.connector.RadiusService.generate_token", Mock(return_value="abcd"))
def test_create_bmr_url_failure1(rest_utility_mock):
    rest_utility_exception = RestUtilityException("400 URL not found")
    rest_utility_exception.response = Mock()
    rest_utility_exception.response.status_code = 400
    rest_utility_mock.side_effect = rest_utility_exception
    output = write.create_bmr(**kwargs)
    assert output == response_failure2


# # delete record api

delete_kwargs = {
    "ipv6Prefix": "2a0e:418::/32",
}

delete_response = ({"status": "SUCCESS", "seqid": 14193}, 200)


@patch("connectors.core.utils.rest_api_utility.RestUtility.delete", Mock(return_value=delete_response))
@patch("connectors.core.services.radius.connector.RadiusService.generate_token", Mock(return_value="abcd"))
def test_delete_bmr_by_ip_success1():
    output = write.delete_bmr_by_ip(**delete_kwargs)
    assert output == delete_response


delete_response2 = (
    {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-015-999-0409",
                "message": "Failed to delete BMR record for prefix '2a0e:418::/32': Conflict (Not found)",
            }
        ],
    },
    200,
)


@patch(
    "connectors.core.utils.rest_api_utility.RestUtility.delete",
    Mock(return_value=({"message": "Conflict (Not found)", "status_code": 409}, 409)),
)
@patch("connectors.core.services.radius.connector.RadiusService.generate_token", Mock(return_value="abcd"))
def test_delete_bmr_by_ip_success2():
    output = write.delete_bmr_by_ip(**delete_kwargs)
    assert output == delete_response2


response_delete_failure1 = {
    "status": "FAILURE",
    "errorCategory": "FAILED",
    "errors": [
        {"code": "ERR-015-999-0001", "message": "Failed to delete BMR record for prefix '2a0e:418::/32': URL not found"}
    ],
}


@patch("connectors.core.utils.rest_api_utility.RestUtility.delete")
@patch("connectors.core.services.radius.connector.RadiusService")
@patch("connectors.core.services.radius.connector.RadiusService.generate_token", Mock(return_value="abcd"))
def test_delete_bmr_by_ip_token_failure2(rest_utility_mock, radius_mock):
    rest_utility_mock.side_effect = GenericConnectorsException("URL not found")
    output = write.delete_bmr_by_ip(**delete_kwargs)
    assert output == (response_delete_failure1, 200)


@patch("connectors.core.utils.rest_api_utility.RestUtility.delete")
@patch("connectors.core.services.radius.connector.RadiusService")
@patch("connectors.core.services.radius.connector.RadiusService.generate_token", Mock(return_value="abcd"))
def test_delete_bmr_by_ip_url_failure1(rest_utility_mock, radius_mock):
    rest_utility_mock.side_effect = RestUtilityException("URL not found")
    output = write.delete_bmr_by_ip(**delete_kwargs)
    assert output == (response_delete_failure1, 200)
