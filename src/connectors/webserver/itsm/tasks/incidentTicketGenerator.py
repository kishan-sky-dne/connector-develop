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
import logging

# DNE Library
from connectors.core.services.itsm.incident import Incident
from connectors.core.utils.helpers import exception_handler

logger = logging.getLogger(__name__)


@exception_handler
def create_incident_ticket(**kwargs):
    """
    calling Incident module to generate an incident ticket through CAG in SPARK
    kwargs:
        request_body
    Returns:
        dictionary with success or failure status
    """
    payload = kwargs["body"]
    logger.debug(f"Entering 'create_incident_ticket' API with payload '{payload}")
    result = Incident(**kwargs).create_incident_ticket()
    logger.debug("Returning the status of the incident ticket generation request")
    return result
