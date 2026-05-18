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
from jinja2 import exceptions as jinjaException  # noqa: N812

# DNE Library
from connectors.core.services.mailer.exceptions import (
    GenericConnectorsException,
    TemplateDesignerException,
    TemplateNotFoundException,
)
from connectors.core.services.mailer.templateDesigner import EmailTemplateDesigner

template_parameters = [
    (
        "json",
        "taskAssignment",
        "en",
        {
            "orderNumber": "123",
            "orderType": "OLT Commissioning",
            "taskName": "taskAssignment",
            "siteId": "1",
            "url": "https://testurl.com",
        },
    ),
    ("html", "orderTemplate", "en", {"requiredParams": "orderType, orderNumber, taskName, siteId, url"}),
]

exception_design = [ValueError, TypeError, AttributeError]

exception_template_designer = [
    (jinjaException.TemplateNotFound, TemplateNotFoundException),
    (jinjaException.TemplatesNotFound, TemplateNotFoundException),
    (jinjaException.UndefinedError, TemplateDesignerException),
    (jinjaException.FilterArgumentError, TemplateDesignerException),
    (jinjaException.SecurityError, TemplateDesignerException),
    (jinjaException.TemplateRuntimeError, TemplateDesignerException),
    (jinjaException.TemplateError, TemplateDesignerException),
    (ValueError, GenericConnectorsException),
    (TypeError, GenericConnectorsException),
    (AttributeError, GenericConnectorsException),
]


@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.html_j2_template_designer")
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.json_template_designer")
@pytest.mark.parametrize("template_type, template_name, template_language, parameters", template_parameters)
def test_design(mock_json_designer, mock_html_j2_designer, template_type, template_name, template_language, parameters):
    """
    Test to check the functionality of design() function
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
    mock_json_designer.return_value = rendered_json
    mock_html_j2_designer.return_value = """<html/>"""
    EmailTemplateDesigner().design(
        template_type=template_type,
        template_name=template_name,
        template_language=template_language,
        parameters=parameters,
    )
    if template_type == "json":
        mock_json_designer.assert_called_once()
    elif template_type == "html":
        mock_html_j2_designer.assert_called_once()


@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.html_j2_template_designer")
@patch("connectors.core.services.mailer.templateDesigner.EmailTemplateDesigner.json_template_designer")
@pytest.mark.parametrize("template_type, template_name, template_language, parameters", template_parameters)
@pytest.mark.parametrize("exception_type", exception_design)
def test_design_generic_connectors_exception(
    mock_json_designer,
    mock_html_j2_designer,
    template_type,
    template_name,
    template_language,
    parameters,
    exception_type,
):
    """
    Test to check if design() function is raising GenericConnectorsException
    """
    mock_json_designer.side_effect = exception_type("dummy")
    mock_html_j2_designer.side_effect = exception_type("dummy")
    with pytest.raises(GenericConnectorsException):
        EmailTemplateDesigner().design(
            template_type=template_type,
            template_name=template_name,
            template_language=template_language,
            parameters=parameters,
        )


@patch("connectors.core.services.mailer.templateDesigner.Environment.get_template")
@pytest.mark.parametrize("template_type, template_name, template_language, parameters", template_parameters)
@pytest.mark.parametrize("exception_caused, raised_exception", exception_template_designer)
def test_design_template_designer_exception(
    mock_env, template_type, template_name, template_language, parameters, exception_caused, raised_exception
):
    """
    Test to check if design()-> template designer is raising TemplateDesignerException and GenericConnectorsException
    """
    mock_env.side_effect = exception_caused("dummy error")
    with pytest.raises(raised_exception):
        EmailTemplateDesigner().design(
            template_type=template_type,
            template_name=template_name,
            template_language=template_language,
            parameters=parameters,
        )
