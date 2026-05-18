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
import smtplib
import socket
from unittest import mock

# Third Party Library
import pytest

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.services.mailer.connector import Mailer
from connectors.core.services.mailer.exceptions import MailerSMTPException

smtp_server = config.get(section="mailer", key="smtp_server")
smtp_port = config.get(section="mailer", key="smtp_port")
from_address = config.get(section="mailer", key="from_address")

exception_cause1 = [(socket.gaierror, MailerSMTPException), (smtplib.SMTPConnectError, MailerSMTPException)]
exception_cause2 = [(smtplib.SMTPHeloError, MailerSMTPException), (smtplib.SMTPNotSupportedError, MailerSMTPException)]
exception_cause3 = [
    (smtplib.SMTPHeloError, MailerSMTPException),
    (smtplib.SMTPAuthenticationError, MailerSMTPException),
    (smtplib.SMTPNotSupportedError, MailerSMTPException),
    (smtplib.SMTPException, MailerSMTPException),
]
exception_cause4 = [
    (smtplib.SMTPHeloError, MailerSMTPException),
    (smtplib.SMTPDataError, MailerSMTPException),
]


def test_add_attachment():
    """
    Test to check the functionality of add_attachment
    """
    attachment = {"fileName": "taskAssignment.pdf", "fileContent": "YWJjMTIzIT8kKiYoKScPUB+="}
    mailer = Mailer(
        "test_smtp.bskyb.com",
        25,
        "test@sky.uk",
        ["test1@sky.uk"],
        ["test2@sky.uk"],
        ["test3@sky.uk"],
        "dummy oops",
        """<html/>""",
    )
    mailer.add_attachment(attachment["fileName"], attachment["fileContent"])


@mock.patch("smtplib.SMTP")
def test_send_email(mock_smtp_server):
    """
    Test to check the functionality of send_email
    """
    mailer = Mailer(
        "test_smtp.bskyb.com",
        25,
        "test@sky.uk",
        ["test1@sky.uk"],
        ["test2@sky.uk"],
        ["test3@sky.uk"],
        "dummy oops",
        """<html/>""",
    )
    mock_smtp_server.return_value = mock.Mock(return_value=True)
    mailer.send_email()
    mock_smtp_server.return_value.sendmail.assert_called_once()


@mock.patch("smtplib.SMTP")
@pytest.mark.parametrize("exception_caused, raised_exception", exception_cause1)
def test_send_email_mailer_smtp_exception_cause1(mock_smtp_server, exception_caused, raised_exception):
    """
    Test to check if send_mail() raises MailerSMTPException due to SMTPConnectError or socket gaierror
    """
    mailer = Mailer(
        "test_smtp.bskyb.com",
        25,
        "test@sky.uk",
        ["test1@sky.uk"],
        ["test2@sky.uk"],
        ["test3@sky.uk"],
        "dummy oops",
        """<html/>""",
    )
    mock_smtp_server.side_effect = exception_caused(500, "dummy error")
    with pytest.raises(raised_exception):
        mailer.send_email()


@mock.patch("smtplib.SMTP")
@pytest.mark.parametrize("exception_caused, raised_exception", exception_cause2)
def test_send_email_mailer_smtp_exception_cause2(mock_smtp_server, exception_caused, raised_exception):
    """
    Test to check if send_mail() raises MailerSMTPException due to SMTPHeloError or SMTPNotSupportedError in case of tls
    """
    mailer = Mailer(
        "test_smtp.bskyb.com",
        25,
        "test@sky.uk",
        ["test1@sky.uk"],
        ["test2@sky.uk"],
        ["test3@sky.uk"],
        "dummy oops",
        """<html/>""",
        use_tls=True,
    )
    mock_smtp_server.return_value = mock.Mock(return_value=True)
    mock_smtp_server.return_value.starttls.side_effect = exception_caused(500, "dummy error")
    with pytest.raises(raised_exception):
        mailer.send_email()


@mock.patch("smtplib.SMTP")
@pytest.mark.parametrize("exception_caused, raised_exception", exception_cause3)
def test_send_email_mailer_smtp_exception_cause3(mock_smtp_server, exception_caused, raised_exception):
    """
    Test to check if send_mail() raises MailerSMTPException while SMTP login attempt
    """
    mailer = Mailer(
        "test_smtp.bskyb.com",
        25,
        "test@sky.uk",
        ["test1@sky.uk"],
        ["test2@sky.uk"],
        ["test3@sky.uk"],
        "dummy oops",
        """<html/>""",
        login=("test_user", "test123"),
        use_tls=True,
    )
    mock_smtp_server.return_value = mock.Mock(return_value=True)
    mock_smtp_server.return_value.login.side_effect = exception_caused(500, "dummy error")
    with pytest.raises(raised_exception):
        mailer.send_email()


@mock.patch("smtplib.SMTP")
@pytest.mark.parametrize("exception_caused, raised_exception", exception_cause4)
def test_send_email_mailer_smtp_exception_cause4(mock_smtp_server, exception_caused, raised_exception):
    """
    Test to check if send_mail() raises MailerSMTPException while sending mail
    """
    mailer = Mailer(
        "test_smtp.bskyb.com",
        25,
        "test@sky.uk",
        ["test1@sky.uk"],
        ["test2@sky.uk"],
        ["test3@sky.uk"],
        "dummy oops",
        """<html/>""",
        login=("test_user", "test123"),
        use_tls=True,
    )
    mock_smtp_server.return_value = mock.Mock(return_value=True)
    mock_smtp_server.return_value.login.return_value = True
    mock_smtp_server.return_value.sendmail.side_effect = exception_caused(500, "dummy error")
    with pytest.raises(raised_exception):
        mailer.send_email()
