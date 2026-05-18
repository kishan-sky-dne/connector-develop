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
import json
from unittest.mock import Mock, patch

# Third Party Library
import pytest
import requests

# DNE Library
from connectors.core.services.inca.connector import IncaService
from connectors.core.utils.helpers import generic_secret
from connectors.webserver.inca.tasks import update
from connectors.webserver.inca.tasks.update import _validate_gea_cease, _validate_inca_update_data

from ...helpers import exception_cmd_apis

secret = generic_secret()

# NEXA rest test
access_token_nexa = "xyz"
body = {
    "circuitDetails": [
        {
            "circuitId": "OGHP63837190",
            "configStatus": "inprogress",
            "sparkReference": "CTASK1234578",
            "configDate": "9/3/2021",
        },
        {
            "circuitId": "OGHP64724816",
            "configStatus": "inprogress",
            "sparkReference": "CHG123458812",
            "configDate": "9/3/2021",
        },
    ]
}


body_no_spark = {
    "circuitDetails": [
        {
            "circuitId": "OGHP63837190",
            "configStatus": "inprogress",
            "sparkReference": None,
            "configDate": "9/3/2021",
            "circuitState": "Ready-For-Service",
        },
        {
            "circuitId": "OGHP64724816",
            "configStatus": "success",
            "sparkReference": None,
            "configDate": "9/3/2021",
            "circuitState": "Ready-For-Service",
        },
    ]
}
body_no_date = {
    "circuitDetails": [
        {
            "circuitId": "OGHP64724816",
            "configStatus": "success",
            "sparkReference": "CTASK1234578",
        },
    ]
}

body_circuit_state_1 = {
    "circuitDetails": [
        {
            "circuitId": "OGHP63837190",
            "configStatus": "success",
            "sparkReference": "CTASK1234578",
            "configDate": "9/3/2021",
            "circuitState": "Ready-For-Config",
            "testRef": "25486CG",
        },
        {
            "circuitId": "OGHP64724816",
            "configStatus": "success",
            "sparkReference": "CHG123458812",
            "configDate": "9/3/2021",
            "circuitState": "Ready-For-Config",
            "testRef": "25486CG",
        },
    ]
}

body_circuit_state_2 = {
    "circuitDetails": [
        {
            "circuitId": "OGHP64724816",
            "configStatus": "inprogress",
            "sparkReference": "CTASK1234578",
            "circuitState": "Ready-For-Config",
            "testRef": "25486CG",
        },
    ]
}

body_circuit_state_3 = {
    "circuitDetails": [
        {
            "circuitId": "OGHP64724816",
            "configStatus": "success",
            "sparkReference": "CTASK1234578",
            "testRef": "25486CG",
            "configDate": "9/3/2021",
            "comments": "OR Testing success with 25486CG",
        },
    ]
}

body_circuit_state_4 = {
    "circuitDetails": [
        {
            "circuitId": "OGHP64724816",
            "configStatus": "invalid",
            "sparkReference": "CTASK1234578",
            "circuitState": "Ready-For-Config",
            "testRef": "25486CG",
        },
    ]
}

body_circuit_state_5 = {
    "circuitDetails": [
        {
            "circuitId": "OGHP64724816",
            "configStatus": "success",
            "configDate": "9/3/2024",
            "sparkReference": "CTASK1234578",
            "circuitState": "Ready-For-Config",
        },
    ]
}

body_circuit_state_6 = {
    "circuitDetails": [
        {
            "circuitId": "OGHP64724816",
            "configStatus": "success",
            "configDate": "9/3/2024",
            "circuitState": "Ready-For-Config",
            "testRef": "25486CG",
            "orderRef": "dummy",
        },
    ]
}


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth")
def test_update_inca_details_case1(mock_oauth, post_mocked, mock_post):
    mock_oauth.token_generator.return_value = access_token_nexa
    inst_inca = IncaService()
    post_mocked.return_value = {"result": "OK", "id": "5549"}
    # update._validate_inca_update_data = Mock(return_value=(True, []))
    inst_inca.update_inca_type_details = Mock(return_value={"jobId": "GC-5549"})
    output = update.update_inca_details(type="gea", body=body)
    assert output == {"jobId": "GC-5549"}


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth")
def test_update_inca_details_case2(mock_oauth, post_mocked, mock_post):
    mock_oauth.token_generator.return_value = access_token_nexa
    inst_inca = IncaService()
    post_mocked.return_value = {"result": "OK", "id": "5549"}
    update._validate_inca_new_switch_data = Mock(return_value=(True, [], {}))
    update._validate_inca_update_data = Mock(return_value=(True, [], {}))
    inst_inca.update_inca_type_details = Mock(return_value={"jobId": "GC-5549"})
    output = update.update_inca_details(type="ge", body=body)
    assert output == ""


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth")
def test_update_inca_details_case3(mock_oauth, post_mocked, mock_post):
    mock_oauth.token_generator.return_value = access_token_nexa
    inst_inca = IncaService()
    post_mocked.return_value = {"result": "OK", "id": "5549"}
    inst_inca.gea_inca_update_status = Mock(return_value={"jobId": "GC-5549"})
    inst_inca.update_inca_type_details = Mock(return_value={"jobId": "GC-5549"})
    output = update.update_inca_details(**{"type": "gea", "body": body_no_spark})
    assert output == {
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-011-999-0001",
                "message": "sparkReference must be provided for circuit OGHP63837190 as configStatus is inprogress",
            },
            {
                "code": "ERR-011-999-0001",
                "message": "sparkReference must be provided for circuit OGHP64724816 as configStatus is success",
            },
        ],
    }


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth")
def test_update_inca_details_case4(mock_oauth, post_mocked, mock_post):
    mock_oauth.token_generator.return_value = access_token_nexa
    inst_inca = IncaService()
    post_mocked.return_value = {"result": "OK", "id": "5549"}
    inst_inca.gea_inca_update_status = Mock(return_value={"jobId": "GC-5549"})
    inst_inca.update_inca_type_details = Mock(return_value={"jobId": "GC-5549"})
    output = update.update_inca_details(**{"type": "gea", "body": body_no_date})
    assert output == {
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-011-999-0002",
                "message": "configDate must be provided for circuit OGHP64724816 as configStatus is success",
            },
        ],
    }


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth")
def test_update_inca_details_case5(mock_oauth, post_mocked, mock_post):
    mock_oauth.token_generator.return_value = access_token_nexa
    inst_inca = IncaService()
    post_mocked.return_value = {"result": "OK", "id": "5549"}
    inst_inca.update_inca_type_details = Mock(return_value={"jobId": "GC-5549"})
    output = update.update_inca_details(type="gea", body=body_circuit_state_1)
    assert output == {"jobId": "GC-5549"}


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth")
def test_update_inca_details_case6(mock_oauth, post_mocked, mock_post):
    mock_oauth.token_generator.return_value = access_token_nexa
    inst_inca = IncaService()
    post_mocked.return_value = {"result": "OK", "id": "5549"}
    update._validate_inca_new_switch_data = Mock(return_value=(True, [], {}))
    update._validate_inca_update_data = Mock(return_value=(True, [], {}))
    inst_inca.update_inca_type_details = Mock(return_value={"jobId": "GC-5549"})
    output = update.update_inca_details(type="ge", body=body_circuit_state_1)
    assert output == ""


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth")
def test_update_inca_details_case7(mock_oauth, post_mocked, mock_post):
    mock_oauth.token_generator.return_value = access_token_nexa
    inst_inca = IncaService()
    post_mocked.return_value = {"result": "OK", "id": "5549"}
    inst_inca.gea_inca_update_status = Mock(return_value={"jobId": "GC-5549"})
    inst_inca.update_inca_type_details = Mock(return_value={"jobId": "GC-5549"})
    output = update.update_inca_details(**{"type": "gea", "body": body_circuit_state_2})
    assert output == {
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-011-999-0002",
                "message": (
                    "'orderRef' must be provided for circuit OGHP64724816 when "
                    "'circuitState' is 'Ready-For-Config' and 'configStatus' is 'inprogress'"
                ),
            },
        ],
    }


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth")
def test_update_inca_details_case8(mock_oauth, post_mocked, mock_post):
    mock_oauth.token_generator.return_value = access_token_nexa
    inst_inca = IncaService()
    post_mocked.return_value = {"result": "OK", "id": "5549"}
    inst_inca.gea_inca_update_status = Mock(return_value={"jobId": "GC-5549"})
    inst_inca.update_inca_type_details = Mock(return_value={"jobId": "GC-5549"})
    output = update.update_inca_details(**{"type": "gea", "body": body_circuit_state_3})
    assert output == {
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-011-999-0002",
                "message": "testRef or comments must not be provided for circuit OGHP64724816 as circuitState "
                "is not Ready-For-Config",
            },
        ],
    }


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth")
def test_update_inca_details_case9(mock_oauth, post_mocked, mock_post):
    mock_oauth.token_generator.return_value = access_token_nexa
    inst_inca = IncaService()
    post_mocked.return_value = {"result": "OK", "id": "5549"}
    inst_inca.gea_inca_update_status = Mock(return_value={"jobId": "GC-5549"})
    inst_inca.update_inca_type_details = Mock(return_value={"jobId": "GC-5549"})
    output = update.update_inca_details(**{"type": "gea", "body": body_circuit_state_4})
    assert output == {
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-011-999-0002",
                "message": "configStatus must be one of ['success', 'inprogress', 'failure'] "
                "for circuit OGHP64724816 as circuitState is Ready-For-Config",
            },
        ],
    }


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth")
def test_update_inca_details_case10(mock_oauth, post_mocked, mock_post):
    mock_oauth.token_generator.return_value = access_token_nexa
    inst_inca = IncaService()
    post_mocked.return_value = {"result": "OK", "id": "5549"}
    inst_inca.gea_inca_update_status = Mock(return_value={"jobId": "GC-5549"})
    inst_inca.update_inca_type_details = Mock(return_value={"jobId": "GC-5549"})
    output = update.update_inca_details(**{"type": "gea", "body": body_circuit_state_5})
    assert output == {
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-011-999-0002",
                "message": "testRef must be provided for circuit OGHP64724816 "
                "as circuitState is Ready-For-Config and configStatus is success",
            },
        ],
    }


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth")
def test_update_inca_details_case11(mock_oauth, post_mocked, mock_post):
    mock_oauth.token_generator.return_value = access_token_nexa
    inst_inca = IncaService()
    post_mocked.return_value = {"result": "OK", "id": "5549"}
    inst_inca.gea_inca_update_status = Mock(return_value={"jobId": "GC-5549"})
    inst_inca.update_inca_type_details = Mock(return_value={"jobId": "GC-5549"})
    output = update.update_inca_details(**{"type": "gea", "body": body_circuit_state_6})
    assert output == {
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-011-999-0002",
                "message": "'orderRef' is required only when 'circuitState' is "
                "'inprogress' and 'configStatus' is 'Ready-For-Config'",
            },
        ],
    }


@patch.object(requests.Session, "post")
@patch.object(requests.Session, "put")
@patch("connectors.core.utils.rest_api_utility.RestUtility.put")
@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth")
@pytest.mark.parametrize("exception_type, error_code", exception_cmd_apis)
def test_update_inca_details_exception(mock_oauth, post_mocked, put_mocked, s_put, s_post, exception_type, error_code):
    mock_oauth.token_generator.return_value = access_token_nexa
    inst_inca = IncaService()
    post_mocked.side_effect = exception_type("dummy error message")
    put_mocked.side_effect = exception_type("dummy error message")
    s_post.get = Mock()
    s_put.get = Mock()
    update._validate_inca_update_data.side_effect = exception_type("dummy error message")
    inst_inca.gea_inca_update_status = exception_type("dummy error message")
    output = update.update_inca_details(type="gea", body=body)
    assert output.status_code == error_code


access_token_wholesale = secret
circuit_req_body = {
    "asset-id": "SKY-TEST-DNE-018",
    "spark-change-ticket": "CHG1234567",
    "completion-date": "22-Sep-2022",
    "ani-engineer-name": "John Baggs",
}


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.oauth.token_generator", return_value=access_token_wholesale)
@patch(
    "connectors.core.services.inca.connector.IncaService.update_wholesale_details",
    return_value={"status": "SUCCESS"},
)
@patch("connectors.webserver.inca.tasks.update.validate_json_request_payload", return_value=(True, ""))
def test_update_wholesale_details_case1(put_mocked, mock_post, mock_oauth, validation_mock):
    """
    verify circuit request for requestType new and serviceType uni
    """

    output = update.update_wholesale_details(body=circuit_req_body, requestType="new", serviceType="uni")
    assert output == {"status": "SUCCESS"}


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.oauth.token_generator", return_value=access_token_wholesale)
@patch(
    "connectors.core.services.inca.connector.IncaService.update_wholesale_details",
    return_value={"status": "SUCCESS"},
)
@patch("connectors.webserver.inca.tasks.update.validate_json_request_payload", return_value=(True, ""))
def test_update_wholesale_details_case2(put_mocked, mock_post, mock_oauth, validation_mock):
    """
    verify circuit request for requestType update and serviceType uni
    """
    output = update.update_wholesale_details(body=circuit_req_body, requestType="update", serviceType="uni")
    assert output == {"status": "SUCCESS"}


circuit_req_cease_body = {
    "asset-id": "SKY-TEST-DNE-018",
    "spark-change-ticket": "CHG1234567",
    "completion-date": "22-Sep-2022",
}


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.oauth.token_generator", return_value=access_token_wholesale)
@patch(
    "connectors.core.services.inca.connector.IncaService.update_wholesale_details",
    return_value={"status": "SUCCESS"},
)
@patch("connectors.webserver.inca.tasks.update.validate_json_request_payload", return_value=(True, ""))
def test_update_wholesale_details_case3(put_mocked, mock_post, mock_oauth, validation_mock):
    """
    verify circuit request for requestType cease
    """
    output = update.update_wholesale_details(body=circuit_req_cease_body, requestType="cease", serviceType="uni")
    assert output == {"status": "SUCCESS"}


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.oauth.token_generator", return_value=access_token_wholesale)
@patch("connectors.core.services.inca.connector.IncaService.update_wholesale_details", return_value=None)
@patch("connectors.webserver.inca.tasks.update.validate_json_request_payload", return_value=(True, ""))
def test_update_wholesale_details_case4(put_mocked, mock_post, mock_oauth, validation_mock):
    """
    verify circuit request for failure case
    """
    output = update.update_wholesale_details(body=circuit_req_cease_body, requestType="cease", serviceType="uni")
    response = None
    assert output == response


inca_response2 = {"result": "Asset ID is not found"}

response2 = {
    "errorCategory": "FAILED",
    "errors": [{"code": "ERR-011-999-0007", "message": "No matching request found for given Asset ID"}],
    "status": "FAILED",
}


class Response2:
    def __init__(self):
        self.status_code = 409
        self._content = json.dumps(inca_response2)


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.oauth.token_generator", return_value=access_token_wholesale)
@patch("connectors.core.services.inca.connector.IncaService.update_wholesale_details", return_value=response2)
@patch("connectors.webserver.inca.tasks.update.validate_json_request_payload", return_value=(True, ""))
def test_update_wholesale_details_case5(put_mocked, mock_post, mock_oauth, validation_mock):
    """
    Test to check the functionality of update_wholesale_details() for Asset ID
    """
    output = update.update_wholesale_details(body=circuit_req_body, requestType="new", serviceType="uni")
    assert output == response2


inca_response3 = {"result": "Update is not allowed"}
response3 = {
    "errorCategory": "FAILED",
    "errors": [{"code": "ERR-011-999-0009", "message": "Wholesale request update is not allowed"}],
    "status": "FAILED",
}


class Response3:
    def __init__(self):
        self.status_code = 409
        self._content = json.dumps(inca_response3)


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.oauth.token_generator", return_value=access_token_wholesale)
@patch("connectors.core.services.inca.connector.IncaService.update_wholesale_details", return_value=response3)
@patch("connectors.webserver.inca.tasks.update.validate_json_request_payload", return_value=(True, ""))
def test_update_wholesale_details_case6(put_mocked, mock_post, mock_oauth, validation_mock):
    """
    Test to check the functionality of update_wholesale_details() for new is not allowed
    """
    output = update.update_wholesale_details(body=circuit_req_body, requestType="new", serviceType="uni")
    assert output == response3


partner_req_body = {
    "partner-code": "Sky Business-5230",
    "partner-name": "Sky Business-5230",
    "wholesale-service-type": "activeStandby",
    "uni-service-type": "unTagged",
}

partner_req_cease_body = {"partner-code": "OFNL", "partner-cease-date": "2022-08-07"}

validation_uni_err_msg = {
    "detail": [{"'completion-date' is a required property": ""}],
    "status": 400,
    "title": "Bad Request",
    "type": "about:blank",
}


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.oauth.token_generator", return_value=access_token_wholesale)
@patch("connectors.core.services.inca.connector.IncaService.update_wholesale_details", return_value=response3)
@patch(
    "connectors.webserver.inca.tasks.update.validate_json_request_payload", return_value=(False, validation_uni_err_msg)
)
def test_update_wholesale_details_case7(put_mocked, mock_post, mock_oauth, validation_mock):
    """
    Test to check the failure validation functionality of update_wholesale_details() for new is not allowed
    """
    output = update.update_wholesale_details(body=circuit_req_body, requestType="new", serviceType="uni")
    assert output == validation_uni_err_msg


circuit_req_body_cease = {"asset-id": "SKY-TEST-DNE-018", "spark-change-ticket": "CHG1234567"}


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.oauth.token_generator", return_value=access_token_wholesale)
@patch(
    "connectors.core.services.inca.connector.IncaService.update_wholesale_details",
    return_value={"status": "SUCCESS"},
)
@patch("connectors.webserver.inca.tasks.update.validate_json_request_payload", return_value=(True, ""))
def test_update_wholesale_details_case8(put_mocked, mock_post, mock_oauth, validation_mock):
    """
    verify requestType new and serviceType partner success case
    """
    output = update.update_wholesale_details(body=partner_req_body, requestType="new", serviceType="partner")
    assert output == {"status": "SUCCESS"}


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.oauth.token_generator", return_value=access_token_wholesale)
@patch(
    "connectors.core.services.inca.connector.IncaService.update_wholesale_details",
    return_value={"status": "SUCCESS"},
)
@patch("connectors.webserver.inca.tasks.update.validate_json_request_payload", return_value=(True, ""))
def test_update_wholesale_details_case9(put_mocked, mock_post, mock_oauth, validation_mock):
    """
    verify requestType cease and serviceType partner success case
    """
    output = update.update_wholesale_details(body=partner_req_cease_body, requestType="cease", serviceType="partner")
    assert output == {"status": "SUCCESS"}


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.oauth.token_generator", return_value=access_token_wholesale)
@patch("connectors.core.services.inca.connector.IncaService.update_wholesale_details", return_value=None)
@patch("connectors.webserver.inca.tasks.update.validate_json_request_payload", return_value=(True, ""))
def test_update_wholesale_details_case10(put_mocked, mock_post, mock_oauth, validation_mock):
    """
    verify  failure scenario when requestType is cease and serviceType partner
    """
    output = update.update_wholesale_details(body=partner_req_cease_body, requestType="cease", serviceType="partner")
    response = None
    assert output == response


response_err_1 = {
    "errorCategory": "FAILED",
    "errors": [{"code": "ERR-011-999-0011", "message": "Partner code already exists in INCA"}],
    "status": "FAILED",
}
response_err_2 = {
    "errorCategory": "FAILED",
    "errors": [{"code": "ERR-011-999-0012", "message": "Partner name already exists in INCA"}],
    "status": "FAILED",
}
response_err_3 = {
    "errorCategory": "FAILED",
    "errors": [{"code": "ERR-011-999-0015", "message": "Partner code is not found in INCA"}],
    "status": "FAILED",
}


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.oauth.token_generator", return_value=access_token_wholesale)
@patch("connectors.core.services.inca.connector.IncaService.update_wholesale_details", return_value=response_err_1)
@patch("connectors.webserver.inca.tasks.update.validate_json_request_payload", return_value=(True, ""))
def test_update_wholesale_details_case11(put_mocked, mock_post, mock_oauth, validation_mock):
    """
    Verify when duplicate Partner code is passed for requestType:new & serviceType:partner
    """
    output = update.update_wholesale_details(body=partner_req_body, requestType="new", serviceType="partner")
    assert output == response_err_1


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.oauth.token_generator", return_value=access_token_wholesale)
@patch("connectors.core.services.inca.connector.IncaService.update_wholesale_details", return_value=response_err_2)
@patch("connectors.webserver.inca.tasks.update.validate_json_request_payload", return_value=(True, ""))
def test_update_wholesale_details_case12(put_mocked, mock_post, mock_oauth, validation_mock):
    """
    Test to check the functionality of update_wholesale_details() when Partner name already exists
    """
    output = update.update_wholesale_details(body=partner_req_body, requestType="new", serviceType="partner")
    assert output == response_err_2


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.oauth.token_generator", return_value=access_token_wholesale)
@patch("connectors.core.services.inca.connector.IncaService.update_wholesale_details", return_value=response_err_3)
@patch("connectors.webserver.inca.tasks.update.validate_json_request_payload", return_value=(True, ""))
def test_update_wholesale_details_case13(put_mocked, mock_post, mock_oauth, validation_mock):
    """
    Verify to check requestType:"cease" and serviceType:"partner" when Invalid partner code is given
    """
    output = update.update_wholesale_details(body=partner_req_cease_body, requestType="cease", serviceType="partner")
    assert output == response_err_3


validation_partner_err_msg = {
    "errorCategory": "FAILED",
    "errors": [
        {
            "code": "ERR-011-999-0010",
            "message": "Wholesale validation failed for parameter: "
            "`{'code': 'NotFound', 'message': 'Not Found', 'type': 'tag:oracle.com,2020:error/NotFound', "
            "'instance': 'tag:oracle.com,2020:ecid/tBM718asd3KJcjhch8KcXg'}`",
        }
    ],
    "status": "FAILED",
}


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.oauth.token_generator", return_value=access_token_wholesale)
@patch(
    "connectors.core.services.inca.connector.IncaService.update_wholesale_details",
    return_value=validation_partner_err_msg,
)
@patch("connectors.webserver.inca.tasks.update.validate_json_request_payload", return_value=(True, ""))
def test_update_wholesale_details_case14(put_mocked, mock_post, mock_oauth, validation_mock):
    """
    verify to check the functionality of update_wholesale_details() when Invalid INCA API URL is passed
    """
    output = update.update_wholesale_details(body=partner_req_cease_body, requestType="cease", serviceType="partner")
    assert output == validation_partner_err_msg


interconnect_new_req_payload = {
    "partner-code": "SKY-TEST-DNE-103",
    "asset-id": "SKY-LNTW-FLDA-18",
    "nni-name": "London Bricklane",
    "remote-nni-pe": "ar0-wifi.bllon",
    "remote-nni-lag": "lag11",
    "rfs-date": "11-Jan-2023",
    "ports": [{"interface": "po1/1/2", "bearer-rate": "10", "circuit-id": "TIC-063341"}],
}


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.oauth.token_generator", return_value=access_token_wholesale)
@patch(
    "connectors.core.services.inca.connector.IncaService.update_wholesale_details",
    return_value={"status": "SUCCESS"},
)
@patch("connectors.webserver.inca.tasks.update.validate_json_request_payload", return_value=(True, ""))
def test_update_wholesale_details_case15(put_mocked, mock_post, mock_oauth, validation_mock):
    """
    verify requestType new and serviceType interconnect success case
    """
    output = update.update_wholesale_details(
        body=interconnect_new_req_payload, requestType="new", serviceType="interconnect"
    )
    assert output == {"status": "SUCCESS"}


interconnect_update_req_payload = {
    "partner-code": "SKY-TEST-DNE-103",
    "asset-id": "SKY-LNTW-FLDA-18",
    "remote-nni-pe": "ar0-wifi.bllon",
    "remote-nni-lag": "lag11",
    "rfs-date": "11-Feb-2023",
    "ports": [{"interface": "po1/1/2", "bearer-rate": "10", "circuit-id": "TIC-063341"}],
}


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.oauth.token_generator", return_value=access_token_wholesale)
@patch(
    "connectors.core.services.inca.connector.IncaService.update_wholesale_details",
    return_value={"status": "SUCCESS"},
)
@patch("connectors.webserver.inca.tasks.update.validate_json_request_payload", return_value=(True, ""))
def test_update_wholesale_details_case16(put_mocked, mock_post, mock_oauth, validation_mock):
    """
    verify requestType update and serviceType interconnect success case
    """
    output = update.update_wholesale_details(
        body=interconnect_update_req_payload, requestType="update", serviceType="interconnect"
    )
    assert output == {"status": "SUCCESS"}


interconnect_cease_req_payload = {"asset-id": "SKY-LNTW-FLDA-18", "cease-date": "12-Oct-2022"}


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.oauth.token_generator", return_value=access_token_wholesale)
@patch(
    "connectors.core.services.inca.connector.IncaService.update_wholesale_details",
    return_value={"status": "SUCCESS"},
)
@patch("connectors.webserver.inca.tasks.update.validate_json_request_payload", return_value=(True, ""))
def test_update_wholesale_details_case17(put_mocked, mock_post, mock_oauth, validation_mock):
    """
    verify requestType cease and serviceType interconnect success case
    """
    output = update.update_wholesale_details(
        body=interconnect_cease_req_payload, requestType="cease", serviceType="interconnect"
    )
    assert output == {"status": "SUCCESS"}


response_err_4 = {
    "errorCategory": "FAILED",
    "errors": [{"code": "ERR-011-999-0013", "message": "Partner code not found in INCA"}],
    "status": "FAILED",
}


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.oauth.token_generator", return_value=access_token_wholesale)
@patch("connectors.core.services.inca.connector.IncaService.update_wholesale_details", return_value=response_err_4)
@patch("connectors.webserver.inca.tasks.update.validate_json_request_payload", return_value=(True, ""))
def test_update_wholesale_details_case18(put_mocked, mock_post, mock_oauth, validation_mock):
    """
    Verify when invalid Partner code is passed for requestType:new & serviceType:interconnect
    """
    output = update.update_wholesale_details(
        body=interconnect_new_req_payload, requestType="new", serviceType="interconnect"
    )
    assert output == response_err_4


response_err_5 = {
    "errorCategory": "FAILED",
    "errors": [{"code": "ERR-011-999-0016", "message": "nniCode not found in INCA"}],
    "status": "FAILED",
}


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.oauth.token_generator", return_value=access_token_wholesale)
@patch("connectors.core.services.inca.connector.IncaService.update_wholesale_details", return_value=response_err_5)
@patch("connectors.webserver.inca.tasks.update.validate_json_request_payload", return_value=(True, ""))
def test_update_wholesale_details_case19(put_mocked, mock_post, mock_oauth, validation_mock):
    """
    Verify when invalid nni code is passed for requestType:new & serviceType:interconnect
    """
    output = update.update_wholesale_details(
        body=interconnect_new_req_payload, requestType="new", serviceType="interconnect"
    )
    assert output == response_err_5


new_switch_payload = {"body": {"hostname": "me0.bllab.isp.sky.com"}}
new_switch_payload_resp = {"body": {"hostname": "me0.bllab"}}


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_validate_inca_new_switch_data_case1(get_mocked):
    get_mocked.return_value = (True, 200, {}, "")
    response = update._validate_inca_new_switch_data(**new_switch_payload)
    assert response == (True, [], {})


@patch.object(requests.Session, "get")
@patch.object(requests.Session, "post")
@patch.object(requests.Session, "put")
@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.rest_api_utility.RestUtility.put")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_inca_rfs_details_case1(mock_oauth, put_mocked, get_mocked, mock_put, mock_post, mock_get):
    inst_inca = IncaService()
    get_mocked.return_value = {"snmp_sysdescr": "NCS-540", "status": "development"}
    put_mocked.return_value = {"result": "OK"}
    update._validate_inca_new_switch_data = Mock(return_value=(True, [], new_switch_payload))
    inst_inca.update_inca_type_details = Mock(
        return_value={"status": "SUCCESS", "result": "OK", "metadata": {"hostname": "me0.bllab"}}
    )
    output = update.update_inca_rfs_details(type="newMetroSwitch", body=new_switch_payload["body"])
    assert output == {"status": "SUCCESS", "result": "OK", "metadata": {"hostname": "me0.bllab"}}


class TestGet:
    pass


@patch.object(requests.Session, "post")
@patch.object(requests.Session, "put")
@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.rest_api_utility.RestUtility.put")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_inca_rfs_details_case2(mock_oauth, put_mocked, get_mocked, mock_put, mock_post):
    inst_inca = IncaService()
    get_mocked.return_value = {"snmp_sysdescr": "NCS-540", "status": "decommissioned"}
    put_mocked.return_value = {"result": "OK"}
    update._validate_inca_new_switch_data = Mock(return_value=(True, [], new_switch_payload))
    inst_inca.update_inca_type_details = Mock(
        return_value={"status": "SUCCESS", "result": "OK", "metadata": {"hostname": "me0.bllab"}}
    )
    output = update.update_inca_rfs_details(type="newMetroSwitch", body=new_switch_payload["body"])
    assert output == {"status": "SUCCESS", "result": "OK", "metadata": {"hostname": "me0.bllab"}}
    # Device is not NCS-540
    get_mocked.return_value = {"snmp_sysdescr": "NCS-5500", "status": "development", "model": "NCS-5500"}
    put_mocked.return_value = {"result": "OK"}
    update._validate_inca_new_switch_data = Mock(return_value=(True, [], new_switch_payload))
    inst_inca.update_inca_type_details = Mock(
        return_value={"status": "SUCCESS", "result": "OK", "metadata": {"hostname": "me0.bllab"}}
    )
    output = update.update_inca_rfs_details(type="newMetroSwitch", body=new_switch_payload["body"])
    assert output == {"status": "SUCCESS", "result": "OK", "metadata": {"hostname": "me0.bllab"}}
    # Device response is not Dict
    get_test = TestGet()
    get_mocked.return_value = get_test
    put_mocked.return_value = {"result": "OK"}
    update._validate_inca_new_switch_data = Mock(return_value=(True, [], new_switch_payload))
    inst_inca.update_inca_type_details = Mock(
        return_value={"status": "SUCCESS", "result": "OK", "metadata": {"hostname": "me0.bllab"}}
    )
    output = update.update_inca_rfs_details(type="newMetroSwitch", body=new_switch_payload["body"])
    assert output == {
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-011-999-0002",
                "message": "Device me0.bllab is decommissioned or not found in dcs",
            }
        ],
    }


response_err_6 = {
    "detail": "Multiple interfaces are not allowed when remote-nni-lag is not given",
    "status": 400,
    "title": "Bad Request",
    "type": "about:blank",
}

interconnect_new_req_body = {
    "partner-code": "Sky Business-107",
    "asset-id": "Sky Business-214",
    "nni-name": "London Brick Lane",
    "remote-nni-pe": "ar0-wifi.bllon",
    "rfs-date": "09-nov-2022",
    "ports": [
        {"interface": "po1/1/1", "bearer-rate": 10, "circuit-id": "TIC-063340"},
        {"interface": "po1/1/2", "bearer-rate": 100, "circuit-id": "TIC-063340"},
    ],
}

interconnect_kwargs = {
    "requestType": "new",
    "serviceType": "interconnect",
    "body": interconnect_new_req_body,
}

response_6 = {"status": "success"}

interconnect_new_req_body_1 = {
    "partner-code": "Sky Business-107",
    "asset-id": "Sky Business-214",
    "nni-name": "London Brick Lane",
    "remote-nni-pe": "ar0-wifi.bllon",
    "remote-nni-lag": "lag 10",
    "rfs-date": "09-nov-2022",
    "ports": [
        {"interface": "po1/1/1", "bearer-rate": 10, "circuit-id": "TIC-063340"},
        {"interface": "po1/1/2", "bearer-rate": 100, "circuit-id": "TIC-063340"},
    ],
}


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.oauth.token_generator", return_value=access_token_wholesale)
@patch("connectors.core.services.inca.connector.IncaService.update_wholesale_details", return_value=response_6)
@patch("connectors.webserver.inca.tasks.update.validate_json_request_payload", return_value=(False, response_6))
def test_update_wholesale_details_case20(put_mocked, mock_post, mock_oauth, validation_mock):
    """
    Verify success scenario when remote-nni-lag is given and multiple interfaces are given
    """
    output = update.update_wholesale_details(
        body=interconnect_new_req_body_1, requestType="new", serviceType="interconnect"
    )
    assert output == response_6


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.oauth.token_generator", return_value=access_token_wholesale)
@patch("connectors.webserver.inca.tasks.update.update_wholesale_details", return_value=response_err_6)
def test_update_wholesale_details_case21(put_mocked, mock_post, mock_oauth):
    """
    Verify failure scenario when remote-nni-lag is not given and multiple interfaces are given
    """
    output = update.update_wholesale_details(**interconnect_kwargs)
    assert output == response_err_6


def test_validate_item_spark_ref_failure():
    """
    Test sparkReference is conditional mandatory
    """
    errors = []
    circuit_details = {
        "circuitId": "OGHP33333333",
        "configStatus": "inprogress",
        "circuitState": "Ready-For-Config",
        "orderRef": "BPM-123TEST",
    }
    update._validate_item(circuit_details, errors)
    assert errors == [
        {
            "code": "ERR-011-999-0001",
            "message": (
                "sparkReference must be provided for circuit OGHP33333333 "
                "as configStatus is inprogress and circuitState is Ready-For-Config"
            ),
        }
    ]


def test_validate_item_spark_ref_success():
    """
    Test sparkReference is conditional mandatory
    """
    errors = []
    circuit_details = {"circuitId": "OGHP33333333", "configStatus": "failure", "circuitState": "Ready-For-Config"}
    update._validate_item(circuit_details, errors)
    assert not errors


@patch("connectors.webserver.inca.tasks.update._validate_gea_cease")
@patch("connectors.webserver.inca.tasks.update._validate_item")
def test_validate_inca_update_data_gea_cease(validate_item_mock, validate_gea_cease_mock):
    """
    Test when circuitState is "GEA-CEASE"
    """
    data = {
        "type": "gea",
        "body": {
            "circuitDetails": [
                {
                    "circuitCeaseOrderRef": "OGHP64783778-3456789-CEASE",
                    "circuitId": "OGHP00806248",
                    "configStatus": "failure",
                    "circuitState": "GEA-CEASE",
                }
            ]
        },
    }
    assert _validate_inca_update_data(**data) == (True, [], data)
    validate_item_mock.assert_not_called()
    validate_gea_cease_mock.assert_called_once_with(data["body"]["circuitDetails"][0], [])


@patch("connectors.webserver.inca.tasks.update._validate_gea_cease")
@patch("connectors.webserver.inca.tasks.update._validate_item")
def test_validate_inca_update_data(validate_item_mock, validate_gea_cease_mock):
    """
    Test when circuitState is not "GEA-CEASE"
    """
    data = {
        "type": "gea",
        "body": {
            "circuitDetails": [
                {
                    "circuitId": "OGHP14062301",
                    "configStatus": "success",
                    "circuitState": "Ready-For-Config",
                    "testRef": "test11111",
                    "configDate": "11/5/2024",
                    "sparkReference": "CHG1234565",
                }
            ]
        },
    }
    assert _validate_inca_update_data(**data) == (True, [], data)
    validate_item_mock.assert_called_once_with(data["body"]["circuitDetails"][0], [])
    validate_gea_cease_mock.assert_not_called()


def test_validate_gea_cease_success_case_1():
    """
    Test _validate_gea_cease success case when
    configStatus is success
    """
    errors = []
    circuit_details = {
        "circuitCeaseOrderRef": "OGHP64783778-3456789-CEASE",
        "circuitId": "OGHP00806248",
        "configStatus": "success",
        "orCeaseDate": "11/5/2021",
        "configCeaseDate": "11/5/2021",
        "circuitState": "GEA-CEASE",
        "orCeaseRef": "94262CG",
        "sparkReference": "CHG12345672",
    }
    _validate_gea_cease(circuit_details, errors)
    assert not errors


def test_validate_gea_cease_success_case_2():
    """
    Test _validate_gea_cease success case when
    configStatus is failure
    """
    errors = []
    circuit_details = {
        "circuitCeaseOrderRef": "OGHP64783778-3456789-CEASE",
        "circuitId": "OGHP00806248",
        "configStatus": "failure",
        "circuitState": "GEA-CEASE",
    }
    _validate_gea_cease(circuit_details, errors)
    assert not errors


def test_validate_gea_cease_missing_args():
    """
    Test _validate_gea_cease failure case when
    mandatory args are missing
    """
    errors = []
    circuit_details = {
        "circuitId": "OGHP00806248",
        "configStatus": "success",
        "circuitState": "GEA-CEASE",
    }
    _validate_gea_cease(circuit_details, errors)
    assert errors == [
        {
            "code": "ERR-011-999-0003",
            "message": (
                "sparkReference must be provided for GEA-CEASE circuit " "OGHP00806248 when configStatus is success."
            ),
        },
        {
            "code": "ERR-011-999-0004",
            "message": (
                "configCeaseDate must be provided for GEA-CEASE circuit " "OGHP00806248 when configStatus is success."
            ),
        },
        {
            "code": "ERR-011-999-0005",
            "message": "orCeaseDate must be provided for GEA-CEASE circuit OGHP00806248 when configStatus is success.",
        },
        {
            "code": "ERR-011-999-0006",
            "message": "orCeaseRef must be provided for GEA-CEASE circuit OGHP00806248 when configStatus is success.",
        },
        {
            "code": "ERR-011-999-0007",
            "message": (
                "circuitCeaseOrderRef must be provided for GEA-CEASE circuit OGHP00806248 "
                "when configStatus is success."
            ),
        },
    ]


def test_validate_gea_cease_invalid_config_status():
    """
    Test _validate_gea_cease failure case when
    configStatus is invalid
    """
    errors = []
    circuit_details = {
        "circuitId": "OGHP00806248",
        "configStatus": "inprogress",
        "circuitState": "GEA-CEASE",
    }
    _validate_gea_cease(circuit_details, errors)
    assert errors == [
        {
            "code": "ERR-011-999-0008",
            "message": "configStatus must be either 'failure' or 'success' for GEA-CEASE circuit OGHP00806248 ",
        }
    ]


@patch("connectors.webserver.inca.tasks.update.IncaService")
@patch("connectors.webserver.inca.tasks.update.token_generator")
def test_update_device_decommissioned(mock_oauth, mock_inca_service):
    """
    Tests device decommissioned update state for IncaService
    """
    mock_inca_service_object = mock_inca_service.return_value
    mock_inca_service_object.update_inca_device_decommissioned = Mock(return_value={"status": "SUCCESS"})
    output = update.update_device_decommissioned(
        type="deviceDecommissioned", body={"hostname": "me0.bllab.isp.sky.com"}
    )
    assert output == {"status": "SUCCESS"}
