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
from unittest.mock import patch

# Third Party Library
import pytest

# DNE Library
from connectors.core.services.itsm.exceptions import InvalidRequest, ResourceServiceNotAvailable
from connectors.core.utils.exceptions import RestUtilityException
from connectors.webserver.itsm.tasks.ticketRestrictions import change_restrictions

exceptions_chng_rest = [
    (ValueError, 404),
    (KeyError, 404),
    (TypeError, 404),
    (OverflowError, 404),
    (InvalidRequest, 404),
    (RestUtilityException, 403),
    (ResourceServiceNotAvailable, 404),
    (Exception, 500),
]

param_start_end_dates = [(1643753531, 1645395131)]


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@pytest.mark.parametrize("start_date, end_date", param_start_end_dates)
def test_change_restrictions(mock_rest_get, start_date, end_date):
    """
    Test to check the functionality of change_restrictions() function
    """
    dummy_result = [
        {
            "applies_to": "cmdb_ci",
            "blackout_schedule": "Olympics 2022 & Super Bowl - NBCU Change Freeze",
            "blackout_schedule_type": "Change Freeze",
            "condition": "Business areas CONTAINS UK - Metro Network - Metro Aggregation (MA)",
            "event_end_time": "22/02/2022 04:59:59",
            "event_name": "Olympics 2022 & Super Bowl - NBCU Change Freeze",
            "event_start_time": "31/01/2022 05:00:00",
        }
    ]
    mock_rest_get.return_value = dummy_result
    response = change_restrictions(start_date=start_date, end_date=end_date, serviceType="metroMigration")
    assert response == dummy_result


def test_change_restrictions_key_error():
    """
    Test to check if change_restrictions() function raises KeyError when mandatory parameter is missing
    """
    response = change_restrictions(start_date=1572794340)
    assert response.body["status"] == 404
    assert "problem in preparing request" in response.body["title"].lower()


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_change_restrictions_error_in_results(mock_rest_get):
    """
    Test to check the functionality of change_restrictions() function with error in result
    """
    dummy_err_response = {"result": {"error_details": "dummy error"}}
    mock_rest_get.return_value = dummy_err_response
    response = change_restrictions(start_date=1572794340, end_date=1572894600)
    assert response == []


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@pytest.mark.parametrize("exception_type, error_code", exceptions_chng_rest)
def test_change_restrictions_different_exceptions(mock_srvc3020, exception_type, error_code):
    """
    Test to check if change_restrictions() function handles different exceptions
    """
    mock_srvc3020.side_effect = exception_type("dummy error")
    response = change_restrictions(start_date=1572794340, end_date=1572894600)
    assert response.body["status"] == error_code
