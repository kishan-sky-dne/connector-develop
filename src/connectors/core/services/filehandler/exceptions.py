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


class EncodedFileError(ConnectorsException):
    """Encoded File Error"""

    pass


class TemplateNotFound(ConnectorsException):
    """Template file not available in the store"""

    pass


class ColumnParse(ConnectorsException):
    """Column wise parsing not in the scope"""

    pass


class FileWriteError(ConnectorsException):
    """File encoding error"""

    pass


class RaiseDbError(ConnectorsException):
    """exception occurred while connecting DB"""
