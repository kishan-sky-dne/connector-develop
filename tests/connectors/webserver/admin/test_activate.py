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

# DNE Library
from connectors.webserver.admin.tasks.activate import update_status


@patch("connectors.core.services.admin.activate_operation.UpdateStatus.get_device_status")
@patch("connectors.core.services.admin.activate_operation.UpdateStatus.update_status_active")
@patch("connectors.core.services.admin.activate_operation.UpdateStatus.update_status_inactive")
def test_update_status(update_status_inactive_mock, update_status_active_mock, get_device_status_mock):
    get_device_status_mock.return_value = [("Active",)]
    result = update_status(deviceOsVersionId=5)
    assert result == {
        "status": "failure",
        "errorCategory": "FAILED",
        "errors": [{"code": "ERR-000-009-0008", "message": "Device OS Version is already in Active State"}],
    }
    get_device_status_mock.return_value = [("InActive",)]
    update_status_active_mock.return_value = "Active"
    update_status_inactive_mock.return_value = True
    result = update_status(deviceOsVersionId=5)
    assert result == {"status": "success"}
    get_device_status_mock.return_value = None
    result = update_status(deviceOsVersionId=5)
    assert result == {
        "status": "failure",
        "errorCategory": "FAILED",
        "errors": [
            {"code": "ERR-000-009-0001", "message": "Database Operation Failed.deviceOsVersionId doesn't exist"}
        ],
    }
