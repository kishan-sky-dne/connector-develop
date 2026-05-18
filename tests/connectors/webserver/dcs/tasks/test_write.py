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
from connectors.core.exceptions import ConnectorsException
from connectors.core.utils.exceptions import RestUtilityException
from connectors.webserver.dcs.tasks import write

payload_add_device = {
    "hostname": "xyz.bllab.com",
    "deviceVendor": "Cisco",
    "deviceModel": "NCS-5508",
    "os": "ios-xr",
    "osVersion": "7.0.2",
    "adminGroup": "sky",
    "owner": "MD_IPCore",
    "status": "development",
    "tacacsGroup": "IP_OVN_CRS",
    "tacacsSecret": "8ttmavqtpnhODGst",
    "deviceType": "Cisco",
}

exception_add_device = [
    (RestUtilityException, 403),
    (ValueError, 500),
    (TypeError, 500),
    (AttributeError, 500),
    (KeyError, 500),
    (ConnectorsException, 500),
]


@patch("connectors.core.services.dcs.connector.DeviceConfigurationService.add_device")
def test_add_device_success(mock_core_add_device):
    """
    Test to check the functionality of add_device(webserver.dcs.tasks.write) success case.
    Note : add_device (core.services.dcs.connectors) is being mocked here. It is being tested separately under
    core.services.dcs.connectors
    """
    mock_core_add_device.return_value = "SUCCESS"
    response = write.add_device(body=payload_add_device)
    assert response == "SUCCESS"


@patch("connectors.core.services.dcs.connector.DeviceConfigurationService.add_device")
def test_add_device_failed(mock_core_add_device):
    """
    Test to check the functionality of add_device(webserver.dcs.tasks.write) failure case.
    Note : add_device (core.services.dcs.connectors) is being mocked here. It is being tested separately under
    core.services.dcs.connectors
    """
    mock_core_add_device.return_value = "FAILURE"
    response = write.add_device(body=payload_add_device)
    assert response == "FAILURE"


@patch("connectors.core.services.dcs.connector.DeviceConfigurationService.add_device")
@pytest.mark.parametrize("exception_type, error_code", exception_add_device)
def test_add_device_raises_exception(mock_core_add_device, exception_type, error_code):
    """
    Test to check if add_device raises different exceptions.
    """
    mock_core_add_device.side_effect = exception_type("dummy error message")
    response = write.add_device(body=payload_add_device)
    assert response.status_code == error_code
