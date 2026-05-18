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

# DNE Library
from connectors.core.services.service_record.connector import ServiceRecordService

user_model = {
    "service": "wholesale",
    "data": "service",
    "filters": [{"param": "orderId", "operator": "eq", "values": ["BPM-123"]}],
    "sort": [{"param": "createdDate", "order": "dsc"}],
}

schema_record = {
    "_id": "6308650aeab9aa28c1b84b77",
    "usecase": "wholesale",
    "service": {
        "responseMap": {
            "_id": 0,
            "service.wholesale.ma.neighbors": 0,
            "service.wholesale.ma.commitIds": 0,
            "service.wholesale.ma.qos": 0,
            "service.wholesale.ma.oldQos": 0,
            "service.wholesale.ma.interfaceInfo": 0,
            "service.wholesale.wspe.primary.neighbors": 0,
            "service.wholesale.wspe.primary.commitIds": 0,
            "service.wholesale.wspe.primary.qos": 0,
            "service.wholesale.wspe.primary.oldQos": 0,
            "service.wholesale.wspe.primary.interfaceInfo": 0,
            "service.wholesale.wspe.secondary.commitIds": 0,
            "service.wholesale.wspe.secondary.neighbors": 0,
            "service.wholesale.wspe.secondary.qos": 0,
            "service.wholesale.wspe.secondary.oldQos": 0,
            "service.wholesale.wspe.secondary.interfaceInfo": 0,
        },
        "responseMapBrief": {"_id": 0, "data": 0},
        "filterMaps": [
            {"serviceId": "serviceId", "pattern": "^[0-9a-zA-Z-\\/_.]*$"},
            {"orderId": "orderId", "pattern": "^[A-Z]+-[0-9]+[0-9]*$"},
            {"jobId": "jobId"},
            {
                "state": "state",
                "pattern": "PLANNED | PROVISIONING | PROVISIONED | ACTIVE | INACTIVE | ROLLBACK | EXCEPTION | "
                "DECOMMISSIONING | DECOMMISSIONED | ROLLBACK-VERIFIED ",
            },
            {"assetId": "assetId", "pattern": "^SKY"},
        ],
        "sortMaps": [{"createdDate": "createdDate"}, {"modifiedDate": "modifiedDate"}, {"orderId": "orderId"}],
    },
    "audit": {
        "responseMap": {"_id": 0, "data.config.metadata.commitId": 0},
        "filterMaps": [
            {"serviceId": "serviceId", "pattern": "^[0-9a-zA-Z-\\/_.]*$"},
            {"orderId": "orderId", "pattern": "^[A-Z]+-[0-9]+[0-9]*$"},
            {"jobId": "jobId"},
            {
                "state": "state",
                "pattern": "PLANNED | PROVISIONING | PROVISIONED | ACTIVE | INACTIVE | ROLLBACK | EXCEPTION | "
                "DECOMMISSIONING | DECOMMISSIONED | ROLLBACK-VERIFIED ",
            },
            {"assetId": "assetId", "pattern": "^SKY"},
        ],
        "sortMaps": [{"createdDate": "createdDate"}, {"modifiedDate": "modifiedDate"}, {"orderId": "orderId"}],
    },
}


def test_get_match_query_case1():
    """
    Test to check the functionality of get_match_query - with no filterLogicalOperator
    """
    expected_query = {"orderId": {"$eq": "BPM-123"}}
    local_user_model = deepcopy(user_model)
    service_instance = ServiceRecordService(local_user_model, {})
    query = service_instance.get_match_query()
    assert expected_query == query


def test_get_match_query_case2():
    """
    Test to check the functionality of get_match_query - with filterLogicalOperator
    """
    expected_query = {
        "$and": [
            {"assetId": {"$eq": "SKY-FLDA-132"}},
            {"state": {"$nq": "ACTIVE"}},
            {"jobId": {"$gt": "2ve-0620-4f50-fb9-75d82b9a8"}},
            {"orderId": {"$in": ["BPM-2817", "BPM-896807", "BPM-157737"]}},
        ]
    }
    local_user_model = deepcopy(user_model)
    local_user_model["filters"] = [
        {"param": "assetId", "operator": "eq", "values": ["SKY-FLDA-132"], "filterLogicalOperator": "and"},
        {"param": "state", "operator": "nq", "values": ["ACTIVE"], "filterLogicalOperator": "and"},
        {"param": "jobId", "operator": "gt", "values": ["2ve-0620-4f50-fb9-75d82b9a8"], "filterLogicalOperator": "and"},
        {"param": "orderId", "operator": "in", "values": ["BPM-2817", "BPM-896807", "BPM-157737"]},
    ]
    service_instance = ServiceRecordService(local_user_model, {})
    query = service_instance.get_match_query()
    assert expected_query == query


def test_get_sort_query_case1():
    """
    Test to check the functionality of get_sort_query with decreasing order
    """
    expected_query = {"createdDate": -1}
    local_user_model = deepcopy(user_model)
    service_instance = ServiceRecordService(local_user_model, {})
    query = service_instance.get_sort_query()
    assert expected_query == query


def test_get_sort_query_case2():
    """
    Test to check the functionality of get_sort_query with increasing order
    """
    expected_query = {"createdDate": 1}
    local_user_model = deepcopy(user_model)
    local_user_model["sort"][0]["order"] = "asc"
    service_instance = ServiceRecordService(local_user_model, {})
    query = service_instance.get_sort_query()
    assert expected_query == query


@patch("connectors.core.services.service_record.connector.ServiceDB")
def test_get_service_record(db_mock):
    """
    Test to check the functionality of get_service_record
    """
    expected_total_records = 77
    expected_start_index = 71
    expected_end_index = 77
    local_user_model = deepcopy(user_model)
    local_schema_record = deepcopy(schema_record)
    local_user_model["pageNumber"] = 8
    service_instance = ServiceRecordService(local_user_model, local_schema_record)
    service_instance.get_total_records = Mock()
    service_instance.get_total_records.return_value = [{"totalRecords": 77}]
    db_mock.aggregate.return_value = []
    result = service_instance.get_service_record()
    assert result["totalRecords"] == expected_total_records
    assert result["pageStartIndex"] == expected_start_index
    assert result["pageEndIndex"] == expected_end_index


@patch("connectors.core.services.service_record.connector.ServiceDB")
def test_get_service_record_query(db_mock):
    """
    Test the built query in _get_service_record
    """
    local_user_model = deepcopy(user_model)
    local_schema_record = deepcopy(schema_record)
    local_user_model["pageNumber"] = 8
    service_instance = ServiceRecordService(local_user_model, local_schema_record)
    service_instance.get_total_records = Mock(return_value=[{"totalRecords": 77}])
    service_instance.get_service_record()
    db_mock().aggregate.assert_called_once_with(
        [
            {"$match": {"orderId": {"$eq": "BPM-123"}}},
            {"$sort": {"createdDate": -1}},
            {
                "$project": {
                    "_id": 0,
                    "service.wholesale.ma.neighbors": 0,
                    "service.wholesale.ma.commitIds": 0,
                    "service.wholesale.ma.qos": 0,
                    "service.wholesale.ma.oldQos": 0,
                    "service.wholesale.ma.interfaceInfo": 0,
                    "service.wholesale.wspe.primary.neighbors": 0,
                    "service.wholesale.wspe.primary.commitIds": 0,
                    "service.wholesale.wspe.primary.qos": 0,
                    "service.wholesale.wspe.primary.oldQos": 0,
                    "service.wholesale.wspe.primary.interfaceInfo": 0,
                    "service.wholesale.wspe.secondary.commitIds": 0,
                    "service.wholesale.wspe.secondary.neighbors": 0,
                    "service.wholesale.wspe.secondary.qos": 0,
                    "service.wholesale.wspe.secondary.oldQos": 0,
                    "service.wholesale.wspe.secondary.interfaceInfo": 0,
                }
            },
            {"$skip": 70},
            {"$limit": 10},
        ],
        maxTimeMS=ANY,
    )


@patch("connectors.core.services.service_record.connector.ServiceDB")
def test_get_service_record_query_include(db_mock):
    """
    Test the built query in _get_service_record with include brief
    """
    local_user_model = deepcopy(user_model)
    local_schema_record = deepcopy(schema_record)
    local_user_model["pageNumber"] = 8
    service_instance = ServiceRecordService(local_user_model, local_schema_record, include="brief")
    service_instance.get_total_records = Mock(return_value=[{"totalRecords": 77}])
    service_instance.get_service_record()
    db_mock().aggregate.assert_called_once_with(
        [
            {"$match": {"orderId": {"$eq": "BPM-123"}}},
            {"$sort": {"createdDate": -1}},
            {"$project": {"_id": 0, "data": 0}},
            {"$skip": 70},
            {"$limit": 10},
        ],
        maxTimeMS=ANY,
    )
