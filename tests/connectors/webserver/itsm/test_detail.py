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
from connectors.webserver.itsm.tasks.ticketDetail import get_ticket

data = {"ticketNumber": ["CHG0108229"]}
data1 = {"ticketNumber": None}
data2 = {}
data3 = {"ticketNumber": [""]}
data4 = {"ticketNumber": ["CHG0108999"]}
data_pc = {"ticketNumber": ["CTASK0108229"], "parentChange": True}


@pytest.mark.parametrize("kwargs", [data])
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3400")
def test_detail(service3400, kwargs):
    service3400.return_value = {
        "result": [
            {"state": "APPROVED", "chgtktNumber": "CHG0108229", "end_date": "1572794340", "start_date": "1572794340"}
        ]
    }
    expected = {
        "results": [
            {"state": "APPROVED", "chgtktNumber": "CHG0108229", "endDate": "1572794340", "startDate": "1572794340"}
        ]
    }
    result = get_ticket(**kwargs)
    assert result == expected


@pytest.mark.parametrize("kwargs", [data1])
def test_detail1(kwargs):
    result = get_ticket(**kwargs)
    assert result.status_code == 404, "failed"


@pytest.mark.parametrize("kwargs", [data2])
def test_detail2(kwargs):
    result = get_ticket(**kwargs)
    assert result.status_code == 404, "failed"
    assert result.__dict__["body"]["title"] == "Error in response from Spark or ticket not found"


@pytest.mark.parametrize("kwargs", [data3])
def test_detail3(kwargs):
    result = get_ticket(**kwargs)
    assert result.status_code == 400, "failed"
    assert result.__dict__["body"]["detail"] == "Mandatory key `ticket` missing from the payload"
    assert result.__dict__["body"]["title"] == "Error in request for ticket details"


@pytest.mark.parametrize("kwargs", [data4])
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3400")
def test_detail4(service3400, kwargs):
    service3400.return_value = {"result": [{"error_details": "failed"}]}
    expected = {"results": [{"state": None, "chgtktNumber": "CHG0108999", "endDate": None, "startDate": None}]}
    result = get_ticket(**kwargs)
    assert result == expected


@pytest.mark.parametrize("kwargs", [data4])
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3400")
def test_detail5(service3400, kwargs):
    e = Exception("test")
    service3400.side_effect = e
    result = get_ticket(**kwargs)
    assert result.status_code == 500, "failed"


@pytest.mark.parametrize("kwargs", [data_pc])
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3400")
def test_detail6(service3400, kwargs):
    service3400.return_value = {
        "result": [
            {
                "state": "Authorised",
                "chgtktNumber": "CTASK0108229",
                "end_date": "1572794340",
                "start_date": "1572794340",
                "change_request": {"display_value": "CHG1234567"},
            }
        ]
    }
    expected = {
        "results": [
            {
                "state": "Authorised",
                "chgtktNumber": "CTASK0108229",
                "endDate": "1572794340",
                "startDate": "1572794340",
                "parentTicketNumber": "CHG1234567",
            }
        ]
    }
    result = get_ticket(**kwargs)
    assert result == expected
