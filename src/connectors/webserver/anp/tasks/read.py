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
import sys

# Third Party Library
import connexion

# Sky Library
from isp_config import ConfigManagerException

# DNE Library
from connectors.core.config import connectors_config
from connectors.core.services.anp.connector import ReadTGService
from connectors.core.services.anp.exceptions import DataUnavailable, InvalidRequest
from connectors.core.utils.exceptions import RestUtilityException

logger = logging.getLogger(__name__)

try:
    config = connectors_config.ConnectorsConfigManager()
    config.load_config()
except ConfigManagerException:
    sys.exit(1)

username = config.get(section="anp", key="ad_username")
password = config.get(section="anp", key="ad_password")


def read_tg_reference(**kwargs):
    try:
        logger.info(
            f"Entering into A&P read module with TgRef {kwargs['tgReference']} for " f"project {kwargs['projectName']}"
        )
        anp = ReadTGService(kwargs, username, password)
        response = anp.read_tg()
        logger.info(f"Exiting A&P read module after sending the response")
    except DataUnavailable as err:
        return connexion.problem(
            status=404,
            title=f"Data not found for provided payload",
            detail=err.args[0],
        )
    except InvalidRequest as err:
        return connexion.problem(
            status=400,
            title=f"Invalid request",
            detail=err.args[0],
        )
    except RestUtilityException as err:
        return connexion.problem(
            status=403,
            title=f"Request Exception while accessing the URL",
            detail=err.args[0],
        )
    except Exception as err:
        return connexion.problem(
            status=500,
            title=f"Connector exception raised while reading TG {kwargs['tgReference']} in anp portal",
            detail=err.args[0],
        )
    else:
        return response
