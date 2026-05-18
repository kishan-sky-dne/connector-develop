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
from unittest.mock import ANY, Mock, patch

# Third Party Library
import requests

# DNE Library
from connectors.core.services.inca.connector import IncaService
from connectors.core.utils.exceptions import RestUtilityException
from connectors.core.utils.helpers import generic_secret
from connectors.webserver.inca.tasks import read

secret = generic_secret()

access_token = secret
kwargs = {"type": "gea", "state": "config-ready", "limit": 90}
headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}",
}
kwargs["headers"] = headers
inca_cease_response = {
    "items": [
        {
            "requestDate": "11-APR-2022",
            "exchange": "EMNORTH",
            "tgReference": None,
            "requiredByDate": "10-JUL-2021",
            "switch": "BAACEM",
            "orderReference": "OGHP51402630-CEASE",
            "cablelinkRef": "OGHP51402630",
        },
        {
            "requestDate": "14-DEC-2023",
            "exchange": "WNWX",
            "tgReference": "TG1234",
            "requiredByDate": "31-DEC-2023",
            "switch": "BAACHK",
            "orderReference": "OGHP64783778-CEASE",
            "cablelinkRef": "OGHP64783778",
        },
        {
            "requestDate": "21-DEC-2023",
            "exchange": "WNCA",
            "tgReference": "cease_OGHP59258028",
            "requiredByDate": "20-JAN-2024",
            "switch": "BAAGIX",
            "orderReference": "OGHP59258028-CEASE",
            "cablelinkRef": "OGHP59258028",
        },
    ]
}
inca_plugup_ready_response = {
    "orderList": [
        {
            "mdf": "SDCRWLY",
            "exchangeName": "CRAWLEY",
            "plugupJobRef": "J03RWN",
            "sparkTicketRef": "CHG0083918",
            "reference": "BAABBI-SDCRWLY43846",
            "upgradeType": "18G -> 19G",
            "circuitDetails": {
                "hostname": "me2.sdcrwly.isp.sky.com",
                "location": "Ground Floor, MUA, Suite 25/26",
                "buildRef": "LLUC50001766",
                "port": "GigabitEthernet0/3/36",
                "switch": "BAABBI",
                "cablelinkRef": "OGHP63836712",
                "capacity": 1,
                "opticType": None,
                "picType": None,
                "cablelinkType": "NGA1",
                "couplerType": "None",
                "fiberDetails": None,
                "l2UsageType": "FTTC",
            },
            "patchPanelDetails": {
                "isNewPanelRequired": False,
                "isNewBrushPanelRequired": False,
                "rack": "Comms1",
                "panel": "pp23",
                "port": "3",
                "type": "Hybrid",
                "buildRef": "LLUC50001766",
                "buildNumber": 2,
            },
            "feName": "Paul Clark",
            "time": "Daytime",
        },
        {
            "mdf": "SDCRWLY",
            "exchangeName": "CRAWLEY",
            "plugupJobRef": "J03T7C",
            "sparkTicketRef": "CHG0084168",
            "reference": "BAABBI-SDCRWLY43854",
            "upgradeType": "17G -> 27G",
            "circuitDetails": {
                "hostname": "me2.sdcrwly.isp.sky.com",
                "location": "Ground Floor, MUA, Suite 25/26",
                "buildRef": "LLUC50001766",
                "port": "GigabitEthernet0/3/3",
                "switch": "BAABBI",
                "cablelinkRef": "OGHP63951182",
                "capacity": 10,
                "opticType": None,
                "picType": None,
                "cablelinkType": "NGA1",
                "couplerType": "None",
                "fiberDetails": None,
                "l2UsageType": "FTTC",
            },
            "patchPanelDetails": {
                "isNewPanelRequired": False,
                "isNewBrushPanelRequired": False,
                "rack": "Comms1",
                "panel": "pp23",
                "port": "4",
                "type": "Hybrid",
                "buildRef": "LLUC50001766",
                "buildNumber": 2,
            },
            "feName": "Paul Clark",
            "time": "Daytime",
        },
    ]
}

inca_url_response = {
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
inca_response = {
    "state": "config-ready",
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
    ],
}


@patch("connectors.webserver.inca.tasks.read._process_data")
@patch("connectors.webserver.inca.tasks.read.IncaService")
@patch("connectors.webserver.inca.tasks.read.token_generator")
def test_get_inca_details_config_ready(token_generator_mock, inca_mock, _process_data_mock):
    """
    Test to check the functionality of get_inca_details() for gea config_ready
    """
    _process_data_mock.return_value = inca_response
    output = read.get_inca_details(type="gea", state="config-ready", limit=90)
    assert output == inca_response
    inca_mock().get_details.assert_called_once_with(
        type="gea",
        state="config-ready",
        limit=90,
        headers=ANY,
        url="apex/incaREST/v0/GEAReadyForConfigJSON?p_max_rows=90",
    )


@patch("connectors.webserver.inca.tasks.read._process_data")
@patch("connectors.webserver.inca.tasks.read.IncaService")
@patch("connectors.webserver.inca.tasks.read.token_generator")
def test_get_inca_details_plugup_ready(token_generator_mock, inca_mock, _process_data_mock):
    """
    Test to check the functionality of get_inca_details() for gea plugup_ready
    """
    _process_data_mock.return_value = inca_response
    output = read.get_inca_details(type="gea", state="plugup-ready", limit=80)
    assert output == inca_response
    inca_mock().get_details.assert_called_once_with(
        type="gea", state="plugup-ready", limit=80, headers=ANY, url="apex/incaREST/v0/GEAPlugUpJSON?p_max_rows=80"
    )


@patch("connectors.webserver.inca.tasks.read._process_data")
@patch("connectors.webserver.inca.tasks.read.IncaService")
@patch("connectors.webserver.inca.tasks.read.token_generator")
def test_get_inca_details_cease(token_generator_mock, inca_mock, _process_data_mock):
    """
    Test to check the functionality of get_inca_details() for gea cease-requested
    """
    _process_data_mock.return_value = inca_response
    output = read.get_inca_details(type="gea", state="cease-requested", limit=70)
    assert output == inca_response
    inca_mock().get_details.assert_called_once_with(
        type="gea", state="cease-requested", limit=70, headers=ANY, url="apex/incaREST/v0/GEACeaseJSON?p_max_rows=70"
    )


@patch("connectors.webserver.inca.tasks.read._process_data")
@patch("connectors.webserver.inca.tasks.read.IncaService")
@patch("connectors.webserver.inca.tasks.read.token_generator")
def test_get_inca_details_cease_with_param(token_generator_mock, inca_mock, _process_data_mock):
    """
    Test to check the functionality of get_inca_details() for gea cease-requested with params
    """
    _process_data_mock.return_value = inca_response
    output = read.get_inca_details(type="gea", state="cease-requested", limit=70, cablelinkRef="OGHP00001000")
    assert output == inca_response
    inca_mock().get_details.assert_called_once_with(
        type="gea",
        state="cease-requested",
        limit=70,
        headers=ANY,
        cablelinkRef="OGHP00001000",
        url="apex/incaREST/v0/GEACeaseJSON?p_max_rows=70&cablelink_ref=OGHP00001000",
    )


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth")
def test_get_inca_details(mock_oauth, get_mocked, mock_post):
    """
    Test to check the functionality of get_inca_details()
    """
    mock_oauth.token_generator.return_value = access_token
    inst_inca = IncaService()
    get_mocked.return_value = inca_url_response
    inst_inca.get_details = Mock(return_value=inca_url_response)
    output = read.get_inca_details(type="gea", state="config-ready", limit=90)
    assert output == inca_response


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth")
def test_get_inca_details_case1(mock_oauth, get_mocked, mock_post):
    """
    Test to check the functionality of get_inca_details()
    """
    mock_oauth.token_generator.return_value = access_token
    inst_inca = IncaService()
    get_mocked.return_value = TypeError
    inst_inca.get_details = Mock(return_value=inca_url_response)
    read._process_data.side_effect = TypeError
    output = read.get_inca_details(type="gea", state="config-ready", limit=90)
    assert output == (
        {
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-011-999-0002",
                    "message": (
                        "Connector exception raised while sending url "
                        "for type gea to INCA  type object 'TypeError' has no attribute 'get'"
                    ),
                }
            ],
        },
        500,
    )


class ResponseRest1:
    def __init__(self):
        self.status_code = 400


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth")
def test_get_inca_details_case2(mock_oauth, get_mocked, mock_post):
    """
    Test to check the functionality of get_inca_details()
    """
    mock_oauth.token_generator.return_value = access_token
    inst_inca = IncaService()
    get_mocked.side_effect = RestUtilityException(message="url issue", response=ResponseRest1())
    inst_inca.get_details = Mock()
    inst_inca.get_details.side_effect = RestUtilityException(message="url issue", response=ResponseRest1())
    output = read.get_inca_details(type="gea", state="config-ready", limit=90)
    assert output == (
        {
            "errorCategory": "FAILED",
            "errors": [{"code": "ERR-011-999-0001", "message": "Request Exception while accessing the URL url issue"}],
        },
        500,
    )


class ResponseRest2:
    def __init__(self):
        self.status_code = 404


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth")
def test_get_inca_details_type_mismatch(mock_oauth, get_mocked, mock_post):
    """
    Test to check the functionality of get_inca_details()
    """
    mock_oauth.token_generator.return_value = access_token
    test_kwargs = kwargs
    test_kwargs["type"] = "test"
    inst_inca1 = IncaService()
    inst_inca1.get_details = Mock(return_value=inca_response)
    output = read.get_inca_details(**test_kwargs)
    assert output == {"items": []}


# nexa get job status
access_token_nexa = "xyz"
body1 = {
    "circuitDetails": [
        {
            "circuitId": "OGHP63837190",
            "configStatus": "inprogress",
            "configDate": "9/3/2021",
        },
        {
            "circuitId": "OGHP64724816",
            "configStatus": "success",
            "sparkReference": "CHG123458812",
        },
    ]
}
kwargs["body"] = body1

get_resp = {
    "id": "5549",
    "results": [
        {"or_cablelink_reference": "OGHP63837190", "response": "OK"},
        {"or_cablelink_reference": "OGHP64724816", "response": "OK"},
    ],
}
job_status = {
    "jobId": "GC-5549",
    "metadata": {
        "circuitsStatus": [
            {"circuitId": "OGHP63837190", "status": "success"},
            {"circuitId": "OGHP64724816", "status": "success"},
        ]
    },
    "status": "SUCCESS",
}
kwargs_status = {
    "job_id": "GC-5549",
    "headers": {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer F-xD4duMUvGThv5QBfO3sA",
    },
    "url": "apex/nexaREST/v0/response",
}


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth")
def test_get_inca_status_case1(mock_oauth, get_mocked, mock_post):
    mock_oauth.token_generator.return_value = access_token_nexa
    inst_inca = IncaService()
    get_mocked.return_value = get_resp
    inst_inca.get_inca_update_status = Mock(return_value=job_status)
    output = read.get_inca_status(**kwargs_status)
    assert output == job_status


class RestUtility403:
    def __init__(self):
        self.status_code = 403


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth")
def test_get_inca_status_exception(mock_oauth, get_mocked, s_post):
    mock_oauth.token_generator.return_value = access_token_nexa
    get_mocked.side_effect = RestUtilityException(message="dummy error", response=RestUtility403())
    inca_inst = IncaService()
    inca_inst.get_inca_update_status = Mock()
    output = read.get_inca_status(**kwargs_status)
    assert output.status_code == 403


inca_device_response = {
    "deviceList": [
        {
            "deviceInfo": [
                {
                    "buildNo": 0,
                    "buildRef": "LLUC30001647",
                    "configHostname": "vm0.eakln.isp.sky.com",
                    "deviceInterfaces": {
                        "deviceInterface": [
                            {
                                "aEndDeviceHostname": "me0.eakln",
                                "aEndDeviceInterface": "me0.eakln:ge0-3-26",
                                "aEndDeviceIp": None,
                                "aEndLagNo": None,
                                "bEndDeviceInterface": "ge11-0",
                                "bEndDeviceIp": None,
                                "bEndLagNo": None,
                                "reference": "NA",
                            }
                        ]
                    },
                    "deviceStatus": "Live",
                    "liveDate": "06-MAY-2014",
                    "sdpIds": [],
                    "subnetInterfaces": {
                        "subnetInterface": [
                            {
                                "LLUMGMTPE1": None,
                                "interfaceType": "ISAM MGMT VM",
                                "ipAddress": "87.87.112.228",
                                "subnet": "87.87.112.224/28",
                                "vlanNo": "256",
                            }
                        ]
                    },
                    "vlans": {
                        "vlan": [
                            {
                                "interfaces": {
                                    "interface": [
                                        {
                                            "IPAddress": "87.87.69.193",
                                            "hostname": "sr10.enpet",
                                            "interfaceType": "LLU MGMT PE1",
                                            "vlanNo": 208,
                                        }
                                    ]
                                },
                                "subnet": "87.87.69.192/27",
                                "vlanNo": 208,
                                "vlanType": "LLU Management",
                            },
                            {
                                "interfaces": {
                                    "interface": [
                                        {
                                            "IPAddress": "87.87.112.225",
                                            "hostname": "sr10.enpet",
                                            "interfaceType": "ISAM MGMT PE1",
                                            "vlanNo": 256,
                                        }
                                    ]
                                },
                                "subnet": "87.87.112.224/28",
                                "vlanNo": 256,
                                "vlanType": "ISAM Management",
                            },
                        ]
                    },
                }
            ],
            "hostname": "vm0.eakln",
        }
    ]
}

inca_device_response_partial_success = deepcopy(inca_device_response)

inca_device_response_partial_success["deviceList"].append(
    {"hostname": "vm1.eakl", "error_message": "Device not found in INCA"}
)

error_response_for_invalid_query = {
    "errorCategory": "FAILED",
    "errors": [
        {"code": "ERR-011-999-0001", "message": "Validation failed: Either hostname or exchangeName is mandatory"}
    ],
}


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth")
def test_get_device_details_with_hostname(mock_oauth, get_mocked, mock_post):
    """
    Test to check the functionality of get_device_details() with valid hostname
    """
    expected_response = inca_device_response
    expected_response.update({"status": "Success"})
    mock_oauth.token_generator.return_value = access_token
    inst_inca = IncaService()
    get_mocked.return_value = inca_device_response
    inst_inca.get_details = Mock(return_value=inca_device_response)
    output = read.get_device_details(hostname="vm0.eakln")
    assert output == expected_response
    get_mocked.assert_called_once_with(url=ANY, headers=ANY)


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth")
def test_get_device_details_with_exchangename(mock_oauth, get_mocked, mock_post):
    """
    Test to check the functionality of get_device_details() with valid hostname
    """
    expected_response = inca_device_response
    expected_response.update({"status": "Success"})
    mock_oauth.token_generator.return_value = access_token
    inst_inca = IncaService()
    get_mocked.return_value = inca_device_response
    inst_inca.get_details = Mock(return_value=inca_device_response)
    output = read.get_device_details(exchangeName="bllon")
    assert output == expected_response


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth")
def test_get_device_details_with_invalid_partial_hostname(mock_oauth, get_mocked, mock_post):
    """
    Test to check the functionality of get_device_details() with valid hostname
    """
    expected_response = inca_device_response
    expected_response["status"] = "Partial Success"
    expected_response["errors"] = [
        {"code": "ERR-011-999-0006", "hostname": "vm1.eakl", "message": "Device not found in INCA"}
    ]
    expected_response["errorCategory"] = "FAILED"
    mock_oauth.token_generator.return_value = access_token
    inst_inca = IncaService()
    get_mocked.return_value = inca_device_response_partial_success
    inst_inca.get_details = Mock(return_value=inca_device_response_partial_success)
    kwargs = {"hostname": ["vm0.eakln", "vm1.eakl"]}
    output = read.get_device_details(**kwargs)
    assert output == expected_response


inca_hostname_failure_resp = {
    "deviceList": [
        {"hostname": "vm0.bllo1n", "error_message": "Device not found in INCA"},
        {"hostname": "bm0.bllon1", "error_message": "Device not found in INCA"},
    ]
}


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth")
def test_get_device_details_with_invalid_hostname(mock_oauth, get_mocked, mock_post):
    """
    Test to check the functionality of get_device_details() with valid hostname
    """
    expected_response = {
        "deviceList": [],
        "status": "Error",
        "errors": [
            {"code": "ERR-011-999-0006", "hostname": "vm0.bllo1n", "message": "Device not found in INCA"},
            {"code": "ERR-011-999-0006", "hostname": "bm0.bllon1", "message": "Device not found in INCA"},
        ],
        "errorCategory": "FAILED",
    }
    expected_response["errorCategory"] = "FAILED"
    mock_oauth.token_generator.return_value = access_token
    inst_inca = IncaService()
    get_mocked.return_value = inca_hostname_failure_resp
    inst_inca.get_details = Mock(return_value=inca_hostname_failure_resp)
    kwargs = {"hostname": ["vm0.bllo1n", "bm0.bllon1"]}
    output = read.get_device_details(**kwargs)
    assert output == expected_response


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth")
def test_get_device_details_with_invalid_exchangename(mock_oauth, get_mocked, mock_post):
    """
    Test to check the functionality of get_device_details() with valid hostname
    """
    device_response = {"deviceList": []}
    expected_response = deepcopy(device_response)
    expected_response["status"] = "Error"
    expected_response["errors"] = [
        {
            "code": "ERR-011-999-0006",
            "exchangeName": "smlea1",
            "message": "No Records are available in INCA for the matching filter criteria",
        }
    ]
    expected_response["errorCategory"] = "FAILED"
    mock_oauth.token_generator.return_value = access_token
    inst_inca = IncaService()
    get_mocked.return_value = device_response
    inst_inca.get_details = Mock(return_value=device_response)
    kwargs = {"exchangeName": "smlea1"}
    output = read.get_device_details(**kwargs)
    assert output == expected_response


def test_get_device_details_case1():
    """
    Test to check whether both hostname and exchangeName is present
    """
    output = read.get_device_details(hostname="vm0.eakln", exchangeName="bllon")
    assert output == error_response_for_invalid_query


def test_get_device_details_case2():
    """
    Test to check whether both hostname and exchangeName is not present
    """
    output = read.get_device_details()
    assert output == error_response_for_invalid_query


def test_process_data_config_ready():
    """
    Test _process_data when state is config-ready
    """
    kwargs = {"type": "gea", "state": "config-ready"}
    assert read._process_data(inca_url_response, **kwargs) == inca_response


def test_process_data_plugup_ready():
    """
    Test _process_data when state is plugup-ready
    """
    kwargs = {"type": "gea", "state": "plugup-ready"}
    assert read._process_data(inca_plugup_ready_response, **kwargs) == {
        "items": inca_plugup_ready_response["orderList"],
        "state": "plugup-ready",
    }


def test_process_data_cease_requested():
    """
    Test _process_data when state is cease_requested
    """
    kwargs = {"type": "gea", "state": "cease-requested"}
    assert read._process_data(inca_cease_response, **kwargs) == {
        "items": inca_cease_response["items"],
        "state": "cease-requested",
    }


def test_process_data_plugup_ready_no_records():
    """
    Test _process_data when state is plugup-ready and no records
    """
    kwargs = {"type": "gea", "state": "plugup-ready"}
    data = {"error_message": "No records found"}
    assert read._process_data(data, **kwargs) == {"items": [], "state": "plugup-ready"}


def test_process_data_cease_requested_no_records():
    """
    Test _process_data when state is plugup-ready and no records
    """
    kwargs = {"type": "gea", "state": "cease-requested", "cablelinkRef": "OGHP0000100011"}
    data = {"error_message": "Matching GEA Request not found"}
    assert read._process_data(data, **kwargs) == {
        "errorCategory": "FAILED",
        "errors": [{"code": "ERR-011-032-0001", "message": "INCA Error: Matching GEA Request not found"}],
    }


def test_process_data_cease_requested_completed():
    """
    Test _process_data when state is cease_requested
    and the order is completed
    """
    kwargs = {"type": "gea", "state": "cease-requested", "cablelinkRef": "OGHP00001000"}
    data = {"error_message": "GEA is available, but Cease is already completed"}
    assert read._process_data(data, **kwargs) == {
        "errorCategory": "FAILED",
        "errors": [
            {"code": "ERR-011-032-0001", "message": "INCA Error: GEA is available, but Cease is already completed"}
        ],
    }


def test_process_data_cease_requested_cancelled():
    """
    Test _process_data when state is cease_requested
    and the order is cancelled or not started
    """
    kwargs = {"type": "gea", "state": "cease-requested", "cablelinkRef": "OGHP00001000"}
    data = {"error_message": "GEA is available in INCA but GEA cease not started"}
    assert read._process_data(data, **kwargs) == {
        "errorCategory": "FAILED",
        "errors": [
            {"code": "ERR-011-032-0001", "message": "INCA Error: GEA is available in INCA but GEA cease not started"}
        ],
    }


def test_process_data_config_ready_no_records():
    """
    Test _process_data when state is config-ready and no records
    """
    kwargs = {"type": "gea", "state": "config-ready"}
    data = {"error_message": "No records found"}
    assert read._process_data(data, **kwargs) == {"items": [], "state": "config-ready"}
