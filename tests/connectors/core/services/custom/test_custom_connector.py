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
from unittest import mock

# Third Party Library
import pytest

# DNE Library
from connectors.core.exceptions import ConnectorsException
from connectors.core.services.custom.connector import CustomService

site = "eacol"
option = "-l"
username = "abcd"
password = "xyz"

exception_tma_fn = (ValueError, TypeError, AttributeError)


def test_connector_get_tma_instance():
    """
     test to tma Instance
    :return:
    """
    tma_obj = CustomService()
    assert isinstance(tma_obj, CustomService)


@mock.patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@pytest.mark.parametrize("exception_type", exception_tma_fn)
def test_get_tma_connectors_exception(mock_rest_get, exception_type):
    """
    Test to verify if get_tma raises ConnectorsException(for ValueError/TypeError/AttributeError)
    """
    tma = CustomService()
    mock_rest_get.side_effect = exception_type("dummy error message")
    with pytest.raises(ConnectorsException):
        tma.read_tma(site=site, option=option, password=password, username=username)


@mock.patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@pytest.mark.parametrize("exception_type", exception_tma_fn)
def test_get_grandma_connectors_exception(mock_rest_get, exception_type):
    """
    Test to verify if get_tma raises ConnectorsException(for ValueError/TypeError/AttributeError)
    """
    tma = CustomService()
    mock_rest_get.side_effect = exception_type("dummy error message")
    with pytest.raises(ConnectorsException):
        tma.read_grandma(site=site)
