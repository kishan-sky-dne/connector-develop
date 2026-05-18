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
# standard Library
# Standard Library
import asyncio
import logging

# Third Party Library
import connexion

# DNE Library
from connectors.core.services.itsm.aio_connector import SparkTicketService as AioSparkTicketService
from connectors.core.services.itsm.exceptions import InvalidRequest, ResourceServiceNotAvailable
from connectors.core.utils.exceptions import RestUtilityException

logger = logging.getLogger(__name__)


def update_ci_relationships(**kwargs):
    """
    Method to run Asynchronous Spark CI relationship update API
    """
    logger.info("Entering into ITSM module to update ci relationships")
    spark_service_instance = AioSparkTicketService()
    try:
        response = asyncio.run(spark_service_instance.service3605(**kwargs))
        logger.info("Exiting ITSM module after sending the response")
        return response
    except (ValueError, KeyError, TypeError, OverflowError, InvalidRequest) as err:
        logger.exception(err)
        return connexion.problem(status=404, title="Problem in preparing request", detail=err.args[0])
    except RestUtilityException as err:
        return connexion.problem(
            status=403,
            title="Request Exception while accessing the URL",
            detail=err.args[0],
        )
    except ResourceServiceNotAvailable as err:
        logger.exception(err)
        return connexion.problem(
            status=404,
            title="Error in accessing Spark ticketing system",
            detail=err.args[0],
        )
    except Exception as err:
        logger.exception(err)
        return connexion.problem(
            status=500,
            title="Connector exception raised while running custom query",
            detail=err.args[0],
        )
