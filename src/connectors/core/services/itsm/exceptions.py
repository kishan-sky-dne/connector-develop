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


class ResourceServiceNotAvailable(ConnectorsException):
    """Exception raised when the resource system is not available."""

    pass


class InvalidStateRequest(ConnectorsException):
    """Exception raised when the ticket update request is not proper."""

    pass


class DateGeneratorError(ConnectorsException):
    """Exception raised when the resource system is not available."""

    pass


class DateValidateError(ConnectorsException):
    """Exception raised when the resource system is not available."""

    pass


class InvalidRequest(ConnectorsException):
    """Exception raised when an invalid response is received from the ITSM connector"""

    pass


class DataUnavailable(ConnectorsException):
    """Exception raised when an invalid data received from the ITSM connector"""

    pass


class SizeLimitExceeded(ConnectorsException):
    """Exception raised when an size limit exceeds"""

    pass
