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
# Third Party Library
import pytest

# DNE Library
from connectors.core.services.mailer.exceptions import EmailValidatorException, MaxRecipientsException
from connectors.core.services.mailer.validator import EmailValidator


def test_mailer_max_recipients_exception():
    """
    Function to test the mailer method raises the right exception when the service is not available.
    """
    with pytest.raises(MaxRecipientsException):
        EmailValidator().check_max_recipients(
            to_list="abc@com", bcc_list="abc@com", cc_list="abc@com", conf_total_recipients=""
        )


def test_mailer_service_exception():
    """
    Function to test the mailer method raises the right exception when the service is not available.
    """
    with pytest.raises(EmailValidatorException):
        EmailValidator().email_classifier(email_list=123)
