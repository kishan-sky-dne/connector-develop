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
from connectors.core.exceptions import ServiceDBException
from connectors.webserver.service_status.read import get_service_status


@patch("connectors.webserver.service_status.read.ServiceStatus")
def test_track_orders(object_mock):
    """
    Test if the landing function calls ServiceStatus with the given params
    """
    get_service_status(params="dummy param")
    object_mock.assert_called_once_with(params="dummy param")


@patch("connectors.core.services.service_status.read.ServiceDB")
def test_get_service_status_exception(db_mock):
    """
    Test if intended connexion problem is raised in case of a serviceDB exception
    """
    db_mock.side_effect = ServiceDBException("dummy error")
    connexion_resp = get_service_status(orderId="BPM-123", serviceType="deltaBase", operationType="create")
    assert connexion_resp.body["title"] == "Failed to connect to the serviceDB."
