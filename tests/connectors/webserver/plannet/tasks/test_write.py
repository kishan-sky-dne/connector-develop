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
from connectors.webserver.plannet.tasks import write


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_get_card_id(get_mock):
    """
    Test for get_card_id function
    """
    get_mock.return_value = {"results": [{"slot": {"name": "0/1"}, "name": "hostname abc", "id": 1}]}
    card_id = write.get_card_id("hostname", "0/1", "abcdefg")
    assert card_id == 1


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_get_card_type_id(get_mock):
    """
    Test for get_card_type_id function
    """
    get_mock.return_value = {"results": [{"name": "test_type_name", "id": 2}]}
    card_type_id = write.get_card_type_id("test_type_name", "abcdefg")
    assert card_type_id == 2


@patch("connectors.core.utils.oauth.ConfidentialClientApplication")
@patch("connectors.core.services.plannet.connector.PlannetService.patch_plannet_details")
def test_udpate_card_details(patch_mock, post_mock):
    """
    Test update_card_details function
    """
    post_mock.return_value.acquire_token_by_username_password.return_value = {"access_token": "abcdefg"}
    write.get_card_id = Mock(return_value=1)
    write.get_card_type_id = Mock(return_value=2)
    patch_mock.return_value = {"status_ok": True}
    request = {"body": {"hostname": "box.abc", "slot_name": "0/1", "card_type": "new_card"}}
    output = write.udpate_card_details(**request)
    assert output == {"status_ok": True}


@patch("connectors.core.services.plannet.connector.PlannetService.patch_plannet_details")
def test_update_transition_group(patch_mock):
    """
    Test update_card_details function
    """
    patch_mock.return_value = {"status_ok": True}
    request = {
        "body": {
            "name": "Test_Transition_Group_Updated",
            "date": "2024-01-26",
            "description": "Updated description",
            "coordinator": "Updated coordinator",
            "nis_ref": "new_nisref",
            "domains": [7],
        },
        "id": "tg666",
    }
    output = write.update_transition_group(**request)
    assert output == {"status_ok": True}
