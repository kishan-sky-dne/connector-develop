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


class UnauthorizedException(ConnectorsException):
    """Exception raised when the resource system is not available."""

    pass


class GenericConnectorsException(ConnectorsException):
    """Exception raised for the unhandled."""

    pass


class RestUtilityException(ConnectorsException):
    """Exception raised when the resource system is not available."""

    def __init__(self, message, response=None):
        self.message = message
        self.response = response
        super().__init__(self.message)


class ResourceServiceNotAvailable(ConnectorsException):
    """Exception raised when the resource system is not available."""

    pass


class ConnectorException(ConnectorsException):
    """Exception raised for the unhandled."""

    pass


class ConflictException(ConnectorsException):
    """Exception raised for the conflict."""

    pass


class ConnectorInvalidRequest(ConnectorsException):
    pass
