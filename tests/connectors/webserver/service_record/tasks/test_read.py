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
from unittest.mock import patch

# DNE Library
from connectors.webserver.service_record.tasks.read import validate_payload

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


@patch("connectors.webserver.service_record.tasks.read.ServiceDB")
def test_validate_payload_case1(db_mock):
    """
    Test to check the functionality of validate payload - Provided sort param createdDate1 is not present in
    schema mapper sortMaps
    """
    expected_error = [
        {
            "code": "ERR-011-078-1005",
            "message": "Provided sort param createdDate1 is not present in schema mapper sortMaps: "
            "['createdDate', 'modifiedDate', 'orderId']",
        }
    ]
    local_user_model = deepcopy(user_model)
    local_user_model["sort"][0]["param"] = "createdDate1"
    error_details = validate_payload(local_user_model, schema_record, [])
    assert error_details == expected_error


@patch("connectors.webserver.service_record.tasks.read.ServiceDB")
def test_validate_payload_case2(db_mock):
    """
    Test to check the functionality of validate payload - Provided filter param createdDate is not present in
    schema mapper filterMaps
    """
    expected_error = [
        {
            "code": "ERR-011-078-1002",
            "message": "Provided filter param createdDate is not present in schema mapper filterMaps: ['serviceId',"
            " 'orderId', 'jobId', 'state', 'assetId']",
        }
    ]
    local_user_model = deepcopy(user_model)
    local_user_model["filters"][0]["param"] = "createdDate"
    error_details = validate_payload(local_user_model, schema_record, [])
    assert error_details == expected_error


@patch("connectors.webserver.service_record.tasks.read.ServiceDB")
def test_validate_payload_case3(db_mock):
    """
    Test to check the functionality of validate payload - Provided filter value $$$ must not contain $ character
    """
    expected_error = [{"code": "ERR-011-078-1003", "message": "Provided filter value $$$ must not contain $ character"}]
    local_user_model = deepcopy(user_model)
    local_user_model["filters"][0]["param"] = "jobId"
    local_user_model["filters"][0]["values"] = ["$$$"]
    error_details = validate_payload(local_user_model, schema_record, [])
    assert error_details == expected_error


@patch("connectors.webserver.service_record.tasks.read.ServiceDB")
def test_validate_payload_case4(db_mock):
    """
    Test to check the functionality of validate payload - Provided filter value 123 did not match with the pattern
    """
    expected_error = [
        {
            "code": "ERR-011-078-1004",
            "message": "Provided filter value 123 did not match with the pattern ^[A-Z]+-[0-9]+[0-9]*$",
        }
    ]
    local_user_model = deepcopy(user_model)
    local_user_model["filters"][0]["values"] = ["123"]
    error_details = validate_payload(local_user_model, schema_record, [])
    assert error_details == expected_error
