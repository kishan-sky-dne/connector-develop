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
from unittest.mock import patch

# Third Party Library
import pytest
from connexion.lifecycle import ConnexionResponse

# DNE Library
from connectors.core.utils.exceptions import ResourceServiceNotAvailable, RestUtilityException
from connectors.webserver.custom.tasks import read

exception_get_tma = [(RestUtilityException, 403), (ResourceServiceNotAvailable, 404), (Exception, 500)]

grandma_data_json = {"bm0.eacol.isp.sky.com": 0, "cr0.eacol.uk.easynet.net": 3}


grandma_data_csv = (
    "EXCHANGE_CODE,HOST_NAME,SLOT_NUMBER,SKY_CUSTOMER_COUNT,ENTERPRISE_CUSTOMER_COUNT,"
    "SKYWIFI_CUSTOMER_COUNT\nEACOL,bm0.eacol.isp.sky.com,1,43,0,0\nEACOL,bm0.eacol.isp.sky.com,2,39,0,"
    "0\nEACOL,cr0.eacol.uk.easynet.net,3,43,6,0\nEACOL,cr0.eacol.uk.easynet.net,3,43,3,0\n"
)


@patch("connectors.core.services.custom.connector.CustomService.read_tma")
def test_get_tma_details(mock_core_tma_fn):
    """
    Test to check the functionality of getTmaData()
    """
    mock_core_tma_fn.return_value = ConnexionResponse(
        body=b"<html><body>TMA Output</body></html>", mimetype="text/html"
    )
    output = read.getTmaData(site="tma", option="-l")
    assert isinstance(output, ConnexionResponse)
    assert output.status_code == 200


@patch("connectors.core.services.custom.connector.CustomService.read_tma")
@pytest.mark.parametrize("exception_type, error_code", exception_get_tma)
def test_get_tma_details_raises_exception(mock_core_tma_fn, exception_type, error_code):
    """
    Test to check if getTmaDetails raises different exceptions.
    """
    mock_core_tma_fn.side_effect = exception_type("dummy error message")
    response = read.getTmaData(site="tma", option="-l")
    assert response.status_code == error_code


@mock.patch("connectors.core.services.custom.connector.CustomService.read_grandma")
def test_get_grandma_output(mock_rest_grandma):
    """
    Test to verify if get_tma raises ConnectorsException(for ValueError/TypeError/AttributeError)
    """
    mock_rest_grandma.return_value = grandma_data_csv
    response = read.getGrandmaData(site="EACOL")
    assert response == grandma_data_json
