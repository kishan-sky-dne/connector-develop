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

# Third Party Library
import connexion

# DNE Library
from connectors.core.services.cisco.smart_license_services import CiscoSmartLicense
from connectors.core.utils.exceptions import GenericConnectorsException, RestUtilityException

logger = logging.getLogger(__name__)


def get_cisco_smart_license(**kwargs):
    """"""
    try:
        logger.info(f"Entering into Cisco module to fetch the cisco smart token")
        csml_obj = CiscoSmartLicense()
        return csml_obj.get_smart_token()
    except RestUtilityException as err:
        return {
            "status": "FAILURE",
            "errorCategory": "FAILED",
            "errors": [{"code": "ERR-008-012-1001", "message": "Failed to generate token: " + err.args[0]}],
        }
    except GenericConnectorsException as err:
        return connexion.problem(
            status=500,
            title=f"Connector exception raised while fetching the cisco smart licence token",
            detail=err.args[0],
        )
