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
from connectors.core.config.connectors_config import config
from connectors.core.services.anp.connector import UpdateTGService
from connectors.core.utils.helpers import generic_secret

secret = generic_secret()


anp_prod_url = config.get(section="anp", key="prod_url")
anp_uat_url = config.get(section="anp", key="uat_url")

request_body = {
    "comment": "xxx",
    "deliveryDate": "2022-07-20",
    "domain": "core",
    "environment": "qa",
    "projectName": "Sacramento",
    "requiredDate": "2021-12-12",
    "status": "new",
    "tgReference": "TG9989",
}

dummy_project_data = {
    "_links": {
        "self": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core/projects/35"},
        "parent": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core"},
        "deliverables": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core/projects/35/deliverables"},
        "userspaces": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core/projects/35/userspaces"},
        "actions": {
            "checkin": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core/projects/35/checkin"},
            "checkout": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core/projects/35/checkout"},
        },
    },
    "uid": "4a6f6971-b535-473e-8a0e-4bec201772b2",
    "name": "Sacramento",
    "description": "",
    "manager": "xyz@sky.uk",
    "owner": "abc@sky.uk",
    "mailbox": "test@bskyb.com",
    "locked": {},
}

dummy_deliverables_data = {
    "_links": {
        "self": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core/deliverables?reference=TG9989"},
        "parent": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core"},
    },
    "deliverables": [
        {
            "_links": {
                "self": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core/deliverables/834"},
                "parent": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core/projects/35"},
                "userspaces": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core/projects/35/userspaces"},
            },
            "uid": "7c036094-c75b-4c7d-a5eb-5f5b9ef49701",
            "name": "sr10.pomnc-pr2.hobir migration to ta0.pomnc",
            "description": "",
            "reference": "TG9989",
            "impact": "low",
            "status": "new",
            "system": False,
            "created": "2020-07-13T14:17:37.457799+01:00",
            "effective_from": "2020-07-13T14:17:37.457799+01:00",
            "dates": {"delivery": "None", "required": "2020-07-21"},
            "managers": ["xyz@sky.uk"],
        }
    ],
}

param_environment = ["production", "qa"]


@pytest.mark.parametrize("environment", param_environment)
def test_instantiate_update_tg_service(environment):
    """
    Test to check the instantiation of UpdateTGService().
    """
    request_body["environment"] = environment
    upd_tg_srv = UpdateTGService(request_body, "dummy_user", secret)
    assert upd_tg_srv.environment == request_body["environment"]
    assert upd_tg_srv.domain == request_body["domain"]
    assert upd_tg_srv.projectName == request_body["projectName"]
    assert upd_tg_srv.requiredDate == request_body["requiredDate"]
    assert upd_tg_srv.deliveryDate == request_body["deliveryDate"]
    assert upd_tg_srv.status == request_body["status"]
    assert upd_tg_srv.comment == request_body["comment"]
    assert upd_tg_srv.tgReference == request_body["tgReference"]
    assert upd_tg_srv.username == "dummy_user"
    assert upd_tg_srv.password == secret
    if "production" in upd_tg_srv.environment.lower():
        assert upd_tg_srv.url == anp_prod_url
    else:
        assert upd_tg_srv.url == anp_uat_url


@patch("connectors.core.services.anp.connector.CommonOperations.post")
@patch("connectors.core.services.anp.connector.CommonOperations.put")
@patch("connectors.core.services.anp.connector.CommonOperations.get")
@patch("connectors.core.services.anp.connector.UpdateTGService.get_project_data")
@patch("connectors.core.services.anp.connector.CommonOperations.login")
@pytest.mark.parametrize("environment", param_environment)
def test_update_tg_success(mock_login, mock_proj_data, mock_get, mock_put, mock_post, environment):
    """
    Test to check the functionality of update_tg function.
    """
    request_body["environment"] = environment
    mock_login.return_value = "dummy_token"
    mock_proj_data.return_value = dummy_project_data
    mock_get.return_value = dummy_deliverables_data
    mock_put.return_value = dummy_deliverables_data
    mock_post.return_value = {"data": "dummy"}
    upd_tg_srv = UpdateTGService(request_body, "dummy_user", secret)
    response = upd_tg_srv.update_tg()
    if "production" in environment.lower():
        url = anp_prod_url
    else:
        url = anp_uat_url
    mock_login.assert_called_once_with(url, "dummy_user", secret)
    mock_proj_data.assert_called_once()
    mock_get.assert_called()
    mock_put.assert_called_once()
    mock_post.assert_called_once()
    assert response["success"]


@patch("connectors.core.services.anp.connector.CommonOperations.login")
def test_update_tg_exception_while_login(mock_login):
    """
    Test to check the functionality of update_tg function with login resulting into exception
    """
    mock_login.side_effect = Exception("dummy error")
    upd_tg_srv = UpdateTGService(request_body, "dummy_user", secret)
    response = upd_tg_srv.update_tg()
    assert not response["success"]
    assert "login to a&p failed" in response["message"].lower()


@patch("connectors.core.services.anp.connector.UpdateTGService.get_project_data")
@patch("connectors.core.services.anp.connector.CommonOperations.login")
def test_update_tg_exception_while_fetching_project_data(mock_login, mock_proj_data):
    """
    Test to check the functionality of update_tg function wherein exception occurs in get_project_data
    """
    mock_login.return_value = "dummy_token"
    mock_proj_data.side_effect = Exception("dummy error")
    upd_tg_srv = UpdateTGService(request_body, "dummy_user", secret)
    response = upd_tg_srv.update_tg()
    assert not response["success"]
    assert "could not get project data" in response["message"].lower()


@patch("connectors.core.services.anp.connector.UpdateTGService.get_project_data")
@patch("connectors.core.services.anp.connector.CommonOperations.login")
def test_update_tg_project_data_none(mock_login, mock_proj_data):
    """
    Test to check the functionality of update_tg function with results not obtained for project data
    """
    mock_login.return_value = "dummy_token"
    mock_proj_data.return_value = None
    upd_tg_srv = UpdateTGService(request_body, "dummy_user", secret)
    response = upd_tg_srv.update_tg()
    assert not response["success"]
    assert f"project {request_body['projectName'].lower()} doesn't seem to exist" in response["message"].lower()


@patch("connectors.core.services.anp.connector.UpdateTGService.update_deliverable")
@patch("connectors.core.services.anp.connector.UpdateTGService.get_project_data")
@patch("connectors.core.services.anp.connector.CommonOperations.login")
def test_update_tg_exception_update_deliverable(mock_login, mock_proj_data, mock_upd_deliver):
    """
    Test to check the functionality of update_tg function wherein exception occurs in update_deliverable
    """
    mock_login.return_value = "dummy_token"
    mock_proj_data.return_value = dummy_project_data
    mock_upd_deliver.side_effect = Exception("dummy error")
    upd_tg_srv = UpdateTGService(request_body, "dummy_user", secret)
    response = upd_tg_srv.update_tg()
    assert not response["success"]
    assert "failed to update" in response["message"].lower()


@patch("connectors.core.services.anp.connector.CommonOperations.post")
@patch("connectors.core.services.anp.connector.UpdateTGService.update_deliverable")
@patch("connectors.core.services.anp.connector.UpdateTGService.get_project_data")
@patch("connectors.core.services.anp.connector.CommonOperations.login")
def test_update_tg_project_check_in_error(mock_login, mock_proj_data, mock_upd_deliver, mock_post):
    """
    Test to check the functionality of update_tg function wherein error in project check-in response
    """
    mock_login.return_value = "dummy_token"
    mock_proj_data.return_value = dummy_project_data
    mock_upd_deliver.return_value = dummy_deliverables_data
    mock_post.return_value = {"error": "dummy error"}
    upd_tg_srv = UpdateTGService(request_body, "dummy_user", secret)
    response = upd_tg_srv.update_tg()
    assert not response["success"]
    assert "failed to check in" in response["message"].lower()


@patch("connectors.core.services.anp.connector.CommonOperations.post")
@patch("connectors.core.services.anp.connector.UpdateTGService.update_deliverable")
@patch("connectors.core.services.anp.connector.UpdateTGService.get_project_data")
@patch("connectors.core.services.anp.connector.CommonOperations.login")
def test_update_tg_exception_while_project_check_in(mock_login, mock_proj_data, mock_upd_deliver, mock_post):
    """
    Test to check the functionality of update_tg function wherein exception occurs during project check-in
    """
    mock_login.return_value = "dummy_token"
    mock_proj_data.return_value = dummy_project_data
    mock_upd_deliver.return_value = dummy_deliverables_data
    mock_post.side_effect = Exception("dummy error")
    upd_tg_srv = UpdateTGService(request_body, "dummy_user", secret)
    response = upd_tg_srv.update_tg()
    assert not response["success"]
    assert "failed to check in" in response["message"].lower()
