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
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Third Party Library
import pytest
import pytz

# DNE Library
from connectors.core.utils.exceptions import ConnectorException
from connectors.webserver.itsm.tasks.ticketUpdater import _extract_date_timestamp, update_data_datetime, update_ticket

start_date = int(time.time() + 3600 * 5)
end_date = int(time.time() + 3600 * 55)
data = {
    "body": {
        "affectedCIs": [{"ciName": "ma0.test.bllab.it.bb.sky.com", "impactType": "No Service Impact"}],
        "changeType": "normal",
        "createdBy": "vsh18",
        "endDate": end_date,
        "offset": 0,
        "shortDescription": "12345",
        "startDate": start_date,
        "templateName": "UK CDN: STD29 - 3rd Party CDN Planned Maintenance - BBC",
        "attachments": [
            {"fileName": "PatchingRequest.log", "fileContent": "R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="}
        ],
        "reScheduledInfo": {"prevTktNumber": "CHG0092700", "justification": "Reasons for previous failure"},
    }
}

data1 = {
    "body": {
        "ticketNumber": "CTASK0780216",
        "updatedBy": "MCI11",
        "assignedTo": "SVC-APP-DNE",
        "state": "Authorised",
        "workNotes": "jumptest1",
    }
}
data2 = {
    "body": {
        "ticketNumber": "CTASK22290388",
        "updatedBy": "MCI11",
        "assignedTo": "MCI11",
        "state": "Authorised",
        "workNotes": "jumptest1",
    }
}
data3 = {
    "body": {
        "state": "New",
        "ticketNumber": "CHG0117784",
        "updatedBy": "cjs04",
        "workNotes": "Change completed successfully",
        "startDate": start_date,
        "endDate": end_date,
        "implementationCode": "Successful",
    }
}
data4 = {
    "body": {
        "state": "Post Implementation Review",
        "ticketNumber": "CHG0117784",
        "updatedBy": "cjs04",
        "workNotes": "Change completed successfully",
        "startDate": 1605014912,
        "endDate": 1605014968,
        "implementationDetails": "success",
        "implementationCode": "Successful",
    }
}
data5 = {
    "body": {
        "state": "Post Implementation Review",
        "ticketNumber": "CHG0117784",
        "updatedBy": "cjs04",
        "workNotes": "Change completed successfully",
        "startDate": 1605014912,
        "endDate": 1605014906,
        "implementationDetails": "success",
        "implementationCode": "Successful",
    }
}
data6 = {
    "body": {
        "ticketNumber": "CHG0117784",
        "updatedBy": "cjs04",
        "workNotes": "Change completed successfully",
        "startDate": 1605014912,
        "endDate": 1605014968,
        "implementationDetails": "success",
        "implementationCode": "Successful",
    }
}
data7 = {
    "body": {
        "ticketNumber": "CHG0117784",
        "state": "Post Implementation Review",
        "updatedBy": "cjs04",
        "assignedTo": "MCI11",
        "assignmentGrp": "MCI11",
        "workNotes": "Change completed successfully",
        "implementation_code": "test",
        "startDate": 1605014912,
        "endDate": 1605014968,
        "implementationDetails": "success",
        "implementationCode": "Successful",
    }
}
data8 = {
    "body": {
        "ticketNumber": "CHG0117784",
        "state": "Post Implementation Review",
        "assignedTo": "MCI11",
        "assignmentGrp": "MCI11",
        "workNotes": "Change completed successfully",
        "implementation_code": "Unsuccessful",
        "startDate": 1605014912,
        "endDate": 1605014968,
        "implementationDetails": "success",
        "implementationCode": "Successful",
    }
}
data9 = {
    "body": {
        "ticketNumber": "CHB0117784",
        "state": "Post Implementation Review",
        "updatedBy": "cjs04",
        "assignedTo": "MCI11",
        "assignmentGrp": "MCI11",
        "implementation_code": "test",
        "startDate": 1605014912,
        "endDate": 1605014968,
        "implementationDetails": "success",
        "implementationCode": "Successful",
    }
}

data10 = {
    "body": {
        "ticketNumber": "CHG1380033",
        "updatedBy": "cjs04",
        "state": "Post Implementation Review",
        "implementationCode": "Unsuccessful",
        "startDate": start_date,
        "endDate": end_date,
        "failureDescp": "Implementation failed due to Faulty Console port on Remote Console Server",
        "causeOfFailure": "Other",
        "backedOut": "Yes",
        "correctedPlan": "Corrected plan test",
        "implementationDetails": "implementation details test",
    }
}

data11 = {
    "body": {
        "ticketNumber": "CHG1670934",
        "updatedBy": "SVC-APP-DNE",
        "assignedTo": "SVC-APP-DNE",
        "workNotes": "Reschedule request from Jess",
        "state": "Closed",
        "newStartDate": 1772582400,
        "newEndDate": 1772604000,
        "rescheduleReason": "Implementation Team Not Ready",
    }
}

data12 = {
    "body": {
        "ticketNumber": "CHG1672100",
        "updatedBy": "SVC-APP-DNE",
        "assignedTo": "SVC-APP-DNE",
        "workNotes": "Reschedule request from Jess",
        "reschedule": "true",
        "newStartDate": "1773477821",
        "newEndDate": "1773564221",
        "rescheduleReason": "Infrastructure Not Ready",
    }
}

data_minor = {
    "body": {
        "affectedCIs": [
            {"ciName": "ma0.test.bllab.it.bb.sky.com", "impactType": "No Service Impact"},
            {"ciName": "ma0.test1.bllab.it.bb.sky.com", "impactType": "Full Outage"},
        ],
        "changeType": "minor",
        "serviceType": "evpn",
        "changeWindow": 6,
        "createdBy": "vsh18",
        "offset": 0,
        "shortDescription": "12345",
        "waitTime": 2,
        "templateName": "UK CDN: STD29 - 3rd Party CDN Planned Maintenance - BBC",
    }
}


@pytest.mark.parametrize("kwargs", [data1])
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3406")
def test_ticket_updation1(service3406_mock, kwargs):
    service3406_mock.return_value = {"result": {"details": "CTASK2229038 (UPDATED)"}}
    result = update_ticket(**kwargs)
    assert result == {"result": {"details": "CTASK2229038 (UPDATED)"}}


@pytest.mark.parametrize("kwargs", [data2])
@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
def test_ticket_updation2(service3406_mock, kwargs):
    service3406_mock.return_value = {"result": {"error_details": "ticket_number must be active"}}
    result = update_ticket(**kwargs)
    assert result["result"]["error_details"] == "ticket_number must be active", "failed"


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3402")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3050")
def test_ticket_updation3(service3402, service3050):
    service3402.return_value = {"result": {"details": "CHG0117784 (UPDATED)"}}
    service3050.return_value = {"result": {"details": "CHG0117784 (UPDATED)"}}

    result = update_ticket(**data3)
    assert result == {"result": {"details": "CHG0117784 (UPDATED)"}}


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3400")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3402")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3050")
def test_ticket_updation4(service3402, service3050, service3400):
    service3400.return_value = {"result": [{"end_date": "01/05/2024 11:52:04", "start_date": "01/05/2024 09:55:56"}]}
    service3402.return_value = {"result": {"details": "CHG0117784 (UPDATED)"}}
    service3050.return_value = {"result": {"details": "CHG0117784 (UPDATED)"}}
    result = update_ticket(**data4)
    assert result == {"result": {"details": "CHG0117784 (UPDATED)"}}


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3400")
def test_ticket_updation5(service3400):
    service3400.return_value = {"result": [{"end_date": "01/05/2024 11:52:04", "start_date": "01/05/2024 09:55:56"}]}
    result = update_ticket(**data5)
    assert result.__dict__["body"]["title"] == "Error in request body"
    assert result.status_code == 400, "failed"


def test_ticket_updation6():
    result = update_ticket(**data6)
    assert result.__dict__["body"]["title"] == "Error in request body"
    assert (
        result.__dict__["body"]["detail"]
        == "For updating Normal tickets state or assignment group or assigned to is mandatory"
    )
    assert result.status_code == 400, "failed"


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3400")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3402")
def test_ticket_updation7(service3402, service3400):
    service3402.return_value = {"result": {"error_details": "failed"}}
    service3400.return_value = {"result": [{"end_date": "01/05/2024 11:52:04", "start_date": "01/05/2024 09:55:56"}]}
    result = update_ticket(**data7)
    assert result.status_code == 403, "failed"


def test_ticket_updation8():
    result = update_ticket(**data8)
    assert result.__dict__["body"]["title"] == "Error in request body"
    assert result.__dict__["body"]["detail"] == "`updatedBy` is a required property"
    assert result.status_code == 400, "failed"


def test_ticket_updation9():
    result = update_ticket(**data9)
    assert result.__dict__["body"]["title"] == "Error in request body"
    assert result.__dict__["body"]["detail"] == "`workNotes` is a required property"
    assert result.status_code == 400, "failed"


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3402")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3400")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3050")
def test_ticket_updation10(service3050_mock, service3400_mock, service3402_mock):
    service3402_mock.return_value = {"result": {"details": "CHG1380033 (UPDATED)"}}
    service3400_mock.return_value = {
        "result": [{"end_date": "01/05/2024 11:52:04", "start_date": "01/05/2024 09:55:56"}]
    }
    service3050_mock.return_value = {"result": {"details": "CHG1380033 (UPDATED)"}}

    result = update_ticket(**data10)
    assert result == {"result": {"details": "CHG1380033 (UPDATED)"}}


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3402")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3400")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3050")
def test_ticket_updation11(service3050_mock, service3400_mock, service3402_mock):
    service3402_mock.return_value = {"result": {"details": "CHG1670934 (UPDATED)"}}
    service3400_mock.return_value = {
        "result": [{"end_date": "01/05/2024 11:52:04", "start_date": "01/05/2024 09:55:56"}]
    }
    service3050_mock.return_value = {"result": {"details": "CHG1670934 (UPDATED)"}}

    result = update_ticket(**data11)
    assert result == {"result": {"details": "CHG1670934 (UPDATED)"}}


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3402")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3050")
def test_ticket_updation12_reschedule(service3050_mock, service3402_mock):
    service3402_mock.return_value = {"result": {"details": "CHG1672100 (UPDATED)"}}
    service3050_mock.return_value = {"result": {"details": "CHG1672100 (UPDATED)"}}

    result = update_ticket(**data12)
    assert result == {"result": {"details": "CHG1672100 (UPDATED)"}}
    service3402_mock.assert_called_once_with(
        ticket_number="CHG1672100",
        updated_by="SVC-APP-DNE",
        assigned_to="SVC-APP-DNE",
        reschedule="true",
        reschedule_reason="Infrastructure%20Not%20Ready",
        new_start_date="1773477821",
        new_end_date="1773564221",
    )
    service3050_mock.assert_called_once_with(
        ticket_number="CHG1672100",
        work_notes="Reschedule%20request%20from%20Jess",
        updated_by="SVC-APP-DNE",
    )


def calculate_current_day(current_time_london):
    """
    Test function representing ticketUpdater epoch and current day calculator.

    Args:
        current_time_london (Mock)

    Returns:
        datetime: current day
    """
    if current_time_london.dst() != timedelta(0):
        dst_in_effect = current_time_london.dst()
    else:
        dst_in_effect = timedelta(0)
    epoch = datetime(1970, 1, 1, tzinfo=pytz.utc) + dst_in_effect
    return (datetime(2023, 12, 1, 12, 0, 0, tzinfo=pytz.utc) - epoch).total_seconds()


def test_dst_in_effect():
    current_time_london = Mock()
    current_time_london.dst.return_value = timedelta(hours=1)
    result = calculate_current_day(current_time_london)
    assert str(datetime.fromtimestamp(result)) == "2023-12-01 11:00:00"


def test_dst_not_in_effect():
    current_time_london = Mock()
    current_time_london.dst.return_value = timedelta(hours=0)
    result = calculate_current_day(current_time_london)
    assert str(datetime.fromtimestamp(result)) == "2023-12-01 12:00:00"


def test_update_data_datetime_case1():
    """
    Testing update_data_datetime
    Case 'bpm_end_date_timestamp <= spark_end_date_timestamp' and 'bpm_start_date_timestamp>=spark_start_date_timestamp'
    """
    ticket = [{"startDate": 1714557356, "endDate": 1714564204}]
    data = [{}]
    update_data_datetime(
        ticket[0],
        data[0],
        {"result": [{"end_date": "01/05/2024 11:52:04", "start_date": "01/05/2024 09:55:56"}]},
        1714564208,
    )
    assert data == [{"end_date": 1714564202, "start_date": 1714557356}]


def test_update_data_datetime_case2():
    """
    Testing update_data_datetime
    Case 'bpm_end_date_timestamp > spark_end_date_timestamp', 'current_date_timestamp < spark_end_date_timestamp'
    and 'bpm_start_date_timestamp < spark_start_date_timestamp'
    """
    ticket = [{"startDate": 1714557358, "endDate": 1714564326}]
    data = [{}]
    update_data_datetime(
        ticket[0],
        data[0],
        {"result": [{"end_date": "01/05/2024 11:52:04", "start_date": "01/05/2024 09:55:56"}]},
        1714564322,
    )
    assert data == [{"end_date": 1714564320, "start_date": 1714557358}]


def test_update_data_datetime_case3():
    """
    Testing update_data_datetime
    Case 'bpm_end_date_timestamp > spark_end_date_timestamp', 'current_date_timestamp > spark_end_date_timestamp'
    and 'bpm_start_date_timestamp < spark_start_date_timestamp'
    """
    ticket = [{"startDate": 1714557358, "endDate": 1714564326}]
    data = [{}]
    update_data_datetime(
        ticket[0],
        data[0],
        {"result": [{"end_date": "01/05/2024 11:52:04", "start_date": "01/05/2024 09:55:56"}]},
        1714564682,
    )
    assert data == [{"end_date": 1714564322, "start_date": 1714557358}]


def test_extract_date_timestamp_case1():
    """
    Testing _extract_date_timestamp
    Case start_date is not retrieved
    """
    spark_results = [{"end_date": "14/05/2024 05:00:00"}]
    date = "start_date"
    u_planned_date = "u_planned_start_date"
    response = _extract_date_timestamp(spark_results, date, u_planned_date)
    assert response == 0


def test_extract_date_timestamp_case2():
    """
    Testing _extract_date_timestamp
    Case end_date is not retrieved
    """
    spark_results = [{"start_date": "14/05/2024 05:00:00"}]
    date = "end_date"
    u_planned_date = "u_planned_end_date"
    with pytest.raises(ConnectorException, match="Spark end_date is not available in Spark"):
        _extract_date_timestamp(spark_results, date, u_planned_date)
