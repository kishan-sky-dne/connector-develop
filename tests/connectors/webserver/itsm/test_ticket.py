# Standard Library
import copy
import json
import os
import time
from datetime import datetime
from unittest.mock import Mock, call, patch

# Third Party Library
import connexion
import pytest

# DNE Library
from connectors.core.exceptions import ServiceDBException
from connectors.core.services.itsm.exceptions import InvalidRequest, ResourceServiceNotAvailable
from connectors.core.utils.exceptions import RestUtilityException
from connectors.webserver.itsm.tasks.ticketGenerator import (
    _apply_change_creation_defaults_from_db,
    _validate_third_party_inputs,
    calculate_wait_time_offset,
    create_standard_ticket,
    create_third_party_ticket,
    create_ticket,
    get_downstream_cis,
    get_plannet_cid,
    notify_cw_change,
    process_custom_scripts,
    third_party_ticket_creation,
)

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
        "serviceType": "ethernetSegment",
        "templateName": "UK CDN: STD29 - 3rd Party CDN Planned Maintenance - BBC",
        "attachments": [
            {"fileName": "PatchingRequest.log", "fileContent": "R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="}
        ],
        "reScheduledInfo": {"prevTktNumber": "CHG0092700", "justification": "Reasons for previous failure"},
    }
}
data_standard = {
    "body": {
        "affectedCIs": [{"ciName": "ma0.test.bllab.it.bb.sky.com", "impactType": "No Service Impact"}],
        "changeType": "standard",
        "serviceType": "ethernetSegment",
        "createdBy": "vsh18",
        "endDate": 1605014906,
        "offset": 0,
        "shortDescription": "12345",
        "startDate": 1605014912,
        "templateName": "UK CDN: STD29 - 3rd Party CDN Planned Maintenance - BBC",
        "attachments": [
            {"fileName": "PatchingRequest.log", "fileContent": "R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="}
        ],
        "reScheduledInfo": {"prevTktNumber": "CHG0092700", "justification": "Reasons for previous failure"},
    }
}
data_standard1 = {
    "body": {
        "affectedCIs": [{"ciName": "ma0.test.bllab.it.bb.sky.com", "impactType": "No Service Impact"}],
        "changeType": "standard",
        "createdBy": "vsh18",
        "serviceType": "ethernetSegment",
        "endDate": end_date + 9092000,
        "offset": 0,
        "shortDescription": "12345",
        "startDate": start_date + 100,
        "templateName": "UK CDN: STD29 - 3rd Party CDN Planned Maintenance - BBC",
        "reScheduledInfo": {"prevTktNumber": "CHG0092700", "justification": "Reasons for previous failure"},
    }
}
data_standard2 = {
    "body": {
        "affectedCIs": [{"ciName": "ma0.test.bllab.it.bb.sky.com", "impactType": "No Service Impact"}],
        "changeType": "standard",
        "serviceType": "ethernetSegment",
        "createdBy": "vsh18",
        "endDate": end_date,
        "offset": 0,
        "isDummy": True,
        "shortDescription": "12345",
        "startDate": start_date,
        "templateName": "UK CDN: STD29 - 3rd Party CDN Planned Maintenance - BBC",
        "attachments": [
            {"fileName": "PatchingRequest.log", "fileContent": "R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="}
        ],
        "reScheduledInfo": {"justification": "Reasons for previous failure"},
    }
}
data_standard3 = {
    "body": {
        "affectedCIs": [{"ciName": "ma0.test.bllab.it.bb.sky.com", "impactType": "No Service Impact"}],
        "changeType": "standard",
        "serviceType": "ethernetSegment",
        "createdBy": "vsh18",
        "endDate": end_date,
        "offset": 0,
        "isDummy": True,
        "shortDescription": "12345",
        "startDate": start_date,
        "templateName": "UK CDN: STD29 - 3rd Party CDN Planned Maintenance - BBC",
        "attachments": [
            {"fileName": "PatchingRequest.log", "fileContent": "R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="}
        ],
        "reScheduledInfo": "Reasons for previous failure",
    }
}
data_standard4 = {
    "body": {
        "changeType": "standard",
        "isDummy": True,
        "serviceType": "lagUpgrade",
        "configurationItem": "UK - Core Network - Transport Aggregation (TA)",
        "createdBy": "ABC01",
        "templateName": "Group: NSOS - STD4629 - Supercore Capacity - TA LAG Upgrade [EFT2]",
        "startDate": 2721122000,
        "endDate": 2721122010,
        "assignmentGroup": "TestAssignmentGroup",
        "affectedCIs": [{}],
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

data_minor1 = {
    "body": {
        "affectedCIs": [
            {"ciName": "ma0.test1.bllab.it.bb.sky.com", "impactType": "No Service Impact"},
            {"impactType": "Full Outage"},
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
data_minor2 = {
    "body": {
        "affectedCIs": [
            {"ciName": "ma0.test1.bllab.it.bb.sky.com", "impactType": "No Service Impact"},
            {"ciName": "ma0.test1.bllab.it.bb.sky.com", "impactType": "Full Outage"},
        ],
        "changeType": "minor",
        "serviceType": "evpn",
        "changeWindow": 7,
        "createdBy": "vsh18",
        "offset": 0,
        "shortDescription": "12345",
        "waitTime": 2,
        "templateName": "UK CDN: STD29 - 3rd Party CDN Planned Maintenance - BBC",
    }
}
data_minor3 = {
    "body": {
        "affectedCIs": [
            {"ciName": "ma0.test1.bllab.it.bb.sky.com", "impactType": "No Service Impact"},
            {"ciName": "ma0.test1.bllab.it.bb.sky.com", "impactType": "Full Outage"},
        ],
        "changeType": "minor",
        "serviceType": "evpn",
        "startDate": start_date + 10000,
        "endDate": end_date + 100001,
        "createdBy": "vsh18",
        "shortDescription": "12345",
        "templateName": "UK CDN: STD29 - 3rd Party CDN Planned Maintenance - BBC",
    }
}
data_minor4 = {
    "body": {
        "affectedCIs": [
            {"ciName": "ma0.test1.bllab.it.bb.sky.com", "impactType": "No Service Impact"},
            {"ciName": "ma0.test1.bllab.it.bb.sky.com", "impactType": "Full Outage"},
        ],
        "changeType": "minor",
        "serviceType": "evpn",
        "createdBy": "vsh18",
        "shortDescription": "12345",
        "templateName": "UK CDN: STD29 - 3rd Party CDN Planned Maintenance - BBC",
    }
}
data2 = copy.deepcopy(data)
data2["body"]["attachments"].extend(
    [
        {"fileName": "PatchingRequest4.bin", "fileContent": "R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="},
        {"fileName": "PatchingRequest3.log", "fileContent": "R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="},
        {"fileName": "PatchingRequest2.log", "fileContent": "R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="},
        {"fileName": "PatchingRequest1.log", "fileContent": "R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="},
        {"fileName": "NIasdasdasdP.log", "fileContent": "R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="},
    ]
)
data3 = copy.deepcopy(data)
data3["body"]["implementationPlanDtls"] = {}

data4 = copy.deepcopy(data)
data4["body"]["implementationPlanDtls"] = {
    "freeText": "Connect A and B",
    "templatedText": {
        "templateName": "dnsCfgRequest",
        "templateAttribute": {
            "previousTktNo": "CHG12345",
            "deviceToDel": {"hostName": "mr1-dvn.enlba.isp.sky.com", "ipaddress": "89.200.128.62"},
            "configuration": [{"record": "mr1-dvn.enlba.isp.sky.com", "value": "89.200.128.62", "status": "NEW"}],
        },
    },
}

data5 = copy.deepcopy(data)
data5["body"]["implementationPlanDtls"] = {"freeText": "Connect A and B"}

data6 = copy.deepcopy(data4)
data6["body"]["implementationPlanDtls"].pop("freeText")

data7 = copy.deepcopy(data6)
data7["body"]["isDummy"] = False

data8 = copy.deepcopy(data7)
del data8["body"]["affectedCIs"]

data9 = copy.deepcopy(data6)
data7["body"]["isDummy"] = True

data15 = copy.deepcopy(data)
data15["body"]["serviceType"] = "metroMigration"
data15["body"]["affectedCIs"][0]["ciName"] = "ma0.eacol.bllab.it.bb.sky.com"
del data15["body"]["attachments"]
del data15["body"]["reScheduledInfo"]

data16 = copy.deepcopy(data)
data16["body"]["serviceType"] = "newSwitchInstall"
data16["body"]["affectedCIs"][0]["ciName"] = "ma0.eacol.bllab.it.bb.sky.com"
del data16["body"]["attachments"]
del data16["body"]["reScheduledInfo"]


data_with_dne_prepended = {
    "body": {
        "affectedCIs": [{"ciName": "ma0.test.bllab.it.bb.sky.com", "impactType": "No Service Impact"}],
        "changeType": "normal",
        "createdBy": "vsh18",
        "endDate": end_date,
        "offset": 0,
        "shortDescription": "[DNE]12345",
        "startDate": start_date,
        "serviceType": "ethernetSegment",
        "templateName": "UK CDN: STD29 - 3rd Party CDN Planned Maintenance - BBC",
        "attachments": [
            {"fileName": "PatchingRequest.log", "fileContent": "R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="}
        ],
        "reScheduledInfo": {"prevTktNumber": "CHG0092700", "justification": "Reasons for previous failure"},
    }
}


def get_working_day_side_effect(*args, **kwargs):
    class Dummy:
        def json(self, **kwargs):
            return {"england-and-wales": {"events": []}}

    return Dummy()


@patch("connectors.webserver.itsm.tasks.ticketGenerator.create_standard_ticket")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_adjacent_ci_details")
def test_ticket_creation_preprended_dne(
    get_adjacent_ci_details_mock,
    rest_get_mock,
    service3040,
    service3045,
    service3401,
    service3020,
    service3800,
    email_notify_mock,
    create_standard_ticket,
):
    rest_get_mock.side_effect = get_working_day_side_effect
    service3800.return_value = []
    service3020.return_value = [
        {
            "event_name": "DE Bank Holiday: MariÃ¤ Himmelfahrt",
            "event_start_time": "14/08/2020 22:00:00",
            "event_end_time": "15/08/2020 21:59:59",
            "applies_to": "cmdb_ci_service",
            "condition": "Business areas CONTAINS Group Digital Platforms .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "DE - Bank Holidays ",
            "blackout_schedule_type": "Change Freeze",
        }
    ]
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3045.return_value = {"result": {"status": "CHG0115712 (ATTACHMENT ADDED)", "ticketNumber": "CHG0115712"}}
    create_standard_ticket.return_value = {"status": "SUCCESSFUL"}
    service3040.return_value = True
    result = create_ticket(**data_with_dne_prepended)
    assert result["status"] == "SUCCESSFUL"
    create_standard_ticket.assert_called_once_with(
        body={
            "affectedCIs": [{"ciName": "ma0.test.bllab.it.bb.sky.com", "impactType": "No Service Impact"}],
            "changeType": "normal",
            "createdBy": "vsh18",
            "endDate": end_date,
            "offset": 0,
            "shortDescription": "[DNE]12345",
            "startDate": start_date,
            "serviceType": "ethernetSegment",
            "templateName": "UK CDN: STD29 - 3rd Party CDN Planned Maintenance - BBC",
            "attachments": [
                {
                    "fileName": "PatchingRequest.log",
                    "fileContent": "R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==",
                }
            ],
            "reScheduledInfo": {"prevTktNumber": "CHG0092700", "justification": "Reasons for previous failure"},
        }
    )


@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_adjacent_ci_details")
def test_ticket_creation(
    get_adjacent_ci_details_mock,
    rest_get_mock,
    service3040,
    service3045,
    service3401,
    service3020,
    service3800,
    email_notify_mock,
):
    rest_get_mock.side_effect = get_working_day_side_effect
    service3800.return_value = []
    service3020.return_value = [
        {
            "event_name": "DE Bank Holiday: MariÃ¤ Himmelfahrt",
            "event_start_time": "14/08/2020 22:00:00",
            "event_end_time": "15/08/2020 21:59:59",
            "applies_to": "cmdb_ci_service",
            "condition": "Business areas CONTAINS Group Digital Platforms .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "DE - Bank Holidays ",
            "blackout_schedule_type": "Change Freeze",
        }
    ]
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3045.return_value = {"result": {"status": "CHG0115712 (ATTACHMENT ADDED)", "ticketNumber": "CHG0115712"}}
    service3040.return_value = True
    result = create_ticket(**data)
    assert result["status"] == "SUCCESSFUL"


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
def test_ticket_creation2(service3040, service3045, service3401, service3020, service3800):
    service3800.return_value = []
    service3020.return_value = [
        {
            "event_name": "DE Bank Holiday: MariÃ¤ Himmelfahrt",
            "event_start_time": "14/08/2020 22:00:00",
            "event_end_time": "15/08/2020 21:59:59",
            "applies_to": "cmdb_ci_service",
            "condition": "Business areas CONTAINS Group Digital Platforms .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "DE - Bank Holidays ",
            "blackout_schedule_type": "Change Freeze",
        }
    ]
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3045.return_value = {"result": {"status": "CHG0115712 (ATTACHMENT ADDED)", "ticketNumber": "CHG0115712"}}
    service3040.return_value = True
    result = create_ticket(**data2)
    assert result.status_code == 400, "failed"
    assert (
        result.__dict__["body"]["detail"] == "Problem with no of attachments, "  # noqa: E126
        "current count is 6 and which exceeds the set limit of 3"
    )


@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_adjacent_ci_details")
def test_ticket_creation3(
    get_adjacent_ci_details_mock,
    rest_get_mock,
    service3040,
    service3045,
    service3401,
    service3020,
    service3800,
    email_notify_mock,
):
    rest_get_mock.side_effect = get_working_day_side_effect
    service3800.return_value = []
    service3020.return_value = [
        {
            "event_name": "DE Bank Holiday: MariÃƒÂ¤ Himmelfahrt",
            "event_start_time": "14/08/2020 22:00:00",
            "event_end_time": "15/08/2020 21:59:59",
            "applies_to": "cmdb_ci_service",
            "condition": "Business areas CONTAINS Group Digital Platforms .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "DE - Bank Holidays ",
            "blackout_schedule_type": "Change Freeze",
        }
    ]
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3045.return_value = {"result": {"detail": "CHG0115712 (ATTACHMENT ADDED)", "ticketNumber": "CHG0115712"}}
    service3040.return_value = True
    result = create_ticket(**data)
    assert result["status"] == "SUCCESSFUL"


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_adjacent_ci_details")
def test_ticket_creation4(
    get_adjacent_ci_details_mock, rest_get_mock, service3040, service3045, service3401, service3020, service3800
):
    rest_get_mock.side_effect = get_working_day_side_effect
    service3800.return_value = []
    service3020.return_value = [
        {
            "event_name": "DE Bank Holiday: MariÃ¤ Himmelfahrt",
            "event_start_time": "14/08/2020 22:00:00",
            "event_end_time": "15/08/2020 21:59:59",
            "applies_to": "cmdb_ci_service",
            "condition": "Business areas CONTAINS Group Digital Platforms .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "DE - Bank Holidays ",
            "blackout_schedule_type": "Change Freeze",
        }
    ]
    service3401.return_value = {"result": {"error_details": "CHG0115712 (RAISED)"}}
    service3045.return_value = {"result": {"status": "CHG0115712 (ATTACHMENT ADDED)", "ticketNumber": "CHG0115712"}}
    service3040.return_value = True
    result = create_ticket(**data)
    assert result["status"] == "UNSUCCESSFUL"


@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_adjacent_ci_details")
def test_ticket_creation5(
    get_adjacent_ci_details_mock,
    rest_get_mock,
    service3040,
    service3045,
    service3401,
    service3020,
    service3800,
    email_notify_mock,
):
    rest_get_mock.side_effect = get_working_day_side_effect
    service3800.return_value = []
    service3020.return_value = [
        {
            "event_name": "DE Bank Holiday: MariÃ¤ Himmelfahrt",
            "event_start_time": "14/08/2020 22:00:00",
            "event_end_time": "15/08/2020 21:59:59",
            "applies_to": "cmdb_ci_service",
            "condition": "Business areas CONTAINS Group Digital Platforms .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "DE - Bank Holidays ",
            "blackout_schedule_type": "Change Freeze",
        }
    ]
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3045.return_value = {"result": {"status": "CHG0115712 (ATTACHMENT ADDED)", "ticketNumber": "CHG0115712"}}
    service3040.return_value = []
    result = create_ticket(**data)
    assert result["ciAddError"][0]["ciName"] == "ma0.test.bllab.it.bb.sky.com"


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_adjacent_ci_details")
def test_ticket_creation6(
    get_adjacent_ci_details_mock, rest_get_mock, service3040, service3045, service3401, service3020, service3800
):
    rest_get_mock.side_effect = get_working_day_side_effect
    service3800.return_value = []
    service3020.return_value = [
        {
            "event_name": "DE Bank Holiday: MariÃ¤ Himmelfahrt",
            "event_start_time": "14/08/2020 22:00:00",
            "event_end_time": "15/08/2020 21:59:59",
            "applies_to": "cmdb_ci_service",
            "condition": "Business areas CONTAINS Group Digital Platforms .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "DE - Bank Holidays ",
            "blackout_schedule_type": "Change Freeze",
        }
    ]
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3045.return_value = {"result": {"status": "CHG0115712 (ATTACHMENT ADDED)", "ticketNumber": "CHG0115712"}}
    service3040.return_value = True
    result = create_ticket(**data3)
    assert result.status_code == 400, "failed"
    assert (
        result.__dict__["body"]["detail"] == "freeText and templatedText, both or none of the "  # noqa: E126
        "attributes are "
        "present. Only one of them is required."
    )


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_adjacent_ci_details")
def test_ticket_creation7(
    get_adjacent_ci_details_mock, rest_get_mock, service3040, service3045, service3401, service3020, service3800
):
    rest_get_mock.side_effect = get_working_day_side_effect
    service3800.return_value = []
    service3020.return_value = [
        {
            "event_name": "DE Bank Holiday: MariÃƒÂ¤ Himmelfahrt",
            "event_start_time": "14/08/2020 22:00:00",
            "event_end_time": "15/08/2020 21:59:59",
            "applies_to": "cmdb_ci_service",
            "condition": "Business areas CONTAINS Group Digital Platforms .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "DE - Bank Holidays ",
            "blackout_schedule_type": "Change Freeze",
        }
    ]
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3045.return_value = {"result": {"status": "CHG0115712 (ATTACHMENT ADDED)", "ticketNumber": "CHG0115712"}}
    service3040.return_value = True
    result = create_ticket(**data4)
    assert result.status_code == 400, "failed"
    assert (
        result.__dict__["body"]["detail"]  # noqa: E126
        == "freeText and templatedText, both or none of the attributes are present. "
        "Only one of them is required."
    )


@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_adjacent_ci_details")
def test_ticket_creation8(
    get_adjacent_ci_details_mock,
    rest_get_mock,
    service3040,
    service3045,
    service3401,
    service3020,
    service3800,
    email_notify_mock,
):
    rest_get_mock.side_effect = get_working_day_side_effect
    service3800.return_value = []
    service3020.return_value = [
        {
            "event_name": "DE Bank Holiday: MariÃƒÆ’Ã‚Â¤ Himmelfahrt",
            "event_start_time": "14/08/2020 22:00:00",
            "event_end_time": "15/08/2020 21:59:59",
            "applies_to": "cmdb_ci_service",
            "condition": "Business areas CONTAINS Group Digital Platforms .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "DE - Bank Holidays ",
            "blackout_schedule_type": "Change Freeze",
        }
    ]
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3045.return_value = {"result": {"detail": "CHG0115712 (ATTACHMENT ADDED)", "ticketNumber": "CHG0115712"}}
    service3040.return_value = True
    result = create_ticket(**data5)
    assert result["status"] == "SUCCESSFUL"


@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_adjacent_ci_details")
def test_ticket_creation9(
    get_adjacent_ci_details_mock,
    rest_get_mock,
    service3040,
    service3045,
    service3401,
    service3020,
    service3800,
    design,
    email_notify_mock,
):
    rest_get_mock.side_effect = get_working_day_side_effect
    design.return_value = "sample data"
    service3800.return_value = []
    service3020.return_value = [
        {
            "event_name": "DE Bank Holiday: MariÃƒÂ¤ Himmelfahrt",
            "event_start_time": "14/08/2020 22:00:00",
            "event_end_time": "15/08/2020 21:59:59",
            "applies_to": "cmdb_ci_service",
            "condition": "Business areas CONTAINS Group Digital Platforms .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "DE - Bank Holidays ",
            "blackout_schedule_type": "Change Freeze",
        }
    ]
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3045.return_value = {"result": {"detail": "CHG0115712 (ATTACHMENT ADDED)", "ticketNumber": "CHG0115712"}}
    service3040.return_value = True
    result = create_ticket(**data6)
    assert result["status"] == "SUCCESSFUL"


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3405")
@patch("connectors.core.services.itsm.customValidator.requests.get")
def test_minor(rest_get_mock, service3405, service3020, service3800):
    rest_get_mock.side_effect = get_working_day_side_effect
    service3800.return_value = []
    service3020.return_value = []
    service3405.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    result = create_ticket(**data_minor)
    assert result["status"] == "SUCCESSFUL"


def test_minor1():
    result = create_ticket(**data_minor1)
    assert result.__dict__["body"]["title"] == "Error in request body"
    assert result.__dict__["body"]["detail"] == "`ciName` is a required property"
    assert result.status_code == 400, "failed"


def test_minor2():
    result = create_ticket(**data_minor2)
    assert result.__dict__["body"]["title"] == "Invalid Request"
    assert (
        result.__dict__["body"]["detail"]  # noqa: E126
        == "Minimum and  Maximum allowed change window after round-off should be between 1 hour to 6 hours"
    )
    assert result.status_code == 400, "failed"


def test_minor3():
    result = create_ticket(**data_minor3)
    assert result.__dict__["body"]["title"] == "Invalid Request"
    assert (
        result.__dict__["body"]["detail"]  # noqa: E126
        == "Minimum and  Maximum allowed change window after round-off should be between 1 hour to 6 hours"
    )
    assert result.status_code == 400, "failed"


def test_minor4():
    result = create_ticket(**data_minor4)
    assert result.__dict__["body"]["title"] == "Invalid Request"
    assert (
        result.__dict__["body"]["detail"]  # noqa: E126
        == f"Combination of Start Date & End Date or Change Window & Wait time should be given and greater than 0"
    )  # noqa: E126
    assert result.status_code == 400, "failed"


@patch("connectors.webserver.itsm.tasks.ticketGenerator.spark")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.resolver")
@patch("connectors.core.services.itsm.customValidator.requests.get")
def test_minor5(rest_get_mock, resolver, spark):
    rest_get_mock.side_effect = get_working_day_side_effect
    spark.service3800 = Mock(
        return_value=[
            {"u_impact_start_date": "26/5/2020 01:00:00", "u_impact_end_date": "26/5/2020 05:00:00"},
            {"u_impact_start_date": "28/5/2020 01:00:00", "u_impact_end_date": "28/5/2020 05:00:00"},
            {"u_impact_start_date": "25/5/2020 01:00:00", "u_impact_end_date": "25/5/2020 05:00:00"},
        ]
    )
    spark.service3020 = Mock(
        return_value=[
            {
                "event_name": "DE Bank Holiday: MariÃ¤ Himmelfahrt",
                "event_start_time": "14/08/2020 22:00:00",
                "event_end_time": "15/08/2020 21:59:59",
                "applies_to": "cmdb_ci_service",
                "condition": "Business areas CONTAINS Group Digital Platforms .or. Business areas CONTAINS Group OTT",
                "blackout_schedule": "DE - Bank Holidays ",
                "blackout_schedule_type": "Change Freeze",
            }
        ]
    )
    resolver.find_time_slot = Mock(return_value=(True, "", ""))
    spark.service3405.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    result = create_ticket(**data_minor)
    assert result["status"] == "SUCCESSFUL"


def test_standard():
    result = create_ticket(**data_standard)
    assert result.__dict__["body"]["title"] == "Invalid Request"
    assert result.__dict__["body"]["detail"] == "Either Start Date is in past or Start Date is greater than End Date"
    assert result.status_code == 400, "failed"


@patch("connectors.core.services.itsm.customValidator.requests.get")
def test_standard1(rest_get_mock):
    rest_get_mock.side_effect = get_working_day_side_effect
    result = create_ticket(**data_standard1)
    assert result.__dict__["body"]["title"] == "Invalid Request"
    assert result.__dict__["body"]["detail"] == "Change duration start date and end date are not falling under 2 weeks"
    assert result.status_code == 400, "failed"


@patch("connectors.core.services.itsm.customValidator.requests.get")
def test_standard2(rest_get_mock):
    rest_get_mock.side_effect = get_working_day_side_effect
    result = create_ticket(**data_standard2)
    assert result.__dict__["body"]["title"] == "Error while creating the ticket on Spark"
    assert (
        result.__dict__["body"]["detail"] == "Problems with "
        "`Error while fetching required parameters for reScheduledInfo key in payload: prevTktNumber` key"
    )
    assert result.status_code == 404, "failed"


@patch("connectors.core.services.itsm.customValidator.requests.get")
def test_standard3(rest_get_mock):
    rest_get_mock.side_effect = get_working_day_side_effect
    result = create_ticket(**data_standard3)
    assert result.__dict__["body"]["title"] == "Error in request body"
    assert result.__dict__["body"]["detail"] == "`string indices must be integers` is a required property"
    assert result.status_code == 400, "failed"


@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3402")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_adjacent_ci_details")
def test_standard4_config_item(
    get_adjacent_ci_details_mock,
    rest_get_mock,
    service3040,
    service3045,
    service3401,
    service3402,
    service3020,
    service3800,
    design,
    email_notify_mock,
):
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3040.return_value = True
    service3402.return_value = {"result": []}
    rest_get_mock.side_effect = get_working_day_side_effect
    result = create_standard_ticket(**data_standard4)
    assert result == {
        "endDate": 2721122010,
        "startDate": 2721122000,
        "status": "SUCCESSFUL",
        "templateName": "Group: NSOS - STD4629 - Supercore Capacity - TA LAG Upgrade [EFT2]",
        "ticketNumber": "CHG0115712",
    }
    service3401.assert_has_calls(
        [
            call(
                templateName="Group%3A%20NSOS%20-%20STD4629%20-%20Supercore%"
                "20Capacity%20-%20TA%20LAG%20Upgrade%20%5BEFT2%5D",
                createdBy="ABC01",
                start_date="2721122000",
                end_date="2721122010",
                short_description="None",
                justification="",
                implementation_plan="",
                configuration_item="UK%20-%20Core%20Network%20-%20Transport%20Aggregation%20%28TA%29",
                assigned_to="SVC-APP-DNE",
            )
        ]
    )
    service3402.assert_called_once_with(
        ticket_number="CHG0115712", updated_by="SVC-APP-DNE", assignment_group="TestAssignmentGroup"
    )
    service3040.assert_called_once_with(
        ticket="CHG0115712",
        ci_list=[{}],
        impact_start="2721122000",
        impact_end="2721122010",
        operation="add",
        operation_by="ABC01",
    )
    service3045.assert_not_called()
    service3020.assert_not_called()
    service3800.assert_not_called()
    design.assert_not_called()
    email_notify_mock.assert_not_called()


@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3402")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_adjacent_ci_details")
def test_standard4_config_item_assignment_group_error(
    get_adjacent_ci_details_mock,
    rest_get_mock,
    service3040,
    service3045,
    service3401,
    service3402,
    service3020,
    service3800,
    design,
    email_notify_mock,
):
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3040.return_value = True
    service3402.return_value = {"result": {"error_details": "TestError"}}
    rest_get_mock.side_effect = get_working_day_side_effect
    result = create_standard_ticket(**data_standard4)
    assert result == {
        "endDate": 2721122010,
        "startDate": 2721122000,
        "status": "UNSUCCESSFUL",
        "templateName": "Group: NSOS - STD4629 - Supercore Capacity - TA LAG Upgrade [EFT2]",
        "ticketNumber": "CHG0115712",
        "assignmentGroupError": "TestError",
    }


@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_adjacent_ci_details")
def test_ticket_creation10(
    get_adjacent_ci_details_mock,
    rest_get_mock,
    service3040,
    service3045,
    service3401,
    service3020,
    service3800,
    design,
    email_notify_mock,
):
    rest_get_mock.side_effect = get_working_day_side_effect
    design.return_value = "sample data"
    service3800.return_value = [
        {"u_impact_start_date": "26/5/2020 01:00:00", "u_impact_end_date": "26/5/2020 05:00:00"},
        {"u_impact_start_date": "28/5/2020 01:00:00", "u_impact_end_date": "28/5/2020 05:00:00"},
        {"u_impact_start_date": "25/5/2020 01:00:00", "u_impact_end_date": "25/5/2020 05:00:00"},
    ]
    service3020.return_value = [
        {
            "event_name": "DE Bank Holiday: MariÃƒÂ¤ Himmelfahrt",
            "event_start_time": "14/08/2020 22:00:00",
            "event_end_time": "15/08/2020 21:59:59",
            "applies_to": "cmdb_ci_service",
            "condition": "Business areas CONTAINS Group Digital Platforms .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "DE - Bank Holidays ",
            "blackout_schedule_type": "Change Freeze",
        }
    ]
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3045.return_value = {"result": {"detail": "CHG0115712 (ATTACHMENT ADDED)", "ticketNumber": "CHG0115712"}}
    service3040.return_value = True
    result = create_ticket(**data6)
    assert result["status"] == "SUCCESSFUL"


@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.CustomService")
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
def test_ticket_creation11(
    rest_get_mock, service3040, service3045, service3401, service3800, design, tma_mock, email_notify_mock
):
    """
    Test case when isDummy is False and Standard ticket creation called with affectedCIs payload
    """
    rest_get_mock.side_effect = get_working_day_side_effect
    design.return_value = "sample data"
    service3800.return_value = [
        {"u_impact_start_date": "26/5/2020 01:00:00", "u_impact_end_date": "26/5/2020 05:00:00"},
        {"u_impact_start_date": "28/5/2020 01:00:00", "u_impact_end_date": "28/5/2020 05:00:00"},
        {"u_impact_start_date": "25/5/2020 01:00:00", "u_impact_end_date": "25/5/2020 05:00:00"},
    ]
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3045.return_value = {"result": {"detail": "CHG0115712 (ATTACHMENT ADDED)", "ticketNumber": "CHG0115712"}}
    service3040.return_value = True
    tma_mock.post_tma_cis_from_sparkid.return_value = {"devs": {"dne": {}}}
    result = create_ticket(**data7)
    assert result["status"] == "SUCCESSFUL"


@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.CustomService")
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.customValidator.requests.get")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_adjacent_ci_details")
def test_ticket_creation_freeze_holiday_false(
    get_adjacent_ci_details_mock,
    rest_get_mock,
    service3020,
    service3040,
    service3045,
    service3401,
    service3800,
    design,
    tma_mock,
    email_notify_mock,
):
    """
    Test case when isDummy is False and Standard ticket creation called with affectedCIs payload
    """
    data_freeze_holiday = copy.deepcopy(data7)
    data_freeze_holiday["body"]["isDummy"] = False
    data_freeze_holiday["body"]["isChgOnFreeze"] = False
    data_freeze_holiday["body"]["isChgOnHoliday"] = False
    rest_get_mock.side_effect = get_working_day_side_effect
    design.return_value = "sample data"
    service3800.return_value = [
        {"u_impact_start_date": "26/5/2020 01:00:00", "u_impact_end_date": "26/5/2020 05:00:00"},
        {"u_impact_start_date": "28/5/2020 01:00:00", "u_impact_end_date": "28/5/2020 05:00:00"},
        {"u_impact_start_date": "25/5/2020 01:00:00", "u_impact_end_date": "25/5/2020 05:00:00"},
    ]
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3045.return_value = {"result": {"detail": "CHG0115712 (ATTACHMENT ADDED)", "ticketNumber": "CHG0115712"}}
    service3040.return_value = True
    tma_mock.post_tma_cis_from_sparkid.return_value = {"devs": {"dne": {}}}
    result = create_ticket(**data_freeze_holiday)
    assert result["status"] == "SUCCESSFUL"
    assert service3020.call_count == 1


@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.CustomService")
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.customValidator.requests.get")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_adjacent_ci_details")
def test_ticket_creation_freeze_holiday_true(
    get_adjacent_ci_details_mock,
    rest_get_mock,
    service3020,
    service3040,
    service3045,
    service3401,
    service3800,
    design,
    tma_mock,
    email_notify_mock,
):
    """
    Test case when isDummy is False and Standard ticket creation called with affectedCIs payload
    """
    data_freeze_holiday = copy.deepcopy(data7)
    data_freeze_holiday["body"]["isDummy"] = False
    data_freeze_holiday["body"]["isChgOnFreeze"] = True
    data_freeze_holiday["body"]["isChgOnHoliday"] = True
    rest_get_mock.side_effect = get_working_day_side_effect
    design.return_value = "sample data"
    service3800.return_value = [
        {"u_impact_start_date": "26/5/2020 01:00:00", "u_impact_end_date": "26/5/2020 05:00:00"},
        {"u_impact_start_date": "28/5/2020 01:00:00", "u_impact_end_date": "28/5/2020 05:00:00"},
        {"u_impact_start_date": "25/5/2020 01:00:00", "u_impact_end_date": "25/5/2020 05:00:00"},
    ]
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3045.return_value = {"result": {"detail": "CHG0115712 (ATTACHMENT ADDED)", "ticketNumber": "CHG0115712"}}
    service3040.return_value = True
    tma_mock.post_tma_cis_from_sparkid.return_value = {"devs": {"dne": {}}}
    result = create_ticket(**data_freeze_holiday)
    assert result["status"] == "SUCCESSFUL"
    assert service3020.call_count == 0


@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
def test_ticket_creation12(rest_get_mock, service3040, service3045, service3401, service3800, design):
    """
    Test case when isDummy is False and Standard ticket creation called without affectedCIs payload
    """
    rest_get_mock.side_effect = get_working_day_side_effect
    design.return_value = "sample data"
    service3800.return_value = [
        {"u_impact_start_date": "26/5/2020 01:00:00", "u_impact_end_date": "26/5/2020 05:00:00"},
        {"u_impact_start_date": "28/5/2020 01:00:00", "u_impact_end_date": "28/5/2020 05:00:00"},
        {"u_impact_start_date": "25/5/2020 01:00:00", "u_impact_end_date": "25/5/2020 05:00:00"},
    ]
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3045.return_value = {"result": {"detail": "CHG0115712 (ATTACHMENT ADDED)", "ticketNumber": "CHG0115712"}}
    service3040.return_value = True
    result = create_ticket(**data8)
    assert result.__dict__["body"]["title"] == "Error in request body"
    assert result.__dict__["body"]["detail"] == "`affectedCIs` is a required property"
    assert result.status_code == 400, "failed"


@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.customValidator.requests.get")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_adjacent_ci_details")
def test_ticket_creation13(
    get_adjacent_ci_details_mock,
    rest_get_mock,
    service3020,
    service3040,
    service3045,
    service3401,
    service3800,
    design,
    email_notify_mock,
):
    """
    Test case when isDummy is True and Standard ticket creation called without affectedCIs payload
    """
    rest_get_mock.side_effect = get_working_day_side_effect
    design.return_value = "sample data"
    service3800.return_value = []
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3045.return_value = {"result": {"detail": "CHG0115712 (ATTACHMENT ADDED)", "ticketNumber": "CHG0115712"}}
    service3040.return_value = True
    service3020.return_value = [
        {
            "event_name": "ITA Broadband & Talk summer 2022 Change Freeze",
            "event_start_time": "11/08/2022 23:00:00",
            "event_end_time": "22/08/2022 22:59:59",
            "applies_to": "cmdb_ci",
            "condition": "Business areas CONTAINS ITA Broadband & Talk",
            "blackout_schedule": "ITA Broadband & Talk summer Change Freeze",
            "blackout_schedule_type": "Change Freeze",
        },
        {
            "event_name": "UK - High Profile Content Weekend - PPV, HOTD etc",
            "event_start_time": "19/08/2022 23:00:00",
            "event_end_time": "22/08/2022 22:59:59",
            "applies_to": "cmdb_ci",
            "condition": "Business areas CONTAINS Group CT&I .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "Group Product Content Events",
            "blackout_schedule_type": "Change Freeze",
        },
        {
            "event_name": "DE Change Freeze - House of the Dragon",
            "event_start_time": "21/08/2022 22:00:00",
            "event_end_time": "22/08/2022 21:59:59",
            "applies_to": "cmdb_ci_service",
            "condition": "Business areas CONTAINS DE Broadcasting .or. Business areas CONTAINS DE CTO .or. "
            "Business areas CONTAINS DE IT Corporate Function .or. Business areas CONTAINS DE IT CRM "
            "& Billing "
            ".or. Business areas CONTAINS DE IT Customer Engagement .or. Business areas CONTAINS DE IT Data & "
            "Analytics .or. Business areas CONTAINS DE IT Infrastructure Services .or. Business "
            "areas CONTAINS DE "
            "GPD&P .or. Business areas CONTAINS DE CT&P .or. Business areas CONTAINS DE Information Security, "
            "Risk & Compliance .or. Business areas CONTAINS DE IT Data & Analytics",
            "blackout_schedule": "DE - Change Freeze",
            "blackout_schedule_type": "Change Freeze",
        },
        {
            "event_name": "Group  Change Freeze -  House of the Dragon",
            "event_start_time": "21/08/2022 22:00:00",
            "event_end_time": "22/08/2022 21:59:59",
            "applies_to": "cmdb_ci_service",
            "condition": "Business areas CONTAINS ITA CTO Reporting .or. Business areas CONTAINS ITA IT OTT "
            "Applications/Backend .or. Business areas CONTAINS ITA Network .or. Business areas "
            "CONTAINS ITA PBC "
            "Production .or. Business areas CONTAINS ITA TECH broadcasting processing and delivery "
            ".or. Business "
            "areas CONTAINS ITA TECH Content Protection and metadata .or. Business areas CONTAINS ITA TECH data "
            "center/lab .or. Business areas CONTAINS ITA TECH infrastructure .or. Business areas "
            "CONTAINS ITA "
            "Tech Interactivity .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "ITA - Change Freeze ",
            "blackout_schedule_type": "Change Freeze",
        },
        {
            "event_name": "House of The Dragon - Will air at 2am, 4pm, 9pm",
            "event_start_time": "21/08/2022 23:00:00",
            "event_end_time": "22/08/2022 22:59:59",
            "applies_to": "cmdb_ci",
            "condition": "Business areas CONTAINS Group CT&I .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "Group Product Content Events",
            "blackout_schedule_type": "Change Freeze",
        },
    ]
    result = create_ticket(**data9)
    assert result["status"] == "SUCCESSFUL"


@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.customValidator.requests.get")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_adjacent_ci_details")
def test_ticket_creation14(
    get_adjacent_ci_details_mock,
    rest_get_mock,
    service3020,
    service3040,
    service3045,
    service3401,
    service3800,
    design,
    email_notify_mock,
):
    """
    Test case when isDummy is False and Standard ticket creation called with affectedCIs as "UNSUCCESSFUL"
    """
    rest_get_mock.side_effect = get_working_day_side_effect
    design.return_value = "sample data"
    service3800.return_value = []
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3045.return_value = {"result": {"detail": "CHG0115712 (ATTACHMENT ADDED)", "ticketNumber": "CHG0115712"}}
    service3040.return_value = False
    service3020.return_value = [
        {
            "event_name": "ITA Broadband & Talk summer 2022 Change Freeze",
            "event_start_time": "11/08/2022 23:00:00",
            "event_end_time": "22/08/2022 22:59:59",
            "applies_to": "cmdb_ci",
            "condition": "Business areas CONTAINS ITA Broadband & Talk",
            "blackout_schedule": "ITA Broadband & Talk summer Change Freeze",
            "blackout_schedule_type": "Change Freeze",
        },
        {
            "event_name": "UK - High Profile Content Weekend - PPV, HOTD etc",
            "event_start_time": "19/08/2022 23:00:00",
            "event_end_time": "22/08/2022 22:59:59",
            "applies_to": "cmdb_ci",
            "condition": "Business areas CONTAINS Group CT&I .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "Group Product Content Events",
            "blackout_schedule_type": "Change Freeze",
        },
        {
            "event_name": "DE Change Freeze - House of the Dragon",
            "event_start_time": "21/08/2022 22:00:00",
            "event_end_time": "22/08/2022 21:59:59",
            "applies_to": "cmdb_ci_service",
            "condition": "Business areas CONTAINS DE Broadcasting .or. Business areas CONTAINS DE CTO .or. "
            "Business areas CONTAINS DE IT Corporate Function .or. Business areas CONTAINS DE IT CRM "
            "& Billing "
            ".or. Business areas CONTAINS DE IT Customer Engagement .or. Business areas CONTAINS DE IT Data & "
            "Analytics .or. Business areas CONTAINS DE IT Infrastructure Services .or. Business "
            "areas CONTAINS DE "
            "GPD&P .or. Business areas CONTAINS DE CT&P .or. Business areas CONTAINS DE Information Security, "
            "Risk & Compliance .or. Business areas CONTAINS DE IT Data & Analytics",
            "blackout_schedule": "DE - Change Freeze",
            "blackout_schedule_type": "Change Freeze",
        },
        {
            "event_name": "Group  Change Freeze -  House of the Dragon",
            "event_start_time": "21/08/2022 22:00:00",
            "event_end_time": "22/08/2022 21:59:59",
            "applies_to": "cmdb_ci_service",
            "condition": "Business areas CONTAINS ITA CTO Reporting .or. Business areas CONTAINS ITA IT OTT "
            "Applications/Backend .or. Business areas CONTAINS ITA Network .or. Business areas "
            "CONTAINS ITA PBC "
            "Production .or. Business areas CONTAINS ITA TECH broadcasting processing and delivery "
            ".or. Business "
            "areas CONTAINS ITA TECH Content Protection and metadata .or. Business areas CONTAINS ITA TECH data "
            "center/lab .or. Business areas CONTAINS ITA TECH infrastructure .or. Business areas "
            "CONTAINS ITA "
            "Tech Interactivity .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "ITA - Change Freeze ",
            "blackout_schedule_type": "Change Freeze",
        },
        {
            "event_name": "House of The Dragon - Will air at 2am, 4pm, 9pm",
            "event_start_time": "21/08/2022 23:00:00",
            "event_end_time": "22/08/2022 22:59:59",
            "applies_to": "cmdb_ci",
            "condition": "Business areas CONTAINS Group CT&I .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "Group Product Content Events",
            "blackout_schedule_type": "Change Freeze",
        },
    ]
    result = create_ticket(**data9)
    assert result["status"] == "UNSUCCESSFUL"


success_third_party = {"result": {"details": "TPCHG0023017 (WHOLESALE PORTAL TASK CREATED)"}}
failure_third_party = {
    "result": {"error_details": "cannot create wholesale portal task. task already exists for: Flexgrid in CHG0225341"}
}
request_body = {
    "body": {
        "parentTicket": "CHG0225341",
        "ticketType": "change",
        "customerName": ["Flexgrid"],
        "impact": "Reduced capacity",
        "reason": "Maintenance-Sky network Upgrade",
    }
}
request_body_inc = {
    "parentTicket": "CHG0225341",
    "ticketType": "inctask",
    "customerName": ["Flexgrid"],
    "impact": "Reduced capacity",
    "reason": "Maintenance-Sky network Upgrade",
}
# request_body1 = {
#     "body": {
#         "parentTicket": "CHG0225341",
#         "ticketType": "change",
#         "customerName": ["Amdocs", "Flexgrid"],
#         "impact": "Reduced capacity",
#         "reason": "Maintenance-Sky network Upgrade",
#     }
# }
success_response = {
    "successResponse": [
        {
            "customer": "Flexgrid",
            "message": "TPCHG0023017 (WHOLESALE PORTAL TASK CREATED)",
        },
    ]
}
error_response = {
    "status": "PARTIAL-SUCCESS",
    "successResponse": [],
    "failedResponse": [
        {
            "code": "ERR-003-999-0002",
            "message": "cannot create wholesale portal task. task already exists for: Flexgrid in CHG0225341",
            "customer": "Flexgrid",
        }
    ],
}
# error_response_partial = {
#     "status": "PARTIAL-SUCCESS",
#     "failedResponse": [
#         {
#             "code": "ERR-003-999-0002",
#             "message": "cannot create wholesale portal task. task already exists for: Flexgrid in CHG0225341",
#             "customer": "Flexgrid",
#         }
#     ],
#     "successResponse": [{"customer": "Amdocs", "message": "TPCHG0023017 (WHOLESALE PORTAL TASK CREATED)"}],
# }
request_body_impact_reason = {
    "body": {
        "parentTicket": "CHG0225341",
        "ticketType": "change",
        "customerName": ["Flexgrid"],
        "impact": "Reduced capacit",
        "reason": "Maintenance-Sky network Upgrad",
    }
}
tp_mapper = {
    "change": {
        "type": "TPCHG",
        "valid_impact": [
            "Full outage to service",
            "Intermittent service outages",
            "Reduced capacity",
            "Reduced resiliency",
        ],
        "valid_reason": [
            "Delivering new capability",
            "Equipment replacement-fixing faulty equipment",
            "Increasing capacity-bandwidth",
            "Increasing capacity-infrastructure",
            "Maintenance-Sky network Upgrade",
            "Maintenance-Sky work",
            "Maintenance-Third party work",
            "Repair-fix following an incident",
        ],
    }
}
impact_reason_error = [
    (
        f"`{request_body_impact_reason['body']['impact']}` is not valid impact for ticketType `change`. "
        f"Please provide valid impact from list {tp_mapper['change']['valid_impact']}"
    ),
    (
        f"`{request_body_impact_reason['body']['reason']}` is not valid reason for ticketType `change`. "
        f"Please provide valid reason from list {tp_mapper['change']['valid_reason']}"
    ),
]


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3030")
def test_create_third_party_ticket_case1(service3030):
    service3030.return_value = success_third_party
    response = create_third_party_ticket(**request_body)
    assert response == success_response


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3030")
def test_create_third_party_ticket_case2(service3030):
    service3030.return_value = failure_third_party
    response = create_third_party_ticket(**request_body)
    assert response == error_response


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3030")
def test_create_third_party_ticket_validate_input(service3030):
    _validate_third_party_inputs.side_effect = (False, impact_reason_error)
    service3030.return_value = success_third_party
    response = create_third_party_ticket(**request_body_impact_reason)
    # assert response == {"status": "FAILURE", "errorCategory": "FAILED", "errors": impact_reason_error}
    assert response.status_code == 400
    assert response.body["detail"] == impact_reason_error


# @patch("connectors.core.services.itsm.connector.SparkTicketService.service3030")
# def test_create_third_party_ticket_partial_success(service3030):
#     service3030.side_effect = [success_third_party, failure_third_party]
#     response = create_third_party_ticket(**request_body1)
#     assert response == error_response_partial


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3030")
def test_create_third_party_ticket_case3(service3030):
    service3030.side_effect = RestUtilityException("Problem in accessing the ITSM Service 3030")
    response = create_third_party_ticket(**request_body)
    assert response.status_code == 403


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3030")
def test_create_third_party_ticket_case4(service3030):
    service3030.side_effect = ResourceServiceNotAvailable("Error while creating the ticket on Spark")
    response = create_third_party_ticket(**request_body)
    assert response.status_code == 404


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3030")
def test_create_third_party_ticket_case5(service3030):
    service3030.side_effect = InvalidRequest("Invalid Request")
    response = create_third_party_ticket(**request_body)
    assert response.status_code == 500


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3030")
def test_create_third_party_ticket_case6(service3030):
    service3030.side_effect = TypeError("Error")
    response = create_third_party_ticket(**request_body)
    assert response.status_code == 400


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3030")
def test_create_third_party_ticket_case7(service3030):
    service3030.side_effect = Exception("Error")
    response = create_third_party_ticket(**request_body)
    assert response.status_code == 500


def test_validate_third_party_inputs():
    assert _validate_third_party_inputs(request_body_impact_reason["body"]) == (False, impact_reason_error)


def test_validate_third_party_inputs_case1():
    assert _validate_third_party_inputs(request_body_inc) == (True, [])


# Third party
data_normal_third_party_ticket = data
data_normal_third_party_ticket["thirdPartyTicket"] = {
    "thirdpartyImpact": "Full outage to service",
    "thirdpartyImpactReason": "Maintenance-Sky network Upgrade",
}


@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
def test_ticket_creation_third(service3020, service3040, service3045, service3401, service3800, design):
    """
    Test case when isDummy is False and Standard ticket creation called without affectedCIs payload
    """
    design.return_value = "sample data"
    service3800.return_value = [
        {"u_impact_start_date": "26/5/2020 01:00:00", "u_impact_end_date": "26/5/2020 05:00:00"},
        {"u_impact_start_date": "28/5/2020 01:00:00", "u_impact_end_date": "28/5/2020 05:00:00"},
        {"u_impact_start_date": "25/5/2020 01:00:00", "u_impact_end_date": "25/5/2020 05:00:00"},
    ]
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3045.return_value = {"result": {"detail": "CHG0115712 (ATTACHMENT ADDED)", "ticketNumber": "CHG0115712"}}
    service3040.return_value = True
    service3800.return_value = ["test"]
    service3020.return_value = [
        {
            "event_name": "ITA Broadband & Talk summer 2022 Change Freeze",
            "event_start_time": "11/08/2022 23:00:00",
            "event_end_time": "22/08/2022 22:59:59",
            "applies_to": "cmdb_ci",
            "condition": "Business areas CONTAINS ITA Broadband & Talk",
            "blackout_schedule": "ITA Broadband & Talk summer Change Freeze",
            "blackout_schedule_type": "Change Freeze",
        },
        {
            "event_name": "UK - High Profile Content Weekend - PPV, HOTD etc",
            "event_start_time": "19/08/2022 23:00:00",
            "event_end_time": "22/08/2022 22:59:59",
            "applies_to": "cmdb_ci",
            "condition": "Business areas CONTAINS Group CT&I .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "Group Product Content Events",
            "blackout_schedule_type": "Change Freeze",
        },
        {
            "event_name": "DE Change Freeze - House of the Dragon",
            "event_start_time": "21/08/2022 22:00:00",
            "event_end_time": "22/08/2022 21:59:59",
            "applies_to": "cmdb_ci_service",
            "condition": "Business areas CONTAINS DE Broadcasting .or. Business areas CONTAINS DE CTO .or. "
            "Business areas CONTAINS DE IT Corporate Function .or. Business areas CONTAINS DE IT CRM "
            "& Billing "
            ".or. Business areas CONTAINS DE IT Customer Engagement .or. Business areas CONTAINS DE IT Data & "
            "Analytics .or. Business areas CONTAINS DE IT Infrastructure Services .or. Business "
            "areas CONTAINS DE "
            "GPD&P .or. Business areas CONTAINS DE CT&P .or. Business areas CONTAINS DE Information Security, "
            "Risk & Compliance .or. Business areas CONTAINS DE IT Data & Analytics",
            "blackout_schedule": "DE - Change Freeze",
            "blackout_schedule_type": "Change Freeze",
        },
        {
            "event_name": "Group  Change Freeze -  House of the Dragon",
            "event_start_time": "21/08/2022 22:00:00",
            "event_end_time": "22/08/2022 21:59:59",
            "applies_to": "cmdb_ci_service",
            "condition": "Business areas CONTAINS ITA CTO Reporting .or. Business areas CONTAINS ITA IT OTT "
            "Applications/Backend .or. Business areas CONTAINS ITA Network .or. Business areas "
            "CONTAINS ITA PBC "
            "Production .or. Business areas CONTAINS ITA TECH broadcasting processing and delivery "
            ".or. Business "
            "areas CONTAINS ITA TECH Content Protection and metadata .or. Business areas CONTAINS ITA TECH data "
            "center/lab .or. Business areas CONTAINS ITA TECH infrastructure .or. Business areas "
            "CONTAINS ITA "
            "Tech Interactivity .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "ITA - Change Freeze ",
            "blackout_schedule_type": "Change Freeze",
        },
        {
            "event_name": "House of The Dragon - Will air at 2am, 4pm, 9pm",
            "event_start_time": "21/08/2022 23:00:00",
            "event_end_time": "22/08/2022 22:59:59",
            "applies_to": "cmdb_ci",
            "condition": "Business areas CONTAINS Group CT&I .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "Group Product Content Events",
            "blackout_schedule_type": "Change Freeze",
        },
    ]
    result = create_ticket(**data_normal_third_party_ticket)
    assert result.status_code == 500


interface_links = {"count": 0, "next": None, "previous": None, "results": []}
circuit_types = {
    "count": 27,
    "results": [
        {"created": "2021-03-18", "id": 2, "last_updated": "2021-03-18T16:05:08.681860Z", "name": "Backhaul"},
        {"created": "2021-07-19", "id": 6, "last_updated": "2021-07-19T22:45:58.400998Z", "name": "BES"},
        {"created": "2021-07-19", "id": 8, "last_updated": "2021-07-19T22:50:39.318270Z", "name": "CableLink"},
        {"created": "2021-07-20", "id": 13, "last_updated": "2021-07-20T01:05:15.071812Z", "name": "DFx"},
        {"created": "2021-07-21", "id": 23, "last_updated": "2021-07-21T08:08:16.962289Z", "name": "DSLAM"},
        {"created": "2021-07-19", "id": 4, "last_updated": "2021-07-19T22:45:57.620558Z", "name": "EAD"},
        {"created": "2021-07-19", "id": 5, "last_updated": "2021-07-19T22:45:58.154207Z", "name": "EBD"},
        {"created": "2021-03-18", "id": 1, "last_updated": "2021-03-18T11:27:03.346742Z", "name": "Fibre"},
        {"created": "2021-07-20", "id": 17, "last_updated": "2021-07-20T14:53:39.193006Z", "name": "FTTC"},
        {"created": "2021-07-20", "id": 18, "last_updated": "2021-07-20T14:53:50.285011Z", "name": "FTTP"},
        {"created": "2021-07-20", "id": 16, "last_updated": "2021-07-20T14:53:36.547679Z", "name": "FTTX"},
        {"created": "2021-07-20", "id": 15, "last_updated": "2021-07-20T14:53:36.451988Z", "name": "GEA cablelink"},
        {"created": "2021-07-20", "id": 19, "last_updated": "2021-07-20T17:42:09.841531Z", "name": "GFAST"},
        {
            "created": "2021-07-20",
            "id": 14,
            "last_updated": "2021-07-20T10:04:24.832899Z",
            "name": "Intra-exchange link",
        },
        {"created": "2021-07-21", "id": 22, "last_updated": "2021-07-21T08:07:11.687271Z", "name": "ISAM-B"},
        {"created": "2021-07-21", "id": 21, "last_updated": "2021-07-21T08:07:09.495602Z", "name": "ISAM-V"},
        {"created": "2021-03-18", "id": 3, "last_updated": "2021-03-18T16:08:44.728361Z", "name": "Leased Line"},
        {"created": "2021-07-21", "id": 20, "last_updated": "2021-07-21T08:07:09.405437Z", "name": "MSAN"},
        {"created": "2021-07-19", "id": 7, "last_updated": "2021-07-19T22:47:19.263714Z", "name": "OSA"},
        {"created": "2021-07-20", "id": 10, "last_updated": "2021-07-20T00:50:14.363047Z", "name": "OSA_10TCE"},
        {"created": "2021-07-20", "id": 12, "last_updated": "2021-07-20T00:55:01.744458Z", "name": "OSA_CC"},
        {"created": "2021-07-20", "id": 11, "last_updated": "2021-07-20T00:52:18.815873Z", "name": "OSA_XG210_RF"},
        {"created": "2021-07-20", "id": 9, "last_updated": "2021-07-20T00:48:39.144711Z", "name": "OSA_XG210_SFW"},
        {"created": "2021-07-21", "id": 24, "last_updated": "2021-07-21T08:08:17.043432Z", "name": "Stinger"},
        {
            "created": "2021-07-22",
            "id": 26,
            "last_updated": "2021-07-22T12:57:39.276235Z",
            "name": "T1 Optical Bearer",
        },
        {
            "created": "2021-07-22",
            "id": 27,
            "last_updated": "2021-07-22T13:10:20.932454Z",
            "name": "T1 Optical Wavelength",
        },
        {
            "created": "2021-07-22",
            "id": 25,
            "last_updated": "2021-07-22T08:15:39.893631Z",
            "name": "Wholesale Access",
        },
    ],
}


@patch("connectors.webserver.itsm.tasks.ticketGenerator.CustomService")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_circuit_types")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_interface_links")
def test_get_plannet_cid_case_1(get_interface_links_mock, get_circuit_types_mock, tma_mock):
    ticket = {
        "affectedCIs": [{"ciName": "as102.mrold.isp.sky.com", "impactType": "Full Outage"}],
        "changeType": "normal",
        "createdBy": "AMR45",
        "endDate": 1631357527,
        "shortDescription": "PARENT Ticket for Metro Migration Order",
        "startDate": 1631271127,
        "serviceType": "evpn",
        "templateName": "A Test Template",
        "thirdPartyTicket": {
            "thirdpartyImpact": "Full outage to service",
            "thirdpartyImpactReason": "Maintenance-Sky network Upgrade====",
        },
    }
    get_circuit_types_mock.return_value = circuit_types
    get_interface_links_mock.return_value = interface_links
    tma_mock.post_tma_cis_from_sparkid.return_value = {"devs": {"dne": {}}}
    result = get_plannet_cid(
        ticket=ticket, affected_ci_list=ticket["affectedCIs"], ticket_number="CHG123", exchanges=["mrold"]
    )
    assert result == ([], [], [], [])


@patch("connectors.webserver.itsm.tasks.ticketGenerator.CustomService")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_circuit_types")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_interface_links")
def test_get_plannet_cid_case_2(get_interface_links_mock, get_circuit_types_mock, tma_mock):
    ticket = {
        "affectedCIs": [{"ciName": "as102.mrold.isp.sky.com", "impactType": "Full Outage"}],
        "changeType": "normal",
        "createdBy": "AMR45",
        "endDate": 1631357527,
        "shortDescription": "PARENT Ticket for Metro Migration Order",
        "startDate": 1631271127,
        "serviceType": "evpn",
        "templateName": "A Test Template",
        "thirdPartyTicket": {
            "thirdpartyImpact": "Full outage to service",
            "thirdpartyImpactReason": "Maintenance-Sky network Upgrade====",
        },
    }
    get_circuit_types_mock.return_value = circuit_types
    get_interface_links_mock.return_value = {
        "count": 7,
        "next": None,
        "previous": None,
        "results": [
            {
                "atg": {
                    "coordinator": None,
                    "date": "2016-08-15",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 84890,
                    "name": "link_as102.mrold.1/1/23_as2.mrold.1/0/28: starting on 2016-08-15_enabled_2016-08-15",
                    "name_str": "TG84890 link_as102.mrold.1/1/23_as2.mrold.1/0/28: starting on 2016-08-15_enabled_"
                    "2016-08-15 (15/08/2016)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "as102.mrold.1/1/23_as2.mrold.1/0/28",
                    "created": "2021-07-20",
                    "description": None,
                    "id": 14164,
                    "is_protected": False,
                    "last_updated": "2021-07-20T12:25:56.510479Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/7",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": None,
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/14",
                },
                "created": "2021-07-20",
                "description": "as102.mrold.1/1/23_as2.mrold.1/0/28: starting on 2016-08-15",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 36348,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261474,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:02.993558Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/23 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/28487",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 287931,
                    "lag": None,
                    "last_updated": "2021-07-19T19:46:01.438567Z",
                    "mac_address": None,
                    "name": "as2.mrold.uk.easynet.net GigabitEthernet1/0/28 | TG28487 (07/09/2013) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/8476",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "is_active": None,
                "last_updated": "2021-07-20T12:25:58.520333Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/23_as2.mrold:GigabitEthernet1/0/28",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/28487",
                    "created": "2021-07-19",
                    "description": "as2.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 1,
                    "hostname": "as2.mrold",
                    "id": 8476,
                    "last_updated": "2021-07-19T19:46:00.696087Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as2.mrold.uk.easynet.net",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/172",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/54",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/12",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2016-08-15",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 82758,
                    "name": "link_as102.mrold.1/1/7_as2.mrold.1/0/27: starting on 2016-08-15_enabled_2016-08-15",
                    "name_str": "TG82758 link_as102.mrold.1/1/7_as2.mrold.1/0/27: starting on 2016-08-15_enabled_"
                    "2016-08-15 (15/08/2016)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "as102.mrold.1/1/7_as2.mrold.1/0/27",
                    "created": "2021-07-20",
                    "description": None,
                    "id": 13098,
                    "is_protected": False,
                    "last_updated": "2021-07-20T11:45:23.883926Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/7",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": None,
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/14",
                },
                "created": "2021-07-20",
                "description": "as102.mrold.1/1/7_as2.mrold.1/0/27: starting on 2016-08-15",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 35292,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261458,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:01.945577Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/7 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/28487",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 287930,
                    "lag": None,
                    "last_updated": "2021-07-19T19:46:01.413116Z",
                    "mac_address": None,
                    "name": "as2.mrold.uk.easynet.net GigabitEthernet1/0/27 | TG28487 (07/09/2013) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/8476",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "is_active": None,
                "last_updated": "2021-07-20T11:45:25.851394Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/7_as2.mrold:GigabitEthernet1/0/27",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/28487",
                    "created": "2021-07-19",
                    "description": "as2.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 1,
                    "hostname": "as2.mrold",
                    "id": 8476,
                    "last_updated": "2021-07-19T19:46:00.696087Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as2.mrold.uk.easynet.net",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/172",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/54",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/12",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2018-02-12",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 219654,
                    "name": "link_bm0.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12",
                    "name_str": "TG219654 link_bm0.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12 "
                    "(12/02/2018)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "bm0.mrold.isp:ge9-0",
                    "created": "2021-07-21",
                    "description": None,
                    "id": 65367,
                    "is_protected": False,
                    "last_updated": "2021-07-21T23:15:01.241690Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/7",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/22",
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/20",
                },
                "created": "2021-07-21",
                "description": "bm0.mrold.isp:ge9-0: starting on 2018-02-12",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 98980,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261452,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:01.560413Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/1 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": None,
                "is_active": None,
                "last_updated": "2021-07-21T23:15:03.044471Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/1_dslam.mrold",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154790",
                    "created": "2021-07-21",
                    "description": "dslam.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154791",
                    "face": 0,
                    "height": 1,
                    "hostname": "dslam.mrold",
                    "id": 19720,
                    "last_updated": "2021-07-21T06:25:07.182241Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "dslam.mrold",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/175",
                    "ne_subrole": None,
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/65",
                    "parent": None,
                    "platform": None,
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2018-02-12",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 166562,
                    "name": "link_bm1.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12",
                    "name_str": "TG166562 link_bm1.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12"
                    " (12/02/2018)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "bm1.mrold.isp:ge9-0",
                    "created": "2021-07-21",
                    "description": None,
                    "id": 38024,
                    "is_protected": False,
                    "last_updated": "2021-07-21T09:14:44.983176Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/7",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/22",
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/20",
                },
                "created": "2021-07-21",
                "description": "bm1.mrold.isp:ge9-0: starting on 2018-02-12",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 72378,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261453,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:01.626147Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/2 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": None,
                "is_active": None,
                "last_updated": "2021-07-21T09:14:46.521793Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/2_dslam.mrold",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154790",
                    "created": "2021-07-21",
                    "description": "dslam.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154791",
                    "face": 0,
                    "height": 1,
                    "hostname": "dslam.mrold",
                    "id": 19720,
                    "last_updated": "2021-07-21T06:25:07.182241Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "dslam.mrold",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/175",
                    "ne_subrole": None,
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/65",
                    "parent": None,
                    "platform": None,
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2018-02-12",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 171826,
                    "name": "link_bm7.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12",
                    "name_str": "TG171826 link_bm7.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12 "
                    "(12/02/2018)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "bm7.mrold.isp:ge9-0",
                    "created": "2021-07-21",
                    "description": None,
                    "id": 40749,
                    "is_protected": False,
                    "last_updated": "2021-07-21T10:36:42.692928Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/7",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/22",
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/20",
                },
                "created": "2021-07-21",
                "description": "bm7.mrold.isp:ge9-0: starting on 2018-02-12",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 75010,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261454,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:01.690104Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/3 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": None,
                "is_active": None,
                "last_updated": "2021-07-21T10:36:44.184876Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/3_dslam.mrold",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154790",
                    "created": "2021-07-21",
                    "description": "dslam.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154791",
                    "face": 0,
                    "height": 1,
                    "hostname": "dslam.mrold",
                    "id": 19720,
                    "last_updated": "2021-07-21T06:25:07.182241Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "dslam.mrold",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/175",
                    "ne_subrole": None,
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/65",
                    "parent": None,
                    "platform": None,
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2021-04-29",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 258113,
                    "name": "link_ONEA45462911: starting on 2021-04-29_enabled_2021-04-29",
                    "name_str": "TG258113 link_ONEA45462911: starting on 2021-04-29_enabled_2021-04-29 (29/04/2021)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "ONEA45462911",
                    "created": "2021-07-22",
                    "description": None,
                    "id": 71289,
                    "is_protected": False,
                    "last_updated": "2021-07-22T09:51:09.266862Z",
                    "length": 0.0,
                    "parent_ref": "SKY-SECT-1874",
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/44",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/4",
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/25",
                },
                "created": "2021-07-22",
                "description": "ONEA45462911: starting on 2021-04-29",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 118242,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261455,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:01.754023Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/4 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": None,
                "is_active": None,
                "last_updated": "2021-07-22T09:51:11.251072Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/4_ws-access.mrold",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/160172",
                    "created": "2021-07-21",
                    "description": "ws-access.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/160173",
                    "face": 0,
                    "height": 1,
                    "hostname": "ws-access.mrold",
                    "id": 22411,
                    "last_updated": "2021-07-21T07:46:36.273979Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "ws-access.mrold",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/176",
                    "ne_subrole": None,
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/66",
                    "parent": None,
                    "platform": None,
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2021-01-25",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 78082,
                    "name": "link_EBCL201288:ma4.mrold.0/0/0/11_as102.mrold.1/1/25: starting on 2021-01-25_enabled_"
                    "2021-01-25",
                    "name_str": "TG78082 link_EBCL201288:ma4.mrold.0/0/0/11_as102.mrold.1/1/25: starting on 2021-01-25_"
                    "enabled_2021-01-25 (25/01/2021)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 10000,
                    "cct_no": None,
                    "cid": "EBCL201288:ma4.mrold.0/0/0/11_as102.mrold.1/1/25",
                    "created": "2021-07-20",
                    "description": None,
                    "id": 10758,
                    "is_protected": False,
                    "last_updated": "2021-07-20T10:15:38.991824Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/44",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/3",
                    "subtype": None,
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/14",
                },
                "created": "2021-07-20",
                "description": "EBCL201288:ma4.mrold.0/0/0/11_as102.mrold.1/1/25: starting on 2021-01-25",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 32974,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/14961",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 89813,
                    "lag": None,
                    "last_updated": "2021-07-19T15:47:57.763682Z",
                    "mac_address": None,
                    "name": "ma4.mrold.isp.sky.com TenGigE0/0/0/11 | TG14961 (03/11/2020) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/2194",
                    "rates": [1, 3, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261476,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:03.134342Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/25 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [3],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "is_active": None,
                "last_updated": "2021-07-20T10:15:41.015238Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_ma4.mrold:TenGigE0/0/0/11_as102.mrold:1/1/25",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/14961",
                    "created": "2021-07-19",
                    "description": "ma4.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 1,
                    "hostname": "ma4.mrold",
                    "id": 2194,
                    "last_updated": "2021-07-19T15:47:57.396271Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "ma4.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/169",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/39",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/3",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "10G rate", "id": 3, "name": "10G", "unit_id": 3, "value": 10.0},
                "subrate": None,
            },
        ],
    }
    tma_mock.post_tma_cis_from_sparkid.return_value = {"devs": {"dne": {}}}
    result = get_plannet_cid(
        ticket=ticket, affected_ci_list=ticket["affectedCIs"], ticket_number="CHG123", exchanges=["mrold"]
    )
    assert result == (
        [],
        [{"ciName": "ONEA45462911", "impactType": "Full Outage"}],
        [
            {"ciName": "as102.mrold.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "as2.mrold.uk.easynet.net", "impactType": "Full Outage"},
            {"ciName": "dslam.mrold", "impactType": "Full Outage"},
            {"ciName": "ws-access.mrold", "impactType": "Full Outage"},
        ],
        [],
    )  # noqa: E501


@patch("connectors.webserver.itsm.tasks.ticketGenerator.CustomService")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_circuit_types")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_interface_links")
def test_get_plannet_cid_case_3(get_interface_links_mock, get_circuit_types_mock, tma_mock):
    ticket = {
        "affectedCIs": [{"ciName": "as102.mrold.isp.sky.com", "impactType": "Full Outage"}],
        "changeType": "normal",
        "createdBy": "AMR45",
        "endDate": 1631357527,
        "shortDescription": "PARENT Ticket for Metro Migration Order",
        "startDate": 1631271127,
        "serviceType": "evpn",
        "templateName": "A Test Template",
        "thirdPartyTicket": {
            "thirdpartyImpact": "Full outage to service",
            "thirdpartyImpactReason": "Maintenance-Sky network Upgrade====",
        },
    }
    get_circuit_types_mock.return_value = circuit_types
    get_interface_links_mock.return_value = {
        "count": 7,
        "next": None,
        "previous": None,
        "results": [
            {
                "atg": {
                    "coordinator": None,
                    "date": "2016-08-15",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 84890,
                    "name": "link_as102.mrold.1/1/23_as2.mrold.1/0/28: starting on 2016-08-15_enabled_2016-08-15",
                    "name_str": "TG84890 link_as102.mrold.1/1/23_as2.mrold.1/0/28: starting on 2016-08-15_enabled_"
                    "2016-08-15 (15/08/2016)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "as102.mrold.1/1/23_as2.mrold.1/0/28",
                    "created": "2021-07-20",
                    "description": None,
                    "id": 14164,
                    "is_protected": False,
                    "last_updated": "2021-07-20T12:25:56.510479Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/7",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": None,
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/14",
                },
                "created": "2021-07-20",
                "description": "as102.mrold.1/1/23_as2.mrold.1/0/28: starting on 2016-08-15",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 36348,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261474,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:02.993558Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/23 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/28487",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 287931,
                    "lag": None,
                    "last_updated": "2021-07-19T19:46:01.438567Z",
                    "mac_address": None,
                    "name": "as2.mrold.uk.easynet.net GigabitEthernet1/0/28 | TG28487 (07/09/2013) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/8476",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "is_active": None,
                "last_updated": "2021-07-20T12:25:58.520333Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/23_as2.mrold:GigabitEthernet1/0/28",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/28487",
                    "created": "2021-07-19",
                    "description": "as2.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 1,
                    "hostname": "as2.mrold",
                    "id": 8476,
                    "last_updated": "2021-07-19T19:46:00.696087Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as2.mrold.uk.easynet.net",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/172",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/54",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/12",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2016-08-15",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 82758,
                    "name": "link_as102.mrold.1/1/7_as2.mrold.1/0/27: starting on 2016-08-15_enabled_2016-08-15",
                    "name_str": "TG82758 link_as102.mrold.1/1/7_as2.mrold.1/0/27: starting on 2016-08-15_enabled_"
                    "2016-08-15 (15/08/2016)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "as102.mrold.1/1/7_as2.mrold.1/0/27",
                    "created": "2021-07-20",
                    "description": None,
                    "id": 13098,
                    "is_protected": False,
                    "last_updated": "2021-07-20T11:45:23.883926Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/7",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": None,
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/14",
                },
                "created": "2021-07-20",
                "description": "as102.mrold.1/1/7_as2.mrold.1/0/27: starting on 2016-08-15",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 35292,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261458,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:01.945577Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/7 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/28487",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 287930,
                    "lag": None,
                    "last_updated": "2021-07-19T19:46:01.413116Z",
                    "mac_address": None,
                    "name": "as2.mrold.uk.easynet.net GigabitEthernet1/0/27 | TG28487 (07/09/2013) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/8476",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "is_active": None,
                "last_updated": "2021-07-20T11:45:25.851394Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/7_as2.mrold:GigabitEthernet1/0/27",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/28487",
                    "created": "2021-07-19",
                    "description": "as2.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 1,
                    "hostname": "as2.mrold",
                    "id": 8476,
                    "last_updated": "2021-07-19T19:46:00.696087Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as2.mrold.uk.easynet.net",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/172",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/54",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/12",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2018-02-12",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 219654,
                    "name": "link_bm0.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12",
                    "name_str": "TG219654 link_bm0.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12 "
                    "(12/02/2018)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "bm0.mrold.isp:ge9-0",
                    "created": "2021-07-21",
                    "description": None,
                    "id": 65367,
                    "is_protected": False,
                    "last_updated": "2021-07-21T23:15:01.241690Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/7",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/22",
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/20",
                },
                "created": "2021-07-21",
                "description": "bm0.mrold.isp:ge9-0: starting on 2018-02-12",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 98980,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261452,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:01.560413Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/1 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": None,
                "is_active": None,
                "last_updated": "2021-07-21T23:15:03.044471Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/1_dslam.mrold",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154790",
                    "created": "2021-07-21",
                    "description": "dslam.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154791",
                    "face": 0,
                    "height": 1,
                    "hostname": "dslam.mrold",
                    "id": 19720,
                    "last_updated": "2021-07-21T06:25:07.182241Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "dslam.mrold",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/175",
                    "ne_subrole": None,
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/65",
                    "parent": None,
                    "platform": None,
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2018-02-12",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 166562,
                    "name": "link_bm1.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12",
                    "name_str": "TG166562 link_bm1.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12"
                    " (12/02/2018)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "bm1.mrold.isp:ge9-0",
                    "created": "2021-07-21",
                    "description": None,
                    "id": 38024,
                    "is_protected": False,
                    "last_updated": "2021-07-21T09:14:44.983176Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/7",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/22",
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/20",
                },
                "created": "2021-07-21",
                "description": "bm1.mrold.isp:ge9-0: starting on 2018-02-12",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 72378,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261453,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:01.626147Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/2 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": None,
                "is_active": None,
                "last_updated": "2021-07-21T09:14:46.521793Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/2_dslam.mrold",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154790",
                    "created": "2021-07-21",
                    "description": "dslam.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154791",
                    "face": 0,
                    "height": 1,
                    "hostname": "dslam.mrold",
                    "id": 19720,
                    "last_updated": "2021-07-21T06:25:07.182241Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "dslam.mrold",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/175",
                    "ne_subrole": None,
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/65",
                    "parent": None,
                    "platform": None,
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2018-02-12",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 171826,
                    "name": "link_bm7.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12",
                    "name_str": "TG171826 link_bm7.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12 "
                    "(12/02/2018)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "bm7.mrold.isp:ge9-0",
                    "created": "2021-07-21",
                    "description": None,
                    "id": 40749,
                    "is_protected": False,
                    "last_updated": "2021-07-21T10:36:42.692928Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/7",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/22",
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/20",
                },
                "created": "2021-07-21",
                "description": "bm7.mrold.isp:ge9-0: starting on 2018-02-12",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 75010,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261454,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:01.690104Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/3 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": None,
                "is_active": None,
                "last_updated": "2021-07-21T10:36:44.184876Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/3_dslam.mrold",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154790",
                    "created": "2021-07-21",
                    "description": "dslam.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154791",
                    "face": 0,
                    "height": 1,
                    "hostname": "dslam.mrold",
                    "id": 19720,
                    "last_updated": "2021-07-21T06:25:07.182241Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "dslam.mrold",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/175",
                    "ne_subrole": None,
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/65",
                    "parent": None,
                    "platform": None,
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2021-04-29",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 258113,
                    "name": "link_ONEA45462911: starting on 2021-04-29_enabled_2021-04-29",
                    "name_str": "TG258113 link_ONEA45462911: starting on 2021-04-29_enabled_2021-04-29 (29/04/2021)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "EBCL45462911",
                    "created": "2021-07-22",
                    "description": None,
                    "id": 71289,
                    "is_protected": False,
                    "last_updated": "2021-07-22T09:51:09.266862Z",
                    "length": 0.0,
                    "parent_ref": "SKY-SECT-1874",
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/44",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/4",
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/25",
                },
                "created": "2021-07-22",
                "description": "ONEA45462911: starting on 2021-04-29",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 118242,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261455,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:01.754023Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/4 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": None,
                "is_active": None,
                "last_updated": "2021-07-22T09:51:11.251072Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/4_ws-access.mrold",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/160172",
                    "created": "2021-07-21",
                    "description": "ws-access.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/160173",
                    "face": 0,
                    "height": 1,
                    "hostname": "ws-access.mrold",
                    "id": 22411,
                    "last_updated": "2021-07-21T07:46:36.273979Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "ws-access.mrold",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/176",
                    "ne_subrole": None,
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/66",
                    "parent": None,
                    "platform": None,
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2021-01-25",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 78082,
                    "name": "link_EBCL201288:ma4.mrold.0/0/0/11_as102.mrold.1/1/25: starting on 2021-01-25_enabled_"
                    "2021-01-25",
                    "name_str": "TG78082 link_EBCL201288:ma4.mrold.0/0/0/11_as102.mrold.1/1/25: starting on 2021-01-25_"
                    "enabled_2021-01-25 (25/01/2021)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 10000,
                    "cct_no": None,
                    "cid": "EBCL201288:ma4.mrold.0/0/0/11_as102.mrold.1/1/25",
                    "created": "2021-07-20",
                    "description": None,
                    "id": 10758,
                    "is_protected": False,
                    "last_updated": "2021-07-20T10:15:38.991824Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/44",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/3",
                    "subtype": None,
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/14",
                },
                "created": "2021-07-20",
                "description": "EBCL201288:ma4.mrold.0/0/0/11_as102.mrold.1/1/25: starting on 2021-01-25",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 32974,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/14961",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 89813,
                    "lag": None,
                    "last_updated": "2021-07-19T15:47:57.763682Z",
                    "mac_address": None,
                    "name": "ma4.mrold.isp.sky.com TenGigE0/0/0/11 | TG14961 (03/11/2020) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/2194",
                    "rates": [1, 3, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261476,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:03.134342Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/25 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [3],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "is_active": None,
                "last_updated": "2021-07-20T10:15:41.015238Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_ma4.mrold:TenGigE0/0/0/11_as102.mrold:1/1/25",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/14961",
                    "created": "2021-07-19",
                    "description": "ma4.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 1,
                    "hostname": "ma4.mrold",
                    "id": 2194,
                    "last_updated": "2021-07-19T15:47:57.396271Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "ma4.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/169",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/39",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/3",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "10G rate", "id": 3, "name": "10G", "unit_id": 3, "value": 10.0},
                "subrate": None,
            },
        ],
    }
    tma_mock.post_tma_cis_from_sparkid.return_value = {"devs": {"dne": {}}}
    result = get_plannet_cid(
        ticket=ticket, affected_ci_list=ticket["affectedCIs"], ticket_number="CHG123", exchanges=["mrold"]
    )
    assert result == (
        [],
        [{"ciName": "EBCL45462911/SKY-SECT-1874", "impactType": "Full Outage"}],
        [
            {"ciName": "as102.mrold.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "as2.mrold.uk.easynet.net", "impactType": "Full Outage"},
            {"ciName": "dslam.mrold", "impactType": "Full Outage"},
            {"ciName": "ws-access.mrold", "impactType": "Full Outage"},
        ],
        [],
    )  # noqa: E501


@patch("connectors.webserver.itsm.tasks.ticketGenerator.CustomService")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_circuit_types")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_interface_links")
def test_get_plannet_cid_case_4(get_interface_links_mock, get_circuit_types_mock, tma_mock):
    ticket = {
        "affectedCIs": [{"ciName": "as102.mrold.isp.sky.com", "impactType": "Full Outage"}],
        "changeType": "normal",
        "createdBy": "AMR45",
        "endDate": 1631357527,
        "shortDescription": "PARENT Ticket for Metro Migration Order",
        "startDate": 1631271127,
        "serviceType": "evpn",
        "templateName": "A Test Template",
        "thirdPartyTicket": {
            "thirdpartyImpact": "Full outage to service",
            "thirdpartyImpactReason": "Maintenance-Sky network Upgrade====",
        },
    }
    get_circuit_types_mock.return_value = circuit_types
    get_interface_links_mock.return_value = {
        "count": 7,
        "next": None,
        "previous": None,
        "results": [
            {
                "atg": {
                    "coordinator": None,
                    "date": "2016-08-15",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 84890,
                    "name": "link_as102.mrold.1/1/23_as2.mrold.1/0/28: starting on 2016-08-15_enabled_2016-08-15",
                    "name_str": "TG84890 link_as102.mrold.1/1/23_as2.mrold.1/0/28: starting on 2016-08-15_enabled_"
                    "2016-08-15 (15/08/2016)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "as102.mrold.1/1/23_as2.mrold.1/0/28",
                    "created": "2021-07-20",
                    "description": None,
                    "id": 14164,
                    "is_protected": False,
                    "last_updated": "2021-07-20T12:25:56.510479Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/7",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": None,
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/14",
                },
                "created": "2021-07-20",
                "description": "as102.mrold.1/1/23_as2.mrold.1/0/28: starting on 2016-08-15",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 36348,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261474,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:02.993558Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/23 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/28487",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 287931,
                    "lag": None,
                    "last_updated": "2021-07-19T19:46:01.438567Z",
                    "mac_address": None,
                    "name": "as2.mrold.uk.easynet.net GigabitEthernet1/0/28 | TG28487 (07/09/2013) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/8476",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "is_active": None,
                "last_updated": "2021-07-20T12:25:58.520333Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/23_as2.mrold:GigabitEthernet1/0/28",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/28487",
                    "created": "2021-07-19",
                    "description": "as2.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 1,
                    "hostname": "as2.mrold",
                    "id": 8476,
                    "last_updated": "2021-07-19T19:46:00.696087Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as2.mrold.uk.easynet.net",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/172",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/54",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/12",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2016-08-15",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 82758,
                    "name": "link_as102.mrold.1/1/7_as2.mrold.1/0/27: starting on 2016-08-15_enabled_2016-08-15",
                    "name_str": "TG82758 link_as102.mrold.1/1/7_as2.mrold.1/0/27: starting on 2016-08-15_enabled_"
                    "2016-08-15 (15/08/2016)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "as102.mrold.1/1/7_as2.mrold.1/0/27",
                    "created": "2021-07-20",
                    "description": None,
                    "id": 13098,
                    "is_protected": False,
                    "last_updated": "2021-07-20T11:45:23.883926Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/7",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": None,
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/14",
                },
                "created": "2021-07-20",
                "description": "as102.mrold.1/1/7_as2.mrold.1/0/27: starting on 2016-08-15",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 35292,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261458,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:01.945577Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/7 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/28487",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 287930,
                    "lag": None,
                    "last_updated": "2021-07-19T19:46:01.413116Z",
                    "mac_address": None,
                    "name": "as2.mrold.uk.easynet.net GigabitEthernet1/0/27 | TG28487 (07/09/2013) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/8476",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "is_active": None,
                "last_updated": "2021-07-20T11:45:25.851394Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/7_as2.mrold:GigabitEthernet1/0/27",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/28487",
                    "created": "2021-07-19",
                    "description": "as2.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 1,
                    "hostname": "as2.mrold",
                    "id": 8476,
                    "last_updated": "2021-07-19T19:46:00.696087Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as2.mrold.uk.easynet.net",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/172",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/54",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/12",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2018-02-12",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 219654,
                    "name": "link_bm0.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12",
                    "name_str": "TG219654 link_bm0.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12 "
                    "(12/02/2018)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "bm0.mrold.isp:ge9-0",
                    "created": "2021-07-21",
                    "description": None,
                    "id": 65367,
                    "is_protected": False,
                    "last_updated": "2021-07-21T23:15:01.241690Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/7",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/22",
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/20",
                },
                "created": "2021-07-21",
                "description": "bm0.mrold.isp:ge9-0: starting on 2018-02-12",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 98980,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261452,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:01.560413Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/1 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": None,
                "is_active": None,
                "last_updated": "2021-07-21T23:15:03.044471Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/1_dslam.mrold",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154790",
                    "created": "2021-07-21",
                    "description": "dslam.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154791",
                    "face": 0,
                    "height": 1,
                    "hostname": "dslam.mrold",
                    "id": 19720,
                    "last_updated": "2021-07-21T06:25:07.182241Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "dslam.mrold",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/175",
                    "ne_subrole": None,
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/65",
                    "parent": None,
                    "platform": None,
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2018-02-12",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 166562,
                    "name": "link_bm1.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12",
                    "name_str": "TG166562 link_bm1.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12"
                    " (12/02/2018)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "bm1.mrold.isp:ge9-0",
                    "created": "2021-07-21",
                    "description": None,
                    "id": 38024,
                    "is_protected": False,
                    "last_updated": "2021-07-21T09:14:44.983176Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/7",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/22",
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/20",
                },
                "created": "2021-07-21",
                "description": "bm1.mrold.isp:ge9-0: starting on 2018-02-12",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 72378,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261453,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:01.626147Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/2 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": None,
                "is_active": None,
                "last_updated": "2021-07-21T09:14:46.521793Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/2_dslam.mrold",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154790",
                    "created": "2021-07-21",
                    "description": "dslam.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154791",
                    "face": 0,
                    "height": 1,
                    "hostname": "dslam.mrold",
                    "id": 19720,
                    "last_updated": "2021-07-21T06:25:07.182241Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "dslam.mrold",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/175",
                    "ne_subrole": None,
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/65",
                    "parent": None,
                    "platform": None,
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2018-02-12",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 171826,
                    "name": "link_bm7.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12",
                    "name_str": "TG171826 link_bm7.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12 "
                    "(12/02/2018)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "bm7.mrold.isp:ge9-0",
                    "created": "2021-07-21",
                    "description": None,
                    "id": 40749,
                    "is_protected": False,
                    "last_updated": "2021-07-21T10:36:42.692928Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/7",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/22",
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/20",
                },
                "created": "2021-07-21",
                "description": "bm7.mrold.isp:ge9-0: starting on 2018-02-12",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 75010,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261454,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:01.690104Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/3 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": None,
                "is_active": None,
                "last_updated": "2021-07-21T10:36:44.184876Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/3_dslam.mrold",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154790",
                    "created": "2021-07-21",
                    "description": "dslam.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154791",
                    "face": 0,
                    "height": 1,
                    "hostname": "dslam.mrold",
                    "id": 19720,
                    "last_updated": "2021-07-21T06:25:07.182241Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "dslam.mrold",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/175",
                    "ne_subrole": None,
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/65",
                    "parent": None,
                    "platform": None,
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2021-04-29",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 258113,
                    "name": "link_ONEA45462911: starting on 2021-04-29_enabled_2021-04-29",
                    "name_str": "TG258113 link_ONEA45462911: starting on 2021-04-29_enabled_2021-04-29 (29/04/2021)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "EBCL45462911",
                    "created": "2021-07-22",
                    "description": None,
                    "id": 71289,
                    "is_protected": False,
                    "last_updated": "2021-07-22T09:51:09.266862Z",
                    "length": 0.0,
                    "parent_ref": "SKY-SECT-1874",
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/44",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/4",
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/25",
                },
                "created": "2021-07-22",
                "description": "ONEA45462911: starting on 2021-04-29",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 118242,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261455,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:01.754023Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/4 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": None,
                "is_active": None,
                "last_updated": "2021-07-22T09:51:11.251072Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/4_ws-access.mrold",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/160172",
                    "created": "2021-07-21",
                    "description": "ws-access.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/160173",
                    "face": 0,
                    "height": 1,
                    "hostname": "ws-access.mrold",
                    "id": 22411,
                    "last_updated": "2021-07-21T07:46:36.273979Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "ws-access.mrold",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/176",
                    "ne_subrole": None,
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/66",
                    "parent": None,
                    "platform": None,
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2021-04-29",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 258113,
                    "name": "link_ONEA45462911: starting on 2021-04-29_enabled_2021-04-29",
                    "name_str": "TG258113 link_ONEA45462911: starting on 2021-04-29_enabled_2021-04-29 (29/04/2021)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "ONEA45462911",
                    "created": "2021-07-22",
                    "description": None,
                    "id": 71289,
                    "is_protected": False,
                    "last_updated": "2021-07-22T09:51:09.266862Z",
                    "length": 0.0,
                    "parent_ref": "SKY-SECT-1874",
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/44",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/4",
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/25",
                },
                "created": "2021-07-22",
                "description": "ONEA45462911: starting on 2021-04-29",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 118242,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261455,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:01.754023Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/4 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": None,
                "is_active": None,
                "last_updated": "2021-07-22T09:51:11.251072Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/4_ws-access.mrold",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/160172",
                    "created": "2021-07-21",
                    "description": "ws-access.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/160173",
                    "face": 0,
                    "height": 1,
                    "hostname": "ws-access.mrold",
                    "id": 22411,
                    "last_updated": "2021-07-21T07:46:36.273979Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "ws-access.mrold",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/176",
                    "ne_subrole": None,
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/66",
                    "parent": None,
                    "platform": None,
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
        ],
    }
    tma_mock.post_tma_cis_from_sparkid.return_value = {"devs": {"dne": {}}}
    result = get_plannet_cid(
        ticket=ticket, affected_ci_list=ticket["affectedCIs"], ticket_number="CHG123", exchanges=["mrold"]
    )
    assert result == (
        [],
        [
            {"ciName": "EBCL45462911/SKY-SECT-1874", "impactType": "Full Outage"},
            {"ciName": "ONEA45462911", "impactType": "Full Outage"},
        ],
        [
            {"ciName": "as2.mrold.uk.easynet.net", "impactType": "Full Outage"},
            {"ciName": "dslam.mrold", "impactType": "Full Outage"},
            {"ciName": "ws-access.mrold", "impactType": "Full Outage"},
        ],
        [],
    )  # noqa: E501


@patch("connectors.webserver.itsm.tasks.ticketGenerator.CustomService")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_circuit_types")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_interface_links")
def test_get_plannet_cid_case_5(get_interface_links_mock, get_circuit_types_mock, tma_mock):
    ticket = {
        "affectedCIs": [{"ciName": "as102.mrold.isp.sky.com", "impactType": "Full Outage"}],
        "changeType": "normal",
        "createdBy": "AMR45",
        "endDate": 1631357527,
        "shortDescription": "PARENT Ticket for Metro Migration Order",
        "startDate": 1631271127,
        "serviceType": "evpn",
        "templateName": "A Test Template",
        "thirdPartyTicket": {
            "thirdpartyImpact": "Full outage to service",
            "thirdpartyImpactReason": "Maintenance-Sky network Upgrade====",
        },
    }
    get_circuit_types_mock.return_value = circuit_types
    get_interface_links_mock.return_value = {
        "count": 7,
        "next": None,
        "previous": None,
        "results": [
            {
                "atg": {
                    "coordinator": None,
                    "date": "2016-08-15",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 84890,
                    "name": "link_as102.mrold.1/1/23_as2.mrold.1/0/28: starting on 2016-08-15_enabled_2016-08-15",
                    "name_str": "TG84890 link_as102.mrold.1/1/23_as2.mrold.1/0/28: starting on 2016-08-15_enabled_"
                    "2016-08-15 (15/08/2016)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "as102.mrold.1/1/23_as2.mrold.1/0/28",
                    "created": "2021-07-20",
                    "description": None,
                    "id": 14164,
                    "is_protected": False,
                    "last_updated": "2021-07-20T12:25:56.510479Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/7",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": None,
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/14",
                },
                "created": "2021-07-20",
                "description": "as102.mrold.1/1/23_as2.mrold.1/0/28: starting on 2016-08-15",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 36348,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261474,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:02.993558Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/23 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/28487",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 287931,
                    "lag": None,
                    "last_updated": "2021-07-19T19:46:01.438567Z",
                    "mac_address": None,
                    "name": "as2.mrold.uk.easynet.net GigabitEthernet1/0/28 | TG28487 (07/09/2013) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/8476",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "is_active": None,
                "last_updated": "2021-07-20T12:25:58.520333Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/23_as2.mrold:GigabitEthernet1/0/28",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/28487",
                    "created": "2021-07-19",
                    "description": "as2.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 1,
                    "hostname": "as2.mrold",
                    "id": 8476,
                    "last_updated": "2021-07-19T19:46:00.696087Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as2.mrold.uk.easynet.net",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/172",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/54",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/12",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2016-08-15",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 82758,
                    "name": "link_as102.mrold.1/1/7_as2.mrold.1/0/27: starting on 2016-08-15_enabled_2016-08-15",
                    "name_str": "TG82758 link_as102.mrold.1/1/7_as2.mrold.1/0/27: starting on 2016-08-15_enabled_"
                    "2016-08-15 (15/08/2016)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "as102.mrold.1/1/7_as2.mrold.1/0/27",
                    "created": "2021-07-20",
                    "description": None,
                    "id": 13098,
                    "is_protected": False,
                    "last_updated": "2021-07-20T11:45:23.883926Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/7",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": None,
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/14",
                },
                "created": "2021-07-20",
                "description": "as102.mrold.1/1/7_as2.mrold.1/0/27: starting on 2016-08-15",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 35292,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261458,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:01.945577Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/7 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/28487",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 287930,
                    "lag": None,
                    "last_updated": "2021-07-19T19:46:01.413116Z",
                    "mac_address": None,
                    "name": "as2.mrold.uk.easynet.net GigabitEthernet1/0/27 | TG28487 (07/09/2013) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/8476",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "is_active": None,
                "last_updated": "2021-07-20T11:45:25.851394Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/7_as2.mrold:GigabitEthernet1/0/27",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/28487",
                    "created": "2021-07-19",
                    "description": "as2.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 1,
                    "hostname": "as2.mrold",
                    "id": 8476,
                    "last_updated": "2021-07-19T19:46:00.696087Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as2.mrold.uk.easynet.net",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/172",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/54",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/12",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2018-02-12",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 219654,
                    "name": "link_bm0.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12",
                    "name_str": "TG219654 link_bm0.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12 "
                    "(12/02/2018)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "bm0.mrold.isp:ge9-0",
                    "created": "2021-07-21",
                    "description": None,
                    "id": 65367,
                    "is_protected": False,
                    "last_updated": "2021-07-21T23:15:01.241690Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/7",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/22",
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/20",
                },
                "created": "2021-07-21",
                "description": "bm0.mrold.isp:ge9-0: starting on 2018-02-12",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 98980,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261452,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:01.560413Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/1 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": None,
                "is_active": None,
                "last_updated": "2021-07-21T23:15:03.044471Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/1_dslam.mrold",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154790",
                    "created": "2021-07-21",
                    "description": "dslam.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154791",
                    "face": 0,
                    "height": 1,
                    "hostname": "dslam.mrold",
                    "id": 19720,
                    "last_updated": "2021-07-21T06:25:07.182241Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "dslam.mrold",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/175",
                    "ne_subrole": None,
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/65",
                    "parent": None,
                    "platform": None,
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2018-02-12",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 166562,
                    "name": "link_bm1.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12",
                    "name_str": "TG166562 link_bm1.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12"
                    " (12/02/2018)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "bm1.mrold.isp:ge9-0",
                    "created": "2021-07-21",
                    "description": None,
                    "id": 38024,
                    "is_protected": False,
                    "last_updated": "2021-07-21T09:14:44.983176Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/7",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/22",
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/20",
                },
                "created": "2021-07-21",
                "description": "bm1.mrold.isp:ge9-0: starting on 2018-02-12",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 72378,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261453,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:01.626147Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/2 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": None,
                "is_active": None,
                "last_updated": "2021-07-21T09:14:46.521793Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/2_dslam.mrold",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154790",
                    "created": "2021-07-21",
                    "description": "dslam.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154791",
                    "face": 0,
                    "height": 1,
                    "hostname": "dslam.mrold",
                    "id": 19720,
                    "last_updated": "2021-07-21T06:25:07.182241Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "dslam.mrold",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/175",
                    "ne_subrole": None,
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/65",
                    "parent": None,
                    "platform": None,
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2018-02-12",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 171826,
                    "name": "link_bm7.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12",
                    "name_str": "TG171826 link_bm7.mrold.isp:ge9-0: starting on 2018-02-12_enabled_2018-02-12 "
                    "(12/02/2018)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "bm7.mrold.isp:ge9-0",
                    "created": "2021-07-21",
                    "description": None,
                    "id": 40749,
                    "is_protected": False,
                    "last_updated": "2021-07-21T10:36:42.692928Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/7",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/22",
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/20",
                },
                "created": "2021-07-21",
                "description": "bm7.mrold.isp:ge9-0: starting on 2018-02-12",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 75010,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261454,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:01.690104Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/3 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": None,
                "is_active": None,
                "last_updated": "2021-07-21T10:36:44.184876Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/3_dslam.mrold",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154790",
                    "created": "2021-07-21",
                    "description": "dslam.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/154791",
                    "face": 0,
                    "height": 1,
                    "hostname": "dslam.mrold",
                    "id": 19720,
                    "last_updated": "2021-07-21T06:25:07.182241Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "dslam.mrold",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/175",
                    "ne_subrole": None,
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/65",
                    "parent": None,
                    "platform": None,
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2021-04-29",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 258113,
                    "name": "link_ONEA45462911: starting on 2021-04-29_enabled_2021-04-29",
                    "name_str": "TG258113 link_ONEA45462911: starting on 2021-04-29_enabled_2021-04-29 (29/04/2021)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "EBCL45462911",
                    "created": "2021-07-22",
                    "description": None,
                    "id": 71289,
                    "is_protected": False,
                    "last_updated": "2021-07-22T09:51:09.266862Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/44",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/4",
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/25",
                },
                "created": "2021-07-22",
                "description": "ONEA45462911: starting on 2021-04-29",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 118242,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261455,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:01.754023Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/4 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": None,
                "is_active": None,
                "last_updated": "2021-07-22T09:51:11.251072Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/4_ws-access.mrold",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/160172",
                    "created": "2021-07-21",
                    "description": "ws-access.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/160173",
                    "face": 0,
                    "height": 1,
                    "hostname": "ws-access.mrold",
                    "id": 22411,
                    "last_updated": "2021-07-21T07:46:36.273979Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "ws-access.mrold",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/176",
                    "ne_subrole": None,
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/66",
                    "parent": None,
                    "platform": None,
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
            {
                "atg": {
                    "coordinator": None,
                    "date": "2021-04-29",
                    "dependencies": [],
                    "domains": ["https://plannet.cf.paas.bskyb.com/api/dcim/domains/1"],
                    "id": 258113,
                    "name": "link_ONEA45462911: starting on 2021-04-29_enabled_2021-04-29",
                    "name_str": "TG258113 link_ONEA45462911: starting on 2021-04-29_enabled_2021-04-29 (29/04/2021)",
                    "nis_ref": None,
                },
                "circuit": {
                    "a_site_external_cable_id": None,
                    "a_site_external_cable_length": None,
                    "b_site_external_cable_id": None,
                    "b_site_external_cable_length": None,
                    "capacity": 1000,
                    "cct_no": None,
                    "cid": "ONEA45462911",
                    "created": "2021-07-22",
                    "description": None,
                    "id": 71289,
                    "is_protected": False,
                    "last_updated": "2021-07-22T09:51:09.266862Z",
                    "length": 0.0,
                    "parent_ref": None,
                    "provider": "https://plannet.cf.paas.bskyb.com/api/dcim/providers/44",
                    "rate": "https://plannet.cf.paas.bskyb.com/api/dcim/rates/2",
                    "subtype": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/4",
                    "tenant": None,
                    "type": "https://plannet.cf.paas.bskyb.com/api/circuits/circuit-types/25",
                },
                "created": "2021-07-22",
                "description": "ONEA45462911: starting on 2021-04-29",
                "dtg": {
                    "coordinator": None,
                    "date": "2099-12-31",
                    "dependencies": [],
                    "domains": [],
                    "id": 9999,
                    "name": "Default End Transition",
                    "name_str": "TG9999 Default End Transition (31/12/2099)",
                    "nis_ref": "TG9999",
                },
                "id": 118242,
                "interface_1": {
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "card": None,
                    "created": "2021-07-19",
                    "description": None,
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "fpe": None,
                    "id": 261455,
                    "lag": None,
                    "last_updated": "2021-07-19T19:18:01.754023Z",
                    "mac_address": None,
                    "name": "as102.mrold.isp.sky.com 1/1/4 | TG27185 (18/07/2016) TG9999 (31/12/2099)",
                    "ne": "https://plannet.cf.paas.bskyb.com/api/dcim/nes/7511",
                    "rates": [1, 2],
                    "related_interface": None,
                    "tagged_vlans": [],
                    "type": "https://plannet.cf.paas.bskyb.com/api/dcim/interface-type/1",
                    "untagged_vlan": None,
                },
                "interface_2": None,
                "is_active": None,
                "last_updated": "2021-07-22T09:51:11.251072Z",
                "link_prev": None,
                "link_type": {"abbreviation": "EB", "id": 2, "layer_id": 3.2, "name": "Ethernet Bearer"},
                "name": "EB_as102.mrold:1/1/4_ws-access.mrold",
                "ne_1": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/27185",
                    "created": "2021-07-19",
                    "description": "as102.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/9999",
                    "face": 0,
                    "height": 2,
                    "hostname": "as102.mrold",
                    "id": 7511,
                    "last_updated": "2021-07-19T19:18:01.500231Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "as102.mrold.isp.sky.com",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/171",
                    "ne_subrole": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/170",
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/52",
                    "parent": None,
                    "platform": "https://plannet.cf.paas.bskyb.com/api/dcim/platforms/14",
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "ne_2": {
                    "asn": None,
                    "atg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/160172",
                    "created": "2021-07-21",
                    "description": "ws-access.mrold",
                    "dtg": "https://plannet.cf.paas.bskyb.com/api/dcim/tgs/160173",
                    "face": 0,
                    "height": 1,
                    "hostname": "ws-access.mrold",
                    "id": 22411,
                    "last_updated": "2021-07-21T07:46:36.273979Z",
                    "local_context_data": None,
                    "logical_site": None,
                    "name": "ws-access.mrold",
                    "ne_role": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-roles/176",
                    "ne_subrole": None,
                    "ne_type": "https://plannet.cf.paas.bskyb.com/api/dcim/ne-types/66",
                    "parent": None,
                    "platform": None,
                    "position": None,
                    "rack": None,
                    "room": None,
                    "serial": None,
                    "site": "https://plannet.cf.paas.bskyb.com/api/dcim/sites/2025",
                    "state": "ACTIVE",
                    "tenant": None,
                },
                "parents": [],
                "rate": {"description": "1G rate", "id": 2, "name": "1G", "unit_id": 3, "value": 1.0},
                "subrate": None,
            },
        ],
    }
    tma_mock.post_tma_cis_from_sparkid.return_value = {"devs": {"dne": {}}}
    result = get_plannet_cid(
        ticket=ticket, affected_ci_list=ticket["affectedCIs"], ticket_number="CHG123", exchanges=["mrold"]
    )
    assert result == (
        [],
        [
            {"ciName": "ONEA45462911", "impactType": "Full Outage"},
        ],
        [
            {"ciName": "as2.mrold.uk.easynet.net", "impactType": "Full Outage"},
            {"ciName": "dslam.mrold", "impactType": "Full Outage"},
            {"ciName": "ws-access.mrold", "impactType": "Full Outage"},
        ],
        [],
    )  # noqa: E501


@patch("connectors.webserver.itsm.tasks.ticketGenerator.custom_query")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.create_third_party_ticket")
def test_third_party_ticket_case_1(create_third_party, custom):
    cilist = [{"ciName": "ONEA45462911", "impactType": "Full Outage"}]
    ticket = {
        "affectedCIs": [{"ciName": "as102.mrold.isp.sky.com", "impactType": "Full Outage"}],
        "changeType": "normal",
        "createdBy": "AMR45",
        "endDate": 1631357527,
        "shortDescription": "PARENT Ticket for Metro Migration Order",
        "startDate": 1631271127,
        "serviceType": "evpn",
        "templateName": "A Test Template",
        "thirdPartyTicket": {
            "thirdpartyImpact": "Full outage to service",
            "thirdpartyImpactReason": "Maintenance-Sky network Upgrade====",
        },
    }
    ticket_number = "Test123"
    create_third_party.return_value = {"status": "SUCCESS"}
    custom.return_value = {
        "result": [
            {"circuitID": "ONEA50106115", "u_customer": {"displayValue": "SSE"}},
            {"circuitID": "ONEA50106661", "u_customer": {"displayValue": "Entanet"}},
        ]
    }
    result = third_party_ticket_creation(affected_ci_list=cilist, ticket=ticket, ticket_number=ticket_number)
    assert result == {"status": "SUCCESS"}


def test_third_party_ticket_case_2():
    cilist = [{"ciName": "ONEA45462911", "impactType": "Full Outage"}]

    with pytest.raises(KeyError):
        result = third_party_ticket_creation(affected_ci_list=cilist, ticket={})
        assert result == {}


grandma_data_csv = (
    "EXCHANGE_CODE,HOST_NAME,SLOT_NUMBER,SKY_CUSTOMER_COUNT,ENTERPRISE_CUSTOMER_COUNT,"
    "SKYWIFI_CUSTOMER_COUNT\nEACOL,bm0.eacol.isp.sky.com,1,43,0,0\nEACOL,bm0.eacol.isp.sky.com,2,39,0,"
    "0\nEACOL,cr0.eacol.uk.easynet.net,3,43,6,0\nEACOL,cr0.eacol.uk.easynet.net,3,43,3,0\n"
)


@patch("connectors.core.services.custom.connector.CustomService.read_grandma")
@patch("connectors.core.services.custom.connector.CustomService.read_tma")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.attach_files")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.create_third_party_ticket")
def test_process_custom_scripts(mock_third_party, mock_attach_files, mock_tma, mock_grandma):
    mock_grandma.return_value = grandma_data_csv
    mock_third_party.return_value = {"status": "SUCCESS"}
    mock_tma.return_value = b"<html></html>"
    mock_attach_files.return_value = True
    result = process_custom_scripts(ticket_number="CHG12345", ticket=data15["body"])
    assert result is True


@patch("connectors.core.services.custom.connector.CustomService.read_grandma")
@patch("connectors.core.services.custom.connector.CustomService.read_tma")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.attach_files")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.create_third_party_ticket")
def test_process_custom_scripts_nsi(mock_third_party, mock_attach_files, mock_tma, mock_grandma):
    mock_grandma.return_value = grandma_data_csv
    mock_third_party.return_value = {"status": "SUCCESS"}
    mock_tma.return_value = b"<html></html>"
    mock_attach_files.return_value = True
    result = process_custom_scripts(ticket_number="CHG12345", ticket=data16["body"])
    assert result is True


def test_calculate_wait_time_offset_case1():
    past_time = int(time.time() - 3600 * 5)
    with pytest.raises(InvalidRequest):
        response = calculate_wait_time_offset(past_time)
        assert response.body["detail"] == "Start Date is in past"


def test_calculate_wait_time_offset_case2():
    date_set = start_date
    epoch = datetime(1970, 1, 1)
    offset = 0
    date_start = datetime.utcfromtimestamp(date_set).date()
    date_today = datetime.today().date()
    wait_time_is = (date_start - date_today).days
    start_date_midnight = (date_start - epoch.date()).total_seconds()
    start_date_offset = (start_date - start_date_midnight) / (60 * 60)
    offset += start_date_offset
    offset_check, wait_time_check = calculate_wait_time_offset(date_set)
    assert offset_check == offset
    assert wait_time_check == wait_time_is


data_service_type_check2 = {
    "body": {
        "affectedCIs": [{"ciName": "ma0.test.bllab.it.bb.sky.com", "impactType": "No Service Impact"}],
        "serviceType": "geaProvisioning",
        "changeType": "minor",
        "createdBy": "amr45",
        "endDate": int(time.time() + 3600 * 39),
        "shortDescription": "PARENT Ticket for Metro Migration Order",
        "configGroup": "ITA - Broadband & Talk - Metro Aggregation",
        "assignmentGroup": "UK Network Integration Team - TechUK",
        "parentChange": "CHG0084714",
        "startDate": int(time.time() + 3600 * 29),
        "templateName": "UK CDN: STD29 - 3rd Party CDN Planned Maintenance - BBC",
        "attachments": [
            {"fileName": "PatchingRequest.log", "fileContent": "R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="}
        ],
        "reScheduledInfo": {"prevTktNumber": "CHG0092700", "justification": "Reasons for previous failure"},
    }
}
data_service_type_check3 = {
    "body": {
        "affectedCIs": [{"ciName": "ma0.test.bllab.it.bb.sky.com", "impactType": "No Service Impact"}],
        "serviceType": "geaProvisioning",
        "changeType": "minor",
        "createdBy": "amr45",
        "endDate": int(time.time() + 3600 * 30),
        "shortDescription": "PARENT Ticket for Metro Migration Order",
        "configGroup": "ITA - Broadband & Talk - Metro Aggregation",
        "assignmentGroup": "UK Network Integration Team - TechUK",
        "parentChange": "CHG0084714",
        "startDate": int(time.time() + 3600 * 24),
        "templateName": "UK CDN: STD29 - 3rd Party CDN Planned Maintenance - BBC",
        "attachments": [
            {"fileName": "PatchingRequest.log", "fileContent": "R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="}
        ],
        "reScheduledInfo": {"prevTktNumber": "CHG0092700", "justification": "Reasons for previous failure"},
    }
}
data_service_type_check4 = {
    "body": {
        "affectedCIs": [{"ciName": "ma0.test.bllab.it.bb.sky.com", "impactType": "No Service Impact"}],
        "serviceType": "geaProvisioning",
        "changeType": "minor",
        "createdBy": "amr45",
        "endDate": start_date,
        "shortDescription": "PARENT Ticket for Metro Migration Order",
        "configGroup": "ITA - Broadband & Talk - Metro Aggregation",
        "assignmentGroup": "UK Network Integration Team - TechUK",
        "parentChange": "CHG0084714",
        "startDate": end_date,
        "templateName": "UK CDN: STD29 - 3rd Party CDN Planned Maintenance - BBC",
        "attachments": [
            {"fileName": "PatchingRequest.log", "fileContent": "R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="}
        ],
        "reScheduledInfo": {"prevTktNumber": "CHG0092700", "justification": "Reasons for previous failure"},
    }
}


@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3405")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
def test_ticket_creation16(
    rest_get_mock, service3040, service3045, service3401, service3020, service3800, service3405, email_notify_mock
):
    rest_get_mock.side_effect = get_working_day_side_effect
    service3800.return_value = []
    service3020.return_value = [
        {
            "event_name": "DE Bank Holiday: Mariä Himmelfahrt",
            "event_start_time": "14/08/2020 22:00:00",
            "event_end_time": "15/08/2020 21:59:59",
            "applies_to": "cmdb_ci_service",
            "condition": "Business areas CONTAINS Group Digital Platforms .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "DE - Bank Holidays ",
            "blackout_schedule_type": "Change Freeze",
        }
    ]
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3045.return_value = {"result": {"status": "CHG0115712 (ATTACHMENT ADDED)", "ticketNumber": "CHG0115712"}}
    service3040.return_value = True
    service3405.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    result = create_ticket(**data_service_type_check2)
    assert result["status"] == "SUCCESSFUL"


@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3405")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
def test_ticket_creation17(
    rest_get_mock, service3040, service3045, service3401, service3020, service3800, service3405, email_notify_mock
):
    rest_get_mock.side_effect = get_working_day_side_effect
    service3800.return_value = []
    service3020.return_value = [
        {
            "event_name": "DE Bank Holiday: Mariä Himmelfahrt",
            "event_start_time": "14/08/2020 22:00:00",
            "event_end_time": "15/08/2020 21:59:59",
            "applies_to": "cmdb_ci_service",
            "condition": "Business areas CONTAINS Group Digital Platforms .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "DE - Bank Holidays ",
            "blackout_schedule_type": "Change Freeze",
        }
    ]
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3045.return_value = {"result": {"status": "CHG0115712 (ATTACHMENT ADDED)", "ticketNumber": "CHG0115712"}}
    service3040.return_value = True
    service3405.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    result = create_ticket(**data_service_type_check3)
    assert result["status"] == "SUCCESSFUL"


@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
def test_ticket_creation18(service3040, service3045, service3401, service3020, service3800):
    service3800.return_value = []
    service3020.return_value = [
        {
            "event_name": "DE Bank Holiday: Mariä Himmelfahrt",
            "event_start_time": "14/08/2020 22:00:00",
            "event_end_time": "15/08/2020 21:59:59",
            "applies_to": "cmdb_ci_service",
            "condition": "Business areas CONTAINS Group Digital Platforms .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "DE - Bank Holidays ",
            "blackout_schedule_type": "Change Freeze",
        }
    ]
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3045.return_value = {"result": {"status": "CHG0115712 (ATTACHMENT ADDED)", "ticketNumber": "CHG0115712"}}
    service3040.return_value = True
    response = create_ticket(**data_service_type_check4)
    assert response.body["detail"] == "Either Start Date is in past or Start Date is greater than End Date"


db_record_1 = {
    "notifychangewindow": [
        {
            "metroMigration": {
                "channel": "email",
                "emailRecipients": {
                    "toList": ["user@sky.uk"],
                    "ccList": ["user@sky.uk"],
                    "bccList": ["user@sky.uk"],
                },
                "notifyChg": True,
                "notifyCtask": False,
            }
        }
    ]
}

db_record_2 = {
    "notifychangewindow": [
        {
            "metroMigration": {
                "channel": "email",
                "emailRecipients": {
                    "toList": ["user@sky.uk"],
                    "ccList": ["user@sky.uk"],
                    "bccList": ["user@sky.uk"],
                },
                "notifyChg": True,
                "notifyCtask": True,
            }
        }
    ]
}

cw_ticket = {
    "affectedCIs": [{"ciName": "ta1.bllabd1.isp.sky.com", "impactType": "At Risk"}],
    "changeType": "normal",
    "createdBy": "SVC-APP-DNE",
    "endDate": 1684656000,
    "serviceType": "metroMigration",
    "shortDescription": "PARENT Ticket for (bllabd1) exchange migration via DNE Order 158931 : DS-LEG-P2B-SP",
    "startDate": 1684634400,
    "templateName": "template5324",
    "orderNumber": "158931",
    "thirdPartyTicket": {
        "thirdpartyImpact": "Full outage to service",
        "thirdpartyImpactReason": "Maintenance-Sky network Upgrade",
    },
}


@patch("connectors.webserver.itsm.tasks.ticketGenerator.email_notifications")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.ServiceDB")
def test_notify_cw_change_case1(db_mock, mock_email_sender):
    db_mock.return_value.find_one.return_value = db_record_1
    mock_email_sender.return_value = True
    result = notify_cw_change(cw_ticket, "CHG12345", 1684720800)
    assert result


@patch("connectors.webserver.itsm.tasks.ticketGenerator.email_notifications")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.ServiceDB")
def test_notify_cw_change_case2(db_mock, mock_email_sender):
    db_mock.return_value.find_one.return_value = None
    mock_email_sender.return_value = True
    result = notify_cw_change(cw_ticket, "CHG12345", 1684720800)
    assert not result


@patch("connectors.webserver.itsm.tasks.ticketGenerator.email_notifications")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.ServiceDB")
def test_notify_cw_change_case3(db_mock, mock_email_sender):
    db_mock.return_value.find_one.return_value = db_record_1
    mock_email_sender.return_value = connexion.problem(
        status=400,
        title=f"There is no valid email address in toList",
        detail=f"Problems with `toList` " f"key",
    )
    result = notify_cw_change(cw_ticket, "CHG12345", 1684720800)
    assert not result


@patch("connectors.webserver.itsm.tasks.ticketGenerator.email_notifications")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.ServiceDB")
def test_notify_cw_change_case4(db_mock, mock_email_sender):
    db_mock.return_value.find_one.return_value = db_record_2
    mock_email_sender.return_value = True
    result = notify_cw_change(data_minor3["body"], "CTASK12345", 1684720800)
    assert result


data_ci_list = {
    "body": {
        "affectedCIs": [
            {"ciName": "OGHP63446144", "impactType": "Full Outage"},
            {"ciName": "bm0.smhh", "impactType": "Full Outage"},
            {"ciName": "bm6.smhh", "impactType": "Full Outage"},
            {"ciName": "OGHP76271324", "impactType": "Full Outage"},
            {"ciName": "OGHP28721918", "impactType": "Full Outage"},
            {"ciName": "OGHP28131842", "impactType": "Full Outage"},
            {"ciName": "br1.bllabd1.isp.sky.com", "impactType": "At Risk"},
            {"ciName": "as1.smhh.uk.easynet.net", "impactType": "Full Outage"},
            {"ciName": "me1.bllabd1.isp.sky.com", "impactType": "At Risk"},
            {"ciName": "OGHP01091130", "impactType": "Full Outage"},
            {"ciName": "OGHP05292165", "impactType": "Full Outage"},
            {"ciName": "bm1.smhh", "impactType": "Full Outage"},
            {"ciName": "bm5.smhh", "impactType": "Full Outage"},
            {"ciName": "OGHP30536396", "impactType": "Full Outage"},
            {"ciName": "OGHP52861225", "impactType": "Full Outage"},
            {"ciName": "OGHP73031152", "impactType": "Full Outage"},
            {"ciName": "OGHP48305512", "impactType": "Full Outage"},
            {"ciName": "ma2.bllabd1.isp.sky.com", "impactType": "At Risk"},
            {"ciName": "OGHP21887660", "impactType": "Full Outage"},
            {"ciName": "br0.bllabd1.isp.sky.com", "impactType": "At Risk"},
            {"ciName": "as100.bllabd1.isp.sky.com", "impactType": "At Risk"},
            {"ciName": "OGHP17146160", "impactType": "Full Outage"},
            {"ciName": "OGHP03338317", "impactType": "Full Outage"},
            {"ciName": "OGHP55225957", "impactType": "Full Outage"},
            {"ciName": "OGHP45051770", "impactType": "Full Outage"},
            {"ciName": "OGHP59351742", "impactType": "Full Outage"},
            {"ciName": "OGHP52861215", "impactType": "Full Outage"},
            {"ciName": "bm3.smhh", "impactType": "Full Outage"},
            {"ciName": "OGHP71003945", "impactType": "Full Outage"},
            {"ciName": "me0.bllabd2.isp.sky.com", "impactType": "At Risk"},
            {"ciName": "bm11.smhh", "impactType": "Full Outage"},
            {"ciName": "OGHP76271308", "impactType": "Full Outage"},
            {"ciName": "bm9.smhh", "impactType": "Full Outage"},
            {"ciName": "OGHP54880551", "impactType": "Full Outage"},
            {"ciName": "OGHP51984449", "impactType": "Full Outage"},
            {"ciName": "br0.bllabd3.isp.sky.com", "impactType": "At Risk"},
            {"ciName": "bm10.smhh", "impactType": "Full Outage"},
            {"ciName": "OGHP51984457", "impactType": "Full Outage"},
            {"ciName": "OGHP63088406", "impactType": "Full Outage"},
            {"ciName": "OGHP62932184", "impactType": "Full Outage"},
            {"ciName": "bm8.smhh", "impactType": "Full Outage"},
            {"ciName": "OGHP70652013", "impactType": "Full Outage"},
            {"ciName": "OGHP32499332", "impactType": "Full Outage"},
            {"ciName": "bm2.smhh", "impactType": "Full Outage"},
            {"ciName": "bm4.smhh", "impactType": "Full Outage"},
            {"ciName": "OGHP75161936", "impactType": "Full Outage"},
            {"ciName": "bm7.smhh", "impactType": "Full Outage"},
            {"ciName": "OGHP46433868", "impactType": "Full Outage"},
            {"ciName": "OGHP51984441", "impactType": "Full Outage"},
            {"ciName": "OGHP14293810", "impactType": "Full Outage"},
            {"ciName": "OGHP46433866", "impactType": "Full Outage"},
            {"ciName": "br1.bllabd3.isp.sky.com", "impactType": "At Risk"},
            {"ciName": "OGHP74591114", "impactType": "Full Outage"},
            {"ciName": "as100.bllabd5.isp.sky.com", "impactType": "At Risk"},
            {"ciName": "OGHP52861239", "impactType": "Full Outage"},
            {"ciName": "OGHP71192824", "impactType": "Full Outage"},
        ],
        "changeType": "normal",
        "createdBy": "vsh18",
        "endDate": end_date,
        "offset": 0,
        "shortDescription": "12345",
        "startDate": start_date,
        "serviceType": "ubbMigration",
        "templateName": "UK CDN: STD29 - 3rd Party CDN Planned Maintenance - BBC",
        "attachments": [
            {"fileName": "PatchingRequest.log", "fileContent": "R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="}
        ],
        "reScheduledInfo": {"prevTktNumber": "CHG0092700", "justification": "Reasons for previous failure"},
        "implementationPlanDtls": {
            "templatedText": {
                "templateName": "dnsCfgRequest",
                "templateAttribute": {
                    "previousTktNo": "CHG12345",
                    "deviceToDel": {"hostName": "mr1-dvn.enlba.isp.sky.com", "ipaddress": "89.200.128.62"},
                    "configuration": [
                        {"record": "mr1-dvn.enlba.isp.sky.com", "value": "89.200.128.62", "status": "NEW"}
                    ],
                },
            },
        },
    }
}

data_ci_list2 = {
    "body": {
        "affectedCIs": [
            {"ciName": "OGHP63446144", "impactType": "Full Outage"},
            {"ciName": "bm0.smhh", "impactType": "Full Outage"},
            {"ciName": "bm6.smhh", "impactType": "Full Outage"},
            {"ciName": "OGHP76271324", "impactType": "Full Outage"},
            {"ciName": "OGHP28721918", "impactType": "Full Outage"},
            {"ciName": "OGHP28131842", "impactType": "Full Outage"},
            {"ciName": "br1.bllabd1.isp.sky.com", "impactType": "At Risk"},
            {"ciName": "as1.smhh.uk.easynet.net", "impactType": "Full Outage"},
            {"ciName": "me1.bllabd1.isp.sky.com", "impactType": "At Risk"},
            {"ciName": "OGHP01091130", "impactType": "Full Outage"},
            {"ciName": "OGHP05292165", "impactType": "Full Outage"},
            {"ciName": "bm1.smhh", "impactType": "Full Outage"},
            {"ciName": "bm5.smhh", "impactType": "Full Outage"},
            {"ciName": "OGHP30536396", "impactType": "Full Outage"},
            {"ciName": "OGHP52861225", "impactType": "Full Outage"},
            {"ciName": "OGHP73031152", "impactType": "Full Outage"},
            {"ciName": "OGHP48305512", "impactType": "Full Outage"},
            {"ciName": "ma2.bllabd1.isp.sky.com", "impactType": "At Risk"},
            {"ciName": "OGHP21887660", "impactType": "Full Outage"},
            {"ciName": "br0.bllabd1.isp.sky.com", "impactType": "At Risk"},
            {"ciName": "as100.bllabd1.isp.sky.com", "impactType": "At Risk"},
            {"ciName": "OGHP17146160", "impactType": "Full Outage"},
            {"ciName": "OGHP03338317", "impactType": "Full Outage"},
            {"ciName": "OGHP55225957", "impactType": "Full Outage"},
            {"ciName": "OGHP45051770", "impactType": "Full Outage"},
            {"ciName": "OGHP59351742", "impactType": "Full Outage"},
            {"ciName": "OGHP52861215", "impactType": "Full Outage"},
            {"ciName": "bm3.smhh", "impactType": "Full Outage"},
            {"ciName": "OGHP71003945", "impactType": "Full Outage"},
            {"ciName": "me0.bllabd2.isp.sky.com", "impactType": "At Risk"},
            {"ciName": "bm11.smhh", "impactType": "Full Outage"},
            {"ciName": "OGHP76271308", "impactType": "Full Outage"},
            {"ciName": "bm9.smhh", "impactType": "Full Outage"},
            {"ciName": "OGHP54880551", "impactType": "Full Outage"},
            {"ciName": "OGHP51984449", "impactType": "Full Outage"},
            {"ciName": "br0.bllabd3.isp.sky.com", "impactType": "At Risk"},
            {"ciName": "bm10.smhh", "impactType": "Full Outage"},
            {"ciName": "OGHP51984457", "impactType": "Full Outage"},
            {"ciName": "OGHP63088406", "impactType": "Full Outage"},
            {"ciName": "OGHP62932184", "impactType": "Full Outage"},
            {"ciName": "bm8.smhh", "impactType": "Full Outage"},
            {"ciName": "OGHP70652013", "impactType": "Full Outage"},
            {"ciName": "OGHP32499332", "impactType": "Full Outage"},
            {"ciName": "bm2.smhh", "impactType": "Full Outage"},
            {"ciName": "bm4.smhh", "impactType": "Full Outage"},
            {"ciName": "OGHP75161936", "impactType": "Full Outage"},
            {"ciName": "bm7.smhh", "impactType": "Full Outage"},
            {"ciName": "OGHP46433868", "impactType": "Full Outage"},
            {"ciName": "OGHP51984441", "impactType": "Full Outage"},
            {"ciName": "OGHP14293810", "impactType": "Full Outage"},
            {"ciName": "OGHP46433866", "impactType": "Full Outage"},
            {"ciName": "br1.bllabd3.isp.sky.com", "impactType": "At Risk"},
            {"ciName": "OGHP74591114", "impactType": "Full Outage"},
            {"ciName": "as100.bllabd5.isp.sky.com", "impactType": "At Risk"},
            {"ciName": "OGHP52861239", "impactType": "Full Outage"},
            {"ciName": "OGHP71192824", "impactType": "Full Outage"},
        ],
        "changeType": "normal",
        "createdBy": "vsh18",
        "endDate": end_date,
        "offset": 0,
        "shortDescription": "12345",
        "startDate": start_date,
        "serviceType": "ubbMigration",
        "templateName": "UK CDN: STD29 - 3rd Party CDN Planned Maintenance - BBC",
        "attachments": [
            {"fileName": "PatchingRequest.log", "fileContent": "R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="}
        ],
        "reScheduledInfo": {"prevTktNumber": "CHG0092700", "justification": "Reasons for previous failure"},
        "implementationPlanDtls": {
            "templatedText": {
                "templateName": "dnsCfgRequest",
                "templateAttribute": {
                    "previousTktNo": "CHG12345",
                    "deviceToDel": {"hostName": "mr1-dvn.enlba.isp.sky.com", "ipaddress": "89.200.128.62"},
                    "configuration": [
                        {"record": "mr1-dvn.enlba.isp.sky.com", "value": "89.200.128.62", "status": "NEW"}
                    ],
                },
            },
        },
        "addDownstreamCIs": [
            {
                "hostname": "ma0.bllabd1.isp.sky.com",
                "impactType": "Full Outage",
                "serviceTypes": ["UBB,VOICE,UM,WSE,ALL"],
                "mode": "recursive",
            }
        ],
    }
}


@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_adjacent_ci_details")
def test_ticket_creation20(
    get_adjacent_ci_details_mock,
    rest_get_mock,
    service3040,
    service3045,
    service3401,
    service3020,
    service3800,
    design,
    email_notify_mock,
):
    rest_get_mock.side_effect = get_working_day_side_effect
    design.return_value = "sample data"
    service3800.return_value = [
        {"u_impact_start_date": "26/5/2020 01:00:00", "u_impact_end_date": "26/5/2020 05:00:00"},
        {"u_impact_start_date": "28/5/2020 01:00:00", "u_impact_end_date": "28/5/2020 05:00:00"},
        {"u_impact_start_date": "25/5/2020 01:00:00", "u_impact_end_date": "25/5/2020 05:00:00"},
    ]
    service3020.return_value = [
        {
            "event_name": "DE Bank Holiday: MariÃƒÂ¤ Himmelfahrt",
            "event_start_time": "14/08/2020 22:00:00",
            "event_end_time": "15/08/2020 21:59:59",
            "applies_to": "cmdb_ci_service",
            "condition": "Business areas CONTAINS Group Digital Platforms .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "DE - Bank Holidays ",
            "blackout_schedule_type": "Change Freeze",
        }
    ]
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3045.return_value = {"result": {"detail": "CHG0115712 (ATTACHMENT ADDED)", "ticketNumber": "CHG0115712"}}
    service3040.return_value = True
    result = create_ticket(**data_ci_list)
    assert result["status"] == "SUCCESSFUL"


ticket = {
    "affectedCIs": [{"ciName": "as100.bllabd1.isp.sky.com", "impactType": "At Risk"}],
    "changeType": "standard",
    "createdBy": "SVC-APP-DNE",
    "endDate": 1702651230,
    "serviceType": "metroServiceMigration",
    "shortDescription": "Migrating Voice services from set of Ports for Exchanges (bllabd1) under DNE Order 161769",
    "startDate": 1702651229,
    "templateName": "EVPN Subscriber Service Configuration for OLTs [ITA BB&T]",
    "addDownstreamCIs": [
        {
            "hostname": "ma0.bllabd3.isp.sky.com",
            "impactType": "Full Outage",
            "serviceTypes": ["ALL"],
            "mode": "recursive",
        },
        {
            "hostname": "as1.bllabd1.isp.sky.com",
            "impactType": "Full Outage",
            "serviceTypes": ["VOICE"],
            "mode": "recursive",
        },
    ],
}

kwargs = {
    "body": {
        "affectedCIs": [{"ciName": "as100.bllabd1.isp.sky.com", "impactType": "At Risk"}],
        "changeType": "standard",
        "createdBy": "SVC-APP-DNE",
        "endDate": 1702651230,
        "serviceType": "metroServiceMigration",
        "shortDescription": "Migrating Voice services from set of Ports for Exchanges (bllabd1) under DNE Order 161769",
        "startDate": 1702651229,
        "templateName": "EVPN Subscriber Service Configuration for OLTs [ITA BB&T]",
        "addDownstreamCIs": [
            {
                "hostname": "ma0.bllabd3.isp.sky.com",
                "impactType": "Full Outage",
                "serviceTypes": ["ALL"],
                "mode": "recursive",
            },
            {
                "hostname": "as1.bllabd1.isp.sky.com",
                "impactType": "Full Outage",
                "serviceTypes": ["VOICE"],
                "mode": "recursive",
            },
        ],
    },
    "user": "ipnd_dne_bpm_test",
    "token_info": {
        "sub": "ipnd_dne_bpm_test",
        "scopes": "orch:read orch:write dial:read dial:write connector:read connector:write",
    },
}

kwargs_with_precedence = {
    "body": {
        "affectedCIs": [
            {"ciName": "as100.bllabd1.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "ma0.bllabd3.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "as1.bllabd1.isp.sky.com", "impactType": "At Risk"},
        ],
        "changeType": "standard",
        "createdBy": "SVC-APP-DNE",
        "endDate": 1702651230,
        "serviceType": "metroServiceMigration",
        "shortDescription": "Migrating Voice services from set of Ports for Exchanges (bllabd1) under DNE Order 161769",
        "startDate": 1702651229,
        "templateName": "EVPN Subscriber Service Configuration for OLTs [ITA BB&T]",
        "addDownstreamCIs": [
            {
                "hostname": "ma0.bllabd3.isp.sky.com",
                "impactType": "At Risk",
                "serviceTypes": ["ALL"],
                "mode": "recursive",
            },
            {
                "hostname": "as1.bllabd1.isp.sky.com",
                "impactType": "Full Outage",
                "serviceTypes": ["VOICE"],
                "mode": "recursive",
            },
        ],
    },
    "user": "ipnd_dne_bpm_test",
    "token_info": {
        "sub": "ipnd_dne_bpm_test",
        "scopes": "orch:read orch:write dial:read dial:write connector:read connector:write",
    },
}


kwargs2 = {
    "body": {
        "affectedCIs": [{"ciName": "as100.bllabd1.isp.sky.com", "impactType": "At Risk"}],
        "changeType": "standard",
        "createdBy": "SVC-APP-DNE",
        "endDate": 1702651230,
        "serviceType": "metroServiceMigration",
        "shortDescription": "Migrating Voice services from set of Ports for Exchanges (bllabd1) under DNE Order 161769",
        "startDate": 1702651229,
        "templateName": "EVPN Subscriber Service Configuration for OLTs [ITA BB&T]",
        "addDownstreamCIs": [
            {
                "hostname": "as1.bllabd1.isp.sky.com",
                "impactType": "Full Outage",
                "serviceTypes": ["UM"],
                "mode": "recursive",
            },
        ],
    },
    "user": "ipnd_dne_bpm_test",
    "token_info": {
        "sub": "ipnd_dne_bpm_test",
        "scopes": "orch:read orch:write dial:read dial:write connector:read connector:write",
    },
}


kwargs3 = {
    "body": {
        "affectedCIs": [{"ciName": "as100.bllabd1.isp.sky.com", "impactType": "At Risk"}],
        "changeType": "standard",
        "createdBy": "SVC-APP-DNE",
        "endDate": 1702651230,
        "serviceType": "metroServiceMigration",
        "shortDescription": "Migrating Voice services from set of Ports for Exchanges (bllabd1) under DNE Order 161769",
        "startDate": 1702651229,
        "templateName": "EVPN Subscriber Service Configuration for OLTs [ITA BB&T]",
        "addDownstreamCIs": [
            {
                "hostname": "as1.bllabd1.isp.sky.com",
                "impactType": "Full Outage",
                "serviceTypes": ["UBB"],
                "mode": "recursive",
            },
        ],
    },
    "user": "ipnd_dne_bpm_test",
    "token_info": {
        "sub": "ipnd_dne_bpm_test",
        "scopes": "orch:read orch:write dial:read dial:write connector:read connector:write",
    },
}


kwargs4 = {
    "body": {
        "affectedCIs": [{"ciName": "as100.bllabd1.isp.sky.com", "impactType": "At Risk"}],
        "changeType": "standard",
        "createdBy": "SVC-APP-DNE",
        "endDate": 1702651230,
        "serviceType": "metroServiceMigration",
        "shortDescription": "Migrating Voice services from set of Ports for Exchanges (bllabd1) under DNE Order 161769",
        "startDate": 1702651229,
        "templateName": "EVPN Subscriber Service Configuration for OLTs [ITA BB&T]",
        "addDownstreamCIs": [
            {
                "hostname": "as1.bllabd1.isp.sky.com",
                "impactType": "Full Outage",
                "serviceTypes": ["WSE"],
                "mode": "recursive",
            },
        ],
    },
    "user": "ipnd_dne_bpm_test",
    "token_info": {
        "sub": "ipnd_dne_bpm_test",
        "scopes": "orch:read orch:write dial:read dial:write connector:read connector:write",
    },
}

kwargs_without_effected_cis = {
    "body": {
        "changeType": "standard",
        "createdBy": "SVC-APP-DNE",
        "endDate": 1702651230,
        "serviceType": "metroServiceMigration",
        "shortDescription": "Migrating Voice services from set of Ports for Exchanges (bllabd1) under DNE Order 161769",
        "startDate": 1702651229,
        "templateName": "EVPN Subscriber Service Configuration for OLTs [ITA BB&T]",
        "addDownstreamCIs": [
            {
                "hostname": "ma0.bllabd3.isp.sky.com",
                "impactType": "Full Outage",
                "serviceTypes": ["ALL"],
                "mode": "recursive",
            },
            {
                "hostname": "as1.bllabd1.isp.sky.com",
                "impactType": "Full Outage",
                "serviceTypes": ["VOICE"],
                "mode": "recursive",
            },
        ],
    },
    "user": "ipnd_dne_bpm_test",
    "token_info": {
        "sub": "ipnd_dne_bpm_test",
        "scopes": "orch:read orch:write dial:read dial:write connector:read connector:write",
    },
}


response_ticket = {
    "affectedCIs": [
        {"ciName": "as100.bllabd1.isp.sky.com", "impactType": "At Risk"},
        {"ciName": "ma0.bllabd3.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "as1.bllabd1.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "me0.bllabd3.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "as100.bllabd3.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "ma0.bllabd4.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "as0.bllabd3.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "as1.bllabd3.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "cr1.bllab.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "cr0.bllab.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "cr2.bllab.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "cr4.bllab.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "ONEA50106731", "impactType": "Full Outage"},
        {"ciName": "ONEA50107345", "impactType": "Full Outage"},
        {"ciName": "ONEA63447398", "impactType": "Full Outage"},
        {"ciName": "ONEA50094158", "impactType": "Full Outage"},
        {"ciName": "ONEA50106751", "impactType": "Full Outage"},
        {"ciName": "ONEA50106661", "impactType": "Full Outage"},
        {"ciName": "ONEA50106741", "impactType": "Full Outage"},
        {"ciName": "ONEA50106115", "impactType": "Full Outage"},
        {"ciName": "vm3.bllabd1.isp.sky.com", "impactType": "Full Outage"},
    ],
    "changeType": "standard",
    "createdBy": "SVC-APP-DNE",
    "endDate": 1702651230,
    "serviceType": "metroServiceMigration",
    "shortDescription": "Migrating Voice services from set of Ports for Exchanges (bllabd1) under DNE Order 161769",
    "startDate": 1702651229,
    "templateName": "EVPN Subscriber Service Configuration for OLTs [ITA BB&T]",
    "addDownstreamCIs": [
        {
            "hostname": "ma0.bllabd3.isp.sky.com",
            "impactType": "Full Outage",
            "serviceTypes": ["ALL"],
            "mode": "recursive",
        },
        {
            "hostname": "as1.bllabd1.isp.sky.com",
            "impactType": "Full Outage",
            "serviceTypes": ["VOICE"],
            "mode": "recursive",
        },
    ],
    "thirdPartyTicket": {
        "thirdpartyImpact": "Full outage to service",
        "thirdpartyImpactReason": "Maintenance-Sky network Upgrade",
    },
    "wholesaleCIs": {
        "ONEA50106731": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        "ONEA50107345": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        "ONEA63447398": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        "ONEA50094158": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        "ONEA50106751": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        "ONEA50106661": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        "ONEA50106741": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        "ONEA50106115": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
    },
}
response_kwargs = {
    "body": {
        "affectedCIs": [
            {"ciName": "as100.bllabd1.isp.sky.com", "impactType": "At Risk"},
            {"ciName": "ma0.bllabd3.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "as1.bllabd1.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "me0.bllabd3.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "as100.bllabd3.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "ma0.bllabd4.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "as0.bllabd3.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "as1.bllabd3.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "cr1.bllab.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "cr0.bllab.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "cr2.bllab.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "cr4.bllab.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "ONEA50106731", "impactType": "Full Outage"},
            {"ciName": "ONEA50107345", "impactType": "Full Outage"},
            {"ciName": "ONEA63447398", "impactType": "Full Outage"},
            {"ciName": "ONEA50094158", "impactType": "Full Outage"},
            {"ciName": "ONEA50106751", "impactType": "Full Outage"},
            {"ciName": "ONEA50106661", "impactType": "Full Outage"},
            {"ciName": "ONEA50106741", "impactType": "Full Outage"},
            {"ciName": "ONEA50106115", "impactType": "Full Outage"},
            {"ciName": "vm3.bllabd1.isp.sky.com", "impactType": "Full Outage"},
        ],
        "changeType": "standard",
        "createdBy": "SVC-APP-DNE",
        "endDate": 1702651230,
        "serviceType": "metroServiceMigration",
        "shortDescription": "Migrating Voice services from set of Ports for Exchanges (bllabd1) under DNE Order 161769",
        "startDate": 1702651229,
        "templateName": "EVPN Subscriber Service Configuration for OLTs [ITA BB&T]",
        "addDownstreamCIs": [
            {
                "hostname": "ma0.bllabd3.isp.sky.com",
                "impactType": "Full Outage",
                "serviceTypes": ["ALL"],
                "mode": "recursive",
            },
            {
                "hostname": "as1.bllabd1.isp.sky.com",
                "impactType": "Full Outage",
                "serviceTypes": ["VOICE"],
                "mode": "recursive",
            },
        ],
        "thirdPartyTicket": {
            "thirdpartyImpact": "Full outage to service",
            "thirdpartyImpactReason": "Maintenance-Sky network Upgrade",
        },
        "wholesaleCIs": {
            "ONEA50106731": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
            "ONEA50107345": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
            "ONEA63447398": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
            "ONEA50094158": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
            "ONEA50106751": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
            "ONEA50106661": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
            "ONEA50106741": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
            "ONEA50106115": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        },
    },
    "user": "ipnd_dne_bpm_test",
    "token_info": {
        "sub": "ipnd_dne_bpm_test",
        "scopes": "orch:read orch:write dial:read dial:write connector:read connector:write",
    },
}
response_ticket_precedence = {
    "affectedCIs": [
        {"ciName": "as100.bllabd1.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "ma0.bllabd3.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "as1.bllabd1.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "me0.bllabd3.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "as100.bllabd3.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "ma0.bllabd4.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "as0.bllabd3.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "as1.bllabd3.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "cr1.bllab.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "cr0.bllab.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "cr2.bllab.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "cr4.bllab.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "ONEA50106731", "impactType": "Full Outage"},
        {"ciName": "ONEA50107345", "impactType": "Full Outage"},
        {"ciName": "ONEA63447398", "impactType": "Full Outage"},
        {"ciName": "ONEA50094158", "impactType": "Full Outage"},
        {"ciName": "ONEA50106751", "impactType": "Full Outage"},
        {"ciName": "ONEA50106661", "impactType": "Full Outage"},
        {"ciName": "ONEA50106741", "impactType": "Full Outage"},
        {"ciName": "ONEA50106115", "impactType": "Full Outage"},
        {"ciName": "vm3.bllabd1.isp.sky.com", "impactType": "Full Outage"},
    ],
    "changeType": "standard",
    "createdBy": "SVC-APP-DNE",
    "endDate": 1702651230,
    "serviceType": "metroServiceMigration",
    "shortDescription": "Migrating Voice services from set of Ports for Exchanges (bllabd1) under DNE Order 161769",
    "startDate": 1702651229,
    "templateName": "EVPN Subscriber Service Configuration for OLTs [ITA BB&T]",
    "addDownstreamCIs": [
        {
            "hostname": "ma0.bllabd3.isp.sky.com",
            "impactType": "Full Outage",
            "serviceTypes": ["ALL"],
            "mode": "recursive",
        },
        {
            "hostname": "as1.bllabd1.isp.sky.com",
            "impactType": "Full Outage",
            "serviceTypes": ["VOICE"],
            "mode": "recursive",
        },
    ],
    "thirdPartyTicket": {
        "thirdpartyImpact": "Full outage to service",
        "thirdpartyImpactReason": "Maintenance-Sky network Upgrade",
    },
    "wholesaleCIs": {
        "ONEA50106731": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        "ONEA50107345": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        "ONEA63447398": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        "ONEA50094158": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        "ONEA50106751": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        "ONEA50106661": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        "ONEA50106741": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        "ONEA50106115": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
    },
}
response_kwargs_precedence = {
    "body": {
        "affectedCIs": [
            {"ciName": "as100.bllabd1.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "ma0.bllabd3.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "as1.bllabd1.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "me0.bllabd3.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "as100.bllabd3.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "ma0.bllabd4.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "as0.bllabd3.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "as1.bllabd3.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "cr1.bllab.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "cr0.bllab.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "cr2.bllab.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "cr4.bllab.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "ONEA50106731", "impactType": "Full Outage"},
            {"ciName": "ONEA50107345", "impactType": "Full Outage"},
            {"ciName": "ONEA63447398", "impactType": "Full Outage"},
            {"ciName": "ONEA50094158", "impactType": "Full Outage"},
            {"ciName": "ONEA50106751", "impactType": "Full Outage"},
            {"ciName": "ONEA50106661", "impactType": "Full Outage"},
            {"ciName": "ONEA50106741", "impactType": "Full Outage"},
            {"ciName": "ONEA50106115", "impactType": "Full Outage"},
            {"ciName": "vm3.bllabd1.isp.sky.com", "impactType": "Full Outage"},
        ],
        "changeType": "standard",
        "createdBy": "SVC-APP-DNE",
        "endDate": 1702651230,
        "serviceType": "metroServiceMigration",
        "shortDescription": "Migrating Voice services from set of Ports for Exchanges (bllabd1) under DNE Order 161769",
        "startDate": 1702651229,
        "templateName": "EVPN Subscriber Service Configuration for OLTs [ITA BB&T]",
        "addDownstreamCIs": [
            {
                "hostname": "ma0.bllabd3.isp.sky.com",
                "impactType": "Full Outage",
                "serviceTypes": ["ALL"],
                "mode": "recursive",
            },
            {
                "hostname": "as1.bllabd1.isp.sky.com",
                "impactType": "Full Outage",
                "serviceTypes": ["VOICE"],
                "mode": "recursive",
            },
        ],
        "thirdPartyTicket": {
            "thirdpartyImpact": "Full outage to service",
            "thirdpartyImpactReason": "Maintenance-Sky network Upgrade",
        },
        "wholesaleCIs": {
            "ONEA50106731": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
            "ONEA50107345": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
            "ONEA63447398": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
            "ONEA50094158": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
            "ONEA50106751": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
            "ONEA50106661": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
            "ONEA50106741": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
            "ONEA50106115": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        },
    },
    "user": "ipnd_dne_bpm_test",
    "token_info": {
        "sub": "ipnd_dne_bpm_test",
        "scopes": "orch:read orch:write dial:read dial:write connector:read connector:write",
    },
}

response_ticket2 = {
    "changeType": "standard",
    "createdBy": "SVC-APP-DNE",
    "endDate": 1702651230,
    "serviceType": "metroServiceMigration",
    "shortDescription": "Migrating Voice services from set of Ports for Exchanges (bllabd1) under DNE Order 161769",
    "startDate": 1702651229,
    "templateName": "EVPN Subscriber Service Configuration for OLTs [ITA BB&T]",
    "addDownstreamCIs": [
        {
            "hostname": "ma0.bllabd3.isp.sky.com",
            "impactType": "Full Outage",
            "serviceTypes": ["ALL"],
            "mode": "recursive",
        },
        {
            "hostname": "as1.bllabd1.isp.sky.com",
            "impactType": "Full Outage",
            "serviceTypes": ["VOICE"],
            "mode": "recursive",
        },
    ],
    "affectedCIs": [
        {"ciName": "ma0.bllabd3.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "as1.bllabd1.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "me0.bllabd3.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "as100.bllabd3.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "ma0.bllabd4.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "as0.bllabd3.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "as1.bllabd3.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "cr1.bllab.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "cr0.bllab.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "cr2.bllab.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "cr4.bllab.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "ONEA50106731", "impactType": "Full Outage"},
        {"ciName": "ONEA50107345", "impactType": "Full Outage"},
        {"ciName": "ONEA63447398", "impactType": "Full Outage"},
        {"ciName": "ONEA50094158", "impactType": "Full Outage"},
        {"ciName": "ONEA50106751", "impactType": "Full Outage"},
        {"ciName": "ONEA50106661", "impactType": "Full Outage"},
        {"ciName": "ONEA50106741", "impactType": "Full Outage"},
        {"ciName": "ONEA50106115", "impactType": "Full Outage"},
        {"ciName": "vm3.bllabd1.isp.sky.com", "impactType": "Full Outage"},
    ],
    "thirdPartyTicket": {
        "thirdpartyImpact": "Full outage to service",
        "thirdpartyImpactReason": "Maintenance-Sky network Upgrade",
    },
    "wholesaleCIs": {
        "ONEA50106731": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        "ONEA50107345": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        "ONEA63447398": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        "ONEA50094158": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        "ONEA50106751": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        "ONEA50106661": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        "ONEA50106741": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        "ONEA50106115": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
    },
}

response_kwargs2 = {
    "body": {
        "changeType": "standard",
        "createdBy": "SVC-APP-DNE",
        "endDate": 1702651230,
        "serviceType": "metroServiceMigration",
        "shortDescription": "Migrating Voice services from set of Ports for Exchanges (bllabd1) under DNE Order 161769",
        "startDate": 1702651229,
        "templateName": "EVPN Subscriber Service Configuration for OLTs [ITA BB&T]",
        "addDownstreamCIs": [
            {
                "hostname": "ma0.bllabd3.isp.sky.com",
                "impactType": "Full Outage",
                "serviceTypes": ["ALL"],
                "mode": "recursive",
            },
            {
                "hostname": "as1.bllabd1.isp.sky.com",
                "impactType": "Full Outage",
                "serviceTypes": ["VOICE"],
                "mode": "recursive",
            },
        ],
        "affectedCIs": [
            {"ciName": "ma0.bllabd3.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "as1.bllabd1.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "me0.bllabd3.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "as100.bllabd3.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "ma0.bllabd4.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "as0.bllabd3.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "as1.bllabd3.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "cr1.bllab.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "cr0.bllab.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "cr2.bllab.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "cr4.bllab.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "ONEA50106731", "impactType": "Full Outage"},
            {"ciName": "ONEA50107345", "impactType": "Full Outage"},
            {"ciName": "ONEA63447398", "impactType": "Full Outage"},
            {"ciName": "ONEA50094158", "impactType": "Full Outage"},
            {"ciName": "ONEA50106751", "impactType": "Full Outage"},
            {"ciName": "ONEA50106661", "impactType": "Full Outage"},
            {"ciName": "ONEA50106741", "impactType": "Full Outage"},
            {"ciName": "ONEA50106115", "impactType": "Full Outage"},
            {"ciName": "vm3.bllabd1.isp.sky.com", "impactType": "Full Outage"},
        ],
        "thirdPartyTicket": {
            "thirdpartyImpact": "Full outage to service",
            "thirdpartyImpactReason": "Maintenance-Sky network Upgrade",
        },
        "wholesaleCIs": {
            "ONEA50106731": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
            "ONEA50107345": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
            "ONEA63447398": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
            "ONEA50094158": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
            "ONEA50106751": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
            "ONEA50106661": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
            "ONEA50106741": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
            "ONEA50106115": {"impactType": "Full Outage", "serviceTypes": ["ALL"]},
        },
    },
    "user": "ipnd_dne_bpm_test",
    "token_info": {
        "sub": "ipnd_dne_bpm_test",
        "scopes": "orch:read orch:write dial:read dial:write connector:read connector:write",
    },
}

downstream_cis1 = {
    "nes": {
        "mas": [
            "ma0.bllabd3.isp.sky.com",
            "me0.bllabd3.isp.sky.com",
            "as100.bllabd3.isp.sky.com",
            "ma0.bllabd4.isp.sky.com",
        ],
        "llus": ["cr1.bllab.isp.sky.com", "cr0.bllab.isp.sky.com", "cr2.bllab.isp.sky.com", "cr4.bllab.isp.sky.com"],
        "switches": ["as0.bllabd3.isp.sky.com", "as1.bllabd3.isp.sky.com"],
    },
    "circuits": {
        "wholesale": [
            "ONEA50106731",
            "ONEA50107345",
            "ONEA63447398",
            "ONEA50094158",
            "ONEA50106751",
            "ONEA50106661",
            "ONEA50106741",
            "ONEA50106115",
        ]
    },
}
downstream_cis2 = {
    "nes": {
        "llus": ["bm1.bllabd1.isp.sky.com", "cr0.bllabd1.isp.sky.com", "vm3.bllabd1.isp.sky.com"],
        "exchangeMgmtNes": ["cm1.bllabd1.isp.sky.com"],
    },
    "circuits": None,
}


@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_cis_details")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
def test_get_downstream_cis(
    rest_get_mock,
    service3040,
    service3045,
    service3401,
    service3020,
    service3800,
    design,
    email_notify_mock,
    get_cis_details_mock,
):
    get_cis_details_mock.side_effect = [downstream_cis1, downstream_cis2]
    result = get_downstream_cis(kwargs)
    assert result == (response_ticket, response_kwargs)


@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_cis_details")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
def test_get_downstream_cis_with_precedence(
    rest_get_mock,
    service3040,
    service3045,
    service3401,
    service3020,
    service3800,
    design,
    email_notify_mock,
    get_cis_details_mock,
):
    get_cis_details_mock.side_effect = [downstream_cis1, downstream_cis2]
    result = get_downstream_cis(kwargs_with_precedence)
    assert result == (response_ticket_precedence, response_kwargs_precedence)


@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_cis_details")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
def test_get_downstream_cis_without_effected_cis(
    rest_get_mock,
    service3040,
    service3045,
    service3401,
    service3020,
    service3800,
    design,
    email_notify_mock,
    get_cis_details_mock,
):
    get_cis_details_mock.side_effect = [downstream_cis1, downstream_cis2]
    result = get_downstream_cis(kwargs_without_effected_cis)
    assert result == (response_ticket2, response_kwargs2)


response_ticket_um = {
    "affectedCIs": [
        {"ciName": "as100.bllabd1.isp.sky.com", "impactType": "At Risk"},
        {"ciName": "as1.bllabd1.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "cr1.bllab.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "cr0.bllab.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "cr2.bllab.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "cr4.bllab.isp.sky.com", "impactType": "Full Outage"},
    ],
    "changeType": "standard",
    "createdBy": "SVC-APP-DNE",
    "endDate": 1702651230,
    "serviceType": "metroServiceMigration",
    "shortDescription": "Migrating Voice services from set of Ports for Exchanges (bllabd1) under DNE Order 161769",
    "startDate": 1702651229,
    "templateName": "EVPN Subscriber Service Configuration for OLTs [ITA BB&T]",
    "addDownstreamCIs": [
        {
            "hostname": "as1.bllabd1.isp.sky.com",
            "impactType": "Full Outage",
            "serviceTypes": ["UM"],
            "mode": "recursive",
        }
    ],
}

response_kwargs_um = {
    "body": {
        "affectedCIs": [
            {"ciName": "as100.bllabd1.isp.sky.com", "impactType": "At Risk"},
            {"ciName": "as1.bllabd1.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "cr1.bllab.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "cr0.bllab.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "cr2.bllab.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "cr4.bllab.isp.sky.com", "impactType": "Full Outage"},
        ],
        "changeType": "standard",
        "createdBy": "SVC-APP-DNE",
        "endDate": 1702651230,
        "serviceType": "metroServiceMigration",
        "shortDescription": "Migrating Voice services from set of Ports for Exchanges (bllabd1) under DNE Order 161769",
        "startDate": 1702651229,
        "templateName": "EVPN Subscriber Service Configuration for OLTs [ITA BB&T]",
        "addDownstreamCIs": [
            {
                "hostname": "as1.bllabd1.isp.sky.com",
                "impactType": "Full Outage",
                "serviceTypes": ["UM"],
                "mode": "recursive",
            }
        ],
    },
    "user": "ipnd_dne_bpm_test",
    "token_info": {
        "sub": "ipnd_dne_bpm_test",
        "scopes": "orch:read orch:write dial:read dial:write connector:read connector:write",
    },
}


@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_cis_details")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
def test_get_downstream_cis_um(
    rest_get_mock,
    service3040,
    service3045,
    service3401,
    service3020,
    service3800,
    design,
    email_notify_mock,
    get_cis_details_mock,
):
    get_cis_details_mock.side_effect = [downstream_cis1]
    result = get_downstream_cis(kwargs2)
    assert result == (response_ticket_um, response_kwargs_um)


response_ticket_ubb = {
    "affectedCIs": [
        {"ciName": "as100.bllabd1.isp.sky.com", "impactType": "At Risk"},
        {"ciName": "as1.bllabd1.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "cr1.bllab.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "cr0.bllab.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "cr2.bllab.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "cr4.bllab.isp.sky.com", "impactType": "Full Outage"},
    ],
    "changeType": "standard",
    "createdBy": "SVC-APP-DNE",
    "endDate": 1702651230,
    "serviceType": "metroServiceMigration",
    "shortDescription": "Migrating Voice services from set of Ports for Exchanges (bllabd1) under DNE Order 161769",
    "startDate": 1702651229,
    "templateName": "EVPN Subscriber Service Configuration for OLTs [ITA BB&T]",
    "addDownstreamCIs": [
        {
            "hostname": "as1.bllabd1.isp.sky.com",
            "impactType": "Full Outage",
            "serviceTypes": ["UBB"],
            "mode": "recursive",
        }
    ],
}

response_kwargs_ubb = {
    "body": {
        "affectedCIs": [
            {"ciName": "as100.bllabd1.isp.sky.com", "impactType": "At Risk"},
            {"ciName": "as1.bllabd1.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "cr1.bllab.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "cr0.bllab.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "cr2.bllab.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "cr4.bllab.isp.sky.com", "impactType": "Full Outage"},
        ],
        "changeType": "standard",
        "createdBy": "SVC-APP-DNE",
        "endDate": 1702651230,
        "serviceType": "metroServiceMigration",
        "shortDescription": "Migrating Voice services from set of Ports for Exchanges (bllabd1) under DNE Order 161769",
        "startDate": 1702651229,
        "templateName": "EVPN Subscriber Service Configuration for OLTs [ITA BB&T]",
        "addDownstreamCIs": [
            {
                "hostname": "as1.bllabd1.isp.sky.com",
                "impactType": "Full Outage",
                "serviceTypes": ["UBB"],
                "mode": "recursive",
            }
        ],
    },
    "user": "ipnd_dne_bpm_test",
    "token_info": {
        "sub": "ipnd_dne_bpm_test",
        "scopes": "orch:read orch:write dial:read dial:write connector:read connector:write",
    },
}


@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_cis_details")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
def test_get_downstream_cis_ubb(
    rest_get_mock,
    service3040,
    service3045,
    service3401,
    service3020,
    service3800,
    design,
    email_notify_mock,
    get_cis_details_mock,
):
    get_cis_details_mock.side_effect = [downstream_cis1]
    result = get_downstream_cis(kwargs3)
    assert result == (response_ticket_ubb, response_kwargs_ubb)


response_ticket_wse = {
    "affectedCIs": [
        {"ciName": "as100.bllabd1.isp.sky.com", "impactType": "At Risk"},
        {"ciName": "as1.bllabd1.isp.sky.com", "impactType": "Full Outage"},
        {"ciName": "ONEA50106731", "impactType": "Full Outage"},
        {"ciName": "ONEA50107345", "impactType": "Full Outage"},
        {"ciName": "ONEA63447398", "impactType": "Full Outage"},
        {"ciName": "ONEA50094158", "impactType": "Full Outage"},
        {"ciName": "ONEA50106751", "impactType": "Full Outage"},
        {"ciName": "ONEA50106661", "impactType": "Full Outage"},
        {"ciName": "ONEA50106741", "impactType": "Full Outage"},
        {"ciName": "ONEA50106115", "impactType": "Full Outage"},
    ],
    "changeType": "standard",
    "createdBy": "SVC-APP-DNE",
    "endDate": 1702651230,
    "serviceType": "metroServiceMigration",
    "shortDescription": "Migrating Voice services from set of Ports for Exchanges (bllabd1) under DNE Order 161769",
    "startDate": 1702651229,
    "templateName": "EVPN Subscriber Service Configuration for OLTs [ITA BB&T]",
    "addDownstreamCIs": [
        {
            "hostname": "as1.bllabd1.isp.sky.com",
            "impactType": "Full Outage",
            "serviceTypes": ["WSE"],
            "mode": "recursive",
        }
    ],
    "thirdPartyTicket": {
        "thirdpartyImpact": "Full outage to service",
        "thirdpartyImpactReason": "Maintenance-Sky network Upgrade",
    },
    "wholesaleCIs": {
        "ONEA50106731": {"impactType": "Full Outage", "serviceTypes": ["WSE"]},
        "ONEA50107345": {"impactType": "Full Outage", "serviceTypes": ["WSE"]},
        "ONEA63447398": {"impactType": "Full Outage", "serviceTypes": ["WSE"]},
        "ONEA50094158": {"impactType": "Full Outage", "serviceTypes": ["WSE"]},
        "ONEA50106751": {"impactType": "Full Outage", "serviceTypes": ["WSE"]},
        "ONEA50106661": {"impactType": "Full Outage", "serviceTypes": ["WSE"]},
        "ONEA50106741": {"impactType": "Full Outage", "serviceTypes": ["WSE"]},
        "ONEA50106115": {"impactType": "Full Outage", "serviceTypes": ["WSE"]},
    },
}

response_kwargs_wse = {
    "body": {
        "affectedCIs": [
            {"ciName": "as100.bllabd1.isp.sky.com", "impactType": "At Risk"},
            {"ciName": "as1.bllabd1.isp.sky.com", "impactType": "Full Outage"},
            {"ciName": "ONEA50106731", "impactType": "Full Outage"},
            {"ciName": "ONEA50107345", "impactType": "Full Outage"},
            {"ciName": "ONEA63447398", "impactType": "Full Outage"},
            {"ciName": "ONEA50094158", "impactType": "Full Outage"},
            {"ciName": "ONEA50106751", "impactType": "Full Outage"},
            {"ciName": "ONEA50106661", "impactType": "Full Outage"},
            {"ciName": "ONEA50106741", "impactType": "Full Outage"},
            {"ciName": "ONEA50106115", "impactType": "Full Outage"},
        ],
        "changeType": "standard",
        "createdBy": "SVC-APP-DNE",
        "endDate": 1702651230,
        "serviceType": "metroServiceMigration",
        "shortDescription": "Migrating Voice services from set of Ports for Exchanges (bllabd1) under DNE Order 161769",
        "startDate": 1702651229,
        "templateName": "EVPN Subscriber Service Configuration for OLTs [ITA BB&T]",
        "addDownstreamCIs": [
            {
                "hostname": "as1.bllabd1.isp.sky.com",
                "impactType": "Full Outage",
                "serviceTypes": ["WSE"],
                "mode": "recursive",
            }
        ],
        "thirdPartyTicket": {
            "thirdpartyImpact": "Full outage to service",
            "thirdpartyImpactReason": "Maintenance-Sky network Upgrade",
        },
        "wholesaleCIs": {
            "ONEA50106731": {"impactType": "Full Outage", "serviceTypes": ["WSE"]},
            "ONEA50107345": {"impactType": "Full Outage", "serviceTypes": ["WSE"]},
            "ONEA63447398": {"impactType": "Full Outage", "serviceTypes": ["WSE"]},
            "ONEA50094158": {"impactType": "Full Outage", "serviceTypes": ["WSE"]},
            "ONEA50106751": {"impactType": "Full Outage", "serviceTypes": ["WSE"]},
            "ONEA50106661": {"impactType": "Full Outage", "serviceTypes": ["WSE"]},
            "ONEA50106741": {"impactType": "Full Outage", "serviceTypes": ["WSE"]},
            "ONEA50106115": {"impactType": "Full Outage", "serviceTypes": ["WSE"]},
        },
    },
    "user": "ipnd_dne_bpm_test",
    "token_info": {
        "sub": "ipnd_dne_bpm_test",
        "scopes": "orch:read orch:write dial:read dial:write connector:read connector:write",
    },
}


@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_cis_details")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
def test_get_downstream_cis_wse(
    rest_get_mock,
    service3040,
    service3045,
    service3401,
    service3020,
    service3800,
    design,
    email_notify_mock,
    get_cis_details_mock,
):
    get_cis_details_mock.side_effect = [downstream_cis1]
    result = get_downstream_cis(kwargs4)
    assert result == (response_ticket_wse, response_kwargs_wse)


def here():
    """Gives data path inside this path"""
    return f"{os.path.dirname(os.path.realpath(__file__))}/data/"


# Loading data from json file
with open(f"{here()}/plannet_data.json", "r") as f:
    plannet_response = json.loads(f.read())
    plannet_response["ticket_data_1"]["body"]["startDate"] = start_date
    plannet_response["ticket_data_1"]["body"]["endDate"] = end_date
    plannet_response["ticket_data_2"]["body"]["startDate"] = start_date
    plannet_response["ticket_data_2"]["body"]["endDate"] = end_date


hydrate_cis_data = [
    {
        "ticket_data": plannet_response["ticket_data_1"],
        "updated_cis": [
            {"ciName": "br0.bllabd1.isp.sky.com", "impactType": "At Risk"},
            {"ciName": "br1.bllabd1.isp.sky.com", "impactType": "Reduced Resiliency"},
            {"ciName": "br105-dist.bllon.isp.sky.com", "impactType": "Reduced Resiliency"},
        ],
    },
    {
        "ticket_data": plannet_response["ticket_data_2"],
        "updated_cis": [{"ciName": "ne0-dist.bllon.isp.sky.com", "impactType": "At Risk"}],
    },
]


@patch("connectors.webserver.itsm.tasks.ticketGenerator.third_party_ticket_creation")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_adjacent_ci_details")
@pytest.mark.parametrize("params", hydrate_cis_data)
def test_hydrate_cis(
    get_adjacent_ci_details_mock,
    rest_get_mock,
    service3040,
    service3045,
    service3401,
    service3020,
    service3800,
    email_notify_mock,
    third_party_tkt,
    params,
):
    """
    Verify tests with ticket when service_type is
     1. bngFailover
     2. wholesaleUni
    """
    ticket = params["ticket_data"]

    get_adjacent_ci_details_mock.return_value = [
        "br1.bllabd1.isp.sky.com",
        "br0.bllabd1.isp.sky.com",
        "br105-dist.bllon.isp.sky.com",
    ]
    third_party_tkt.return_value = {"status": "SUCCESS"}
    rest_get_mock.side_effect = get_working_day_side_effect
    service3800.return_value = []
    service3020.return_value = [
        {
            "event_name": "DE Bank Holiday: Mariä Himmelfahrt",
            "event_start_time": "14/08/2020 22:00:00",
            "event_end_time": "15/08/2020 21:59:59",
            "applies_to": "cmdb_ci_service",
            "condition": "Business areas CONTAINS Group Digital Platforms .or. Business areas CONTAINS Group OTT",
            "blackout_schedule": "DE - Bank Holidays ",
            "blackout_schedule_type": "Change Freeze",
        }
    ]
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3045.return_value = {"result": {"status": "CHG0115712 (ATTACHMENT ADDED)", "ticketNumber": "CHG0115712"}}
    service3040.return_value = True
    response = create_ticket(**ticket)
    assert ticket["body"]["affectedCIs"] == params["updated_cis"]
    assert response["status"] == "SUCCESSFUL"


@patch("connectors.webserver.itsm.tasks.ticketGenerator.Resolver.standard_find_time_slot")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.notify_cw_change")
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.split_ci_list")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3800")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3020")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3401")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3040")
@patch("connectors.core.services.itsm.customValidator.requests.get")
@patch("connectors.webserver.itsm.tasks.ticketGenerator.get_adjacent_ci_details")
def test_standard_ticket_skip_conflict(
    get_adjacent_ci_details_mock,
    rest_get_mock,
    service3040,
    service3045,
    service3401,
    service3020,
    service3800,
    split_ci_list_mock,
    design,
    email_notify_mock,
    standard_find_time_slot_mock,
):
    service3401.return_value = {"result": {"details": "CHG0115712 (RAISED)"}}
    service3040.return_value = True
    rest_get_mock.side_effect = get_working_day_side_effect
    data = copy.deepcopy(data_standard2)
    del data["body"]["isDummy"]
    del data["body"]["reScheduledInfo"]
    del data["body"]["attachments"]
    data["body"]["serviceType"] = "geaPlugup"
    data["body"]["skipConflict"] = True

    result = create_standard_ticket(**data)
    split_ci_list_mock.assert_not_called()
    service3800.assert_not_called()
    service3020.assert_called_once()
    standard_find_time_slot_mock.assert_not_called()
    service3401.assert_called_once()
    service3040.assert_called_once()
    service3045.assert_not_called()
    design.assert_not_called()
    assert result["status"] == "SUCCESSFUL"


@patch("connectors.webserver.itsm.tasks.ticketGenerator.ServiceDB")
def test_apply_change_creation_defaults_from_db_applies_default_config(db_mock):
    ticket123 = {"serviceType": "metroMigration"}

    db_mock.return_value.find_one.return_value = {
        "orderType": "metroMigration",
        "default": {
            "templateName": "tmpl",
            "shortDescription": "short",
            "tag": "[TAG]",
        },
    }

    _apply_change_creation_defaults_from_db(ticket123)
    assert ticket123["templateName"] == "tmpl"
    assert ticket123["shortDescription"] == "[TAG] short"
    db_mock.return_value.find_one.assert_called_once_with({"orderType": "metroMigration"})


@patch("connectors.webserver.itsm.tasks.ticketGenerator.ServiceDB")
def test_apply_change_creation_defaults_from_db_applies_subtype_override(db_mock):
    ticket123 = {"serviceType": "metroMigration", "orderSubType": "evpn"}
    db_mock.return_value.find_one.return_value = {
        "orderType": "metroMigration",
        "default": {
            "templateName": "tmpl",
            "shortDescription": "default desc",
            "tag": "[TAG]",
        },
        "orderSubType": {"evpn": {"shortDescription": "subtype desc"}},
    }

    _apply_change_creation_defaults_from_db(ticket123)
    assert ticket123["templateName"] == "tmpl"
    assert ticket123["shortDescription"] == "[TAG] subtype desc"


@patch("connectors.webserver.itsm.tasks.ticketGenerator.ServiceDB")
def test_apply_change_creation_defaults_from_db_replaces_dne_tag(db_mock):
    ticket123 = {"serviceType": "metroMigration"}

    db_mock.return_value.find_one.return_value = {
        "orderType": "metroMigration",
        "default": {
            "templateName": "tmpl",
            "shortDescription": "[DNE] Router migration",
            "tag": "[TAG]",
        },
    }

    _apply_change_creation_defaults_from_db(ticket123)
    assert ticket123["shortDescription"] == "[TAG] Router migration"


@patch("connectors.webserver.itsm.tasks.ticketGenerator.ServiceDB")
def test_apply_change_creation_defaults_from_db_no_db_record(db_mock):
    ticket123 = {"serviceType": "metroMigration"}
    db_mock.return_value.find_one.return_value = None
    _apply_change_creation_defaults_from_db(ticket123)
    assert "templateName" not in ticket123
    assert "shortDescription" not in ticket123


@patch("connectors.webserver.itsm.tasks.ticketGenerator.ServiceDB")
def test_apply_change_creation_defaults_from_db_no_default_config(db_mock):
    ticket123 = {"serviceType": "metroMigration"}
    db_mock.return_value.find_one.return_value = {"orderType": "metroMigration"}
    _apply_change_creation_defaults_from_db(ticket123)
    assert "templateName" not in ticket123
    assert "shortDescription" not in ticket123


@patch("connectors.webserver.itsm.tasks.ticketGenerator.ServiceDB")
def test_apply_change_creation_defaults_from_db_handles_db_exception(db_mock):
    ticket123 = {"serviceType": "metroMigration"}
    db_mock.return_value.find_one.side_effect = ServiceDBException("boom")
    _apply_change_creation_defaults_from_db(ticket123)
    # should fail silently
    assert "templateName" not in ticket123
