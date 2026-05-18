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
from connectors.webserver.ipam.tasks.get_ip_address import get_available_ips


@patch("connectors.core.services.ipam.connector.PrefixAvailableIps.get_prefix_available_ips")
def test_get_available_ips(get_prefix_available_ips_mock):
    mock_prefix_available_ips = {
        "status": "success",
        "metadata": {
            "vrf": "Global",
            "avlIpAddressList": [
                {"address": "89.200.128.233/24"},
                {"address": "89.200.128.237/24"},
                {"address": "89.200.128.241/24"},
                {"address": "89.200.128.252/24"},
                {"address": "89.200.128.255/24"},
            ],
        },
    }
    get_prefix_available_ips_mock.return_value = mock_prefix_available_ips
    ip_obj = get_available_ips(prefix="89.200.128.0/24", network="UK", domain="Core", quantity=3)
    assert ip_obj == mock_prefix_available_ips
