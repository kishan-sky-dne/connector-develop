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
import os
from unittest.mock import Mock, patch

# Third Party Library
import pytest

# DNE Library
from connectors.core.services.itsm.exceptions import ResourceServiceNotAvailable
from connectors.core.utils.exceptions import ConnectorException
from connectors.core.utils.exceptions import ResourceServiceNotAvailable as serviceDown
from connectors.core.utils.exceptions import RestUtilityException

# from connectors.webserver.itsm.tasks.genericQueryFilter import aio_custom_query
from connectors.webserver.itsm.tasks.genericQueryFilter import custom_query, get_adjacent_ci_details

# from unittest.mock import AsyncMock


@patch("connectors.core.services.itsm.connector.SparkTicketService.execute_query")
@patch("connectors.core.services.itsm.connector.SparkTicketService.get_sys_id")
@patch("connectors.webserver.itsm.tasks.genericQueryFilter.get_adjacent_ci_details")
@pytest.mark.parametrize("db_table", ["incident", "change_request"])
def test_custom_query_success(get_adjacent_ci_details_mock, mock_get_sys_id, mock_execute_query, db_table):
    """
    Test to check the functionality of custom_query() function
    """
    srvc_3800_url = "https://sparkproxyuat.azure-api.net/service3800/request"
    ci_list = ["test1", "test2"]
    ticket = {"serviceType": "bngFailover"}
    dummy_result = {"key1": "val1", "key2": "val2", "keyn": "valn"}
    mock_get_sys_id.return_value = ["1001", "1002"]
    mock_execute_query.return_value = dummy_result
    response = custom_query(
        table=db_table,
        filter="ci_list",
        start_date=1572794340,
        end_date=1572894600,
        ci_list=ci_list,
        service_type=ticket["serviceType"],
    )
    mock_get_sys_id.assert_called_once_with(ci_list, srvc_3800_url, get_single_id=True)
    assert response == dummy_result


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.services.itsm.connector.SparkTicketService.get_sys_id")
@patch("connectors.webserver.itsm.tasks.genericQueryFilter.get_adjacent_ci_details")
@pytest.mark.parametrize("db_table", ["incident", "change_request"])
def test2_custom_query_success(get_adjacent_ci_details_mock, mock_get_sys_id, mock_get, db_table):
    """
    Test to check the functionality of custom_query() function, mocking done at rest-get inside execute query
    """
    srvc_3800_url = "https://sparkproxyuat.azure-api.net/service3800/request"
    ci_list = ["test1", "test2"]
    dummy_result = {"key1": "val1", "key2": "val2", "keyn": "valn"}
    mock_get_sys_id.return_value = ["1001", "1002"]
    mock_get.return_value = {"result": dummy_result}
    ticket = {"serviceType": "bngFailover"}
    response = custom_query(
        table=db_table,
        filter="ci_list",
        start_date=1572794340,
        end_date=1572894600,
        ci_list=ci_list,
        service_type=ticket["serviceType"],
    )
    mock_get_sys_id.assert_called_once_with(ci_list, srvc_3800_url, get_single_id=True)
    assert response == dummy_result


@patch("connectors.webserver.itsm.tasks.genericQueryFilter.SparkTicketService.service3800")
@patch("connectors.webserver.itsm.tasks.genericQueryFilter.mapper")
@patch("connectors.webserver.itsm.tasks.genericQueryFilter.ignore_similar_conflicts_with_pattern")
@patch("connectors.webserver.itsm.tasks.genericQueryFilter.get_adjacent_ci_details")
def test_custom_query_ignore_similar_changes(
    get_adjacent_ci_details_mock, ignore_cr_mock, mapper_mock, service3800_mock
):
    """
    Test to check ignore_similar_conflicts_with_pattern is called when required
    """
    service3800_mock.return_value = [
        {
            "ci_item": {
                "display_value": "br0.bllabd1.isp.sky.com",
            },
            "task": {
                "display_value": "CHG11111",
            },
            "task.short_description": "[DNE] Provisioning GEA under DNE Order 11111",
            "u_impact_end_date": "22/05/2024 23:30:00",
            "u_impact_start_date": "22/05/2024 17:30:00",
            "u_impact_type": "No Service Impact",
        }
    ]
    mapper_mock.get().get().get().get.return_value = {
        "geaProvisioningV2": {"similar_change_pattern": "Provisioning GEA,DNE Order"}
    }
    ignore_cr_mock.return_value = []
    response = custom_query(
        table="change_request",
        filter="ci_list",
        start_date=1716381160,
        end_date=1716467560,
        shortDescription=True,
        ci_list=["br0.bllabd1.isp.sky.com"],
        service_type="geaProvisioningV2",
    )
    ignore_cr_mock.assert_called_once_with(
        change_req_list=[
            {
                "ci_item": {"display_value": "br0.bllabd1.isp.sky.com"},
                "task": {"display_value": "CHG11111"},
                "task.short_description": "[DNE] Provisioning GEA under DNE Order 11111",
                "u_impact_end_date": "22/05/2024 23:30:00",
                "u_impact_start_date": "22/05/2024 17:30:00",
                "u_impact_type": "No Service Impact",
            }
        ],
        pattern={"geaProvisioningV2": {"similar_change_pattern": "Provisioning GEA,DNE Order"}},
    )
    assert response == []


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.webserver.itsm.tasks.genericQueryFilter.get_adjacent_ci_details")
@pytest.mark.parametrize("db_table", ["incident", "change_request"])
def test_custom_query_service3800(get_adjacent_ci_details_mock, mock_srvc3800, db_table):
    """
    Test to check the functionality of custom_query() function when mocking has been done for service3800 function.
    """
    dummy_result = {"key1": "val1", "key2": "val2", "keyn": "valn"}
    mock_srvc3800.return_value = dummy_result
    ticket = {"serviceType": "bngFailover"}
    response = custom_query(
        table=db_table,
        filter="ci_list",
        start_date=1572794340,
        end_date=1572894600,
        ci_list=["test1", "test2"],
        service_type=ticket["serviceType"],
    )
    mapped_db_table = db_table
    if db_table == "change_request":
        mapped_db_table = "task_ci"
    mock_srvc3800.assert_called_once_with(
        db_table=mapped_db_table,
        affected_cis=["test1", "test2"],
        ci_filter="ci_list",
        start_date=1572794340,
        end_date=1572894600,
        hostname=None,
        short_description=None,
        ticket_number=None,
    )
    assert response == dummy_result


def test_custom_query_keyerror():
    """
    Test to check if custom_query() raises KeyError in case of mandatory parameter missing
    """
    ticket = {"serviceType": "bngFailover"}
    response = custom_query(
        table="change_request",
        start_date=1572794340,
        end_date=1572894600,
        ci_list=["test1", "test2"],
        service_type=ticket["serviceType"],
    )
    assert response.body["status"] == 404
    assert "problem in preparing request" in response.body["title"].lower()


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.webserver.itsm.tasks.genericQueryFilter.get_adjacent_ci_details")
def test_custom_query_rest_utility_exception(get_adjacent_ci_details_mock, mock_rest_get):
    """
    Test to check if custom_query() function raises rest utility exception.
    Here, no mocking has been done for rest-get() and as such call to custom_query()-> service3800-> get_sys_id ->
    rest get() results into RestUtilityException and status code 403 returned from custom_query() function
    """
    response = Mock()
    response.status_code.return_value = 403
    ticket = {"serviceType": "bngFailover"}
    mock_rest_get.side_effect = RestUtilityException("error", response=response)
    response = custom_query(
        table="change_request",
        filter="ci_list",
        start_date=1572794340,
        end_date=1572894600,
        ci_list=["test1", "test2"],
        service_type=ticket["serviceType"],
    )
    assert response.body["status"] == 403
    assert "request exception while accessing the url" in response.body["title"].lower()


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.webserver.itsm.tasks.genericQueryFilter.get_adjacent_ci_details")
def test_custom_query_resource_service_not_available_exception(get_adjacent_ci_details_mock, mock_rest_get):
    """
    Test to check if custom_query() function raises ResourceServiceNotAvailable exception
    """
    ticket = {"serviceType": "bngFailover"}
    mock_rest_get.side_effect = ResourceServiceNotAvailable("dummy error")
    response = custom_query(
        table="change_request",
        filter="ci_list",
        start_date=1572794340,
        end_date=1572894600,
        ci_list=["test1", "test2"],
        service_type=ticket["serviceType"],
    )
    assert response.body["status"] == 404
    assert "error in accessing spark ticketing system" in response.body["title"].lower()


@patch("connectors.core.services.itsm.connector.SparkTicketService.get_sys_id")
@patch("connectors.webserver.itsm.tasks.genericQueryFilter.get_adjacent_ci_details")
def test_custom_query_invalid_request_exception(get_adjacent_ci_details_mock, mock_get_sys_id):
    """
    Test to check if custom_query() function causes exception with invalid db_table
    """
    mock_get_sys_id.return_value = ["1001", "1002"]
    ticket = {"serviceType": "bngFailover"}
    response = custom_query(
        table="xyz",
        filter="ci_list",
        start_date=1572794340,
        end_date=1572894600,
        ci_list=["test1", "test2"],
        service_type=ticket["serviceType"],
    )
    assert response.body["status"] == 404
    assert "problem in preparing request" in response.body["title"].lower()


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.webserver.itsm.tasks.genericQueryFilter.get_adjacent_ci_details")
def test_custom_query_generic_exception(get_adjacent_ci_details_mock, mock_srvc3800):
    """
    Test to check if custom_query() function causes generic exception
    """
    ticket = {"serviceType": "bngFailover"}
    mock_srvc3800.side_effect = Exception("dummy error")
    response = custom_query(
        table="change_request",
        filter="ci_list",
        start_date=1572794340,
        end_date=1572894600,
        ci_list=["test1", "test2"],
        service_type=ticket["serviceType"],
    )
    assert response.body["status"] == 500


def here():
    """Gives data path inside this path"""
    return f"{os.path.dirname(os.path.realpath(__file__))}/data/"


# Loading data from json file
with open(f"{here()}/plannet_data.json", "r") as f:
    plannet_response = json.loads(f.read())

plannet_api_checks = [
    {
        "nes_details_response": plannet_response["get_nes_details_response"],
        "nes_details_response_with_id": plannet_response["get_nes_details_response_with_parent_id"],
        "interface_links_response": plannet_response["get_interface_links_response"],
        "service_type": "bngFailover",
        "ci_list": ["br0.bllabd1.isp.sky.com"],
        "output": [],
        "env": "production",
    },
    {
        "nes_details_response": plannet_response["get_nes_details_response"],
        "nes_details_response_with_id": plannet_response["get_nes_details_response_with_parent_id"],
        "interface_links_response": plannet_response["get_interface_links_response"],
        "service_type": "wholesaleUni",
        "ci_list": ["br0.bllabd1.isp.sky.com"],
        "output": [],
    },
    {
        "nes_details_response": plannet_response["get_nes_details_response"],
        "nes_details_response_with_id": plannet_response["get_nes_details_response_without_name"],
        "interface_links_response": plannet_response["get_interface_links_response"],
        "service_type": "bngFailover",
        "ci_list": [],
        "output": [],
    },
]


@patch("connectors.webserver.itsm.tasks.genericQueryFilter.current_environment")
@patch("connectors.webserver.itsm.tasks.genericQueryFilter.get_interface_links")
@patch("connectors.webserver.itsm.tasks.genericQueryFilter.get_nes_details")
@pytest.mark.parametrize("params", plannet_api_checks)
def test_get_adjacent_ci_details(get_nes_details_mock, get_interface_links_mock, environment, params):
    """
    1.Success Case
    2.When the serviceType is not bngFailover
    3.when the ci list is empty
    4.when nes_response has no key as results
    5.when nes_response is empty
    6.when the new ci list is empty

    """
    ci_list = params["ci_list"]
    environment.return_value = params.get("env", "development")
    get_nes_details_mock.side_effect = [params["nes_details_response"], params["nes_details_response_with_id"]]
    get_interface_links_mock.return_value = params["interface_links_response"]
    get_adjacent_ci_details(ci_list, params["service_type"])


error_scenarios = [
    {"error_mock_data": [plannet_response["get_nes_details_response_without_name"]]},
    {"error_mock_data": [plannet_response["plannet_error_response_2"]]},
]


@patch("connectors.webserver.itsm.tasks.genericQueryFilter.get_interface_links")
@patch("connectors.webserver.itsm.tasks.genericQueryFilter.get_nes_details")
@pytest.mark.parametrize("params", error_scenarios)
def test_get_adjacent_ci_details_error_case(get_nes_details_mock, get_interface_links_mock, params):
    """
    Error scenario -Raises Connector exception when ta/pr devices not found
    or when plannet is not reachable/Insufficient data
    """
    ci_list = ["br0.bllabd1.isp.sky.com"]
    with pytest.raises(ConnectorException):
        get_nes_details_mock.side_effect = params["error_mock_data"]
        get_interface_links_mock.return_value = plannet_response["get_nes_details_response_with_parent_id"]
        get_adjacent_ci_details(ci_list, "bngFailover")

    with pytest.raises(serviceDown):
        get_nes_details_mock.side_effect = [plannet_response["plannet_error_response_1"]]
        get_interface_links_mock.return_value = plannet_response["get_nes_details_response_with_parent_id"]
        get_adjacent_ci_details(ci_list, "bngFailover")


# @patch("connectors.core.services.itsm.aio_connector.SparkTicketService.service3800")
# def test_aio_custom_query_case1(mock_aio_srvc3800):
#     """
#     Test to check the functionality of aio_custom_query() function
#     """
#     expected_return_value = {
#         "result": [
#             {
#                 "action": "read",
#                 "childCI": "me0.mypon.isp.sky.com",
#                 "getUrlPath": ("https://sparkproxyuat.azure-api.net//service3800/request?db_table=cmdb_rel_ci"
#                                "&query_filter=child.name%3Dme0.mypon.isp.sky.com"),
#                 "parentCI": "ONEA45266093",
#                 "relationshipStatus": "active",
#                 "relationshipType": "Depends on::Used by"
#             }]}
#     mock_aio_srvc3800.return_value = expected_return_value
#     response = aio_custom_query(table="cmdb_rel_ci", filter="child", ci_list=["me0.mypon.isp.sky.com"])
#     assert response == expected_return_value
#
#
# @patch("connectors.core.services.itsm.aio_connector.SparkTicketService.service3800")
# def test_aio_custom_query_generic_exception(mock_srvc_3800):
#     """
#     Test to check if custom_query() function causes generic exception
#     """
#     mock_srvc_3800.side_effect = Exception("dummy error")
#     response = aio_custom_query(
#         table="cmdb_rel_ci", filter="child", ci_list=["me0.mypon.isp.sky.com"]
#     )
#     assert response.body["status"] == 500
#
#
# @patch("connectors.core.utils.aiohttp_adapter.AioRestUtility.get")
# def test_aio_custom_query_rest_utility_exception(mock_rest_get):
#     """
#     Test to check if aio_custom_query() function raises rest utility exception.
#     """
#     response = AsyncMock()
#     response.status_code.return_value = 403
#     mock_rest_get.side_effect = RestUtilityException("error", response=response)
#     response = aio_custom_query(
#         table="cmdb_rel_ci", filter="child", ci_list=["me0.mypon.isp.sky.com"]
#     )
#     expected_response = {'result':
#         [
#             {'getUrlPath': 'https://sparkproxyuat.azure-api.net//service3800/request?db_table='
#                            'cmdb_rel_ci&query_filter=child.name%3Dme0.mypon.isp.sky.com',
#              'action': 'read',
#              'relationshipStatus': 'CI not found or there are no relationships or resource not found',
#              'parentCI': None, 'childCI': 'me0.mypon.isp.sky.com'}
#         ]}
#     assert response == expected_response
#
#
# @patch("connectors.core.utils.aiohttp_adapter.AioRestUtility.get")
# def test_aio_custom_query_resource_service_not_available_exception(mock_rest_get):
#     """
#     Test to check if aio_custom_query() function raises ResourceServiceNotAvailable exception
#     """
#     expected_response = {'result':
#         [
#             {'getUrlPath': 'https://sparkproxyuat.azure-api.net//service3800/request?db_table='
#                            'cmdb_rel_ci&query_filter=child.name%3Dme0.mypon.isp.sky.com',
#              'action': 'read',
#              'relationshipStatus': 'CI not found or there are no relationships or resource not found',
#              'parentCI': None, 'childCI': 'me0.mypon.isp.sky.com'}
#         ]}
#     mock_rest_get.side_effect = ResourceServiceNotAvailable("dummy error")
#     response = aio_custom_query(
#         table="cmdb_rel_ci", filter="child", ci_list=["me0.mypon.isp.sky.com"]
#     )
#     assert response == expected_response
