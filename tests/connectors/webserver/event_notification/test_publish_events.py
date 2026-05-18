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
from connectors.webserver.event_notification.publish_events import publish_order_status

kwargs = {
    "body": {
        "keyId": "BPM-12345",
        "message": {
            "orderNumber": 12345,
            "orderType": "map-t",
            "orderCreatedDate": "2022-07-25 12:04:59",
            "status": "Success",
        },
        "eventTime": "2022-07-25 04:14:52",
        "eventSource": "DNE-BPM",
    }
}


@patch("connectors.webserver.event_notification.publish_events.OrderStatus")
def test_track_orders(order_status_mock):
    """
    Test if the landing function calls OrderStatus with the given kwargs
    """
    publish_order_status(**kwargs)
    order_status_mock.assert_called_once_with(**kwargs)
    order_status_mock().publish.assert_called_once()
