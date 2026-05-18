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

# DNE Library
from connectors.webserver.horizon.tasks.write import update_horizon_deliverable


@patch("connectors.webserver.horizon.tasks.write.HorizonService")
def test_update_horizon_order(horizon_service_mock):
    horizon_service_mock_obj = Mock()
    horizon_service_mock.return_value = horizon_service_mock_obj
    horizon_service_mock_obj.update_deliverable_details.return_value = {"status": "SUCCESS"}
    assert update_horizon_deliverable() == {"status": "SUCCESS"}
    horizon_service_mock.assert_called_once_with()
    horizon_service_mock_obj.update_deliverable_details.assert_called_once_with()
