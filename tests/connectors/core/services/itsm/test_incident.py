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
from unittest.mock import ANY, patch

# Third Party Library
import pytest

# DNE Library
from connectors.core.services.itsm.incident import Incident
from connectors.core.utils.exceptions import RestUtilityException

example_payload_1 = {
    "body": {
        "alertSummary": "dummy_summary",
        "assignTo": "dummy_assign",
        "detailedDescription": "dummy_description",
        "severity": "p4",
        "monitoredItem": "dummy_monitor_item",
        "affectedArea": "dummy_affected_area",
        "helpURL": "dummy_url",
        "monitoringGroup": "dummy_gp",
        "monitoringSystem": "dummy_system",
        "updatable": "dummy_updatable",
        "orderId": "BPM-12345",
        "orderType": "dummy_order_type",
        "changeTicket": "CHG1234567",
    }
}

example_payload_2 = {
    "body": {
        "alertSummary": "dummy_summary",
        "assignTo": "dummy_assign",
        "detailedDescription": "dummy_description",
        "severity": "p4",
        "monitoredItem": "dummy_monitor_item",
    }
}

example_payload_3 = {
    "body": {
        "assignTo": "dummy_assign",
        "detailedDescription": "dummy_description",
        "severity": "p4",
        "monitoredItem": "dummy_monitor_item",
        "orderId": "BPM-12345",
        "orderType": "dummy_order_type",
        "changeTicket": "CHG1234567",
    }
}

example_payload_4 = {
    "body": {
        "assignTo": "dummy_assign",
        "detailedDescription": "dummy_description",
        "severity": "p4",
        "monitoredItem": "dummy_monitor_item",
    }
}

example_payload_5 = {
    "body": {
        "assignTo": "dummy_assign",
        "detailedDescription": "dummy_description",
        "severity": "p4",
        "monitoredItem": "dummy_monitor_item",
        "orderId": "BPM-12345",
        "changeTicket": "CHG1234567",
    }
}

error_message = {
    "status": "FAILURE",
    "errorCategory": "FAILED",
    "errors": [
        {
            "code": "ERR-003-999-0001",
            "message": "At least one of the following conditions must be met: "
            "1.Include 'alertSummary'  "
            "2.Include all three 'orderId', 'orderType' and 'changeTicket'",
        }
    ],
}


@pytest.mark.parametrize(
    "payload, expected",
    [
        (example_payload_1, (True, "none")),
        (example_payload_2, (True, "none")),
        (example_payload_3, (True, "none")),
        (example_payload_4, (False, error_message)),
        (example_payload_5, (False, error_message)),
    ],
)
@patch("connectors.core.services.itsm.incident.RestUtility")
def test_validate_payload(rest_mock, payload, expected):
    """
    Test error is returned if alert_summary is not given and could not be created
    """
    assert Incident(**payload)._validate_payload() == expected


@patch("connectors.core.services.itsm.incident.RestUtility")
def test_build_payload(rest_mock):
    """
    Test build_payload adds all the present optional parameter to the payload
    """
    assert Incident(**example_payload_1)._build_payload() == {
        "affected_area": "dummy_affected_area",
        "alert_summary": "dummy_summary",
        "apikey": ANY,
        "assign_to": "dummy_assign",
        "detailed_description": "dummy_description",
        "help_url": "dummy_url",
        "monitored_item": "dummy_monitor_item",
        "monitoring_group": "dummy_gp",
        "monitoring_system": "dummy_system",
        "severity": "p4",
        "updatable": "dummy_updatable",
    }


@patch("connectors.core.services.itsm.incident.RestUtility")
def test_build_payload_missing_optional_param(rest_mock):
    """
    Test build_payload does not add the missing optional parameter to the payload
    """
    assert Incident(**example_payload_5)._build_payload() == {
        "alert_summary": None,
        "apikey": ANY,
        "assign_to": "dummy_assign",
        "detailed_description": "dummy_description",
        "monitored_item": "dummy_monitor_item",
        "severity": "p4",
    }


@patch("connectors.core.services.itsm.incident.Incident._validate_payload")
@patch("connectors.core.services.itsm.incident.Incident._build_payload")
@patch("connectors.core.services.itsm.incident.RestUtility")
def test_create_incident_ticket_error(rest_mock, build_payload_mock, validate_payload_mock):
    """
    Test error is returned when payload is not valid
    """
    validate_payload_mock.return_value = (False, "dummy error")
    assert Incident(**example_payload_1).create_incident_ticket() == "dummy error"


@patch("connectors.core.services.itsm.incident.Incident._validate_payload")
@patch("connectors.core.services.itsm.incident.Incident._build_payload")
@patch("connectors.core.services.itsm.incident.RestUtility")
def test_create_incident_ticket(rest_mock, build_payload_mock, validate_payload_mock):
    """
    Test SUCCESS status is added to response when ticket generation is successful
    """
    build_payload_mock.return_value = {}
    rest_mock().post.return_value = {"id": "dummy_id"}
    validate_payload_mock.return_value = (True, "none")
    assert Incident(**example_payload_1).create_incident_ticket() == {"id": "dummy_id", "status": "SUCCESS"}


@patch("connectors.core.services.itsm.incident.Incident._validate_payload")
@patch("connectors.core.services.itsm.incident.Incident._build_payload")
@patch("connectors.core.services.itsm.incident.RestUtility")
def test_create_incident_ticket_execption(rest_mock, build_payload_mock, validate_payload_mock):
    """
    Test error is returned when a RestUtilityException is raised
    """
    build_payload_mock.return_value = {}
    rest_mock().post.side_effect = RestUtilityException("dummy_execption")
    validate_payload_mock.return_value = (True, "none")
    assert Incident(**example_payload_1).create_incident_ticket() == (
        {
            "status": "FAILURE",
            "errorCategory": "FAILED",
            "errors": [
                {"code": "ERR-003-999-0002", "message": "Internal Error Generating Incident Ticket. dummy_execption."}
            ],
        }
    )
