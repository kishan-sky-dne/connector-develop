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
import copy
from unittest.mock import patch

# Third Party Library
import pytest

# DNE Library
from connectors.webserver.itsm.tasks.ticketAddNote import add_note, add_templated_note, split_data

data = {"body": {"chgtktNumber": "CHG0108229", "workNotes": "This is 1st Note"}}
data1 = {"body": {"chgtktNumber": "CHG01082292", "workNotes": "This is 1st Note"}}
data2 = {"body": {"chgtktNumber": "CHG0108229", "workNotes": "This is 1st Note"}}
data3 = {"body": {"chgtktNumber": "CHG0108229"}}

data4 = {
    "body": {
        "chgtktNumber": "CHG123456789",
        "comments": "This is a comment",
        "workNotes": "This is 1st note",
        "templatedWorkNote": {
            "templateName": "metroLink",
            "serviceName": "UBB Service",
            "templateAttributes": [
                {
                    "aEnd": "ma0.stage-uk.bllab",
                    "bEnd": "ta0.stage-uk.bllab",
                    "circuitId": "OGHP00806240",
                    "status": "Provisioned",
                },
                {
                    "aEnd": "ma0.stage-uk.bllab",
                    "bEnd": "ta0.stage-uk.bllab",
                    "circuitId": "OGHP00806240",
                    "status": "Provisioned",
                },
            ],
        },
    }
}

data5 = {
    "body": {
        "chgtktNumber": "CHG123456789",
        "comments": "This is a comment",
        "templatedWorkNote": {
            "templateName": "metroLink",
            "serviceName": "UBB Service",
            "templateAttributes": [
                {
                    "aEnd": "ma0.stage-uk.bllab",
                    "bEnd": "ta0.stage-uk.bllab",
                    "circuitId": "OGHP00806240",
                    "status": "Provisioned",
                },
                {
                    "aEnd": "ma0.stage-uk.bllab",
                    "bEnd": "ta0.stage-uk.bllab",
                    "circuitId": "OGHP00806240",
                    "status": "Provisioned",
                },
            ],
        },
    }
}


data6 = {
    "body": {
        "chgtktNumber": "CHG123456789",
        "comments": "This is a comment",
        "templatedWorkNote": {
            "templateName": "metroLink",
            "serviceName": "UBB Service",
            "templateAttributes": [
                {
                    "aEnd": "ma0.stage-uk.bllab",
                    "bEnd": "ta0.stage-uk.bllab",
                    "circuitId": "OGHP00806240",
                    "status": "Provisioned",
                },
                {"aEnd": "ma0.stage-uk.bllab", "circuitId": "OGHP00806240", "status": "Provisioned"},
            ],
        },
    }
}

data7 = (
    "%0AMetro%20Link%20%28ma0.stage-uk.bllab%29%20----%3E%20Provisioned%0A"
    "Metro%20Link%20%28ma0.stage-uk.bllab%20-%20ta0.stage-uk.bllab%29%20----%3E%20Provisioned%0A"
    "Metro%20Link%20%28ma0.stage-uk.bllab%20-%20ta0.stage-uk.bllab%20%3A%20circuit%20id%20"
    "OGHP00806240%29%20----%3E%20Provisioned%0A"
)

data8 = {
    "templateName": "metroLink",
    "serviceName": "UBB Service",
    "templateAttributes": [
        {
            "aEnd": "ma0.stage-uk.bllab",
            "bEnd": "ta0.stage-uk.bllab",
            "circuitId": "OGHP00806240",
            "status": "Provisioned",
        },
        {
            "aEnd": "ma0.stage-uk.bllab",
            "bEnd": "ta0.stage-uk.bllab",
            "circuitId": "OGHP00806240",
            "status": "Provisioned",
        },
    ],
}

data9 = copy.deepcopy(data5)
data9["body"]["templatedWorkNote"]["templateName"] = "metroLink34546555"


@pytest.mark.parametrize("kwargs", [data])
@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
def test_worknote1(post_mock, kwargs):
    post_mock.return_value = {"result": {"details": "CHG0108229 (UPDATED)"}}
    result = add_note(**kwargs)
    assert result == {"status": "CHG0108229 (UPDATED)"}, "failed"


@pytest.mark.parametrize("kwargs", [data2])
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3050")
def test_worknote3(service3050_mock, kwargs):
    service3050_mock.side_effect = KeyError("dummy error")
    result = add_note(**kwargs)
    assert result.status_code == 404, "failed"
    assert result.__dict__["body"]["title"] == "Error in request body"


@pytest.mark.parametrize("kwargs", [data3])
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3050")
def test_worknote4(service3050_mock, kwargs):
    service3050_mock.return_value = {}
    result = add_note(**kwargs)
    assert result.status_code == 400, "failed"
    assert result.__dict__["body"]["title"] == "Error in request body"
    assert (
        result.__dict__["body"]["detail"] == "workNotes or templatedWorkNote none of the attributes are present. "
        "At least one of them is required."
    )


@pytest.mark.parametrize("kwargs", [data2])
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3050")
def test_worknote5(service3050_mock, kwargs):
    service3050_mock.return_value = {"result": {"error_details": "failed"}}
    result = add_note(**kwargs)
    assert result.status_code == 400, "failed"
    assert result.__dict__["body"]["title"] == "Error in request body"
    assert result.__dict__["body"]["detail"] == "Ticket CHG0108229 is invalid"


@pytest.mark.parametrize("kwargs", [data4])
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3050")
def test_worknote6(service3050_mock, kwargs):
    service3050_mock.return_value = {"result": {"details": "CHG0108229 (UPDATED)"}}
    result = add_note(**kwargs)
    assert result == {"status": "CHG0108229 (UPDATED)"}, "failed"


@pytest.mark.parametrize("kwargs", [data5])
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3050")
def test_worknote7(service3050_mock, design_mock, kwargs):
    service3050_mock.return_value = {"result": {"details": "CHG0108229 (UPDATED)"}}
    design_mock.return_value = (
        "UBB Service (ma0.stage-uk.bllab - ta0.stage-uk.bllab : circuit id OGHP00806240) "
        "----> Provisioned\nUBB Service (ma0.stage-uk.bllab - ta0.stage-uk.bllab : circuit id "
        "OGHP00806240) ----> Provisioned"
    )
    result = add_note(**kwargs)
    assert result == {"status": "CHG0108229 (UPDATED)"}, "failed"


@pytest.mark.parametrize("kwargs", [data6])
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3050")
def test_worknote8(service3050_mock, kwargs):
    service3050_mock.return_value = {}
    result = add_note(**kwargs)
    assert result.status_code == 400, "failed"
    assert result.__dict__["body"]["title"] == "Error in request body"
    assert (
        result.__dict__["body"]["detail"] == "Required bEnd attribute missing in Line Detail {'aEnd': "
        "'ma0.stage-uk.bllab', 'circuitId': 'OGHP00806240', "
        "'status': 'Provisioned'}"
    )


@pytest.mark.parametrize("kwargs", [data5])
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3050")
def test_worknote9(service3050_mock, design_mock, kwargs):
    design_mock.return_value = (
        "UBB Service (ma0.stage-uk.bllab - ta0.stage-uk.bllab : circuit id OGHP00806240) "
        "----> Provisioned\nUBB Service (ma0.stage-uk.bllab - ta0.stage-uk.bllab : circuit id "
        "OGHP00806240) ----> Provisioned"
    )
    service3050_mock.side_effect = KeyError("dummy Error")
    result = add_note(**kwargs)
    assert result.status_code == 404, "failed"
    assert result.__dict__["body"]["title"] == "Error in request body"


@pytest.mark.parametrize("kwargs", [data9])
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3050")
def test_worknote10(service3050_mock, kwargs):
    service3050_mock.return_value = {}
    result = add_note(**kwargs)
    assert result.status_code == 400, "failed"
    assert result.__dict__["body"]["title"] == "Error in request body"
    assert (
        result.__dict__["body"]["detail"] == "Given template is not supported by DNE team currently "
        "Please raise a request for templateName: metroLink34546555 as the "
        "supported templates are metroLink. "
    )


@pytest.mark.parametrize("kwargs", [data7])
def test_splitdata1(kwargs):
    result = split_data(kwargs, 200)
    assert len(result) == 2, "failed"
    assert (
        result[-1] == "Metro%20Link%20%28ma0.stage-uk.bllab%20-%20ta0.stage-uk.bllab%20%3A%20"
        "circuit%20id%20OGHP00806240%29%20----%3E%20Provisioned%0A"
    )


@pytest.mark.parametrize("kwargs", [data7])
def test_splitdata2(kwargs):
    result = split_data(kwargs, 1000)
    assert len(result) == 1, "failed"


@pytest.mark.parametrize("kwargs", [data8])
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
@patch("connectors.webserver.itsm.tasks.ticketAddNote.split_data")
def test_splitdata3(split_data_mock, design_mock, kwargs, template_category="metroLink"):
    design_mock.return_value = (
        "Metro Link (ma0.stage-uk.bllab) ----> Provisioned\n"
        "Metro Link (ma0.stage-uk.bllab - ta0.stage-uk.bllab) ----> Provisioned\n"
        "Metro Link (ma0.stage-uk.bllab - ta0.stage-uk.bllab : "
        "circuit id OGHP00806240) ----> Provisioned"
    )
    split_data_mock.side_effect = RecursionError("maximum recursion depth exceeded while calling a Python object")
    result = add_templated_note(kwargs, template_category)
    assert result.status_code == 500, "failed"
    assert result.__dict__["body"]["title"] == "Connector exception raised while adding the Worknote"
    assert result.__dict__["body"]["detail"] == "maximum recursion depth exceeded while calling a Python object"
