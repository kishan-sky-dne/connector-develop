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
import logging

# Third Party Library
from jinja2 import Environment, FileSystemLoader
from jinja2 import exceptions as jinjaException  # noqa: N812

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.services.mailer.exceptions import (
    GenericConnectorsException,
    PayloadParametersValidationException,
    TemplateDesignerException,
    TemplateNotFoundException,
)

logger = logging.getLogger(__name__)

APP_PATH = config.get(section="internals", key="app_path")


class EmailTemplateDesigner:
    def __init__(self, **kwargs):
        """
        Designing the templates
        """

    def design(self, template_type, template_name, template_language, parameters):
        """
        custom function which loads the template with the inputs provided by consumer

        Args:
            subject, title, subtitle, footerText

        Returns:
            response: valid_to_list, valid_bcc_list, valid_cc_list,
                      invalid_to_list,invalid_bcc_list, invalid_cc_list

        Raises:
            Exception

        """
        try:
            logger.info(
                f"Entering Template Designer Module in Mailer with template type as {template_type},"
                f" template name as {template_name} and template language as {template_language}"
            )
            """
            Template path creation
            """
            template_path = f"{APP_PATH}/templates/{template_type}/locale/{template_language}"
            template_file = f"{template_name}.{template_type}"
            logger.info(f"Template path to be looked for: {template_path}")
            logger.info(f"Template file to be looked for: {template_file}")

            if template_type == "json":
                return self.json_template_designer(template_path, template_file, parameters)
            elif template_type in ["html", "j2"]:
                return self.html_j2_template_designer(template_path, template_file, parameters, template_type)
            else:
                return True

        except (ValueError, TypeError, AttributeError) as err:
            raise GenericConnectorsException(f"Problem in preparing the design template: {str(err)}") from err

    @staticmethod
    def json_template_designer(template_path, template_file, parameters):
        try:
            env = Environment(loader=FileSystemLoader(searchpath=template_path))
            logger.debug(f"List of templates: {env.list_templates()}")
            json_template = env.get_template(template_file, parent=None)
            logger.info(f"Template File found: {json_template}")

            """
            Validating the glossary section in request payload
            """
            rendered_json = json.loads(json_template.render(mappings=parameters))
            required_params_dict = rendered_json["glossary"]
            logger.info(f"Required parameters from the template: " f"{required_params_dict['requiredParams']}")

            required_params_str = required_params_dict["requiredParams"]
            required_params_list = list(map(str.strip, required_params_str.split(",")))
            if parameters.get("xDays") and int(parameters["xDays"]) <= 0:
                raise PayloadParametersValidationException(f"xDays configured should be greater then 0")
            validate_payload_params = all(parameters.get(elem) for elem in required_params_list)
            if not validate_payload_params:
                raise PayloadParametersValidationException(f"Problem in preparing the design template")

            logger.debug(f"JSON Rendered: {rendered_json}")
            return rendered_json
        except (jinjaException.TemplateNotFound, jinjaException.TemplatesNotFound) as err:
            raise TemplateNotFoundException(f"Problem in preparing the design template for JSON: " f"{err.args[0]}")
        except (
            jinjaException.UndefinedError,
            jinjaException.FilterArgumentError,
            jinjaException.SecurityError,
            jinjaException.TemplateRuntimeError,
            jinjaException.TemplateError,
            jinjaException.TemplateSyntaxError,
            jinjaException.TemplateAssertionError,
        ) as err:
            raise TemplateDesignerException(f"Problem in preparing the design template for JSON: " f"{err.args[0]}")
        except (ValueError, TypeError, AttributeError) as err:
            raise GenericConnectorsException(f"Problem in preparing the design template for JSON: {err.args[0]}")

    @staticmethod
    def html_j2_template_designer(template_path, template_file, rendered_json, template_type):
        try:
            env = Environment(loader=FileSystemLoader(searchpath=template_path))
            logger.debug(f"List of templates: {env.list_templates()}")
            template = env.get_template(template_file, parent=None)
            logger.info(f"Template File found: {template}")
            logger.debug(f"Parameters coming inside {template_type} Designer: {rendered_json}")

            """
            Hydrating the html/j2 content
            """
            rendered_html = template.render(mappings=rendered_json)
            logger.debug(f"{template_type} Rendered: {rendered_html}")
            return rendered_html
        except (jinjaException.TemplateNotFound, jinjaException.TemplatesNotFound) as err:
            raise TemplateNotFoundException(
                f"Problem in preparing the design template for " f"{template_type}: " f"{err.args[0]}"
            )
        except (
            jinjaException.UndefinedError,
            jinjaException.FilterArgumentError,
            jinjaException.SecurityError,
            jinjaException.TemplateRuntimeError,
            jinjaException.TemplateError,
            jinjaException.TemplateSyntaxError,
            jinjaException.TemplateAssertionError,
        ) as err:
            raise TemplateDesignerException(
                f"Problem in preparing the design template for " f"{template_type}: " f"{err.args[0]}"
            )
        except (ValueError, TypeError, AttributeError) as err:
            raise GenericConnectorsException(
                f"Problem in preparing the design template for " f"{template_type}: " f"{err.args[0]}"
            )
