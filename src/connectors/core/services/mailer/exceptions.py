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
# DNE Library
from connectors.core.exceptions import ConnectorsException


class MailerSMTPException(ConnectorsException):
    """Exception raised when the resource system is not available."""

    pass


class ToListException(ConnectorsException):
    """Exception raised when ToList is not as expected."""

    pass


class BccListException(ConnectorsException):
    """Exception raised when BccList is not as expected."""

    pass


class CCListException(ConnectorsException):
    """Exception raised when CcList is not as expected."""

    pass


class EmailValidatorException(ConnectorsException):
    """Exception raised for the unhandled."""

    pass


class GenericConnectorsException(ConnectorsException):
    """Exception raised for the unhandled."""

    pass


class TemplateDesignerException(ConnectorsException):
    """Exception raised for the unhandled."""

    pass


class TemplateNotFoundException(ConnectorsException):
    """Exception raised for the unhandled."""

    pass


class MaxRecipientsException(ConnectorsException):
    """Exception raised for the unhandled."""

    pass


class PayloadParametersValidationException(ConnectorsException):
    """Exception raised for the unhandled."""

    pass
