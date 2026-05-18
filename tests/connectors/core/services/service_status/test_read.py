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

# Third Party Library
import pytest

# DNE Library
from connectors.core.exceptions import ServiceDBException
from connectors.core.services.service_status.read import ServiceStatus

kwargs_1 = {"orderId": "BPM-123", "serviceType": ["wholesale"], "operationType": "create"}
kwargs_3 = {"orderId": "BPM-123", "serviceType": ["skyTalk", "wholesale"], "operationType": "create"}

example_delta_base_data_1 = [
    {
        "record": {
            "orderId": "BPM-123",
            "createdDate": "2020-05-13T02:42:28.390Z",
            "state": "CONFIGURING",
        }
    }
]

example_delta_base_data_2 = [
    {
        "record": {
            "orderId": "BPM-123",
            "createdDate": "2020-05-13T02:42:28.390Z",
            "state": "INVALID",
        }
    }
]

example_ubb_logical_data_1 = [
    {
        "record": {
            "orderId": "BPM-123",
            "createdDate": "2020-05-13T02:42:28.390Z",
            "state": "PROVISIONING",
        }
    }
]

example_metro_rr_data_1 = [
    {
        "record": {
            "orderId": "BPM-123",
            "createdDate": "2020-05-13T02:42:28.390Z",
            "state": "ACTIVE",
        }
    }
]

expected_metro_logical_link_data = [
    {
        "record": {
            "orderId": "BPM-123",
            "createdDate": "2020-05-14T02:42:28.390Z",
            "state": "ACTIVE",
            "service": {
                "aEnd": {
                    "hostname": "ma0.eacol.isp.sky.com",
                    "siteType": "T1",
                    "role": "head",
                    "p2pIPv4Address": "10.235.12.92/31",
                    "deviceRole": "m_agg",
                    "vlanId": 0,
                },
                "bEnd": {
                    "hostname": "ma2.eacol.isp.sky.com",
                    "siteType": "T1",
                    "p2pIPv4Address": "10.235.12.90/31",
                    "deviceRole": "m_agg",
                    "role": "child",
                    "vlanId": 0,
                },
            },
        }
    },
    {
        "record": {
            "orderId": "BPM-123",
            "createdDate": "2020-05-14T02:42:28.390Z",
            "state": "INACTIVE",
            "service": {
                "aEnd": {
                    "hostname": "ma0.bllabd2.isp.sky.com",
                    "siteType": "T1",
                    "role": "head",
                    "p2pIPv4Address": "10.235.12.92/31",
                    "deviceRole": "m_agg",
                    "vlanId": 0,
                },
                "bEnd": {
                    "hostname": "ta0.bllabd2.isp.sky.com",
                    "siteType": "T1",
                    "p2pIPv4Address": "10.235.12.90/31",
                    "deviceRole": "m_agg",
                    "role": "child",
                    "vlanId": 0,
                },
            },
        }
    },
]

expected_metro_success_list_1 = [
    {
        "orderId": "BPM-123",
        "createdDate": "2020-05-14T02:42:28.390Z",
        "service": {
            "aEnd": {
                "hostname": "ma0.eacol.isp.sky.com",
                "siteType": "T1",
                "role": "head",
                "p2pIPv4Address": "10.235.12.92/31",
                "deviceRole": "m_agg",
                "vlanId": 0,
            },
            "bEnd": {
                "hostname": "ma2.eacol.isp.sky.com",
                "siteType": "T1",
                "p2pIPv4Address": "10.235.12.90/31",
                "deviceRole": "m_agg",
                "role": "child",
                "vlanId": 0,
            },
        },
    }
]

expected_metro_failure_list_1 = [
    {
        "orderId": "BPM-123",
        "createdDate": "2020-05-14T02:42:28.390Z",
        "service": {
            "aEnd": {
                "hostname": "ma0.bllabd2.isp.sky.com",
                "siteType": "T1",
                "role": "head",
                "p2pIPv4Address": "10.235.12.92/31",
                "deviceRole": "m_agg",
                "vlanId": 0,
            },
            "bEnd": {
                "hostname": "ta0.bllabd2.isp.sky.com",
                "siteType": "T1",
                "p2pIPv4Address": "10.235.12.90/31",
                "deviceRole": "m_agg",
                "role": "child",
                "vlanId": 0,
            },
        },
    }
]

expected_query = [
    {"$match": {"orderId": "BPM-123", "state": {"$exists": True}}},
    {"$sort": {"createdDate": -1}},
    {
        "$group": {
            "_id": "dummy unique keys",
            "createdDate": {"$max": "$createdDate"},
            "document": {"$push": "$$CURRENT"},
        }
    },
    {"$project": {"_id": 0, "record": {"$arrayElemAt": ["$document", 0]}}},
    {"$project": {"record": "dummy return keys"}},
]

example_schema_record_1 = {
    "service": "metroLogicalLink",
    "collection": "metro-link-lifecycle",
    "returnKeys": {"service": {"aEnd": {"hostname": 1}, "bEnd": {"hostname": 1}, "vlanId": 1}},
    "uniqueKeys": "service.aEnd.hostname, service.bEnd.hostname",
}

expected_processed_unique_keys_1 = {
    "serviceaEndhostname": "$service.aEnd.hostname",
    "servicebEndhostname": "$service.bEnd.hostname",
}

expected_processed_return_keys_1 = {
    "service": {"aEnd": {"hostname": 1}, "bEnd": {"hostname": 1}, "vlanId": 1},
    "state": 1,
}

example_schema_record_2 = {
    "service": "skyTalk",
    "collection": "sky-talk-lifecycle",
    "returnKeys": "NA",
    "uniqueKeys": "NA",
}

example_schema_record_3 = {"service": "skyTalk", "noCollection": "invalid", "uniqueKeys": "NA", "returnKeys": "NA"}

example_schema_record_4 = {
    "service": "skyTalk",
    "collection": "sky-talk-lifecycle",
    "uniqueKeys": 1,
    "returnKeys": "NA",
}

example_schema_record_5 = {
    "service": "skyTalk",
    "collection": "sky-talk-lifecycle",
    "uniqueKeys": "NA",
    "returnKeys": 1,
}

example_schema_record_6 = {
    "service": "skyTalk",
    "collection": "sky-talk-lifecycle",
    "noUniqueKeys": "NA",
    "returnKeys": "NA",
}

example_schema_record_7 = {
    "service": "skyTalk",
    "collection": "sky-talk-lifecycle",
    "uniqueKeys": "NA",
    "noReturnKeys": "NA",
}

parameterized_schema_test = [
    (
        example_schema_record_3,
        "'collection' key not found in schema",
    ),
    (
        example_schema_record_4,
        "'uniqueKeys' in schema must have string type",
    ),
    (
        example_schema_record_5,
        "'returnKeys' in schema must have object type or be 'NA'",
    ),
    (
        example_schema_record_6,
        "'uniqueKeys' key not found in schema",
    ),
    (
        example_schema_record_7,
        "'returnKeys' key not found in schema",
    ),
]

expected_processed_unique_keys_2 = {"orderId": "$orderId"}

expected_processed_return_keys_2 = {"record": {"_id": 0}}

example_service_status_details = {
    "metroLogicalLink": "Partial Success",
    "metroLogicalLinkDtls": {
        "failure": [
            {
                "service": {
                    "aEnd": {"hostname": "ma0.bllabd2.isp.sky.com"},
                    "bEnd": {"hostname": "ma0.bllabd1.isp.sky.com"},
                    "vlanId": 0,
                }
            }
        ],
        "success": [
            {
                "service": {
                    "aEnd": {"hostname": "me0.bllabd1.isp.sky.com"},
                    "bEnd": {"hostname": "ma1.bllabd1.isp.sky.com"},
                    "vlanId": 0,
                }
            },
            {
                "service": {
                    "aEnd": {"hostname": "me0.bllabd2.isp.sky.com"},
                    "bEnd": {"hostname": "ta0.bllabd3.isp.sky.com"},
                    "vlanId": 0,
                }
            },
            {
                "service": {
                    "aEnd": {"hostname": "me0.bllabd1.isp.sky.com"},
                    "bEnd": {"hostname": "ma1.dev-uk.bllab.isp.sky.com"},
                    "vlanId": 3600,
                }
            },
        ],
    },
}


@patch("connectors.core.services.service_status.read.ServiceDB")
def test_capture_schema_error(db_mock):
    """
    Test to check capture_schema_error returns False value when called
    """
    service_status = ServiceStatus(**kwargs_1)
    assert service_status._capture_schema_error("dummy") is False


@pytest.mark.parametrize(
    "schema, error_message",
    parameterized_schema_test,
)
@patch("connectors.core.services.service_status.read.ServiceDB")
def test_validate_service_status_schema_record(db_mock, schema, error_message):
    """
    Test to check service_status_db_instance is none if serviceDB exception is raised while connecting to db
    """
    service_status = ServiceStatus(**kwargs_1)
    service_status._capture_schema_error = Mock()
    service_status.schema_record = schema
    service_status._validate_service_status_schema_record()
    service_status._capture_schema_error.assert_called_with(error_message)


@patch("connectors.core.services.service_status.read.ServiceDB")
def test_instantiate_service_db(db_mock):
    """
    Test to check service_status_db_instance is none if serviceDB exception is raised while connecting to db
    """
    db_mock.side_effect = ServiceDBException("dummy error")
    service_status = ServiceStatus(**kwargs_1)
    assert service_status.service_status_db_instance is None


@patch("connectors.core.services.service_status.read.ServiceDB")
def test_get_schema_record(db_mock):
    """
    Test to check schema_record is none if serviceDB exception is raised while querying the db
    """
    service_status = ServiceStatus(**kwargs_1)
    service_status.service_status_db_instance.find_one.side_effect = ServiceDBException("dummy error")
    schema_record = service_status._get_schema_record("dummy service_type")
    assert schema_record is None


@patch("connectors.core.services.service_status.read.ServiceDB")
def test_build_query(db_mock):
    """
    Test to check correct queries are built
    """
    service_status = ServiceStatus(**kwargs_1)
    service_status._process_unique_keys = Mock(return_value="dummy unique keys")
    service_status._process_return_keys = Mock(return_value="dummy return keys")
    query = service_status._build_query()
    assert query == expected_query


@patch("connectors.core.services.service_status.read.ServiceDB")
def test_process_unique_keys(db_mock):
    """
    Test to check unique keys are processed correctly
    """
    service_status = ServiceStatus(**kwargs_1)
    service_status.schema_record = example_schema_record_1
    assert service_status._process_unique_keys() == expected_processed_unique_keys_1

    service_status.schema_record = example_schema_record_2
    assert service_status._process_unique_keys() == expected_processed_unique_keys_2


@patch("connectors.core.services.service_status.read.ServiceDB")
def test_process_return_keys(db_mock):
    """
    Test to check return keys are processed correctly
    """
    service_status = ServiceStatus(**kwargs_1)
    service_status.schema_record = example_schema_record_1
    assert service_status._process_return_keys() == expected_processed_return_keys_1

    service_status.schema_record = example_schema_record_2
    assert service_status._process_return_keys() == expected_processed_return_keys_2


@patch("connectors.core.services.service_status.read.ServiceDB")
def test_check_not_attempted_service(db_mock):
    """
    Test to check "Not Attempted" is assigned to a service without records.
    Also tests if invalid records are removed though invalid records are not supposed to be in the production phase
    """
    service_status = ServiceStatus(**kwargs_1)
    service_status._check_not_attempted_service(data={}, service_type="skyTalk")
    assert service_status.service_status_details["skyTalk"] == "Not Attempted"

    service_status._check_not_attempted_service(data=example_delta_base_data_1, service_type="deltaBase")
    assert "deltaBase" not in service_status.service_status_details


@patch("connectors.core.services.service_status.read.ServiceDB")
def test_check_in_progress_state(db_mock):
    """
    Test to check "In Progress" is correctly assigned to a service status.
    """
    service_status = ServiceStatus(**kwargs_1)
    service_status._check_in_progress_state(data=example_delta_base_data_2, service_type="deltaBase")
    assert "deltaBase" not in service_status.service_status_details

    service_status._check_in_progress_state(data=example_delta_base_data_1, service_type="deltaBase")
    assert service_status.service_status_details["deltaBase"] == "In Progress"

    service_status._check_in_progress_state(data=example_ubb_logical_data_1, service_type="ubbLogical")
    assert service_status.service_status_details["ubbLogical"] == "In Progress"

    service_status._check_in_progress_state(data=example_metro_rr_data_1, service_type="metroRR")
    assert "metroRR" not in service_status.service_status_details


@patch("connectors.core.services.service_status.read.ServiceDB")
def test_segregate_active_inactive_records(db_mock):
    """
    Test to check active and inactive records are correctly segregated
    """
    service_status = ServiceStatus(**kwargs_1)
    success, failure = service_status._segregate_active_inactive_records(expected_metro_logical_link_data)
    assert success == expected_metro_success_list_1
    assert failure == expected_metro_failure_list_1


@patch("connectors.core.services.service_status.read.ServiceDB")
def test_check_success_failure_states(db_mock):
    """
    Test to check "Success" or "Failure" is correctly assigned to a service status.
    """
    service_status = ServiceStatus()
    service_status._segregate_active_inactive_records = Mock(
        return_value=(expected_metro_success_list_1, expected_metro_failure_list_1)
    )
    service_status.schema_record = example_schema_record_1
    service_status._check_success_failure_states(data="dummy", service_type="metroLogicalLink")
    assert service_status.service_status_details["metroLogicalLink"] == "Partial Success"
    assert service_status.service_status_details["metroLogicalLinkDtls"] == {
        "success": expected_metro_success_list_1,
        "failure": expected_metro_failure_list_1,
    }
    service_status = ServiceStatus()
    service_status._segregate_active_inactive_records = Mock(return_value=([], expected_metro_failure_list_1))
    service_status.schema_record = example_schema_record_1
    service_status._check_success_failure_states(data="dummy", service_type="metroLogicalLink")
    assert service_status.service_status_details["metroLogicalLink"] == "Failure"
    assert service_status.service_status_details["metroLogicalLinkDtls"] == {"failure": expected_metro_failure_list_1}

    service_status = ServiceStatus()
    service_status._segregate_active_inactive_records = Mock(return_value=(expected_metro_success_list_1, []))
    service_status.schema_record = example_schema_record_1
    service_status._check_success_failure_states(data="dummy", service_type="metroLogicalLink")
    assert service_status.service_status_details["metroLogicalLink"] == "Success"
    assert service_status.service_status_details["metroLogicalLinkDtls"] == {"success": expected_metro_success_list_1}


@patch("connectors.core.services.service_status.read.ServiceDB")
def test_get_service_status(db_mock):
    """
    Test to check get_service_status returns the expected response
    """
    service_status = ServiceStatus(**kwargs_1)
    service_status.service_status_db_instance = None
    connexion_resp = service_status.get_service_status()
    assert connexion_resp.body["title"] == "Failed to connect to the serviceDB."

    service_status = ServiceStatus(**kwargs_3)
    service_status._get_schema_record = Mock(return_value=None)
    connexion_resp = service_status.get_service_status()
    assert connexion_resp.body["title"] == "Failed to fetch record from service status collection"

    service_status = ServiceStatus(**kwargs_3)
    service_status._instantiate_service_db = Mock(return_value=None)
    service_status._validate_service_status_schema_record = Mock(return_value=True)

    connexion_resp = service_status.get_service_status()
    assert connexion_resp.body["title"] == "Failed to connect to the serviceDB."

    service_status = ServiceStatus(**kwargs_1)
    service_status._capture_schema_error = Mock(return_value=False)
    service_status.schema_record = example_schema_record_3
    connexion_resp = service_status.get_service_status()
    assert connexion_resp.body["title"] == "Service Status Read Schema is not valid for wholesale"

    service_status = ServiceStatus(**kwargs_3)
    service_status._instantiate_service_db = Mock()
    service_status._build_query = Mock()
    service_status._check_not_attempted_service = Mock()
    service_status._check_in_progress_state = Mock()
    service_status._check_success_failure_states = Mock()
    service_status._validate_service_status_schema_record = Mock(return_value=True)
    service_status.service_status_details = example_service_status_details

    api_response = service_status.get_service_status()
    assert api_response == {"orderId": f"{kwargs_3['orderId']}", "serviceStatusDtls": example_service_status_details}
