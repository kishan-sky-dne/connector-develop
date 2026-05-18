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
from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock, call, patch

# Third Party Library
import pytest

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.services.horizon.connector import HorizonService, Tokens
from connectors.core.utils.exceptions import ConnectorException, ConnectorInvalidRequest

HORIZON_ENDPOINT = config.get(section="horizon", key="endpoint")
HORIZON_DNE_EMAIL = config.get(section="horizon", key="email")

get_deliverable_api_response = {
    "page": 1,
    "count": 1,
    "previous": None,
    "next": None,
    "total_count": 1,
    "total_pages": 1,
    "results": [
        {
            "id": 14,
            "status": {
                "id": 43,
                "name": "In Progress",
                "description": None,
                "duration_to_finish": 10,
                "sequence": 1,
                "owner": None,
                "created_at": "2024-12-12T18:10:20.408827Z",
                "updated_at": "2024-12-12T18:10:20.408840Z",
                "deliverable_type": 2,
                "start_status": None,
                "end_status": None,
            },
            "deliverable_type": {
                "id": 2,
                "name": "gea-cease",
                "update_inventory": True,
                "version": 1,
                "load_date": "2024-09-19",
                "created_at": "2024-09-19T13:18:00.298298Z",
                "updated_at": "2024-11-26T15:03:04.871715Z",
                "payload": 4,
                "domain": 1,
                "destination": 2,
                "tracker": 2,
                "notification": 1,
                "status_map": [43, 42, 44],
                "team_map": [],
            },
            "deliverable_reference": "TG558776",
            "remote_order_reference": "193632",
            "name": "Reserve me0.bllabd1 0/3/4",
            "payload": {
                "decommType": "GEA",
                "exchangeId": 1578,
                "inpTicketID": "TG558764",
                "exchangeName": "BLLABD1",
                "requiredByDate": "2023-12-31",
                "ubbLogicalDecommDetails": {
                    "service": {
                        "aEnd": {
                            "vlanId": 2,
                            "hostName": "me0.bllabd1.isp.sky.com",
                            "circuitId": "OGHP59999001",
                            "interface": "GigabitEthernet0/3/4",
                            "remoteDevice": "BAARH",
                        },
                        "bEnd": {
                            "fpe": 1,
                            "pwPort": 5001,
                            "primary": {"pwId": 962555003, "hostName": "br0.bllabd3.isp.sky.com"},
                            "standby": {"pwId": 963555003, "hostName": "br1.bllabd3.isp.sky.com"},
                            "containerName": "br33-grp.isp.sky.com",
                        },
                        "rate": 1000000,
                        "type": "OR-GEA",
                    }
                },
            },
            "requested_date": "None",
            "original_required_by_date": "2024-12-01",
            "current_required_by_date": "2024-12-01",
            "estimated_completion_date": "2025-03-06",
            "completion_date": "None",
            "created_at": "2024-09-20T12:13:05.304023Z",
            "updated_at": "2024-12-12T18:10:24.199120Z",
            "priority": "None",
            "creator": "None",
            "owner": "None",
            "manager": "None",
            "sites": "None",
            "timeline": [58, 59],
            "dependency": "None",
            "remark": [8, 34],
        }
    ],
}


get_deliverable_api_response_no_results = {
    "count": 0,
    "next": None,
    "previous": None,
    "results": [],
}


get_status_api_response = [
    {
        "id": 55,
        "name": "In Progress",
        "description": None,
        "duration_to_finish": 10,
        "sequence": 1,
        "owner": None,
        "created_at": "2024-12-13T11:21:16.871563Z",
        "updated_at": "2024-12-13T11:21:16.871594Z",
        "deliverable_type": 2,
        "start_status": None,
        "end_status": None,
    },
    {
        "id": 57,
        "name": "Aborted",
        "description": None,
        "duration_to_finish": 3,
        "sequence": 3,
        "owner": None,
        "created_at": "2024-12-13T11:21:16.969590Z",
        "updated_at": "2024-12-13T11:21:16.969615Z",
        "deliverable_type": 2,
        "start_status": None,
        "end_status": 2,
    },
    {
        "id": 58,
        "name": "Failed",
        "description": None,
        "duration_to_finish": 3,
        "sequence": 4,
        "owner": None,
        "created_at": "2024-12-13T11:21:17.011387Z",
        "updated_at": "2024-12-13T11:21:17.011414Z",
        "deliverable_type": 2,
        "start_status": None,
        "end_status": 2,
    },
    {
        "id": 54,
        "name": "Requested",
        "description": None,
        "duration_to_finish": 3,
        "sequence": 0,
        "owner": None,
        "created_at": "2024-12-13T11:21:16.811999Z",
        "updated_at": "2024-12-13T11:21:31.481145Z",
        "deliverable_type": 2,
        "start_status": 1,
        "end_status": None,
    },
    {
        "id": 56,
        "name": "Complete",
        "description": None,
        "duration_to_finish": 3,
        "sequence": 2,
        "owner": None,
        "created_at": "2024-12-13T11:21:16.920023Z",
        "updated_at": "2024-12-13T11:21:31.519557Z",
        "deliverable_type": 2,
        "start_status": None,
        "end_status": 2,
    },
]

patch_deliverable_api_response = {
    "unique_reference": "TG1234",
    "remote_order_reference": "1234",
    "name": "Test Horizon Deliverable",
    "creator": None,
    "owner": None,
    "manager": None,
    "payload": {
        "service": [
            {
                "name": "alphanumeric",
                "action": "reserve",
                "circuit": {"vendor": "test_vendor", "reference": "test_reference"},
                "interface": "TenGigE0/0/0/0",
                "link_class": "agg",
            }
        ],
        "hostname": "ma123.bllabd456.isp.sky.com",
    },
    "request_load_date": None,
    "original_required_by_date": None,
    "current_required_by_date": None,
    "estimated_completion_date": "2024-04-21",
    "completion_date": "2024-04-08",
    "created_at": "2024-04-05T02:43:42.360385Z",
    "updated_at": "2024-05-29T10:49:22.612873Z",
    "request_type": "test_request_type_id",
    "status": "test_status_id",
    "priority": None,
    "sites": ["test_sites_id"],
    "timeline": ["test_timeline_id_1", "test_timeline_id_2"],
    "dependency": [],
    "comment": [],
}


def test_constructor():
    horizon_service_obj = HorizonService()
    assert horizon_service_obj.__dict__ == {
        "_rest_util": None,
        "_sql_instance": None,
        "_token": "",
        "dne_horizon_deliverable_id_map": {},
        "warnings": [],
    }
    assert horizon_service_obj.HORIZON_ENDPOINT == HORIZON_ENDPOINT
    assert horizon_service_obj.HORIZON_DNE_EMAIL == HORIZON_DNE_EMAIL


@patch.object(HorizonService, "_decrypt_token")
@patch("connectors.core.services.horizon.connector.datetime")
def test_horizon_token(datetime_mock, _decrypt_token_mock):
    horizon_service_obj = HorizonService()
    horizon_service_obj._sql_instance = MagicMock()
    session_mock = MagicMock()
    response_mock = Mock()
    response_mock.token = "1234"
    response_mock.expiry_at = datetime(2025, 1, 1).date()
    datetime_mock.now.return_value = datetime(2024, 6, 1)
    horizon_service_obj._sql_instance.transactional_session.return_value.__enter__.return_value = session_mock

    query_mock = Mock()
    filter_mock = Mock()
    order_by_mock = Mock()
    limit_mock = Mock()

    session_mock.query.return_value = query_mock
    query_mock.filter.return_value = filter_mock
    filter_mock.order_by.return_value = order_by_mock
    order_by_mock.limit.return_value = limit_mock
    limit_mock.all.return_value = (response_mock,)

    _decrypt_token_mock.return_value = "1234"
    Tokens.id = Mock()
    Tokens.system = Mock()

    assert horizon_service_obj.horizon_token == "1234"
    assert horizon_service_obj.horizon_token == "1234"

    datetime_mock.now.assert_called_once_with(timezone.utc)
    horizon_service_obj._sql_instance.transactional_session.assert_called_once_with()
    session_mock.query.assert_called_once_with(Tokens.token, Tokens.expiry_at)
    query_mock.filter.assert_called_once_with(Tokens.system == "horizon")
    filter_mock.order_by.assert_called_once_with(Tokens.id.desc())
    order_by_mock.limit.assert_called_once_with(1)
    limit_mock.all.assert_called_once_with()
    _decrypt_token_mock.assert_called_once_with("1234")


@patch.object(HorizonService, "_decrypt_token")
@patch("connectors.core.services.horizon.connector.datetime")
def test_horizon_token_no_token_exception(datetime_mock, _decrypt_token_mock):
    horizon_service_obj = HorizonService()
    horizon_service_obj._sql_instance = MagicMock()
    session_mock = MagicMock()
    datetime_mock.now.return_value = datetime(2024, 6, 1)
    horizon_service_obj._sql_instance.transactional_session.return_value.__enter__.return_value = session_mock

    query_mock = Mock()
    filter_mock = Mock()
    order_by_mock = Mock()
    limit_mock = Mock()

    session_mock.query.return_value = query_mock
    query_mock.filter.return_value = filter_mock
    filter_mock.order_by.return_value = order_by_mock
    order_by_mock.limit.return_value = limit_mock
    limit_mock.all.return_value = ()

    Tokens.id = Mock()
    Tokens.system = Mock()

    with pytest.raises(ConnectorException) as err:
        horizon_service_obj.horizon_token
        horizon_service_obj.horizon_token

    datetime_mock.now.assert_not_called()
    horizon_service_obj._sql_instance.transactional_session.assert_called_once_with()
    session_mock.query.assert_called_once_with(Tokens.token, Tokens.expiry_at)
    query_mock.filter.assert_called_once_with(Tokens.system == "horizon")
    filter_mock.order_by.assert_called_once_with(Tokens.id.desc())
    order_by_mock.limit.assert_called_once_with(1)
    limit_mock.all.assert_called_once_with()
    _decrypt_token_mock.assert_not_called()

    assert str(err.value) == "Expecting to find 1 horizon token but found 0"


@patch.object(HorizonService, "_decrypt_token")
@patch("connectors.core.services.horizon.connector.datetime")
def test_horizon_token_expired_token_exception(datetime_mock, _decrypt_token_mock):
    horizon_service_obj = HorizonService()
    horizon_service_obj._sql_instance = MagicMock()
    session_mock = MagicMock()
    response_mock = Mock()
    response_mock.token = "1234"
    response_mock.expiry_at = datetime(2025, 1, 1).date()
    datetime_mock.now.return_value = datetime(2025, 1, 2)
    horizon_service_obj._sql_instance.transactional_session.return_value.__enter__.return_value = session_mock

    query_mock = Mock()
    filter_mock = Mock()
    order_by_mock = Mock()
    limit_mock = Mock()

    session_mock.query.return_value = query_mock
    query_mock.filter.return_value = filter_mock
    filter_mock.order_by.return_value = order_by_mock
    order_by_mock.limit.return_value = limit_mock
    limit_mock.all.return_value = (response_mock,)

    Tokens.id = Mock()
    Tokens.system = Mock()

    with pytest.raises(ConnectorException) as err:
        horizon_service_obj.horizon_token
        horizon_service_obj.horizon_token

    datetime_mock.now.assert_called_once_with(timezone.utc)
    horizon_service_obj._sql_instance.transactional_session.assert_called_once_with()
    session_mock.query.assert_called_once_with(Tokens.token, Tokens.expiry_at)
    query_mock.filter.assert_called_once_with(Tokens.system == "horizon")
    filter_mock.order_by.assert_called_once_with(Tokens.id.desc())
    order_by_mock.limit.assert_called_once_with(1)
    limit_mock.all.assert_called_once_with()
    _decrypt_token_mock.assert_not_called()

    assert str(err.value) == "Horizon token found in DB is expired"


@pytest.mark.parametrize(
    "side_effect, expected_result", [(["decrypted_token"], "decrypted_token"), (Exception(), "\\\\encrypted_token")]
)
@patch("connectors.core.services.horizon.connector.RSA")
def test_decrypt_token(rsa_mock, side_effect, expected_result):
    horizon_service_obj = HorizonService()
    rsa_mock.return_value.decrypt.side_effect = ["decrypted_token"]

    assert horizon_service_obj._decrypt_token("\\\\encrypted_token") == "decrypted_token"

    rsa_mock.assert_called_once_with()
    rsa_mock.return_value.decrypt.assert_called_once_with(b"\\encrypted_token")


@patch("connectors.core.services.horizon.connector.RestUtility")
def test_rest_util(rest_utility_mock):
    horizon_service_obj = HorizonService()
    horizon_service_obj._token = "test_token"
    rest_util_obj = Mock()
    rest_util_obj.headers = {}
    rest_utility_mock.return_value = rest_util_obj

    assert horizon_service_obj.rest_util == rest_util_obj
    assert horizon_service_obj.rest_util.headers == {"Authorization": "Token test_token"}

    rest_utility_mock.assert_called_once_with()


@patch("connectors.core.services.horizon.connector.MySQLDB")
def test_sql_instance(sql_db_mock):
    horizon_service_obj = HorizonService()
    sql_instance_obj = Mock()
    sql_db_mock.return_value = sql_instance_obj

    assert horizon_service_obj.sql_instance == sql_instance_obj

    sql_db_mock.assert_called_once_with(database_name="dne_core")


@pytest.mark.parametrize(
    "kwargs, expected_params",
    [
        ({"order_id": "1234"}, {"remote_order_reference": "1234"}),
        ({"unique_reference": "6789"}, {"deliverable_reference": "6789"}),
        ({}, None),
    ],
)
def test_get_horizon_deliverable(kwargs, expected_params):
    horizon_service_obj = HorizonService()
    horizon_service_obj._rest_util = Mock()
    horizon_service_obj._rest_util.get.return_value = get_deliverable_api_response

    assert horizon_service_obj.get_horizon_deliverable(**kwargs) == (get_deliverable_api_response, expected_params)
    horizon_service_obj._rest_util.get.assert_called_once_with(
        url=f"{HORIZON_ENDPOINT}api/base/deliverable", params=expected_params
    )


def test_get_horizon_deliverable_bad_order_id():
    horizon_service_obj = HorizonService()
    horizon_service_obj._rest_util = Mock()
    horizon_service_obj._rest_util.get.side_effect = [
        get_deliverable_api_response_no_results,
        get_deliverable_api_response,
    ]

    assert horizon_service_obj.get_horizon_deliverable(**{"order_id": "1234", "unique_reference": "6789"}) == (
        get_deliverable_api_response,
        {"deliverable_reference": "6789"},
    )

    horizon_service_obj._rest_util.get.assert_has_calls(
        [
            call(url=f"{HORIZON_ENDPOINT}api/base/deliverable", params={"remote_order_reference": "1234"}),
            call(url=f"{HORIZON_ENDPOINT}api/base/deliverable", params={"deliverable_reference": "6789"}),
        ]
    )


@patch.object(HorizonService, "get_horizon_deliverable")
@patch.object(HorizonService, "_check_response_count")
def test_get_horizon_deliverable_id(_check_response_count_mock, _get_horizon_deliverable_mock):
    horizon_service_obj = HorizonService()
    _get_horizon_deliverable_mock.return_value = (get_deliverable_api_response, {"deliverable_reference": "dummy"})

    assert horizon_service_obj._get_horizon_deliverable_id("test_dne_order_id") == (14, 2)

    _get_horizon_deliverable_mock.assert_called_once_with("test_dne_order_id", None)
    _check_response_count_mock.assert_called_once_with(1, {"deliverable_reference": "dummy"}, "test_dne_order_id", None)
    assert horizon_service_obj.dne_horizon_deliverable_id_map == {"test_dne_order_id": 14}


@pytest.mark.parametrize(
    "count, expected_error",
    [
        (0, "No deliverables found in Horizon with order ID '12345'."),
        (
            3,
            (
                "Duplicate deliverables found in Horizon with order ID '12345'. "
                "The total number of deliverables found is '3'."
            ),
        ),
    ],
)
def test_check_response_count_exception_order_id(count, expected_error):
    horizon_service_obj = HorizonService()

    with pytest.raises(ConnectorInvalidRequest) as error:
        horizon_service_obj._check_response_count(count, {"remote_order_reference": 123}, "12345")

    assert str(error.value) == expected_error


@pytest.mark.parametrize(
    "count, expected_error",
    [
        (0, "No deliverables found in Horizon with order ID '12345' or unique reference 'dummy'."),
        (
            3,
            (
                "No deliverables found in Horizon with order ID '12345', "
                "and '3' duplicate deliverables found with unique reference 'dummy'."
            ),
        ),
    ],
)
def test_check_response_count_exception_reference(count, expected_error):
    horizon_service_obj = HorizonService()

    with pytest.raises(ConnectorInvalidRequest) as error:
        horizon_service_obj._check_response_count(count, {"deliverable_reference": "dummy"}, "12345", "dummy")

    assert str(error.value) == expected_error


def test_check_response_count():
    horizon_service_obj = HorizonService()
    assert horizon_service_obj._check_response_count(1, {"deliverable_reference": "dummy"}, "12345") is None


@patch.object(HorizonService, "_check_response_count")
def test_get_status_id(_check_response_count_mock):
    horizon_service_obj = HorizonService()
    horizon_service_obj._rest_util = Mock()
    horizon_service_obj._rest_util.get.return_value = get_status_api_response

    assert horizon_service_obj._get_status_id("Complete", 2) == 56

    horizon_service_obj._rest_util.get.assert_called_once_with(
        url=f"{HORIZON_ENDPOINT}api/base/status/deliverable_type_id/2"
    )


@patch.object(HorizonService, "_check_response_count")
def test_get_status_id_exception(_check_response_count_mock):
    """
    Test exception scenario where Horizon does not map status with a single ID
    """
    horizon_service_obj = HorizonService()
    horizon_service_obj._rest_util = Mock()
    horizon_service_obj._rest_util.get.return_value = {"dummy": 2}

    with pytest.raises(ConnectorInvalidRequest) as error:
        horizon_service_obj._get_status_id("test_status", 3) == "test_status_id"
    assert str(error.value) == "Failed to fetch corresponding ID for status test_status from Horizon."
    horizon_service_obj._rest_util.get.assert_called_once_with(
        url=f"{HORIZON_ENDPOINT}api/base/status/deliverable_type_id/3"
    )


@patch.object(HorizonService, "_get_status_id")
def test_update_horizon_details_all_params(_get_status_id_mock):
    horizon_service_obj = HorizonService()
    horizon_service_obj._rest_util = Mock()
    horizon_service_obj._rest_util.patch.return_value = patch_deliverable_api_response
    _get_status_id_mock.return_value = "test_status_id"
    update_body = {
        "completion_date": "test_completion_data",
        "estimated_completion_date": "test_estimated_completion_date",
        "original_required_by_date": "test_original_required_by_date",
        "status": "test_status",
    }

    assert (
        horizon_service_obj._update_horizon_details("test_horizon_deliverable_id", 2, **update_body)
        == patch_deliverable_api_response
    )

    _get_status_id_mock.assert_called_once_with("test_status", 2)
    horizon_service_obj._rest_util.patch.assert_called_once_with(
        url=f"{HORIZON_ENDPOINT}api/base/deliverable/test_horizon_deliverable_id",
        data=json.dumps(
            {
                "estimated_completion_date": "test_estimated_completion_date",
                "original_required_by_date": "test_original_required_by_date",
                "status": "test_status_id",
            }
        ),
    )
    assert horizon_service_obj.warnings == ["Not updating completion date as status is not Complete"]


@patch.object(HorizonService, "_get_status_id")
def test_update_horizon_details_not_all_params(_get_status_id_mock):
    horizon_service_obj = HorizonService()
    horizon_service_obj._rest_util = Mock()
    horizon_service_obj._rest_util.patch.return_value = patch_deliverable_api_response
    _get_status_id_mock.return_value = "test_status_id"
    update_body = {
        "completion_date": "test_completion_data",
        "status": "Complete",
    }

    assert (
        horizon_service_obj._update_horizon_details("test_horizon_deliverable_id", 3, **update_body)
        == patch_deliverable_api_response
    )

    _get_status_id_mock.assert_called_once_with("Complete", 3)
    horizon_service_obj._rest_util.patch.assert_called_once_with(
        url=f"{HORIZON_ENDPOINT}api/base/deliverable/test_horizon_deliverable_id",
        data=json.dumps(
            {
                "completion_date": "test_completion_data",
                "status": "test_status_id",
            }
        ),
    )


@patch.object(HorizonService, "_get_status_id")
def test_update_horizon_details_not_all_params_and_in_progress(_get_status_id_mock):
    horizon_service_obj = HorizonService()
    horizon_service_obj._rest_util = Mock()
    horizon_service_obj._rest_util.patch.return_value = patch_deliverable_api_response
    _get_status_id_mock.return_value = "test_status_id"
    update_body = {
        "status": "In Progress",
    }

    assert (
        horizon_service_obj._update_horizon_details("test_horizon_deliverable_id", 5, **update_body)
        == patch_deliverable_api_response
    )

    _get_status_id_mock.assert_called_once_with("In Progress", 5)
    horizon_service_obj._rest_util.patch.assert_called_once_with(
        url=f"{HORIZON_ENDPOINT}api/base/deliverable/test_horizon_deliverable_id",
        data=json.dumps(
            {
                "status": "test_status_id",
            }
        ),
    )


@patch.object(HorizonService, "_get_horizon_deliverable_id")
@patch.object(HorizonService, "_update_horizon_details")
def test_update_deliverable_details(_update_horizon_details_mock, _get_horizon_deliverable_id_mock):
    horizon_service_obj = HorizonService()
    _get_horizon_deliverable_id_mock.return_value = ("test_horizon_deliverable_id", 2)
    horizon_service_obj.dne_horizon_deliverable_id_map = {"test_order_id": "test_horizon_id"}

    kwargs = {"order_id": "test_order_id", "body": {"status": "test_status", "completion_date": "test_completion_date"}}

    assert horizon_service_obj.update_deliverable_details(**kwargs) == {
        "status": "SUCCESS",
    }

    _get_horizon_deliverable_id_mock.assert_called_once_with("test_order_id", None)
    _update_horizon_details_mock.assert_called_once_with(
        "test_horizon_deliverable_id", 2, **{"status": "test_status", "completion_date": "test_completion_date"}
    )


@patch.object(HorizonService, "_get_horizon_deliverable_id")
@patch.object(HorizonService, "_update_horizon_details")
def test_update_deliverable_details_no_body(_update_horizon_details_mock, _get_horizon_deliverable_id_mock):
    horizon_service_obj = HorizonService()

    kwargs = {"order_id": "test_order_id", "body": {}}

    with pytest.raises(ConnectorInvalidRequest) as error:
        horizon_service_obj.update_deliverable_details(**kwargs)

    assert str(error.value) == "Must pass at least on parameter to update on horizon deliverable"

    _get_horizon_deliverable_id_mock.assert_not_called()
    _update_horizon_details_mock.assert_not_called()


@patch.object(HorizonService, "_get_horizon_deliverable_id")
@patch.object(HorizonService, "_update_horizon_details")
def test_update_deliverable_details_no_completion_date(_update_horizon_details_mock, _get_horizon_deliverable_id_mock):
    horizon_service_obj = HorizonService()
    _get_horizon_deliverable_id_mock.return_value = "test_horizon_deliverable_id"
    horizon_service_obj.dne_horizon_deliverable_id_map = {"test_order_id": "test_horizon_id"}

    kwargs = {"order_id": "test_order_id", "body": {"status": "Complete"}}

    with pytest.raises(ConnectorInvalidRequest) as error:
        horizon_service_obj.update_deliverable_details(**kwargs)

    assert str(error.value) == "When updating status to complete must provide completion_date"

    _get_horizon_deliverable_id_mock.assert_not_called()
    _update_horizon_details_mock.assert_not_called()
