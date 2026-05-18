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
import base64
import logging
import sys

# Third Party Library
import connexion

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.services.mailer.connector import Mailer
from connectors.core.services.mailer.exceptions import (
    BccListException,
    CCListException,
    GenericConnectorsException,
    MailerSMTPException,
    MaxRecipientsException,
    PayloadParametersValidationException,
    TemplateDesignerException,
    TemplateNotFoundException,
    ToListException,
)
from connectors.core.services.mailer.templateDesigner import EmailTemplateDesigner
from connectors.core.services.mailer.validator import EmailValidator

logger = logging.getLogger(__name__)

feature_flag = config.get(section="mailer", key="feature_flag")
config_total_recipients = config.get(section="mailer", key="max_recipients")
smtp_server = config.get(section="mailer", key="smtp_server")
smtp_port = config.get(section="mailer", key="smtp_port")
from_address = config.get(section="mailer", key="from_address")
template_category = config.get(section="mailer", key="template_category")
template_locale = config.get(section="mailer", key="template_locale")
max_allowed_attachment_count = int(config.get(section="mailer", key="max_attachment_count"))
max_allowed_attachment_size = int(config.get(section="mailer", key="max_attachment_size"))
max_attachment_size = int(max_allowed_attachment_size) // (1024 * 1024)


def email_notifications(**kwargs):  # noqa: C901
    """
    Sends email notifications via SMTP Service

    Args:
       body = {
                "toList": ["user@sky.uk", "user@sky.it", "user@comcast.com"]
                "bccList": ["user@sky.uk", "user@sky.it", "user@comcast.com"],
                "ccList": ["user@sky.uk", "user@sky.it", "user@comcast.com"],
                "language": "en",
                "mailTemplate": "taskAssignment",
                "parameters":
                   {
                       "orderNumber": "123",
                       "orderType": "OLT Commissioning",
                       "siteId": "1",
                       "url": "https://testurl.com"
                   }
                "attachmentList": [ {
                                   "fileName": "taskAssignment.pdf",
                                   "fileContent": "YWJjMTIzIT8kKiYoKScPUB+="
                                  },
                   {
                                   "fileName": "releaseNotes.jpeg",
                                   "fileContent":"YWJjMTIzIT8kKiYoKScPUB=="
                   }]
              }
    Returns:
       {
         "message": "Success or Error or Partial Success message",
         "status": "Success|Error|Partial Success",
         "targetEmailsStatus":
               {
                   "bccList":
                       {
                        "failedEmails": ["user@example.com"],
                        "successEmails": ["user@example.com"]
                       },
                   "ccList":
                       {
                        "failedEmails": ["user@example.com"],
                       "successEmails": ["user@example.com"]
                       },
                   "toList":
                       {
                        "failedEmails": ["user@example.com"],
                        "successEmails": ["user@example.com"]
                       }
               },
           "attachmentStatus": "Success|None"
       }

    Raises:

    """
    if feature_flag.lower() != "on":
        return connexion.problem(
            status=503,
            title=f"Email Notification feature is temporarily not available",
            detail=f"Email Notification Feature Flag has to be set to 'ON'",
        )

    try:
        mail_content = kwargs["body"]
        logger.info(
            f"Entering into Mailer module for {mail_content['mailTemplate']} " f"with feature flag " f"{feature_flag}"
        )

        """
        Extracting the unique mails from toList, bccList, ccList before checking max recipients allowed
        """
        to_list = list(set(mail_content["toList"]))

        if not to_list:
            return connexion.problem(
                status=400,
                title=f"The toList cannot be empty",
                detail=f"Problems with `toList` key",
            )

        bcc_list = list(set(mail_content.get("bccList") or []))
        cc_list = list(set(mail_content.get("ccList") or []))
        attachment_list = mail_content.get("attachmentList")
        template_name = mail_content["mailTemplate"]
        template_language = mail_content["language"]
        input_parameters = mail_content["parameters"]

        """
        Handling a new template category with new locale dynamically
        """
        category = list(set(template_category.split(",")))
        locale = list(set(template_locale.split(",")))

        logger.info(f"Supported Categories: {category} & Locales {locale}")

        if (template_name.strip() not in category) or (template_language.strip() not in locale):
            return connexion.problem(
                status=404,
                title=f"Given template/language is not supported by DNE team currently",
                detail=f"Please raise a request for templateName: {template_name} in language: {template_language} "
                f"@{from_address} as the supported templates are {template_category} in {template_locale}",
            )  # Bug fix for 3305

        """
        Stripping whitespaces if any in payload keys to ensure empty values are not sent over mail
        """
        parameters = {key.strip(): val for key, val in input_parameters.items()}
        if parameters.get("errorDetails"):
            for item in (('"', " '"), ("\n", "")):
                error_formatting = parameters["errorDetails"].replace(*item)
                parameters["errorDetails"] = error_formatting
        logger.debug(f"Parameters coming from input payload after removing whitespaces: {parameters}")

        """
        Calling JSON Schemas to validate if the required details are present in request body
        """
        email_validator_obj = EmailValidator()
        logger.info(f"Proceed to validate max allowed recipients")
        max_recipients_flag = email_validator_obj.check_max_recipients(
            to_list, bcc_list, cc_list, config_total_recipients
        )
        logger.debug(f"Number of recipients validation is {max_recipients_flag}")
        logger.info(f"Validating max allowed recipients is completed successfully")
        if not max_recipients_flag:
            return connexion.problem(
                status=403,
                title=f"Validation failed due to the number of emails in toList, ccList, bccList",
                detail=f"Email Recipients list should be less than or equal to {config_total_recipients}",
            )

        """
        Calling email validator to validate the allowed recipients in toList, bccList, ccList
        """
        logger.info(f"Proceed to validate emails from request")
        (
            valid_to_list,
            invalid_to_list,
            valid_bcc_list,
            invalid_bcc_list,
            valid_cc_list,
            invalid_cc_list,
        ) = email_validator_obj.validate(to_list, bcc_list, cc_list)

        logger.debug(
            f"Valid recipients of toList {valid_to_list}," f" bccList {valid_bcc_list} & " f" ccList {valid_cc_list}"
        )

        """
        Provide logs for valid and invalid email addresses
        """
        if valid_to_list:
            logger.info(f"Valid ToList recipients: {valid_to_list}")
        if invalid_to_list:
            logger.error(f"Invalid ToList recipients: {invalid_to_list}")
        if valid_cc_list:
            logger.info(f"Valid CcList recipients: {valid_cc_list}")
        if invalid_cc_list:
            logger.error(f"Invalid CcList recipients: {invalid_cc_list}")
        if valid_bcc_list:
            logger.info(f"Valid BccList recipients: {valid_bcc_list}")
        if invalid_bcc_list:
            logger.error(f"Invalid BccList recipients: {invalid_bcc_list}")

        logger.info(f"Validation of email pattern completed successfully")

        """
        Stop triggering mails if validToList is empty
        """
        if not valid_to_list:
            logger.error(f"No valid email address found in ToList recipients: {invalid_to_list}")
            return connexion.problem(
                status=400,
                title=f"There is no valid email address in toList",
                detail=f"Problems with `toList` " f"key",
            )

        """
        Restricting attachments to the configured size/count parameters
        """
        # bug fix DNE-1244 added logs
        # bug fix DNE-1215 count issue
        logger.info(f"Checks for attachments size and count with the configured size/count parameters")
        attachment_status = "None"
        if attachment_list:
            logger.info(f"Checks for number of files attachment with the configured max allowed attachments count")
            if len(attachment_list) > max_allowed_attachment_count:
                logger.error(
                    f"Attachments exceed the configured count limit - current count "
                    f"is {len(attachment_list)} which exceeds set limit of "
                    f"{max_allowed_attachment_count}"
                )
                return connexion.problem(
                    status=403,
                    title=f"Attachments exceed the count limit",
                    detail=f"Problem with no of attachments in `attachmentList` key, current count "
                    f"is {len(attachment_list)} and which exceeds the set limit of "
                    f"{max_allowed_attachment_count}",
                )
            logger.info(f"Checks for files attachment aggregate size with the configured max allowed size")
            total_file_size = 0
            for attachment in attachment_list:
                file_content_size = sys.getsizeof(attachment["fileContent"])
                total_file_size += file_content_size
            if total_file_size > max_allowed_attachment_size:
                logger.error(
                    f"Attachments exceeds the configured size limit - attachments size "
                    f"is {round(int(total_file_size) // (1024 * 1024), 2)} mb which exceeds "
                    f"{max_attachment_size} mb"
                )
                return connexion.problem(
                    status=413,
                    title=f"Attachments exceed the size limit",
                    detail=f"Problem with total size of attachments in `attachmentList` key, attachments size is "
                    f"{round(int(total_file_size) // (1024 * 1024), 2)} mb, which exceeds the set limit of "
                    f"{max_attachment_size} mb",
                )

        """
        Calling Jinja2 template engine to render JSON using template type
        """
        logger.info(f"Proceed to prepare email content using JSON templates")
        email_template = EmailTemplateDesigner()
        rendered_json = email_template.design("json", template_name, template_language, parameters)
        logger.debug(f"Response from EmailDesigner template for JSON is {rendered_json}")
        logger.info(f"Email content creation using JSON templates completed successfully")

        """
        Calling Jinja2 template engine to render HTML using template type
        """
        logger.info(f"Proceed to prepare email content using HTML templates")
        rendered_html = email_template.design(
            "html", rendered_json["htmlTemplate"], template_language, rendered_json["glossary"]
        )
        logger.debug(f"Response from EmailDesigner template for HTML is {rendered_html}")
        logger.info(f"Email content creation using HTML templates completed successfully")

        """
        Response hydration
        """
        if valid_to_list and not invalid_to_list and not invalid_cc_list and not invalid_bcc_list:
            status = "Success"
        else:
            status = "Partial Success"

        # bug fix DNE-1247 and DNE-1274 content size issue
        # handled SMTP exception for attachments
        """
        Sending Mail with the formatted content
        """
        try:
            mailer_service = Mailer(
                smtp_server,
                smtp_port,
                from_address,
                valid_to_list,
                valid_cc_list,
                valid_bcc_list,
                rendered_json["glossary"]["subject"],
                rendered_html,
            )
            if attachment_list:
                for attachment in attachment_list:
                    decoded_file_content = base64.b64decode(attachment["fileContent"])
                    mailer_service.add_attachment(attachment["fileName"], decoded_file_content)
                    attachment_status = "Success"

            mailer_service.add_html_content()
            mailer_service.send_email()
            logger.info(f"Email sent successfully")
        except MailerSMTPException as err:
            logger.exception(f"Unable to send the email via the SMTP server: {err.args[0]}")
            status = "Failed"
            invalid_to_list += valid_to_list
            invalid_cc_list += valid_cc_list
            invalid_bcc_list += valid_bcc_list
            valid_to_list = valid_cc_list = valid_bcc_list = None
            attachment_status = "Failed"

        logger.info("Exiting mailer module after sending the response")

        return {
            "status": status,
            "message": status,
            "targetEmailsStatus": {
                "toList": {"successEmails": valid_to_list, "failedEmails": invalid_to_list},
                "ccList": {"successEmails": valid_cc_list, "failedEmails": invalid_cc_list},
                "bccList": {"successEmails": valid_bcc_list, "failedEmails": invalid_bcc_list},
            },
            "attachmentStatus": attachment_status,
        }

    except MaxRecipientsException as err:
        logger.exception(err)
        return connexion.problem(
            status=403,
            title=f"Error in validating max number of recipients allowed",
            detail=f"Problems with `{err.args[0]}` key",
        )
    except ToListException as err:
        logger.exception(err)
        return connexion.problem(
            status=403,
            title=f"Error in validating toList against the allowed domains",
            detail=f"Problems with `{err.args[0]}` key",
        )
    except BccListException as err:
        logger.exception(err)
        return connexion.problem(
            status=403,
            title=f"Error in validating bccList against the allowed domains",
            detail=f"Problems with `{err.args[0]}` key",
        )
    except CCListException as err:
        logger.exception(err)
        return connexion.problem(
            status=403,
            title=f"Error in validating ccList against the allowed domains",
            detail=f"Problems with `{err.args[0]}` key",
        )
    except TemplateNotFoundException as err:
        logger.exception(err)
        return connexion.problem(
            status=404,
            title=f"Template not found",
            detail=err.args[0],
        )
    except TemplateDesignerException as err:
        logger.exception(err)
        return connexion.problem(
            status=403,
            title=f"Error in preparing the design template for JSON:",
            detail=err.args[0],
        )
    except PayloadParametersValidationException as err:
        logger.exception(err)
        return connexion.problem(
            status=400,
            title=f"Parameters for the template {template_name} is not matching with the payload supplied",
            detail=err.args[0],
        )
    except MailerSMTPException as err:
        logger.exception(err)
        return connexion.problem(
            status=403,
            title=f"Smtp server response",
            detail=err.args[0],
        )
    except GenericConnectorsException as err:
        logger.exception(err)
        return connexion.problem(
            status=403,
            title=f"Connector exception raised while sending the notifications",
            detail=err.args[0],
        )
    except Exception as err:
        logger.exception(err)
        return connexion.problem(
            status=500,
            title=f"Connector exception raised while sending the notifications",
            detail=f"Problems with `{err.args[0]}` key",
        )
