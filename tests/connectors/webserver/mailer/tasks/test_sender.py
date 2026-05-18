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
import re
from unittest.mock import patch

# Third Party Library
import pytest

# DNE Library
from connectors.core.services.mailer.exceptions import (
    BccListException,
    CCListException,
    MailerSMTPException,
    MaxRecipientsException,
    PayloadParametersValidationException,
    TemplateDesignerException,
    TemplateNotFoundException,
    ToListException,
)
from connectors.webserver.mailer.tasks import sender

from .inputs import mailer_payload, payload_empty_to_list, payload_incorrect_template_name, payload_invalid_to_list

exception_to_bcc_cc_list = [ToListException, BccListException, CCListException]


def test_email_notifications_feature_flag_off():
    """
    Test to check the functionality of email_notifications() with feature_flag off.
    """
    sender.feature_flag = "OFF"
    response = sender.email_notifications(body=mailer_payload)
    assert response.body["status"] == 503


@patch("connectors.core.services.mailer.connector.Mailer.send_email")
@patch("connectors.core.services.mailer.connector.Mailer.add_html_content")
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
def test_email_notifications_feature_flag_on(mock_design, mock_add_html, mock_send):
    """
    Test to check the functionality of email_notifications()
    """
    rendered_json = {
        "template": "taskAssignment",
        "language": "en",
        "htmlTemplate": "orderTemplate",
        "glossary": {
            "requiredParams": "orderType, orderNumber, taskName, siteId, url",
            "subject": "task Assignment",
            "title": "foo",
            "subtitle": "foo",
            "footerText": "This is an automated email. Please do not reply to this email.<br>",
        },
    }
    default_feature_flag = sender.feature_flag
    sender.feature_flag = "ON"
    mock_design.return_value = rendered_json
    mock_add_html.return_value = True
    mock_send.return_value = True
    response = sender.email_notifications(body=mailer_payload)
    sender.feature_flag = default_feature_flag
    assert response["status"].lower() == "success"


def test_email_notifications_empty_to_list():
    """
    Test to check the functionality of email_notifications() with empty toList
    """
    default_feature_flag = sender.feature_flag
    sender.feature_flag = "ON"
    response = sender.email_notifications(body=payload_empty_to_list)
    sender.feature_flag = default_feature_flag
    assert response.body["status"] == 400
    assert "toList cannot be empty" in response.body["title"]


def test_email_notifications_incorrect_template_name():
    """
    Test to check the functionality of email_notifications() with incorrect template name
    """
    default_feature_flag = sender.feature_flag
    sender.feature_flag = "ON"
    response = sender.email_notifications(body=payload_incorrect_template_name)
    sender.feature_flag = default_feature_flag
    assert response.body["status"] == 404
    assert response.body["title"] == "Given template/language is not supported by DNE team currently"


def test_email_notifications_assert_recipients_exceed():
    """
    Test to check the functionality of email_notifications() with number of recipients in toList, bccList and ccList
    exceeding the maximum recipients
    """
    default_feature_flag = sender.feature_flag
    sender.feature_flag = "ON"
    default_max_recipients = sender.config_total_recipients
    sender.config_total_recipients = 1
    response = sender.email_notifications(body=mailer_payload)
    sender.feature_flag = default_feature_flag
    sender.config_total_recipients = default_max_recipients
    assert response.body["status"] == 403
    assert response.body["title"] == "Validation failed due to the number of emails in toList, ccList, bccList"


@patch("connectors.core.services.mailer.validator.EmailValidator.check_max_recipients")
def test_email_notifications_max_recipients_exception(mock_check_max_recipients):
    """
    Test to check the functionality of email_notifications() causing MaxRecipientsException
    """
    default_feature_flag = sender.feature_flag
    sender.feature_flag = "ON"
    default_max_recipients = sender.config_total_recipients
    sender.config_total_recipients = 1
    mock_check_max_recipients.side_effect = MaxRecipientsException("dummy exception")
    response = sender.email_notifications(body=mailer_payload)
    sender.feature_flag = default_feature_flag
    sender.config_total_recipients = default_max_recipients
    assert response.body["status"] == 403
    assert response.body["title"] == "Error in validating max number of recipients allowed"


def test_email_notifications_invalid_to_list():
    """
    Test to check the functionality of email_notifications() with no valid email address in toList
    """
    default_feature_flag = sender.feature_flag
    sender.feature_flag = "ON"
    response = sender.email_notifications(body=payload_invalid_to_list)
    sender.feature_flag = default_feature_flag
    assert response.body["status"] == 400
    assert response.body["title"] == "There is no valid email address in toList"


@patch("connectors.core.services.mailer.validator.EmailValidator.validate")
@pytest.mark.parametrize("exception_type", exception_to_bcc_cc_list)
def test_email_notifications_exception_validate_func(mock_validate, exception_type):
    """
    Test to check the functionality of email_notifications() causing exception due to email validate
    """
    default_feature_flag = sender.feature_flag
    sender.feature_flag = "ON"
    mock_validate.side_effect = exception_type("dummy exception")
    response = sender.email_notifications(body=mailer_payload)
    sender.feature_flag = default_feature_flag
    assert response.body["status"] == 403
    assert re.match("Error in validating (to|bcc|cc)List against the allowed domains", response.body["title"])


def test_email_notifications_attachment_count_limit_exceeded():
    """
    Test to check the functionality of email_notifications() with attachments exceeding the count limit
    """
    default_feature_flag = sender.feature_flag
    default_max_attachment_count = sender.max_allowed_attachment_count
    sender.feature_flag = "ON"
    sender.max_allowed_attachment_count = 0
    response = sender.email_notifications(body=mailer_payload)
    sender.feature_flag = default_feature_flag
    sender.max_allowed_attachment_count = default_max_attachment_count
    assert response.body["status"] == 403
    assert response.body["title"] == "Attachments exceed the count limit"


def test_email_notifications_total_attachment_size_exceeded():
    """
    Test to check the functionality of email_notifications() with attachments exceeding the size limit
    """
    default_feature_flag = sender.feature_flag
    default_max_allowed_attachment_size = sender.max_allowed_attachment_size
    sender.feature_flag = "ON"
    sender.max_allowed_attachment_size = 0
    response = sender.email_notifications(body=mailer_payload)
    sender.feature_flag = default_feature_flag
    sender.max_allowed_attachment_size = default_max_allowed_attachment_size
    assert response.body["status"] == 413
    assert response.body["title"] == "Attachments exceed the size limit"


@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
def test_email_notifications_template_not_found_exception(mock_designer):
    """
    Test to check the functionality of email_notifications() causing TemplateNotFoundException
    """
    default_feature_flag = sender.feature_flag
    sender.feature_flag = "ON"
    mock_designer.side_effect = TemplateNotFoundException("dummy exception")
    response = sender.email_notifications(body=mailer_payload)
    sender.feature_flag = default_feature_flag
    assert response.body["status"] == 404
    assert response.body["title"] == "Template not found"


@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
def test_email_notifications_template_designer_exception(mock_designer):
    """
    Test to check the functionality of email_notifications() causing TemplateDesignerException
    """
    default_feature_flag = sender.feature_flag
    sender.feature_flag = "ON"
    mock_designer.side_effect = TemplateDesignerException("dummy exception")
    response = sender.email_notifications(body=mailer_payload)
    sender.feature_flag = default_feature_flag
    assert response.body["status"] == 403
    assert "Error in preparing the design template for JSON" in response.body["title"]


@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
def test_email_notifications_payload_parameters_validation_exception(mock_designer):
    """
    Test to check the functionality of email_notifications() causing PayloadParametersValidationException
    """
    default_feature_flag = sender.feature_flag
    sender.feature_flag = "ON"
    mock_designer.side_effect = PayloadParametersValidationException("dummy exception")
    response = sender.email_notifications(body=mailer_payload)
    sender.feature_flag = default_feature_flag
    assert response.body["status"] == 400
    assert (
        response.body["title"]
        == f"""Parameters for the template {mailer_payload["mailTemplate"]} is not matching with the payload supplied"""
    )


@patch("connectors.core.services.mailer.connector.Mailer.send_email")
@patch("connectors.core.services.mailer.connector.Mailer.add_html_content")
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.design")
def test_email_notifications_mailer_smtp_exception(mock_design, mock_add_html, mock_send):
    """
    Test to check the functionality of email_notifications() causing MailerSMTPException
    """
    rendered_json = {
        "template": "taskAssignment",
        "language": "en",
        "htmlTemplate": "orderTemplate",
        "glossary": {
            "requiredParams": "orderType, orderNumber, taskName, siteId, url",
            "subject": "task Assignment",
            "title": "foo",
            "subtitle": "foo",
            "footerText": "This is an automated email. Please do not reply to this email.<br>",
        },
    }
    default_feature_flag = sender.feature_flag
    sender.feature_flag = "ON"
    mock_design.return_value = rendered_json
    mock_add_html.return_value = True
    mock_send.side_effect = MailerSMTPException("dummy exception")
    response = sender.email_notifications(body=mailer_payload)
    sender.feature_flag = default_feature_flag
    assert response["status"].lower() == "failed"
