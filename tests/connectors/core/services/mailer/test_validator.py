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
from connectors.core.services.mailer.exceptions import (
    BccListException,
    CCListException,
    EmailValidatorException,
    MaxRecipientsException,
    ToListException,
)
from connectors.core.services.mailer.validator import EmailValidator


def test_validate_success():
    """
    Test to check the functionality of validate() function.
    """
    to_list = ["user@sky.uk", "user@sky.it", "user@comcast.com", "abc"]
    bcc_list = ["user@sky.uk", "user@sky.it", "user@comcast.com"]
    cc_list = ["user@sky.uk", "user@sky.it", "user@comcast.com", "user@xyz.com"]
    (
        valid_to_list,
        invalid_to_list,
        valid_bcc_list,
        invalid_bcc_list,
        valid_cc_list,
        invalid_cc_list,
    ) = EmailValidator().validate(to_list=to_list, bcc_list=bcc_list, cc_list=cc_list)
    assert valid_to_list == ["user@sky.uk", "user@sky.it", "user@comcast.com"]
    assert invalid_to_list == ["abc"]
    assert valid_bcc_list == bcc_list
    assert invalid_bcc_list == []
    assert valid_cc_list == ["user@sky.uk", "user@sky.it", "user@comcast.com"]
    assert invalid_cc_list == ["user@xyz.com"]


def test_validate_to_list_exception():
    """
    Test to check if validate() is raising ToListException
    """
    to_list = [123]
    bcc_list = ["user@sky.uk", "user@sky.it", "user@comcast.com"]
    cc_list = ["user@sky.uk", "user@sky.it", "user@comcast.com", "xyz"]
    with pytest.raises(ToListException):
        EmailValidator().validate(to_list=to_list, bcc_list=bcc_list, cc_list=cc_list)


def test_validate_bcc_list_exception():
    """
    Test to check if validate() is raising BccListException
    """
    to_list = ["user@sky.uk", "user@sky.it", "user@comcast.com"]
    bcc_list = [123]
    cc_list = ["user@sky.uk", "user@sky.it", "user@comcast.com", "xyz"]
    with pytest.raises(BccListException):
        EmailValidator().validate(to_list=to_list, bcc_list=bcc_list, cc_list=cc_list)


def test_validate_cc_list_exception():
    """
    Test to check if validate() is raising CCListException
    """
    to_list = ["user@sky.uk", "user@sky.it", "user@comcast.com"]
    bcc_list = ["user@sky.uk", "user@sky.it", "user@comcast.com"]
    cc_list = [123]
    with pytest.raises(CCListException):
        EmailValidator().validate(to_list=to_list, bcc_list=bcc_list, cc_list=cc_list)


def test_email_classifier_category_to():
    """
    Test to check the functionality of email_classifier() function with category "to"
    """
    valid_list, invalid_list = EmailValidator().email_classifier(
        email_list=["user@sky.uk", "user@sky.it", "user@comcast.com", "abc"], category="to"
    )
    assert valid_list == ["user@sky.uk", "user@sky.it", "user@comcast.com"]
    assert invalid_list == ["abc"]


def test_email_classifier_category_bcc():
    """
    Test to check the functionality of email_classifier() function with category "bcc"
    """
    valid_list, invalid_list = EmailValidator().email_classifier(
        email_list=["user@sky.uk", "user@sky.it", "user@comcast.com"], category="bcc"
    )
    assert valid_list == ["user@sky.uk", "user@sky.it", "user@comcast.com"]
    assert invalid_list == []


def test_email_classifier_category_cc():
    """
    Test to check the functionality of email_classifier() function with category "cc"
    """
    valid_list, invalid_list = EmailValidator().email_classifier(email_list=["user@xyz.com"], category="cc")
    assert valid_list == []
    assert invalid_list == ["user@xyz.com"]


def test_email_classifier_email_validator_exception():
    """
    Test to check the functionality of email_classifier() function
    """
    with pytest.raises(EmailValidatorException):
        EmailValidator().email_classifier(email_list=["test@sky.uk"])


def test_check_max_recipients_success():
    """
    Test to check the functionality of check_max_recipients() function.
    """
    to_list = ["user@sky.uk", "user@sky.it", "user@comcast.com"]
    bcc_list = ["user@sky.uk", "user@sky.it", "user@comcast.com"]
    cc_list = ["user@sky.uk", "user@sky.it", "user@comcast.com"]
    return_val = EmailValidator().check_max_recipients(
        to_list=to_list, bcc_list=bcc_list, cc_list=cc_list, conf_total_recipients=10
    )
    assert return_val


def test_check_max_recipients_fail():
    """
    Test to check the functionality of check_max_recipients() function for failure condition
    """
    to_list = ["user@sky.uk", "user@sky.it", "user@comcast.com"]
    bcc_list = ["user@sky.uk", "user@sky.it", "user@comcast.com"]
    cc_list = ["user@sky.uk", "user@sky.it", "user@comcast.com"]
    return_val = EmailValidator().check_max_recipients(
        to_list=to_list, bcc_list=bcc_list, cc_list=cc_list, conf_total_recipients=1
    )
    assert not return_val


def test_check_max_recipients_raises_max_recipient_exception_type_error():
    """
    Test to check if check_max_recipients() function is raising MaxRecipientsException due to TypeError caused out of
    bcc_list being None.
    """
    to_list = ["user@sky.uk", "user@sky.it", "user@comcast.com"]
    bcc_list = None
    cc_list = ["user@sky.uk", "user@sky.it", "user@comcast.com"]
    with pytest.raises(MaxRecipientsException):
        EmailValidator().check_max_recipients(
            to_list=to_list, bcc_list=bcc_list, cc_list=cc_list, conf_total_recipients=10
        )
