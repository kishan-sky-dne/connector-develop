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
import logging
import re

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.services.mailer.exceptions import (
    BccListException,
    CCListException,
    EmailValidatorException,
    MaxRecipientsException,
    ToListException,
)

logger = logging.getLogger(__name__)

config_allowed_domains = config.get(section="mailer", key="allowed_domains")
config_total_recipients = config.get(section="mailer", key="max_recipients")


class EmailValidator:
    def __init__(self, **kwargs):
        """
        Preparing the regex expression to validate the allowed domain list
        """
        logger.debug(f"Entering Validator Module in Mailer")
        self.allowed_domains = config_allowed_domains.replace(",", "|")
        self.regex = re.compile(
            r"^[a-zA-Z0-9_.+-]+@(?:(?:[a-zA-Z0-9-]+\.)?[a-zA-Z]+\.)?" r"(" + self.allowed_domains + ")$"
        )

    def validate(self, to_list, bcc_list, cc_list):
        """
        custom function does the validation of incoming mail ids with allowed domains

        Args:
            toList, ccList and bccList

        Returns:
            response: valid_to_list, valid_bcc_list, valid_cc_list,
                      invalid_to_list,invalid_bcc_list, invalid_cc_list

        Raises:
            Exception

        """
        logger.info(f"Allowed domain for notifications to be sent: {self.allowed_domains}")

        # bug fix DNE-1243 (No logger error when empty failed email address list)
        """
        Classifying toList with valid and invalid to send response back
        """
        try:
            valid_to_list, invalid_to_list = self.email_classifier(email_list=to_list, category="to")
        except EmailValidatorException as err:
            raise ToListException(f"Problem in validating ToList against the allowed domains: " f"{err.args[0]}")
        """
        Classifying bccList with valid and invalid to send response back
        """
        try:
            valid_bcc_list, invalid_bcc_list = self.email_classifier(email_list=bcc_list, category="bcc")
        except EmailValidatorException as err:
            raise BccListException(f"Problem in validating BccList against the allowed domains: " f"{err.args[0]}")
        """
        Classifying ccList with valid and invalid to send response back
        """
        try:
            valid_cc_list, invalid_cc_list = self.email_classifier(email_list=cc_list, category="cc")
        except EmailValidatorException as err:
            raise CCListException(f"Problem in validating CcList against the allowed domains: " f"{err.args[0]}")
        return valid_to_list, invalid_to_list, valid_bcc_list, invalid_bcc_list, valid_cc_list, invalid_cc_list

    def email_classifier(self, **kwargs):  # noqa: N802
        """
        custom function to classify valid and invalid mails

        Returns:
            response: valid & invalid list

        Raises:
            Exception

        """
        try:
            valid_list, invalid_list = [], []
            email_list = kwargs["email_list"]
            category = kwargs["category"]
            logger.info(f"List received into classifier:{email_list} for {category} recipients")
            for email in email_list:
                if self.regex.search(email) is not None:
                    valid_list.append(email)
                else:
                    invalid_list.append(email)
            return valid_list, invalid_list
        except (KeyError, TypeError, AttributeError) as err:
            raise EmailValidatorException(
                f"Problem in validating recipients against the allowed domains: " f"{err.args[0]}"
            )

    @staticmethod
    def check_max_recipients(to_list, bcc_list, cc_list, conf_total_recipients=config_total_recipients):
        """
        custom function to check the count of recipients against the configurable value

        Returns:
            response: True or False

        Raises:
            Exception

        """
        try:
            total_recipients = len(to_list) + len(bcc_list) + len(cc_list)
            logger.info(f"Total Number of recipients from request is {total_recipients}")
            return total_recipients <= int(conf_total_recipients)
        except (ValueError, KeyError, TypeError, ArithmeticError) as err:
            raise MaxRecipientsException(f"Problem in checking the maximum recipients: " f"{err.args[0]}")
