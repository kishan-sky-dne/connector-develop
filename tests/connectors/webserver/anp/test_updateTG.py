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
from unittest.mock import patch

# Third Party Library
import pytest

# DNE Library
from connectors.webserver.anp.tasks.update import ResourceServiceNotAvailable, updateTGReference

request_body = {
    "comment": "xxx",
    "deliveryDate": "2022-07-20",
    "domain": "core",
    "environment": "qa",
    "projectName": "Sacramento",
    "requiredDate": "2021-12-12",
    "status": "new",
    "tgReference": "TG9989",
}

resp_upd_tg = {"message": "OK", "success": True}

exception = [(ResourceServiceNotAvailable, 404), (Exception, 500)]


@patch("connectors.core.services.anp.connector.UpdateTGService.update_tg")
def test_update_tg_reference(mock_core_upd_tg):
    """
    Test to check the functionality of updateTGReference function.
    Note mocking has been done at core.services.anp.connector.UpdateTGService level, internals of this function have
    been separately tested in detail under core->services
    """
    mock_core_upd_tg.return_value = resp_upd_tg
    response = updateTGReference(body=request_body)
    assert response == resp_upd_tg


@patch("connectors.core.services.anp.connector.UpdateTGService.update_tg")
@pytest.mark.parametrize("exception_type, error_code", exception)
def test_update_tg_reference_exception(mock_core_upd_tg, exception_type, error_code):
    """
    Test to check if updateTGReference() raises different exceptions
    """
    mock_core_upd_tg.side_effect = exception_type("dummy exception")
    response = updateTGReference(body=request_body)
    assert response.body["status"] == error_code
