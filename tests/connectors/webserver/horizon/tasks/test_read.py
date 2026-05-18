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
from unittest.mock import Mock, patch

# Third Party Library
import pytest

# DNE Library
from connectors.webserver.horizon.tasks.read import read_horizon_deliverable


@pytest.mark.parametrize(
    "kwargs, order_id, unique_reference",
    [
        ({"order_id": "1234"}, "1234", None),
        ({"unique_reference": "6789"}, None, "6789"),
        ({"order_id": "1234", "unique_reference": "6789"}, "1234", "6789"),
        ({}, None, None),
    ],
)
@patch("connectors.webserver.horizon.tasks.read.HorizonService")
def test_read_horizon_deliverable(horizon_service_mock, kwargs, order_id, unique_reference):
    horizon_service_mock_obj = Mock()
    horizon_service_mock.return_value = horizon_service_mock_obj
    horizon_service_mock_obj.get_horizon_deliverable.return_value = {"status": "SUCCESS"}
    assert read_horizon_deliverable(**kwargs) == {"status": "SUCCESS"}
    horizon_service_mock.assert_called_once_with()
    horizon_service_mock_obj.get_horizon_deliverable.assert_called_once_with(
        order_id=order_id, unique_reference=unique_reference
    )
