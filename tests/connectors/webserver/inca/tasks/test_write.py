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
import requests

# DNE Library
from connectors.core.services.inca.connector import IncaService
from connectors.webserver.inca.tasks import write

body = {
    "geaCeaseDetails": {
        "messageType": "GEACEASE",
        "requestDate": "2024-09-14",
        "exchange": "WNWX",
        "tgReference": "TG1234",
        "requiredByDate": "2024-09-30",
        "btSwitch": "BAACHK",
        "circuitCeaseOrderRef": "OGHP64783778-3456789-CEASE",
        "cablelinkRef": "OGHP64783778",
    }
}

access_token_nexa = "xyz"


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth")
def test_write_inca_details_case1(mock_oauth, post_mocked, mock_post):
    mock_oauth.token_generator.return_value = access_token_nexa
    inst_inca = IncaService()
    post_mocked.return_value = {"result": "OK", "id": "51234"}
    inst_inca.cease_circuit = Mock(return_value={"jobId": "BU-51234"})
    output = write.write_inca_details(type="gea", requestType="cease", body=body)
    assert output == {"jobId": "BU-51234"}


@patch.object(requests.Session, "post")
@patch("connectors.core.utils.rest_api_utility.RestUtility.post")
@patch("connectors.core.utils.oauth")
def test_write_inca_details_case2(mock_oauth, post_mocked, mock_post):
    mock_oauth.token_generator.return_value = access_token_nexa
    inst_inca = IncaService()
    post_mocked.return_value = {"result": "OK", "id": "55498"}
    write._validate_inca_write_data = Mock(return_value=(True, []))
    inst_inca.cease_circuit = Mock(return_value={"jobId": "BU-55498"})
    output = write.write_inca_details(type="ge", requestType="cease", body=body)
    assert output == {}
