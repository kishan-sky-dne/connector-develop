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
from connectors.webserver.itsm.tasks.incidentTicketGenerator import create_incident_ticket

kwargs = {
    "body": {
        "alertSummary": "Incident Raised as part of DNE order <orderId> (<orderType>) under <changeTicket>",
        "assignTo": "UK Digital Network Enabler Platform",
        "detailedDescription": "Rollback on ma0.bllabd1.isp.sky.com failed with <error message>",
        "severity": "p4",
        "monitoredItem": "dummy",
    }
}


@patch("connectors.webserver.itsm.tasks.incidentTicketGenerator.Incident")
def test_track_orders(incident_mock):
    """
    Test if the landing function calls OrderStatus with the given kwargs
    """
    create_incident_ticket(**kwargs)
    incident_mock.assert_called_once_with(**kwargs)
    incident_mock().create_incident_ticket.assert_called_once()
