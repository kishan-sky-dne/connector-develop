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
import sys
from unittest.mock import patch

# Sky Library
from isp_config import ConfigManagerException

# DNE Library
from connectors.core.config import connectors_config
from connectors.core.services.ipam.connector import DeletePrefix

try:
    config = connectors_config.ConnectorsConfigManager()
    config.load_config()
except ConfigManagerException:
    sys.exit(1)

delete_kwargs = {"ID": 123}


def test_delete_prefix_instance():
    delete_prefix_obj = DeletePrefix(delete_kwargs)
    assert isinstance(delete_prefix_obj, DeletePrefix)


@patch("connectors.core.utils.rest_api_utility.RestUtility.delete")
def test_delete_prefix(delete_mock):
    delete_prefix_obj = DeletePrefix(delete_kwargs)
    delete_mock.return_value = 204
    expected_delete_status = {"status": "success"}
    assert delete_prefix_obj.delete_prefix() == expected_delete_status


# Negative case
@patch("connectors.core.utils.rest_api_utility.RestUtility.delete")
def test_delete_prefix_negative(delete_mock):
    delete_prefix_obj = DeletePrefix(delete_kwargs)
    delete_mock.return_value = 404
    expected_delete_status = {
        "errorCategory": "FAILED",
        "errors": [{"code": "ERR-006-999-0009", "message": "Delete Prefix: ID not found"}],
        "status": "failure",
    }
    assert delete_prefix_obj.delete_prefix() == expected_delete_status
