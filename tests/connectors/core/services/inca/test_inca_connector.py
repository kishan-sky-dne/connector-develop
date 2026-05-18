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
from unittest.mock import ANY, patch

# Third Party Library
import pytest

# DNE Library
from connectors.core.services.inca.connector import IncaService
from connectors.core.utils.exceptions import RestUtilityException
from connectors.core.utils.helpers import generic_secret

secret = generic_secret()

access_token = secret
kwargs = {"type": "gea", "state": "config-ready", "limit": 90, "url": "test"}
headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}",
}
kwargs["headers"] = headers
inca_response = {
    "items": [
        {
            "mdf_id": "EACHE",
            "lluc": "LLUC30001427",
            "l2s_id": "BAAITU",
            "sw_name": "me3.eache",
            "sw_port": "1-1-1",
            "or_cablelink_reference": "OGHP65699258",
            "metro_sdp": 13196,
            "cablelink_size": 10,
            "cablelink_type": "NGA2",
            "spark_ref": None,
        },
        {
            "mdf_id": "MRBUX",
            "lluc": "LLUC10001538",
            "l2s_id": "BAACRF",
            "sw_name": "me0.mrbux",
            "sw_port": "0-3-37",
            "or_cablelink_reference": "OGHP63837190",
            "metro_sdp": 13884,
            "cablelink_size": 1,
            "cablelink_type": "NGA1",
            "spark_ref": "CHG0094609",
        },
        {
            "mdf_id": "ESTNT",
            "lluc": "LLUC40003318",
            "l2s_id": "BAAFCF",
            "sw_name": "me0.estnt",
            "sw_port": "0-1-3",
            "or_cablelink_reference": "OGHP63583122",
            "metro_sdp": 13369,
            "cablelink_size": 10,
            "cablelink_type": "NGA1",
            "spark_ref": "CHG0094609",
        },
        {
            "mdf_id": "LVWID",
            "lluc": "LLUC70001215",
            "l2s_id": "BAACKQ",
            "sw_name": "me0.lvwid",
            "sw_port": "0-1-2",
            "or_cablelink_reference": "OGHP64782896",
            "metro_sdp": 12987,
            "cablelink_size": 10,
            "cablelink_type": "NGA1",
            "spark_ref": "CHG0094609",
        },
        {
            "mdf_id": "MYHHL",
            "lluc": "LLUC40001876",
            "l2s_id": "BAACDU",
            "sw_name": "as103.myhhl",
            "sw_port": "1/1/8",
            "or_cablelink_reference": "OGHP64132084",
            "metro_sdp": 12617,
            "cablelink_size": 1,
            "cablelink_type": "NGA1",
            "spark_ref": "CHG0094609",
        },
        {
            "mdf_id": "STWEYMH",
            "lluc": "LLUC80003436",
            "l2s_id": "BAABZA",
            "sw_name": "as100.stweymh",
            "sw_port": "1/1/10",
            "or_cablelink_reference": "OGHP45409807",
            "metro_sdp": 10032,
            "cablelink_size": 1,
            "cablelink_type": "NGA1",
            "spark_ref": "CHG0094609",
        },
        {
            "mdf_id": "NDGIL",
            "lluc": "LLUC60001287",
            "l2s_id": "BAAGMF",
            "sw_name": "me0.ndgil",
            "sw_port": "0-3-0",
            "or_cablelink_reference": "OGHP44869499",
            "metro_sdp": 12938,
            "cablelink_size": 10,
            "cablelink_type": "NGA2",
            "spark_ref": "CHG0094609",
        },
        {
            "mdf_id": "SDSFRD",
            "lluc": "LLUC30001239",
            "l2s_id": "BAAFUG",
            "sw_name": "me0.sdsfrd",
            "sw_port": "0-2-3",
            "or_cablelink_reference": "OGHP44517607",
            "metro_sdp": 13939,
            "cablelink_size": 10,
            "cablelink_type": "NGA1",
            "spark_ref": "CHG0094609",
        },
        {
            "mdf_id": "THDK",
            "lluc": "LLUC60001626",
            "l2s_id": "BAAHQQ",
            "sw_name": "me0.thdk",
            "sw_port": "0-2-3",
            "or_cablelink_reference": "OGHP43931099",
            "metro_sdp": 13516,
            "cablelink_size": 10,
            "cablelink_type": "NGA2",
            "spark_ref": "CHG0094609",
        },
        {
            "mdf_id": "EMRUSHD",
            "lluc": "LLUC30001435",
            "l2s_id": "BAABDR",
            "sw_name": "me0.emrushd",
            "sw_port": "0-2-3",
            "or_cablelink_reference": "OGHP44662645",
            "metro_sdp": 13438,
            "cablelink_size": 10,
            "cablelink_type": "NGA1",
            "spark_ref": "CHG0094609",
        },
        {
            "mdf_id": "LSCHER",
            "lluc": "LLUC40001513",
            "l2s_id": "BAADPD",
            "sw_name": "me1.lscher",
            "sw_port": "0-3-1",
            "or_cablelink_reference": "OGHP44516939",
            "metro_sdp": 14084,
            "cablelink_size": 10,
            "cablelink_type": "NGA1",
            "spark_ref": "CHG0094609",
        },
        {
            "mdf_id": "SMSFD",
            "lluc": "LLUC80004352",
            "l2s_id": "BAACFH",
            "sw_name": "as101.smsfd",
            "sw_port": "1/1/10",
            "or_cablelink_reference": "OGHP45409393",
            "metro_sdp": 10765,
            "cablelink_size": 1,
            "cablelink_type": "NGA1",
            "spark_ref": "CHG0094609",
        },
        {
            "mdf_id": "NELF",
            "lluc": "LLUC50001857",
            "l2s_id": "BAACVA",
            "sw_name": "me1.nelf",
            "sw_port": "0-3-23",
            "or_cablelink_reference": "OGHP63692160",
            "metro_sdp": 13330,
            "cablelink_size": 1,
            "cablelink_type": "NGA1",
            "spark_ref": "CHG0094609",
        },
        {
            "mdf_id": "MYHSF",
            "lluc": "LLUC70001414",
            "l2s_id": "BAACDZ",
            "sw_name": "me0.myhsf",
            "sw_port": "0-3-38",
            "or_cablelink_reference": "OGHP63692130",
            "metro_sdp": 13912,
            "cablelink_size": 1,
            "cablelink_type": "NGA1",
            "spark_ref": "CHG0094609",
        },
        {
            "mdf_id": "WNLEO",
            "lluc": "LLUC20003350",
            "l2s_id": "BAADCC",
            "sw_name": "as100.wnleo",
            "sw_port": "1/1/8",
            "or_cablelink_reference": "OGHP64724816",
            "metro_sdp": 10146,
            "cablelink_size": 1,
            "cablelink_type": "NGA1",
            "spark_ref": "CHG0094609",
        },
        {
            "mdf_id": "SDWTRLV",
            "lluc": "LLUC60001416",
            "l2s_id": "BAAEFR",
            "sw_name": "me0.sdwtrlv",
            "sw_port": "0-3-42",
            "or_cablelink_reference": "OGHP65628858",
            "metro_sdp": 14060,
            "cablelink_size": 1,
            "cablelink_type": "NGA1",
            "spark_ref": "CTASK9999999",
        },
    ],
    "first": {"$ref": "https://apextest2.sns.sky.com/apex/incaREST/v0/GEAReadyForConfigJSON"},
}
gea_response = {
    "items": [
        {
            "cablelink_size": 10,
            "l2s_id": "BAAITU",
            "or_cablelink_reference": "OGHP65699258",
            "spark_ref": None,
            "sw_name": "me3.eache",
            "sw_port": "1-1-1",
        },
        {
            "cablelink_size": 1,
            "l2s_id": "BAACRF",
            "or_cablelink_reference": "OGHP63837190",
            "spark_ref": "CHG0094609",
            "sw_name": "me0.mrbux",
            "sw_port": "0-3-37",
        },
        {
            "cablelink_size": 10,
            "l2s_id": "BAAFCF",
            "or_cablelink_reference": "OGHP63583122",
            "spark_ref": "CHG0094609",
            "sw_name": "me0.estnt",
            "sw_port": "0-1-3",
        },
        {
            "cablelink_size": 10,
            "l2s_id": "BAACKQ",
            "or_cablelink_reference": "OGHP64782896",
            "spark_ref": "CHG0094609",
            "sw_name": "me0.lvwid",
            "sw_port": "0-1-2",
        },
        {
            "cablelink_size": 1,
            "l2s_id": "BAACDU",
            "or_cablelink_reference": "OGHP64132084",
            "spark_ref": "CHG0094609",
            "sw_name": "as103.myhhl",
            "sw_port": "1/1/8",
        },
        {
            "cablelink_size": 1,
            "l2s_id": "BAABZA",
            "or_cablelink_reference": "OGHP45409807",
            "spark_ref": "CHG0094609",
            "sw_name": "as100.stweymh",
            "sw_port": "1/1/10",
        },
        {
            "cablelink_size": 10,
            "l2s_id": "BAAGMF",
            "or_cablelink_reference": "OGHP44869499",
            "spark_ref": "CHG0094609",
            "sw_name": "me0.ndgil",
            "sw_port": "0-3-0",
        },
        {
            "cablelink_size": 10,
            "l2s_id": "BAAFUG",
            "or_cablelink_reference": "OGHP44517607",
            "spark_ref": "CHG0094609",
            "sw_name": "me0.sdsfrd",
            "sw_port": "0-2-3",
        },
        {
            "cablelink_size": 10,
            "l2s_id": "BAAHQQ",
            "or_cablelink_reference": "OGHP43931099",
            "spark_ref": "CHG0094609",
            "sw_name": "me0.thdk",
            "sw_port": "0-2-3",
        },
        {
            "cablelink_size": 10,
            "l2s_id": "BAABDR",
            "or_cablelink_reference": "OGHP44662645",
            "spark_ref": "CHG0094609",
            "sw_name": "me0.emrushd",
            "sw_port": "0-2-3",
        },
        {
            "cablelink_size": 10,
            "l2s_id": "BAADPD",
            "or_cablelink_reference": "OGHP44516939",
            "spark_ref": "CHG0094609",
            "sw_name": "me1.lscher",
            "sw_port": "0-3-1",
        },
        {
            "cablelink_size": 1,
            "l2s_id": "BAACFH",
            "or_cablelink_reference": "OGHP45409393",
            "spark_ref": "CHG0094609",
            "sw_name": "as101.smsfd",
            "sw_port": "1/1/10",
        },
        {
            "cablelink_size": 1,
            "l2s_id": "BAACVA",
            "or_cablelink_reference": "OGHP63692160",
            "spark_ref": "CHG0094609",
            "sw_name": "me1.nelf",
            "sw_port": "0-3-23",
        },
        {
            "cablelink_size": 1,
            "l2s_id": "BAACDZ",
            "or_cablelink_reference": "OGHP63692130",
            "spark_ref": "CHG0094609",
            "sw_name": "me0.myhsf",
            "sw_port": "0-3-38",
        },
        {
            "cablelink_size": 1,
            "l2s_id": "BAADCC",
            "or_cablelink_reference": "OGHP64724816",
            "spark_ref": "CHG0094609",
            "sw_name": "as100.wnleo",
            "sw_port": "1/1/8",
        },
        {
            "cablelink_size": 1,
            "l2s_id": "BAAEFR",
            "or_cablelink_reference": "OGHP65628858",
            "spark_ref": "CTASK9999999",
            "sw_name": "me0.sdwtrlv",
            "sw_port": "0-3-42",
        },
    ]
}


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth.token_generator")
def test_get_gea_details(mock_token_generator, get_mocked):
    """
    Test to check the functionality of get_inca_details()
    """
    inst_inca = IncaService()
    get_mocked.return_value = inca_response
    output = inst_inca.get_details(**kwargs)
    assert output == inca_response


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth.token_generator")
def test_get_gea_details_case1(mock_token_generator, get_mocked):
    """
    Test to check the functionality of get_inca_details()
    """
    inst_inca = IncaService()
    get_mocked.return_value = {"items": []}
    output = inst_inca.get_details(**kwargs)
    assert output == {"items": []}


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth.token_generator")
def test_get_gea_details_exception(mock_token_generator, get_mocked):
    """
    Test to check the functionality of get_inca_details()
    """
    inst_inca = IncaService()
    get_mocked.side_effect = RestUtilityException("url issue", Response1())
    with pytest.raises(RestUtilityException):
        inst_inca.get_details(**kwargs)


# test Nexa rest
post_resp = {"result": "OK", "id": "1234"}
nexa_body = {
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
nexa_body_2 = {
    "circuitDetails": [
        {
            "circuitId": "OGHP33333333",
            "configStatus": "inprogress",
            "circuitState": "Ready-For-Config",
            "orderRef": "BPM-123456",
        },
        {
            "circuitId": "OGHP63837190",
            "configStatus": "failure",
            "sparkReference": "CTASK1234578",
            "configDate": "9/3/2021",
            "comments": "dummy",
            "testRef": "dummy",
        },
        {
            "circuitId": "OGHP64724816",
            "configStatus": "inprogress",
            "sparkReference": "CHG123458812",
            "orderRef": "BPM-123TEST",
            "circuitState": "Ready-For-Config",
        },
    ]
}
nexa_body_cease = {
    "circuitDetails": [
        {
            "circuitCeaseOrderRef": "OGHP00001496-100000-CEASE",
            "circuitId": "OGHP00806248",
            "configStatus": "success",
            "orCeaseDate": "11/11/2024",
            "configCeaseDate": "14/11/2021",
            "circuitState": "GEA-CEASE",
            "orCeaseRef": "94262CG",
            "sparkReference": "CHG12345672",
            "ceaseSubmittedDate": "4/11/2024",
        }
    ]
}
access_token_nexa = "xyz"
headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token_nexa}",
}
kwargs_nexa = {
    "type": "gea",
    "body": nexa_body,
    "url": "apex/nexaREST/v0/message",
    "headers": headers,
    "job_id": "GC-1234",
}
kwargs_nexa_2 = {
    "type": "gea",
    "body": nexa_body_2,
    "url": "apex/nexaREST/v0/message",
    "headers": headers,
    "job_id": "GC-1234",
}
kwargs_nexa_cease = {
    "type": "gea",
    "body": nexa_body_cease,
    "url": "apex/nexaREST/v0/message",
    "headers": headers,
    "job_id": "GC-1234",
}
get_resp1 = {"results": "No new message."}
get_resp2 = {
    "id": "1234",
    "results": [
        {"or_cablelink_reference": "OGHP63837190", "response": "OK"},
        {"or_cablelink_reference": "OGHP64724816", "response": "OK"},
    ],
}
get_resp3 = {
    "id": "1234",
    "results": [
        {"or_cablelink_reference": "OGHP63837190", "response": "already exist"},
        {"or_cablelink_reference": "OGHP64724816", "response": "Ticket issue"},
    ],
}
get_resp4 = {
    "id": "1234",
    "results": [
        {"or_cablelink_reference": "OGHP63837190", "response": "already exist"},
        {"or_cablelink_reference": "OGHP64724816", "response": "OK"},
    ],
}
job_status = {
    "jobId": "GC-1234",
    "metadata": {
        "circuitsStatus": [
            {"circuitId": "OGHP63837190", "status": "success"},
            {"circuitId": "OGHP64724816", "status": "success"},
        ]
    },
    "status": "SUCCESS",
}
job_status_failure = {
    "jobId": "GC-1234",
    "errorCategory": "FAILED",
    "errors": [
        {"code": "ERR-011-999-0004", "message": "State update failed for gea circuitId OGHP63837190: already exist"},
        {"code": "ERR-011-999-0004", "message": "State update failed for gea circuitId OGHP64724816: Ticket issue"},
    ],
    "metadata": {
        "circuitsStatus": [
            {"circuitId": "OGHP63837190", "status": "failure"},
            {"circuitId": "OGHP64724816", "status": "failure"},
        ]
    },
    "status": "FAILURE",
}
job_status_partial = {
    "jobId": "GC-1234",
    "errorCategory": "FAILED",
    "errors": [
        {"code": "ERR-011-999-0004", "message": "State update failed for gea circuitId OGHP63837190: already exist"},
    ],
    "metadata": {
        "circuitsStatus": [
            {"circuitId": "OGHP63837190", "status": "failure"},
            {"circuitId": "OGHP64724816", "status": "success"},
        ]
    },
    "status": "PARTIAL-SUCCESS",
}
post_resp_negate = {"result": "error while generating jobId"}
post_resp_negate1 = {"result": "too many attempts"}


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_inca_type_details_case1(mock_token_generator, post_mocked):
    """
    Test to check the functionality of update_inca_type_details()
    """
    inst_inca = IncaService()
    post_mocked.return_value = post_resp
    output = inst_inca.update_inca_type_details(**kwargs_nexa)
    assert output == {"jobId": "GC-1234"}


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_inca_type_details_case2(mock_token_generator, post_mocked):
    """
    Test to check the functionality of update_inca_type_details()
    """
    inst_inca = IncaService()
    post_mocked.return_value = post_resp_negate
    output = inst_inca.update_inca_type_details(**kwargs_nexa)
    assert output == {
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-011-999-0003",
                "message": f"Failed to generate jobId with error: error while generating jobId",
            }
        ],
    }


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_inca_type_details_case3(mock_token_generator, post_mocked):
    """
    Test to check the functionality of update_inca_type_details()
    """
    inst_inca = IncaService()
    post_mocked.return_value = post_resp_negate1
    output = inst_inca.update_inca_type_details(**kwargs_nexa)
    assert output == {
        "errorCategory": "RETRY",
        "errors": [
            {
                "code": "ERR-011-999-0003",
                "message": f"Failed to generate jobId with error: too many attempts",
            }
        ],
    }


class Response1:
    def __init__(self):
        self.status_code = 404


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_inca_type_details_case4(mock_token_generator, post_mocked):
    """
    Test to check Exception the functionality of update_inca_type_details()
    """
    inst_inca = IncaService()
    post_mocked.side_effect = RestUtilityException("url issue", Response1())
    with pytest.raises(RestUtilityException):
        inst_inca.update_inca_type_details(**kwargs_nexa)


nexa_body_1 = {
    "circuitDetails": [
        {
            "circuitId": "OGHP63837190",
            "configStatus": "success",
            "configDate": "9/3/2021",
            "circuit_state": "Ready-For-Config",
            "testRef": "25486CG",
            "comments": "OR Testing success with 25486CG",
        },
        {
            "circuitId": "OGHP64724816",
            "configStatus": "success",
            "configDate": "9/3/2021",
            "circuit_state": "Ready-For-Config",
            "testRef": "25486CG",
            "comments": "OR Testing success with 25486CG",
        },
    ]
}

kwargs_nexa_1 = {
    "type": "gea",
    "body": nexa_body_1,
    "url": "apex/nexaREST/v0/message",
    "headers": headers,
    "job_id": "GC-1234",
}

post_resp_negate_2 = {"result": "error while generating jobId"}


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_inca_type_details_case5(mock_token_generator, post_mocked):
    """
    Test to check the functionality of update_inca_type_details()
    """
    inst_inca = IncaService()
    post_mocked.return_value = post_resp
    output = inst_inca.update_inca_type_details(**kwargs_nexa_1)
    assert output == {"jobId": "GC-1234"}


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_inca_type_details_case6(mock_token_generator, post_mocked):
    """
    Test to check the functionality of update_inca_type_details()
    """
    inst_inca = IncaService()
    post_mocked.return_value = post_resp_negate_2
    output = inst_inca.update_inca_type_details(**kwargs_nexa_1)
    assert output == {
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-011-999-0003",
                "message": "Failed to generate jobId with error: error while generating jobId",
            }
        ],
    }


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_inca_type_details_case7(mock_token_generator, post_mocked):
    """
    Test to check the functionality of update_inca_type_details()
    """
    inst_inca = IncaService()
    post_mocked.return_value = post_resp_negate1
    output = inst_inca.update_inca_type_details(**kwargs_nexa_1)
    assert output == {
        "errorCategory": "RETRY",
        "errors": [
            {
                "code": "ERR-011-999-0003",
                "message": "Failed to generate jobId with error: too many attempts",
            }
        ],
    }


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth.token_generator")
def test_get_inca_update_status_case1(mock_token_generator, get_mocked):
    """
    Test to check the functionality of update_inca_type_details()
    """
    inst_inca = IncaService()
    get_mocked.return_value = get_resp1
    output = inst_inca.get_inca_update_status(**kwargs_nexa)
    assert output == {"jobId": "GC-1234", "status": "IN-PROGRESS"}


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth.token_generator")
def test_get_inca_update_status_case2(mock_token_generator, get_mocked):
    """
    Test to check the functionality of update_inca_type_details()
    """
    inst_inca = IncaService()
    get_mocked.return_value = get_resp2
    output = inst_inca.get_inca_update_status(**kwargs_nexa)
    assert output == job_status


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth.token_generator")
def test_get_inca_update_status_exception(mock_token_generator, get_mocked):
    """
    Test to check the functionality of update_inca_type_details()
    """
    inst_inca = IncaService()
    get_mocked.side_effect = RestUtilityException("url issue", Response1())
    with pytest.raises(RestUtilityException):
        inst_inca.get_inca_update_status(**kwargs_nexa)


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth.token_generator")
def test_get_inca_update_status_case3(mock_token_generator, get_mocked):
    """
    Test to check the functionality of update_inca_type_details()
    """
    inst_inca = IncaService()
    get_mocked.return_value = get_resp3
    output = inst_inca.get_inca_update_status(**kwargs_nexa)
    assert output == job_status_failure


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth.token_generator")
def test_get_inca_update_status_case4(mock_token_generator, get_mocked):
    """
    Test to check the functionality of update_inca_type_details()
    """
    inst_inca = IncaService()
    get_mocked.return_value = get_resp4
    output = inst_inca.get_inca_update_status(**kwargs_nexa)
    assert output == job_status_partial


get_resp5 = {"error": "statusDetail contains invalid data"}


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth.token_generator")
def test_get_inca_update_status_case5(mock_token_generator, get_mocked):
    """
    Test to check the functionality of update_inca_type_details()
    """
    inst_inca = IncaService()
    get_mocked.return_value = get_resp5
    output = inst_inca.get_inca_update_status(**kwargs_nexa)
    assert output == {
        "jobId": "GC-1234",
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-011-999-0001",
                "message": f"Request Validation failed for jobId GC-1234 with error: circuitDetails contains "
                f"invalid data",
            }
        ],
    }


get_resp6 = {"results": "statusDetail contains invalid data"}


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth.token_generator")
def test_get_inca_update_status_case6(mock_token_generator, get_mocked):
    """
    Test to check the functionality of update_inca_type_details()
    """
    inst_inca = IncaService()
    get_mocked.return_value = get_resp6
    output = inst_inca.get_inca_update_status(**kwargs_nexa)
    assert output == {
        "jobId": "GC-1234",
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-011-999-0001",
                "message": f"Request Validation failed for jobId GC-1234 with error: statusDetail contains "
                f"invalid data",
            }
        ],
    }


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth.token_generator")
def test_get_inca_update_status_case7(mock_token_generator, get_mocked):
    """
    Test when INCA response is not a dictionary
    """
    inst_inca = IncaService()
    get_mocked.return_value = "dummy string response"
    output = inst_inca.get_inca_update_status(**kwargs_nexa)
    assert output == {
        "jobId": "GC-1234",
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [{"code": "ERR-011-999-0001", "message": "Unexpected response from INCA: dummy string response"}],
    }


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth.token_generator")
def test_get_inca_update_status_case8(mock_token_generator, get_mocked):
    """
    Test when INCA response is not a dictionary
    """
    inst_inca = IncaService()
    get_mocked.return_value.text = "dummy string in response.text"
    output = inst_inca.get_inca_update_status(**kwargs_nexa)
    assert output == {
        "jobId": "GC-1234",
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {"code": "ERR-011-999-0001", "message": "Unexpected response from INCA: dummy string in response.text"}
        ],
    }


inca_result_inprogress = {"results": "no new message."}
gea_inprogress_job_id = {"job_id": "GC-12345"}


def test_job_state_response_case1():
    """
    Test to check the functionality of job_state_response()
    """
    inst_inca = IncaService()
    assert inst_inca._job_state_response(inca_result_inprogress, gea_inprogress_job_id) == {
        "jobId": gea_inprogress_job_id["job_id"],
        "status": "IN-PROGRESS",
    }


put_resp_ok = {"result": "ok"}
new_switch_response1 = {"result": "No matching request found"}
new_switch_response2 = {"result": "New Switch Request status does not permit RFS Update"}
new_switch_response3 = {"result": "other"}


class NewSwitchResponse1:
    def __init__(self):
        self.status_code = 409
        self._content = json.dumps(new_switch_response1)


class NewSwitchResponse2:
    def __init__(self):
        self.status_code = 409
        self._content = json.dumps(new_switch_response2)


class NewSwitchResponse3:
    def __init__(self):
        self.status_code = 409
        self._content = json.dumps(new_switch_response3)


@patch("connectors.core.utils.rest_api_utility.RestUtility.put")
@patch("connectors.core.utils.oauth.token_generator")
def test_new_metro_switch_inca_update_status(mock_token_generator, put_mocked):
    """
    Test to check the functionality of new_metro_switch_inca_update_status()
    case 1:
    Success Scenario: result is "ok"
    case 2:
    Record does not exist: result contains "no matching request found"
    case 3:
    permission denied: result contains "status does not permit rfs update"
    """
    inst_inca = IncaService()
    # result is "ok"
    put_mocked.return_value = put_resp_ok
    output = inst_inca.new_metro_switch_inca_update_status(
        {"body": {"hostname": "me0.callbr"}, "url": "", "type": "newMetroSwitch", "headers": headers}
    )
    assert output == {"status": "SUCCESS", "result": "OK", "metadata": {"hostname": "me0.callbr"}}
    # result contains "no matching request found"
    put_mocked.side_effect = RestUtilityException("Invalid request", NewSwitchResponse1())
    output = inst_inca.new_metro_switch_inca_update_status(
        {"body": {"hostname": "me0.callbr"}, "url": "", "type": "newMetroSwitch", "headers": headers}
    )
    assert output == {
        "status": "FAILURE",
        "result": "No matching request found",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-011-999-0007",
                "message": "No matching request found for hostname me0.callbr",
            }
        ],
        "metadata": {"hostname": "me0.callbr"},
    }
    # result contains "status does not permit rfs update"
    put_mocked.side_effect = RestUtilityException("Invalid request", NewSwitchResponse2())
    # put_mocked.return_value = False, 409, {"result": "status does not permit rfs update"}, "error"
    output = inst_inca.new_metro_switch_inca_update_status(
        {"body": {"hostname": "me0.callbr"}, "url": "", "type": "newMetroSwitch", "headers": headers}
    )
    assert output == {
        "status": "FAILURE",
        "result": "New Switch Request status does not permit RFS Update",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-011-999-0008",
                "message": "New Switch Request status does not permit RFS Update for hostname me0.callbr",
            }
        ],
        "metadata": {"hostname": "me0.callbr"},
    }
    # ANY other generic error scenario"
    put_mocked.side_effect = RestUtilityException("Invalid request", NewSwitchResponse3())
    # put_mocked.return_value = False, 409, {"result": "Blah Blah"}, "some blah..error"
    output = inst_inca.new_metro_switch_inca_update_status(
        {"body": {"hostname": "me0.callbr"}, "url": "", "type": "newMetroSwitch", "headers": headers}
    )
    assert output == {
        "status": "FAILURE",
        "result": "New Switch Request status failed",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-011-999-0009",
                "message": "New Switch Request status failed for hostname me0.callbr",
            }
        ],
        "metadata": {"hostname": "me0.callbr"},
    }


kwargs_wholesale_new_circuit = {
    "requestType": "new",
    "serviceType": "uni",
    "formatted_body": {
        "assetRef": "SKY-TEST-DNE-018",
        "plugUpFields": [
            {
                "plugUpSparkRef": "CHG1234567",
                "plugUpCompleteDate": "22-Sep-2022",
            }
        ],
        "testFields": [
            {
                "testingCHG": "CHG1234567",
                "ANIEngineer": "John",
                "testingResult": "PASS",
                "failureReason": None,
                "testingComments": None,
                "providerTestResult": "PASS",
                "providerTestResultComments": None,
            }
        ],
        "configFields": [{"configComplete": "22-Sep-2022"}],
    },
    "url": "apex/incaREST/v0/putWsalePlugUpRFS",
}


@patch("connectors.core.utils.rest_api_utility.RestUtility.put")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_wholesale_details_case1(mock_token_generator, get_mocked):
    """
    Test to check the functionality of update_wholesale_details for requesttype-new success case
    """
    inst_inca = IncaService()
    get_mocked.return_value = {"result": "OK"}
    output = inst_inca.update_wholesale_details(**kwargs_wholesale_new_circuit)
    assert output == {"status": "SUCCESS"}


kwargs_wholesale_cease_circuit = {
    "serviceType": "uni",
    "requestType": "cease",
    "formatted_body": {
        "assetRef": "SKY-TEST-DNE-018",
        "plugUpFields": [
            {
                "plugUpSparkRef": "CHG1234567",
                "plugUpCompleteDate": "22-Sep-2022",
            }
        ],
        "testFields": [
            {
                "testingCHG": "CHG1234567",
                "ANIEngineer": "John",
                "testingResult": "PASS",
                "failureReason": None,
                "testingComments": None,
                "providerTestResult": "PASS",
                "providerTestResultComments": None,
            }
        ],
        "configFields": [{"configComplete": "22-Sep-2022"}],
    },
    "url": "apex/incaREST/v0/putWsaleCeaseComplete",
}


@patch("connectors.core.utils.rest_api_utility.RestUtility.put")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_wholesale_details_case2(mock_token_generator, get_mocked):
    """
    Test to check the functionality of update_wholesale_details request type cease success case
    """
    inst_inca = IncaService()
    get_mocked.return_value = {"result": "OK"}
    output = inst_inca.update_wholesale_details(**kwargs_wholesale_cease_circuit)
    assert output == {"status": "SUCCESS"}


kwargs_wholesale_update_circuit = {
    "requestType": "update",
    "serviceType": "uni",
    "formatted_body": {
        "assetRef": "SKY-TEST-DNE-018",
        "plugUpFields": [
            {
                "plugUpSparkRef": "CHG1234567",
                "plugUpCompleteDate": "22-Sep-2022",
            }
        ],
        "testFields": [
            {
                "testingCHG": "CHG1234567",
                "ANIEngineer": "John",
                "testingResult": "PASS",
                "failureReason": None,
                "testingComments": None,
                "providerTestResult": "PASS",
                "providerTestResultComments": None,
            }
        ],
        "configFields": [{"configComplete": "22-Sep-2022"}],
    },
    "url": "apex/incaREST/v0/putWsalePlugUpRFS",
}


@patch("connectors.core.utils.rest_api_utility.RestUtility.put")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_wholesale_details_case3(mock_token_generator, get_mocked):
    """
    Test to check the functionality of update_wholesale_details for request type-update success case
    """
    inst_inca = IncaService()
    get_mocked.return_value = {"result": "OK"}
    output = inst_inca.update_wholesale_details(**kwargs_wholesale_update_circuit)
    assert output == {"status": "SUCCESS"}


response2 = {
    "errorCategory": "FAILED",
    "errors": [{"code": "ERR-011-999-0007", "message": "No matching request found for given Asset ID"}],
    "status": "FAILED",
}

inca_response2 = {"result": "No matching request found"}


class Response2:
    def __init__(self):
        self.status_code = 409
        self._content = json.dumps(inca_response2)


@patch("connectors.core.utils.rest_api_utility.RestUtility.put")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_wholesale_details_case4(mock_token_generator, put_mocked):
    """
    Test to verify wholesale update Asset ID failure case
    """
    inst_inca = IncaService()
    put_mocked.side_effect = RestUtilityException("Invalid Asset ID", Response2())
    output = inst_inca.update_wholesale_details(**kwargs_wholesale_update_circuit)
    assert output == response2


response3 = {
    "errorCategory": "FAILED",
    "errors": [{"code": "ERR-011-999-0009", "message": "Wholesale request update is not allowed"}],
    "status": "FAILED",
}

inca_response3 = {"result": "Wholesale Request status does not permit Updates"}


class Response3:
    def __init__(self):
        self.status_code = 409
        self._content = json.dumps(inca_response3)


@patch("connectors.core.utils.rest_api_utility.RestUtility.put")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_wholesale_details_case5(mock_token_generator, put_mocked):
    """
    Test to verify wholesale update for Update is not allowed  failure case
    """
    inst_inca = IncaService()
    put_mocked.side_effect = RestUtilityException("url issue", Response3())
    output = inst_inca.update_wholesale_details(**kwargs_wholesale_update_circuit)
    assert output == response3


kwargs_new_partner = {
    "requestType": "new",
    "serviceType": "partner",
    "formatted_body": {
        "companyCode": "Sky Business-1",
        "companyName": "Sky Business-1",
        "parentCompanyName": "Sky Business-1",
        "vcidPrefix": 9899,
        "activeActive": "N",
        "activeActivePlus": "N",
        "hybrid": "N",
        "qualityOfService": 0,
        "UNIService": " Untagged",
        "comment": "Example partner details based on Sky Business",
        "uniqueNetworkCodeRangeStart": 700000,
        "uniqueNetworkCodeRangeEnd": 709999,
        "uniqueNetworkCodePosition": 2,
    },
    "url": "apex/incaREST/v0/postWsalePartner",
}
kwargs_cease_partner = {
    "requestType": "cease",
    "serviceType": "partner",
    "formatted_body": {"companyCode": "Sky Business-1", "ceaseDate": "31-dec-2022"},
    "url": "apex/incaREST/v0/retireWsalePartner",
}


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_wholesale_details_case6(mock_token_generator, get_mocked):
    """
    verify success case for servicetype:partener,RequestType:new
    """
    inst_inca = IncaService()
    get_mocked.return_value = {"result": "OK"}
    output = inst_inca.update_wholesale_details(**kwargs_new_partner)
    assert output == {"status": "SUCCESS"}


@patch("connectors.core.utils.rest_api_utility.RestUtility.put")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_wholesale_details_case7(mock_token_generator, get_mocked):
    """
    verify success  case for servicetype:partener,RequestType:cease
    """
    inst_inca = IncaService()
    get_mocked.return_value = {"result": "OK"}
    output = inst_inca.update_wholesale_details(**kwargs_cease_partner)
    assert output == {"status": "SUCCESS"}


response4 = {
    "errorCategory": "FAILED",
    "errors": [{"code": "ERR-011-999-0011", "message": "Partner code already exists in INCA"}],
    "status": "FAILED",
}
inca_response4 = {"result": "Company Code must be unique"}


class Response4:
    def __init__(self):
        self.status_code = 409
        self._content = json.dumps(inca_response4)


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_wholesale_details_case8(mock_token_generator, post_mocked):
    """
    verify when existing partner code is given for servicetype:partener,RequestType:new
    """
    inst_inca = IncaService()
    post_mocked.side_effect = RestUtilityException("Partner Code Already Exists", Response4())
    output = inst_inca.update_wholesale_details(**kwargs_new_partner)
    assert output == response4


response5 = {
    "errorCategory": "FAILED",
    "errors": [{"code": "ERR-011-999-0012", "message": "Partner name already exists in INCA"}],
    "status": "FAILED",
}
inca_response5 = {"result": "Company Name must be unique"}


class Response5:
    def __init__(self):
        self.status_code = 409
        self._content = json.dumps(inca_response5)


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_wholesale_details_case9(mock_token_generator, post_mocked):
    """
    verify when existing partner name is given for servicetype:partener,RequestType:new
    """
    inst_inca = IncaService()
    post_mocked.side_effect = RestUtilityException("Partner name Already Exists", Response5())
    output = inst_inca.update_wholesale_details(**kwargs_new_partner)
    assert output == response5


response6 = {
    "errorCategory": "FAILED",
    "errors": [{"code": "ERR-011-999-0015", "message": "Partner code is not found in INCA"}],
    "status": "FAILED",
}
inca_response6 = {"result": "Company Code not found"}


class Response6:
    def __init__(self):
        self.status_code = 409
        self._content = json.dumps(inca_response6)


@patch("connectors.core.utils.rest_api_utility.RestUtility.put")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_wholesale_details_case10(mock_token_generator, put_mocked):
    """
    verify wholesale for invalid partner is passed for servicetype:partener,RequestType:cease
    """
    inst_inca = IncaService()
    put_mocked.side_effect = RestUtilityException("Invalid Partner Code", Response6())
    output = inst_inca.update_wholesale_details(**kwargs_cease_partner)
    assert output == response6


wholesale_new_interconnect_args = {
    "requestType": "new",
    "serviceType": "interconnect",
    "formatted_body": {
        "partner-code": "SKY-TEST-DNE-102",
        "asset-id": "SKY-LNTW-FLDA-18",
        "nni-name": "London Bricklane",
        "remote-nni-pe": "ar0-wifi.bllon",
        "remote-nni-lag": "lag11",
        "rfs-date": "11-Jan-2023",
        "ports": [{"interface": "po1/1/2", "bearer-rate": "10", "circuit-id": "TIC-063341"}],
    },
    "url": "apex/incaREST/v0/postWsaleNNI",
}
wholesale_update_interconnect_args = {
    "requestType": "update",
    "serviceType": "interconnect",
    "formatted_body": {
        "partner-code": "SKY-TEST-DNE-102",
        "asset-id": "SKY-LNTW-FLDA-18",
        "remote-nni-pe": "ar0-wifi.bllon",
        "remote-nni-lag": "lag11",
        "rfs-date": "11-Feb-2023",
        "ports": [{"interface": "po1/1/2", "bearer-rate": "10", "circuit-id": "TIC-063341"}],
    },
    "url": "apex/incaREST/v0/putWsaleNNI",
}
wholesale_cease_interconnect_args = {
    "requestType": "cease",
    "serviceType": "interconnect",
    "formatted_body": {"asset-id": "SKY-LNTW-FLDA-102", "cease-date": "12-Oct-2022"},
    "url": "apex/incaREST/v0/retireWsaleNNI",
}


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_wholesale_details_case12(mock_token_generator, get_mocked):
    """
    verify success case for servicetype:interconnect,RequestType:new
    """
    inst_inca = IncaService()
    get_mocked.return_value = {"result": "OK"}
    output = inst_inca.update_wholesale_details(**wholesale_new_interconnect_args)
    assert output == {"status": "SUCCESS"}


@patch("connectors.core.utils.rest_api_utility.RestUtility.put")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_wholesale_details_case13(mock_token_generator, get_mocked):
    """
    Test to check the functionality of update_wholesale_details for
    requesttype-update sericetype-interconnect success case
    """
    inst_inca = IncaService()
    get_mocked.return_value = {"result": "OK"}
    output = inst_inca.update_wholesale_details(**wholesale_update_interconnect_args)
    assert output == {"status": "SUCCESS"}


@patch("connectors.core.utils.rest_api_utility.RestUtility.put")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_wholesale_details_case14(mock_token_generator, get_mocked):
    """
    Test to check the functionality of update_wholesale_details for
    requesttype-cease sericetype-interconnect success case
    """
    inst_inca = IncaService()
    get_mocked.return_value = {"result": "OK"}
    output = inst_inca.update_wholesale_details(**wholesale_cease_interconnect_args)
    assert output == {"status": "SUCCESS"}


response7 = {
    "errorCategory": "FAILED",
    "errors": [{"code": "ERR-011-999-0012", "message": "NNI Asset ID already exists"}],
    "status": "FAILED",
}
inca_response7 = {"result": "NNI Code must be unique"}


class Response7:
    def __init__(self):
        self.status_code = 409
        self._content = json.dumps(inca_response7)


@patch("connectors.core.utils.rest_api_utility.RestUtility.put")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_wholesale_details_case15(mock_token_generator, put_mocked):
    """
    verify wholesale for duplicate nni asset ID is passed for servicetype:interconnect,RequestType:cease
    """
    inst_inca = IncaService()
    put_mocked.side_effect = RestUtilityException("NNI Asset ID already exists", Response7())
    output = inst_inca.update_wholesale_details(**wholesale_cease_interconnect_args)
    assert output == response7


response8 = {
    "errorCategory": "FAILED",
    "errors": [{"code": "ERR-011-999-0014", "message": "Remote NNI-PE hostname not found in INCA"}],
    "status": "FAILED",
}
inca_response8 = {"result": "Remote BB PE hostname not found in INCA"}


class Response8:
    def __init__(self):
        self.status_code = 409
        self._content = json.dumps(inca_response8)


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_wholesale_details_case16(mock_token_generator, post_mocked):
    """
    verify wholesale for invalid Remote BB PE hostname is passed for servicetype:interconnect,RequestType:cease
    """
    inst_inca = IncaService()
    post_mocked.side_effect = RestUtilityException("Remote BB PE hostname not found in INCA", Response8())
    output = inst_inca.update_wholesale_details(**wholesale_new_interconnect_args)
    assert output == response8


response9 = {
    "status": "FAILED",
    "errorCategory": "FAILED",
    "errors": [
        {
            "code": "ERR-011-999-0010",
            "message": "Wholesale validation failed for parameter: "
            "`Wholesale validation failed for parameter: "
            "`{'code': 'NotFound', 'message': 'Not Found', "
            "'type': 'tag:oracle.com,2020:error/NotFound', "
            "'instance': 'tag:oracle.com,2020:ecid/tBM718asd3KJcjhch8KcXg'}``",
        }
    ],
}

inca_response9 = {
    "result": "Wholesale validation failed for parameter: `{'code': 'NotFound', "
    "'message': 'Not Found', 'type': 'tag:oracle.com,2020:error/NotFound', "
    "'instance': 'tag:oracle.com,2020:ecid/tBM718asd3KJcjhch8KcXg'}`"
}


class Response9:
    def __init__(self):
        self.status_code = 409
        self._content = json.dumps(inca_response9)


@patch("connectors.core.utils.rest_api_utility.RestUtility.put")
@patch("connectors.core.utils.oauth.token_generator")
def test_update_wholesale_details_case17(mock_token_generator, put_mocked):
    """
    verify wholesale for invalid INCA API is passed for servicetype:interconnect,RequestType:update
    """
    inst_inca = IncaService()
    put_mocked.side_effect = RestUtilityException("Invalid INCA API", Response9())
    output = inst_inca.update_wholesale_details(**wholesale_update_interconnect_args)
    assert output == response9


@patch("connectors.core.services.inca.connector.RestUtility")
@patch("connectors.core.utils.oauth.token_generator")
def test_gea_inca_update_status(mock_token_generator, rest_mock):
    """
    Test payload creation for GEA INCA update
    """
    inst_inca = IncaService()
    rest_mock().post.return_value = {"result": "OK", "id": "9945"}
    output = inst_inca.gea_inca_update_status(kwargs_nexa_2)
    rest_mock().post.assert_called_once_with(
        url=ANY,
        data='{"status_details": '
        '[{"or_cablelink_reference": "OGHP33333333", "status": "inprogress", "config_date": null, '
        '"circuit_state": "Ready-For-Config", "dne_order_ref": "BPM-123456"}, '
        '{"or_cablelink_reference": "OGHP63837190", "status": "failure", "config_date": "9/3/2021", '
        '"spark_ref": "CTASK1234578", "test_ref": "dummy", "comments": "dummy"}, '
        '{"or_cablelink_reference": "OGHP64724816", "status": "inprogress", "config_date": null, '
        '"circuit_state": "Ready-For-Config", "spark_ref": "CHG123458812", "dne_order_ref": "BPM-123TEST"}]}',
        timeout=20,
        headers=headers,
    )
    assert output == {"jobId": "GC-9945"}


@patch("connectors.core.services.inca.connector.RestUtility")
@patch("connectors.core.utils.oauth.token_generator")
def test_gea_inca_update_status_cease(mock_token_generator, rest_mock):
    """
    Test payload creation for GEA INCA update for cease
    """
    inst_inca = IncaService()
    rest_mock().post.return_value = {"result": "OK", "id": "9945"}
    output = inst_inca.gea_inca_update_status(kwargs_nexa_cease)
    rest_mock().post.assert_called_once_with(
        url=ANY,
        data=(
            '{"status_details": [{"or_cablelink_reference": "OGHP00806248", "status": "success", '
            '"config_date": null, "circuit_state": "GEA-CEASE", "spark_ref": "CHG12345672", '
            '"config_cease_date": "14/11/2021", "or_cease_date": "11/11/2024", '
            '"or_cease_ref": "94262CG", "order_reference": "OGHP00001496-100000-CEASE", '
            '"cease_submitted_date": "4/11/2024"}]}'
        ),
        timeout=20,
        headers=headers,
    )
    assert output == {"jobId": "GC-9945"}


nexa_cease_body = {
    "geaCeaseDetails": {
        "messageType": "GEACEASE",
        "requestDate": "2024-09-14",
        "exchange": "WNWX",
        "tgReference": "TG1234",
        "requiredByDate": "2024-09-30",
        "btSwitch": "BAACHK",
        "circuitCeaseOrderRef": "OGHP64783778-3456789-CEASE",
        "cablelinkRef": "OGHP64783778",
    }
}


kwargs_nexa_3 = {
    "type": "gea",
    "body": nexa_cease_body,
    "url": "apex/nexaREST/v0/message",
    "headers": headers,
    "job_id": "BU-1234",
}


get_resp7 = {
    "id": "11875",
    "results": [
        {
            "order_ref": "OGHP64783778-3456789-CEASE",
            "ring_ref": "",
            "cablelink_ref": "OGHP64783778",
            "bt_switch": "BAACHK",
            "date_requested": "14-SEP-24",
            "update_request_date": "14-SEP-24",
            "response": "OK",
        }
    ],
}

job_status7 = {
    "jobId": "BU-11875",
    "metadata": {"circuitsStatus": [{"circuitId": "OGHP64783778", "status": "success"}]},
    "status": "SUCCESS",
}


get_resp8 = {
    "id": "1234",
    "results": [
        {
            "order_ref": "OGHP77383831-3456789-CEASE",
            "ring_ref": "",
            "cablelink_ref": "OGHP77383831",
            "bt_switch": "BAAAQL",
            "date_requested": "18-AUG-24",
            "update_request_date": "18-AUG-24",
            "response": "Duplicate Request",
        }
    ],
}

job_status8 = {
    "errorCategory": "FAILED",
    "errors": [
        {
            "code": "ERR-011-999-0004",
            "message": "Request failed for Id OGHP77383831: Duplicate Request",
        }
    ],
    "jobId": "BU-1234",
    "metadata": {"circuitsStatus": [{"circuitId": "OGHP77383831", "status": "failure"}]},
    "status": "FAILURE",
}


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth.token_generator")
def test_cease_circuit_case1(mock_token_generator, post_mocked):
    """
    Test to check the functionality of cease_circuit()
    """
    inst_inca = IncaService()
    post_mocked.return_value = post_resp
    output = inst_inca.cease_circuit(**kwargs_nexa_3)
    assert output == {"jobId": "BU-1234"}


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth.token_generator")
def test_cease_circuit_case2(mock_token_generator, post_mocked):
    """
    Test to check the functionality of cease_circuit()
    """
    inst_inca = IncaService()
    post_mocked.return_value = post_resp_negate
    output = inst_inca.cease_circuit(**kwargs_nexa_3)
    assert output == {
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-011-999-0003",
                "message": "GEA Cease request: Failed to generate jobId with error: error while generating jobId",
            }
        ],
    }


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth.token_generator")
def test_cease_circuit_case3(mock_token_generator, post_mocked):
    """
    Test to check the functionality of cease_circuit()
    """
    inst_inca = IncaService()
    post_mocked.return_value = post_resp_negate1
    output = inst_inca.cease_circuit(**kwargs_nexa_3)
    assert output == {
        "errorCategory": "RETRY",
        "errors": [
            {
                "code": "ERR-011-999-0003",
                "message": "GEA Cease request: Failed to generate jobId with error: too many attempts",
            }
        ],
    }


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth.token_generator")
def test_cease_circuit_case4(mock_token_generator, post_mocked):
    """
    Test to check Exception the functionality of cease_circuit()
    """
    inst_inca = IncaService()
    post_mocked.side_effect = RestUtilityException("url issue", Response1())
    with pytest.raises(RestUtilityException):
        inst_inca.cease_circuit(**kwargs_nexa_3)


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth.token_generator")
def test_get_inca_update_status_case9(mock_token_generator, get_mocked):
    """
    Test to check the functionality of get_inca_update_status()
    """
    inst_inca = IncaService()
    get_mocked.return_value = get_resp1
    output = inst_inca.get_inca_update_status(**kwargs_nexa_3)
    assert output == {"jobId": "BU-1234", "status": "IN-PROGRESS"}


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth.token_generator")
def test_get_inca_update_status_case10(mock_token_generator, get_mocked):
    """
    Test to check the functionality of get_inca_update_status()
    """
    inst_inca = IncaService()
    get_mocked.return_value = get_resp8
    output = inst_inca.get_inca_update_status(**kwargs_nexa_3)
    assert output == job_status8


@patch("connectors.core.services.inca.connector.RestUtility")
def test_update_inca_device_decommissioned_success(mock_rest):
    """
    Test to check the functionality of update_inca_device_decommissioned() success case
    """
    inst_inca = IncaService()
    mock_rest_obj = mock_rest.return_value
    mock_rest_obj.put.return_value = {"result": "OK"}
    output = inst_inca.update_inca_device_decommissioned(
        **{
            "body": {"devices": [{"hostname": "decom-device-01"}]},
            "url": "apex/incaREST/v0/putDeviceDecommissioned",
            "headers": headers,
        }
    )
    assert output == {"status": "SUCCESS", "result": "OK"}


@patch("connectors.core.services.inca.connector.RestUtility")
def test_update_inca_device_decommissioned_failure(mock_rest):
    """
    Test to check the functionality of update_inca_device_decommissioned() failure case
    """
    inst_inca = IncaService()
    mock_rest_obj = mock_rest.return_value
    mock_rest_obj.put.return_value = {"result": "TestError"}
    output = inst_inca.update_inca_device_decommissioned(
        **{
            "body": {"devices": [{"hostname": "decom-device-01"}]},
            "url": "apex/incaREST/v0/putDeviceDecommissioned",
            "headers": headers,
        }
    )
    assert output == {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "result": "Update Device to Decomm status in Inca is Failed",
        "errors": [
            {
                "code": "ERR-011-999-0008",
                "message": "Update Device to Decomm status in Inca is Failed: TestError",
            }
        ],
    }


@patch("connectors.core.services.inca.connector.RestUtility")
def test_update_inca_device_decommissioned_status_exception(mock_rest):
    """
    Test to check the functionality of update_inca_device_decommissioned() exception case
    """
    inst_inca = IncaService()
    mock_rest_obj = mock_rest.return_value
    mock_rest_obj.put.side_effect = Exception("TestException")
    output = inst_inca.update_inca_device_decommissioned(
        **{
            "body": {"devices": [{"hostname": "decom-device-01"}]},
            "url": "apex/incaREST/v0/putDeviceDecommissioned",
            "headers": headers,
        }
    )
    assert output == {
        "status": "FAILURE",
        "errorCategory": "FAILED",
        "errors": [
            {
                "code": "ERR-011-999-0009",
                "message": "Update Device to Decomm status in Inca is Failed: TestException",
            }
        ],
        "result": "Update Device to Decomm status in Inca is Failed",
    }
