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
from connectors.core.config.connectors_config import config
from connectors.core.services.anp.connector import UpdateTGService
from connectors.core.services.anp.exceptions import ResourceServiceNotAvailable

logger = logging.getLogger(__name__)


def updateTGReference(**kwargs):  # noqa: N802
    """
    calling anp to update TG

    Args:
        body:
            {
                              "comment": "changing delivery date",
                              "deliveryDate": "2022-07-20",
                              "domain": "metro,cdn,core,enterprise",
                              "environment": "qa/production",
                              "projectName": "Bluebird OLT",
                              "requiredDate": "2021-07-20",
                              "status": "allowed values are, cancelled,delivered,completed,ok,new,risk",
                              "tgReference": "TG9989"
                            }

    Returns:
        {
          "message": "TG9989 update failed",
          "success": "true/false"
        }

    Raises:
        Exception

    """

    try:

        anp = UpdateTGService(
            kwargs["body"], config.get(section="anp", key="ad_username"), config.get(section="anp", key="ad_password")
        )
        logger.info(f"updating anp with details  {kwargs['body']}")
        response = anp.update_tg()
    except ResourceServiceNotAvailable as err:
        return connexion.problem(
            status=404,
            title="Requested resource service not available",
            detail=err.args[0],
        )
    except Exception as err:
        return connexion.problem(
            status=500,
            title=f"Connector exception raised while updating TG "
            f"{kwargs['body']['tgReference']}"
            " in anp portal",  # noqa: E502
            detail=err.args[0],
        )
    else:
        return response
