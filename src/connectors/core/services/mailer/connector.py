"""Mail module"""

# Standard Library
import logging
import smtplib
import socket
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.services.mailer.exceptions import MailerSMTPException

logger = logging.getLogger(__name__)

APP_PATH = config.get(section="internals", key="app_path")


class Mailer:
    """
    Sending emails using SMTP Server
    """

    logger.info(f"Entering Mailer Module")

    def __init__(
        self, server, port, from_address, to_list, cc_list, bcc_list, subject, html_content, login=None, use_tls=False
    ):
        self.server = server
        self.port = port
        self.from_address = from_address
        self.to_list = to_list
        self.cc_list = cc_list
        self.bcc_list = bcc_list
        self.subject = subject
        self.login = login  # login should be a tuple with username and password
        self.use_tls = use_tls
        self.html_content = html_content
        logger.info(
            f"Parameters inside send mail utility are server: {self.server} with port {self.port}. From: "
            f"{self.from_address}, To: {self.to_list}, Cc: {self.cc_list}, Bcc: {self.bcc_list}. Subject:"
            f"{self.subject}"
        )

        self.msg_root = MIMEMultipart("related")
        self.msg_root["From"] = self.from_address
        self.msg_root["To"] = ", ".join(self.to_list)
        self.msg_root["Cc"] = ", ".join(self.cc_list)
        self.msg_root["Bcc"] = ", ".join(self.bcc_list)
        self.msg_root["Subject"] = self.subject
        self.msg_root["Date"] = formatdate(localtime=True)
        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to display.
        self.msg_alternative = MIMEMultipart("alternative")
        self.msg_root.attach(self.msg_alternative)
        # logger.info(f"Composed Message: {self.msg_root.as_string()}")

    def add_attachment(self, filename, content):
        """
        Method to attach files as an attachment to mail
        """
        part = MIMEApplication(content, Name=filename)
        part["Content-Disposition"] = f'attachment; filename="{filename}"'
        self.msg_root.attach(part)

    def add_html_content(self):
        msg_text = MIMEText(self.html_content, "html")
        self.msg_alternative.attach(msg_text)

        with open(f"{APP_PATH}/templates/images/logo.png", "rb") as fp:
            msg_image = MIMEImage(fp.read())

        # Define the image's ID as referenced above
        msg_image.add_header("Content-ID", "<skyLogoReference>")
        self.msg_root.attach(msg_image)

    def send_email(self):  # noqa: C901
        try:
            server = smtplib.SMTP(self.server, self.port)
        except socket.gaierror:
            raise MailerSMTPException(f"An error occured while trying to connect to SMTP server")
        except smtplib.SMTPConnectError:
            raise MailerSMTPException(f"Error occurred during establishment of a connection with the server")

        if self.use_tls:
            try:
                server.starttls()
            except smtplib.SMTPHeloError:
                raise MailerSMTPException(f"The SMTP server didn’t reply properly to the HELLO greeting")
            except smtplib.SMTPNotSupportedError:
                raise MailerSMTPException(f"The SMTP server does not support the STARTTLS extension")
        if self.login is not None:
            try:
                server.login(self.login[0], self.login[1])
            except smtplib.SMTPHeloError:
                raise MailerSMTPException(f"The SMTP server didn’t reply properly to the HELLO greeting")
            except smtplib.SMTPAuthenticationError:
                raise MailerSMTPException(f"The SMTP server didn’t accept the username/password combination")
            except smtplib.SMTPNotSupportedError:
                raise MailerSMTPException(f"The AUTH command is not supported by the SMTP server")
            except smtplib.SMTPException:
                raise MailerSMTPException(f"No suitable authentication method was found")

        try:
            server.sendmail(self.from_address, (self.to_list + self.cc_list + self.bcc_list), self.msg_root.as_string())
        except smtplib.SMTPRecipientsRefused:
            raise MailerSMTPException(f"All recipients were refused. Nobody got the mail")
        except smtplib.SMTPHeloError:
            raise MailerSMTPException(f"The SMTP server didn’t reply properly to the HELLO greeting")
        except smtplib.SMTPSenderRefused:
            raise MailerSMTPException(f"The SMTP server didn’t accept the {self.from_address}")
        except smtplib.SMTPDataError:
            msg = f"The SMTP server replied with an unexpected error code (other than a refusal of a recipient)"
            raise MailerSMTPException(msg)
        finally:
            server.quit()
