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
# """Connectors Exceptions"""
# Standard Library
import logging

logger = logging.getLogger(__name__)


class ConnectorsException(Exception):
    """Exception raised by every module in the Connectors package."""

    def __init__(self, msg=None):
        """

        Args:
            msg (str): human friendly error message.
        """

        if msg is None:
            msg = "Connectors Exception"
        logger.exception(msg)
        super().__init__(msg)


class ServiceDBException(ConnectorsException):
    """Exception raised by every function in the ServiceDB sub-module"""

    pass
