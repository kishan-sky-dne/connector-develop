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
import threading
from unittest.mock import patch

# Third Party Library
import pytest

# DNE Library
from connectors.core.services.itsm import connector
from connectors.core.services.itsm.exceptions import InvalidRequest, ResourceServiceNotAvailable
from connectors.core.utils.exceptions import GenericConnectorsException

headers = {
    "accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
    "ocp-apim-subscription-key": connector.itsm_keys[0],
}
service_url = {
    "3020": "https://sparkproxyuat.azure-api.net/service3020/request",
    "3045": "https://sparkproxyuat.azure-api.net/service3045/request",
    "3400": "https://sparkproxyuat.azure-api.net/service3400/request",
    "3406": "https://sparkproxyuat.azure-api.net/service3406/request",
    "3800": "https://sparkproxyuat.azure-api.net/service3800/request",
    "3030": "https://sparkproxyuat.azure-api.net/service3030/request",
}
param_ci_list = [
    (
        [
            {"ciName": "ma0.test.bllab.it.bb.sky.com", "impactType": "No Service Impact"},
            {"ciName": "ma0.test1.bllab.it.bb.sky.com", "impactType": "Full Outage"},
        ]
    ),
    (
        [
            {"ciName": "ma0.test.bllab.it.bb.sky.com", "impactType": "No Service Impact"},
        ]
    ),
]
param_db_table = ["task_ci", "incident"]
param_sys_id = [
    (["abc.test.bllab.it.bb.sky.com"], ["3433fcd8dbfa18102495a235ca960001"]),
    (
        ["abc.test.bllab.it.bb.sky.com", "xyz.test.bllab.it.bb.sky.com"],
        ["3433fcd8dbfa18102495a235ca960001", "3433fcd8dbfa18102495a235ca960002"],
    ),
]
invalid_date_params = [(None, 1572894600), (1572794340, None)]
exceptions_srvc3020 = [ValueError, TypeError, AttributeError]
exceptions_srvc3045 = [
    (ValueError, GenericConnectorsException),
    (TypeError, GenericConnectorsException),
    (AttributeError, GenericConnectorsException),
    (KeyError, ResourceServiceNotAvailable),
]
exceptions_srvc3400 = [ValueError, TypeError, AttributeError]
exceptions_srvc3405 = [ValueError, TypeError, AttributeError]
exceptions_srvc3406 = [ValueError, TypeError, AttributeError]
exceptions_srvc3030 = [ValueError, TypeError, AttributeError]
exceptions_srvc3030_1 = [KeyError]
operation = ["list", "add", "remove"]


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@pytest.mark.parametrize("cis, sys_id_list", param_sys_id)
def test_get_sys_id(mock_rest_get, cis, sys_id_list):
    """
    Test to check the functionality of get_sys_id()
    """
    mock_rest_get.side_effect = [
        {
            "result": [
                {
                    "sys_id": "3433fcd8dbfa18102495a235ca960001",
                    "operational_status": "Operational",
                    "name": "abc.test.bllab.it.bb.sky.com",
                }
            ]
        },
        {
            "result": [
                {
                    "sys_id": "3433fcd8dbfa18102495a235ca960002",
                    "operational_status": "Operational",
                    "name": "xyz.test.bllab.it.bb.sky.com",
                }
            ]
        },
    ]

    spark = connector.SparkTicketService()
    response = spark.get_sys_id(cis, service_url["3800"])
    assert response == sys_id_list
    assert mock_rest_get.call_count == len(cis)


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_fetch_ci_relationship(mock_rest_get):
    """
    Test to check fetch_ci_relationship validity for table task_ci
    """
    db_table = "task_ci"
    ticket_number = "CHG123"
    request = f"""db_table={db_table}&query_filter=task.number%3DCHG123"""
    spark = connector.SparkTicketService()
    spark.fetch_ci_relationship(
        url=service_url["3800"],
        db_table=db_table,
        ticket_number=ticket_number,
    )
    mock_rest_get.assert_called_once_with(service_url["3800"], headers=headers, params=request)


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_fetch_ci_relationship_with_ci_list(mock_rest_get):
    """
    Test to check fetch_ci_relationship validity for table task_ci
    """
    db_table = "task_ci"
    ticket_number = "CHG123"
    request = f"db_table={db_table}&query_filter=task.number%3DCHG123"
    request = f"{request}^ci_itemLIKEta0.enabd.isp.sky.com^ORci_itemLIKEta1.enabd.isp.sky.com"
    spark = connector.SparkTicketService()
    sys_id_list = ["149cfa651b1dc110d049a932b24bcb52", "189cfa651b1dc110d049a932b24bcb57"]
    affected_ci_mapper = {
        "u_cmdb_ci_circuit": [],
        "task_ci": ["ta0.enabd.isp.sky.com", "ta1.enabd.isp.sky.com"],
        "incident": sys_id_list,
    }
    spark.fetch_ci_relationship(
        url=service_url["3800"],
        db_table=db_table,
        ticket_number=ticket_number,
        sys_id_list=sys_id_list,
        affected_ci_mapper=affected_ci_mapper,
    )
    mock_rest_get.assert_called_once_with(service_url["3800"], headers=headers, params=request)


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_execute_query(mock_rest_get):
    """
    Test to check the functionality of execute_query() function for db_table incident
    """
    db_table = "incident"
    sys_id_list = ["3433fcd8dbfa18102495a235ca960001", "3433fcd8dbfa18102495a235ca960002"]
    incident_return_fields = (
        "number,u_age_of_task,impact,active,notify,u_impact_type,work_start,sys_class_name,"
        "u_actual_impact_start_date,u_affected_ci_list,sys_created_by,u_incident_manager"
    )
    request = (
        f"""db_table={db_table}&query_filter=state%3D2%5Eimpact%3D1%5EORimpact%3D2%5EORimpact%3D3%5E"""
        f"""u_affected_ci_listLIKE{sys_id_list[0]}%5EORu_affected_ci_listLIKE{sys_id_list[1]}&"""
        f"""return_fields={incident_return_fields}"""
    )
    spark = connector.SparkTicketService()
    spark.execute_query(
        url=service_url["3800"],
        db_table=db_table,
        sys_id_list=sys_id_list,
        query=f"state=2^impact=1^ORimpact=2^ORimpact=3",
        ci_filter="u_affected_ci_list",
        return_fields=incident_return_fields,
    )
    mock_rest_get.assert_called_once_with(service_url["3800"], headers=headers, params=request)


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.services.itsm.connector.SparkTicketService.get_sys_id")
@pytest.mark.parametrize("db_table", param_db_table)
def test_service3800(mock_get_sys_id, mock_rest_get, db_table):
    """
    Test to check the functionality of service3800() function
    """
    dummy_result = {"key1": "val1", "key2": "val2", "keyn": "valn"}
    mock_get_sys_id.return_value = ["3433fcd8dbfa18102495a235ca960001"]
    mock_rest_get.return_value = {"result": dummy_result}
    spark = connector.SparkTicketService()
    spark_response = spark.service3800(
        db_table=db_table,
        affected_cis=["xyz.test.bllab.it.bb.sky.com"],
        ci_filter="ci_list",
        start_date=1544681400,
        end_date=1545981400,
    )
    assert spark_response == dummy_result


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.services.itsm.connector.SparkTicketService.get_sys_id")
@pytest.mark.parametrize("db_table", ["task_ci"])
def test_service3800_case1(mock_get_sys_id, mock_rest_get, db_table):
    """
    Test to check the functionality of service3800() function
    """
    dummy_result = [{"task": {"display_value": "xyz"}, "task.short_description": "xxx"}]
    mock_get_sys_id.return_value = ["3433fcd8dbfa18102495a235ca960001"]
    mock_rest_get.return_value = {"result": dummy_result}
    spark = connector.SparkTicketService()
    spark_response = spark.service3800(
        db_table=db_table,
        affected_cis=["xyz.test.bllab.it.bb.sky.com", "abc.test.bllab.it.bb.sky.com"],
        ci_filter="ci_list",
        start_date=1544681400,
        end_date=1545981400,
        short_description=True,
    )
    assert spark_response == dummy_result


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.services.itsm.connector.SparkTicketService.get_sys_id")
@pytest.mark.parametrize("db_table", ["task_ci"])
def test_service3800_case2(mock_get_sys_id, mock_rest_get, db_table):
    """
    Test to check the functionality of service3800() function
    """
    dummy_result = [{"task": {"display_value": "xyz"}, "task.short_description": "xxx"}]
    mock_get_sys_id.return_value = ["3433fcd8dbfa18102495a235ca960001"]
    mock_rest_get.return_value = {"result": dummy_result}
    spark = connector.SparkTicketService()
    spark_response = spark.service3800(
        db_table=db_table,
        affected_cis=["xyz.test.bllab.it.bb.sky.com"],
        ci_filter=None,
        start_date=1544681400,
        end_date=1545981400,
        short_description=True,
    )
    assert spark_response == dummy_result


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_service3020(mock_rest_get):
    """
    Test to check the functionality of service3020 function
    """
    dummy_result = {
        "event_name": "DE Bank Holiday",
        "event_start_time": "14/08/2020 22:00:00",
        "event_end_time": "15/08/2020 21:59:59",
        "applies_to": "cmdb_ci_service",
        "condition": "Business areas CONTAINS DE Broadcasting or Business areas CONTAINS DE Information Technology",
        "blackout_schedule": "DE - Bank Holidays ",
        "blackout_schedule_type": "Change Freeze",
    }
    mock_rest_get.return_value = {"result": dummy_result}
    spark = connector.SparkTicketService()
    spark_response = spark.service3020(start_date=1572794340, end_date=1572894600)
    assert spark_response == dummy_result
    mock_rest_get.assert_called_once_with(
        service_url["3020"], headers=headers, params={"start_date": 1572794340, "end_date": 1572894600}
    )


@pytest.mark.parametrize("start_date, end_date", invalid_date_params)
def test_service_3020_invalid_request(start_date, end_date):
    """
    Test to check the functionality of service3020 function
    """
    with pytest.raises(InvalidRequest):
        spark = connector.SparkTicketService()
        spark.service3020(start_date=start_date, end_date=end_date)


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@pytest.mark.parametrize("exception_type", exceptions_srvc3020)
def test_service3020_exceptions(mock_rest_get, exception_type):
    """
    Test to check if service3020() raises GenericConnectorsException
    """
    mock_rest_get.side_effect = exception_type("dummy error")
    with pytest.raises(GenericConnectorsException):
        spark = connector.SparkTicketService()
        spark.service3020(start_date=1572794340, end_date=1572894600)


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
def test_service3045_operation_list(mock_rest_post):
    """
    Test to check the functionality of service3045() function for attachment list operation.
    """
    request_body = {"operation": "list", "ticket_number": "CHG0115712"}
    dummy_response = {
        "result": [
            {
                "createdOn": "2020-07-06 14:38:10",
                "fileName": "fileName.txt",
                "state": "available",
                "updatedOn": "2020-07-06 14:38:10",
            },
            {
                "createdOn": "2020-06-29 14:46:39",
                "fileName": "document1.doc",
                "state": "available",
                "updatedOn": "2020-06-29 14:46:41",
            },
        ]
    }
    mock_rest_post.return_value = dummy_response
    spark = connector.SparkTicketService()
    srvc3045_response = spark.service3045(**request_body)
    assert srvc3045_response == dummy_response
    mock_rest_post.assert_called_once_with(
        service_url["3045"], headers=headers, data={"ticket_number": f"""{request_body["ticket_number"]}"""}
    )


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
def test_service3045_operation_add(mock_rest_post):
    """
    Test to check the functionality of service3045() function for attachment add operation.
    """
    request_body = {
        "operation": "add",
        "ticket_number": "CHG0115712",
        "filename": "fileName.txt",
        "attachment": "vxhxgjkdxdhlxjsa",
        "operation_by": "xyz",
    }
    dummy_response = {"result": {"details": "CHG0115712 (ATTACHMENT ADDED)"}}
    mock_rest_post.return_value = dummy_response
    spark = connector.SparkTicketService()
    srvc3045_response = spark.service3045(**request_body)
    assert srvc3045_response == dummy_response
    mock_rest_post.assert_called_once_with(
        service_url["3045"],
        headers=headers,
        data=f"""ticket_number={request_body["ticket_number"]}&filename={request_body["filename"]}"""
        f"""&attachment={request_body["attachment"]}&operation_by={request_body["operation_by"]}"""
        f"""&operation={request_body["operation"]}""",
    )


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
def test_service3045_operation_remove(mock_rest_post):
    """
    Test to check the functionality of service3045() function for attachment remove operation.
    """
    request_body = {
        "operation": "remove",
        "ticket_number": "CHG0115712",
        "filename": "fileName.txt",
        "operation_by": "xyz",
    }
    dummy_response = {"result": {"details": "CHG0115712 (ATTACHMENT REMOVED)"}}
    mock_rest_post.return_value = dummy_response
    spark = connector.SparkTicketService()
    srvc3045_response = spark.service3045(**request_body)
    assert srvc3045_response == dummy_response
    mock_rest_post.assert_called_once_with(
        service_url["3045"],
        headers=headers,
        data=f"""ticket_number={request_body["ticket_number"]}&filename={request_body["filename"]}"""
        f"""&operation={request_body["operation"]}&operation_by={request_body["operation_by"]}""",
    )


def test_service3045_operation_remove_invalid_request():
    """
    Test to check if service3045() function raises InvalidRequest due to KeyError occurring out of mandatory parameter
    missing
    """
    request_body = {"operation": "remove", "ticket_number": "CHG0115712", "filename": "fileName.txt"}
    with pytest.raises(InvalidRequest):
        spark = connector.SparkTicketService()
        spark.service3045(**request_body)


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@pytest.mark.parametrize("error_caused, raised_exception", exceptions_srvc3045)
def test_service3045_exceptions(mock_rest_post, error_caused, raised_exception):
    """
    Test to check if service3045() function raises different exceptions
    missing
    """
    request_body = {
        "operation": "remove",
        "ticket_number": "CHG0115712",
        "filename": "fileName.txt",
        "operation_by": "xyz",
    }
    mock_rest_post.side_effect = error_caused("dummy error")
    with pytest.raises(raised_exception):
        spark = connector.SparkTicketService()
        spark.service3045(**request_body)


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_service3400(mock_rest_get):
    """
    Test to check the functionality of service3400() function.
    """
    ticket_number = "CHG0115712"
    dummy_result = {"result ": [{"end_date": "1573994340", "start_date": "1572794340", "state": "APPROVED"}]}
    mock_rest_get.return_value = dummy_result
    spark = connector.SparkTicketService()
    spark_response = spark.service3400(ticket_number=ticket_number)
    assert spark_response == dummy_result
    mock_rest_get.assert_called_once_with(service_url["3400"], headers=headers, params={"ticket_number": ticket_number})


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@pytest.mark.parametrize("exception_type", exceptions_srvc3400)
def test_service3400_exceptions(mock_rest_get, exception_type):
    """
    Test to check if service3400() raises GenericConnectorsException
    """
    mock_rest_get.side_effect = exception_type("dummy error")
    with pytest.raises(GenericConnectorsException):
        spark = connector.SparkTicketService()
        spark.service3400(ticket_number="CHG0115712")


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
def test_service3405(mock_rest_post, mock_srvc_3040):
    """
    Test to check the functionality of service3405() function.
    """
    mock_srvc_3040.return_value = True
    request_params = {
        "cmdbci": [
            {"ciName": "ma0.test.bllab.it.bb.sky.com", "impactType": "No Service Impact"},
            {"ciName": "ma0.test1.bllab.it.bb.sky.com", "impactType": "Full Outage"},
        ],
        "createdBy": "xyz",
        "start_date": "1572794340",
        "end_date": "1573994340",
        "assignment_group": "UK IP Network Development Test and Delivery",
        "parent_change": "CHG0084714",
        "short_description": "ES configuration",
        "description": "Ethernet Segment configuration",
        "config_group": "Broadband & Talk - Metro Aggregation",
    }
    dummy_result = {"result": {"details": "CTASK0071941 (MINOR CHANGE RAISED)"}}
    mock_rest_post.return_value = dummy_result
    spark = connector.SparkTicketService()
    response = spark.service3405(**request_params)
    assert response == dummy_result


def test_service3405_resource_service_not_available():
    """
    Test to check if service3405() function raises ResourceServiceNotAvailable with unsupported chgType (change type)
    """
    request_params = {
        "chgType": "routine",
        "cmdbci": [
            {"ciName": "ma0.test.bllab.it.bb.sky.com", "impactType": "No Service Impact"},
            {"ciName": "ma0.test1.bllab.it.bb.sky.com", "impactType": "Full Outage"},
        ],
        "createdBy": "xyz",
        "start_date": "1572794340",
        "end_date": "1573994340",
        "assignment_group": "UK IP Network Development Test and Delivery",
        "parent_change": "CHG0084714",
        "short_description": "ES configuration",
        "description": "Ethernet Segment configuration",
        "config_group": "Broadband & Talk - Metro Aggregation",
    }
    with pytest.raises(ResourceServiceNotAvailable):
        spark = connector.SparkTicketService()
        spark.service3405(**request_params)


def test_service3405_key_error():
    """
    Test to check if service3405() function raises InvalidRequest due to KeyError out of mandatory parameter missing
    """
    request_params = {
        "cmdbci": [
            {"ciName": "ma0.test.bllab.it.bb.sky.com", "impactType": "No Service Impact"},
            {"ciName": "ma0.test1.bllab.it.bb.sky.com", "impactType": "Full Outage"},
        ],
        "createdBy": "xyz",
        "start_date": "1572794340",
        "end_date": "1573994340",
        "assignment_group": "UK IP Network Development Test and Delivery",
        "short_description": "ES configuration",
        "description": "Ethernet Segment configuration",
        "config_group": "Broadband & Talk - Metro Aggregation",
    }
    with pytest.raises(InvalidRequest):
        spark = connector.SparkTicketService()
        spark.service3405(**request_params)


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
def test_service3405_with_service3040_failing(mock_rest_post, mock_srvc_3040):
    """
    Test to check if service3405() function raises ResourceServiceNotAvailable when service3040 results into failure.
    """
    mock_srvc_3040.return_value = False
    request_params = {
        "cmdbci": [
            {"ciName": "ma0.test.bllab.it.bb.sky.com", "impactType": "No Service Impact"},
            {"ciName": "ma1.test.bllab.it.bb.sky.com", "impactType": "Full Outage"},
        ],
        "createdBy": "xyz",
        "start_date": "1572794340",
        "end_date": "1573994340",
        "assignment_group": "UK IP Network Development Test and Delivery",
        "parent_change": "CHG0084714",
        "short_description": "ES configuration",
        "description": "Ethernet Segment configuration",
        "config_group": "Broadband & Talk - Metro Aggregation",
    }
    dummy_result = {"result": {"details": "CTASK0071941 (MINOR CHANGE RAISED)"}}
    mock_rest_post.return_value = dummy_result
    with pytest.raises(ResourceServiceNotAvailable):
        spark = connector.SparkTicketService()
        spark.service3405(**request_params)


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@pytest.mark.parametrize("exception_type", exceptions_srvc3405)
def test_service3405_exceptions(mock_rest_post, exception_type):
    """
    Test to check if service3405() raises GenericConnectorsException
    """
    request_params = {
        "cmdbci": [
            {"ciName": "ma0.test.bllab.it.bb.sky.com", "impactType": "No Service Impact"},
            {"ciName": "ma0.test1.bllab.it.bb.sky.com", "impactType": "Full Outage"},
        ],
        "createdBy": "xyz",
        "start_date": "1572794340",
        "end_date": "1573994340",
        "assignment_group": "UK IP Network Development Test and Delivery",
        "parent_change": "CHG0084714",
        "short_description": "ES configuration",
        "description": "Ethernet Segment configuration",
        "config_group": "Broadband & Talk - Metro Aggregation",
    }
    mock_rest_post.side_effect = exception_type("dummy error")
    with pytest.raises(GenericConnectorsException):
        spark = connector.SparkTicketService()
        spark.service3405(**request_params)


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.services.itsm.connector.time")
@pytest.mark.parametrize("ci_list", param_ci_list)
def test_service3040_success(mock_time, mock_rest_post, ci_list):
    """
    Test to check the functionality of service3040() function.
    """
    default_sleep = connector.sleep_interval
    connector.sleep_interval = 1
    mock_rest_post.return_value = {"result": {"details": "CHG0115712 dummy_details"}}
    spark = connector.SparkTicketService()
    ret_val = spark.service3040(
        ticket="CHG0115712",
        ci_list=ci_list,
        impact_start="1572794340",
        impact_end="1576994340",
        operation="add",
        operation_by="xyz",
    )
    connector.sleep_interval = default_sleep
    assert ret_val
    assert mock_rest_post.call_count == len(ci_list)


@patch("connectors.core.services.itsm.connector.time")
def test_service3040_failure(time_mock):
    """
    Test to check the functionality of service3040() function. Function fails due to TypeError.
    """
    spark = connector.SparkTicketService()
    ret_val = spark.service3040(
        ticket="CHG0115712",
        ci_list=[{"ciName": "ma0.test.bllab.it.bb.sky.com", "impactType": "No Service Impact"}],
        impact_start=1572794340,
        impact_end=1576994340,
        operation="add",
        operation_by="xyz",
    )
    assert not ret_val


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
def test_service3406(mock_rest_post):
    """
    Test to check the functionality of service3406() function.
    """
    request_body = {
        "ticket_number": "CHG0115712",
        "updated_by": "xyz",
        "assigned_to": "xyz",
        "state": "Closed Successful",
        "work_notes": "Change completed successfully",
    }
    dummy_result = {"result": {"details": "CHG0115712 (CLOSED)"}}
    mock_rest_post.return_value = dummy_result
    spark = connector.SparkTicketService()
    response = spark.service3406(**request_body)
    assert response == dummy_result
    mock_rest_post.assert_called_once_with(
        service_url["3406"],
        headers=headers,
        data=f"""ticket_number={request_body["ticket_number"]}&updated_by={request_body["updated_by"]}"""
        f"""&assigned_to={request_body["assigned_to"]}&state={request_body["state"]}"""
        f"""&work_notes={request_body["work_notes"]}""",
    )


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@pytest.mark.parametrize("exception_type", exceptions_srvc3406)
def test_service3406_exceptions(mock_rest_post, exception_type):
    """
    Test to check if service3406() function raises GenericConnectorsException
    """
    request_body = {
        "ticket_number": "CHG0115712",
        "updated_by": "xyz",
        "assigned_to": "xyz",
        "state": "Closed Successful",
        "work_notes": "Change completed successfully",
    }
    mock_rest_post.side_effect = exception_type("dummy error")
    with pytest.raises(GenericConnectorsException):
        spark = connector.SparkTicketService()
        spark.service3406(**request_body)


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
def test_service3030(mock_rest_post):
    """
    Test to check the functionality of service3030() function.
    """
    request_body = {
        "ticket_type": "TPCHG",
        "ticket_number": "CHG0115712",
        "third_party": "Amdocs",
        "impact": "Reduced capacity",
        "reason": "Maintenance-Sky network Upgrade ",
    }
    dummy_result = {"result": {"details": "TPCHG0023017 (WHOLESALE PORTAL TASK CREATED)"}}
    mock_rest_post.return_value = dummy_result
    spark = connector.SparkTicketService()
    response = spark.service3030(**request_body)
    assert response == dummy_result
    mock_rest_post.assert_called_once_with(
        service_url["3030"],
        headers=headers,
        data=f"""ticket_type={request_body["ticket_type"]}&ticket_number={request_body["ticket_number"]}"""
        f"""&third_party={request_body["third_party"]}&impact={request_body["impact"]}"""
        f"""&reason={request_body["reason"]}""",
    )


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
def test_service3030_error(mock_rest_post):
    """
    Test to check the functionality of service3030() function.
    """
    request_body = {
        "ticket_type": "TPCHG",
        "ticket_number": "CHG0115712",
        "third_party": "Amdocs",
        "impact": "Reduced capacity",
        "reason": "Maintenance-Sky network Upgrade ",
    }
    dummy_result = {
        "result": {
            "error_details": "cannot create wholesale portal task. task already exists for: Flexgrid in CHG0225341"
        }
    }
    mock_rest_post.return_value = dummy_result
    spark = connector.SparkTicketService()
    response = spark.service3030(**request_body)
    assert response == dummy_result
    mock_rest_post.assert_called_once_with(
        service_url["3030"],
        headers=headers,
        data=f"""ticket_type={request_body["ticket_type"]}&ticket_number={request_body["ticket_number"]}"""
        f"""&third_party={request_body["third_party"]}&impact={request_body["impact"]}"""
        f"""&reason={request_body["reason"]}""",
    )


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@pytest.mark.parametrize("exception_type", exceptions_srvc3030)
def test_service3030_case1(mock_rest_post, exception_type):
    """
    Test to check the functionality of service3030() function.
    """
    request_body = {
        "ticket_type": "TPCHG",
        "third_party": "Amdocs",
        "impact": "Reduced capacity",
        "reason": "Maintenance-Sky network Upgrade ",
    }
    mock_rest_post.side_effect = exception_type("dummy error")
    with pytest.raises(InvalidRequest):
        spark = connector.SparkTicketService()
        spark.service3030(**request_body)


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@pytest.mark.parametrize("exception_type", exceptions_srvc3030)
def test_service3030_case2(mock_rest_post, exception_type):
    """
    Test to check the functionality of service3030() function.
    """
    request_body = {
        "ticket_type": "TPCHG",
        "ticket_number": "CHG0115712",
        "third_party": "Amdocs",
        "impact": "Reduced capacity",
        "reason": "Maintenance-Sky network Upgrade ",
    }
    mock_rest_post.side_effect = exception_type("dummy error")
    with pytest.raises(GenericConnectorsException):
        spark = connector.SparkTicketService()
        spark.service3030(**request_body)


@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@pytest.mark.parametrize("exception_type", exceptions_srvc3030_1)
def test_service3030_case3(mock_rest_post, exception_type):
    """
    Test to check the functionality of service3030() function.
    """
    request_body = {
        "ticket_type": "TPCHG",
        "ticket_number": "CHG0115712",
        "third_party": "Amdocs",
        "impact": "Reduced capacity",
        "reason": "Maintenance-Sky network Upgrade ",
    }
    mock_rest_post.side_effect = exception_type("dummy error")
    with pytest.raises(ResourceServiceNotAvailable):
        spark = connector.SparkTicketService()
        spark.service3030(**request_body)


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.services.itsm.connector.SparkTicketService.get_sys_id")
@pytest.mark.parametrize("db_table", ["u_cmdb_ci_circuit"])
def test_service3800_1(mock_get_sys_id, mock_rest_get, db_table):
    """
    Test to check the functionality of service3800() function
    """
    mock_get_sys_id.return_value = ["3433fcd8dbfa18102495a235ca960001"]
    mock_rest_get.return_value = {"result": []}
    spark = connector.SparkTicketService()
    spark_response = spark.service3800(
        db_table=db_table,
        affected_cis=["ONEA123"],
        ci_filter=None,
        start_date=1544681400,
        end_date=1545981400,
    )
    assert spark_response == {"result": []}


@patch("connectors.core.services.itsm.connector.SparkTicketService.get_sys_id")
@patch("connectors.core.services.itsm.connector.SparkTicketService.execute_query")
@pytest.mark.parametrize("db_table", ["u_cmdb_ci_circuit"])
def test_service3800_2(mock_query, mock_sys, db_table):
    """
    Test to check the functionality of service3800() function
    """
    mock_query.return_value = [
        {
            "name": "ONEA50106115",
            "u_customer": {
                "display_value": "SSE",
                "link": "https://skyuat2.service-now.com/api/now/table/core_company/e2df05dcdb0017808efdb54ffe961991",
            },
        },
        {
            "name": "ONEA50106661",
            "u_customer": {
                "display_value": "Entanet",
                "link": "https://skyuat2.service-now.com/api/now/table/core_company/76f10eb9dbd6ab40cfdbb54ffe96199d",
            },
        },
    ]
    mock_sys.return_value = ["3433fcd8dbfa18102495a235ca960001"]
    spark = connector.SparkTicketService()
    spark_response = spark.service3800(
        db_table=db_table,
        affected_cis=["ONEA123"],
        ci_filter=None,
        start_date=1544681400,
        end_date=1545981400,
    )
    assert spark_response == {
        "result": [
            {"circuitID": "ONEA50106115", "u_customer": {"displayValue": "SSE"}},
            {"circuitID": "ONEA50106661", "u_customer": {"displayValue": "Entanet"}},
        ]
    }


def test_empty_list():
    spark = connector.SparkTicketService()
    spark.max_ci_list_length = 30
    assert spark._break_down_list([]) == []


def test_single_list_less_than_25():
    spark = connector.SparkTicketService()
    spark.max_ci_list_length = 20
    assert spark._break_down_list([1, 2, 3]) == [[1, 2, 3]]


def test_single_list_25_elements():
    spark = connector.SparkTicketService()
    spark.max_ci_list_length = 25
    input_list = list(range(25))
    assert spark._break_down_list(input_list) == [input_list]


def test_multiple_lists_25_elements_each():
    spark = connector.SparkTicketService()
    spark.max_ci_list_length = 25
    input_list = list(range(50))
    expected_output = [list(range(25)), list(range(25, 50))]
    assert spark._break_down_list(input_list) == expected_output


def test_multiple_lists_last_list_less_than_25_elements():
    spark = connector.SparkTicketService()
    spark.max_ci_list_length = 25
    input_list = list(range(60))
    expected_output = [list(range(25)), list(range(25, 50)), list(range(50, 60))]
    assert spark._break_down_list(input_list) == expected_output


@patch("connectors.core.services.itsm.connector.SparkTicketService.execute_query")
def test__thread_worker(execute_query_mock):
    execute_query_mock.return_value = [{"dummykey": "dummyval"}]
    spark = connector.SparkTicketService()
    args = ("url", [1], "dummy")
    results = []
    lock = threading.Lock()
    spark._thread_worker(args, results, lock)
    spark.execute_query.assert_called_once_with("url", [1], "dummy")
    assert results == [{"dummykey": "dummyval"}]


@patch("connectors.core.services.itsm.connector.SparkTicketService._break_down_list")
@patch("connectors.core.services.itsm.connector.threading")
@patch("connectors.core.services.itsm.connector.SparkTicketService._thread_worker")
@patch("connectors.core.services.itsm.connector.time")
def test_execute_sub_queries_in_parallel(time_mock, _thread_worker_mock, threading_mock, _break_down_list_mock):
    _break_down_list_mock.return_value = [[1, 2], [3, 4], [5]]
    spark = connector.SparkTicketService()
    assert (
        spark._execute_sub_queries_in_parallel(
            "dummy_url", "dummy_table", [1, 2, 3, 4, 5], "dummy_query", "dummy_ci_filter", "dummy_return_fields"
        )
        == []
    )
    spark._break_down_list.assert_called_once_with([1, 2, 3, 4, 5])
    assert threading_mock.Thread().start.call_count == 3
    assert time_mock.sleep.call_count == 2


@patch("connectors.core.services.itsm.connector.SparkTicketService.execute_query")
@patch("connectors.core.services.itsm.connector.SparkTicketService._execute_sub_queries_in_parallel")
@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.services.itsm.connector.SparkTicketService.get_sys_id")
def test_service3800_affected_ci_not_exceeding_max(
    mock_get_sys_id, mock_rest_get, mock__execute_sub_queries_in_parallel, mock_execute_query
):
    mock_execute_query.return_value = {"key1": "val1", "key2": "val2", "keyn": "valn"}
    spark = connector.SparkTicketService()
    spark_response = spark.service3800(
        db_table="task_ci",
        affected_cis=["xyz.test.bllab.it.bb.sky.com"],
        ci_filter="ci_list",
        start_date=1544681400,
        end_date=1545981400,
    )
    assert spark_response == {"key1": "val1", "key2": "val2", "keyn": "valn"}


@patch("connectors.core.services.itsm.connector.SparkTicketService.execute_query")
@patch("connectors.core.services.itsm.connector.SparkTicketService._execute_sub_queries_in_parallel")
@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.services.itsm.connector.SparkTicketService.get_sys_id")
def test_service3800_affected_ci_exceeding_max(
    mock_get_sys_id, mock_rest_get, mock__execute_sub_queries_in_parallel, mock_execute_query
):
    mock__execute_sub_queries_in_parallel.return_value = {"key1": "val1", "key2": "val2", "keyn": "valn"}
    spark = connector.SparkTicketService()
    spark.max_ci_list_length = 2
    spark_response = spark.service3800(
        db_table="task_ci",
        affected_cis=["xyz.test.bllab.it.bb.sky.com", "abc.test.bllab.it.bb.sky.com", "qwe.test.bllab.it.bb.sky.com"],
        ci_filter="ci_list",
        start_date=1544681400,
        end_date=1545981400,
    )
    assert spark_response == {"key1": "val1", "key2": "val2", "keyn": "valn"}


@patch("connectors.core.services.itsm.connector.SparkTicketService.spark_request")
def test_service_3401(spark_request_mock):
    spark_request_mock.return_value = {"result": {"key": "value"}}

    spark = connector.SparkTicketService()
    response = spark.service3401(
        **{
            "templateName": "test template name",
            "createdBy": "ABC01",
            "start_date": "100",
            "end_date": "110",
            "short_description": "test description",
            "justification": "test justification",
            "implementation_plan": "test implementation_plan",
            "configuration_item": "test configuration_item",
        }
    )

    assert response == {
        "result": {
            "key": "value",
        },
    }
    spark_request_mock.assert_called_once_with(
        "post",
        "https://sparkproxyuat.azure-api.net/service3401/request",
        data="template=test template name&created_by=ABC01&start_date=100&"
        "end_date=110&short_description=test description&implementation_plan=test implementation_plan&"
        "justification=test justification&cmdb_ci=test configuration_item",
    )


def test_get_task_ci_details():
    spark = connector.SparkTicketService()
    ci_filter, query, return_fields = spark._get_task_ci_details(
        **{"ci_filter": True, "start_date": [1, 1], "end_date": [2, 2], "sys_id_list": ["123", "456"]}
    )
    assert ci_filter == "ci_item"
    assert (
        query == "task.numberSTARTSWITHCHG^task.active=true^task.state=-2^ORtask.state=-1^"
        "task.ref_change_request.start_dateBETWEENjavascript:gs.dateGenerate('1','1')"
        "@javascript:gs.dateGenerate('2','2')^ORtask.ref_change_request.end_date"
        "BETWEENjavascript:gs.dateGenerate('1','1')"
        "@javascript:gs.dateGenerate('2','2')^ci_itemLIKE123^ORci_itemLIKE456"
        "^NQtask.numberSTARTSWITHCHG^task.active=true"
        "^task.state=-2^ORtask.state=-1^task.ref_change_request.start_date<javascript:gs.dateGenerate('1','1')"
        "^task.ref_change_request.end_date>javascript:gs.dateGenerate('2','2')"
    )
    assert return_fields == "ci_item,u_impact_type,task,u_impact_start_date,u_impact_end_date"


def test_get_task_ci_details_lag_upgrade():
    spark = connector.SparkTicketService()
    ci_filter, query, return_fields = spark._get_task_ci_details(
        **{
            "ci_filter": True,
            "start_date": [1, 1],
            "end_date": [2, 2],
            "sys_id_list": ["123", "456"],
            "short_description_value": "[DNE] STD6588 - Capacity LAG Upgrade - "
            "[TA-MA NBS] (79018) ma0.lcrib.isp.sky.com|ta0.mimnc.isp.sky.com",
        }
    )
    assert ci_filter == "ci_item"
    assert (
        query == "task.numberSTARTSWITHCHG^task.active=true^task.state=-2^ORtask.state=-1^ORtask.state=-3"
        "^ORtask.state=-7^ORtask.state=-4^"
        "task.ref_change_request.start_dateBETWEENjavascript:gs.dateGenerate('1','1')"
        "@javascript:gs.dateGenerate('2','2')^ORtask.ref_change_request.end_dateBETWEEN"
        "javascript:gs.dateGenerate('1','1')@javascript:gs.dateGenerate('2','2')"
        "^ci_itemLIKE123^ORci_itemLIKE456^NQtask.numberSTARTSWITHCHG"
        "^task.active=true^task.state=-2^ORtask.state=-1^task.ref_change_request.start_date"
        "<javascript:gs.dateGenerate('1','1')^task.ref_change_request.end_date>javascript:gs.dateGenerate('2','2')"
    )
    assert return_fields == "ci_item,u_impact_type,task,u_impact_start_date,u_impact_end_date"
