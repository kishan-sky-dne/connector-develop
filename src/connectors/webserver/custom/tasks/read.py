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
import csv
import logging

# Third Party Library
import connexion
from connexion.lifecycle import ConnexionResponse

# DNE Library
from connectors.core.services.custom.connector import CustomService
from connectors.core.utils.exceptions import ResourceServiceNotAvailable, RestUtilityException

logger = logging.getLogger(__name__)


def getTmaData(**kwargs):  # noqa: N802
    logger.info(f"Entering into TMAs to fetch details for {kwargs['site']}")
    try:
        custom_obj = CustomService()
        output = custom_obj.read_tma(site=kwargs["site"], option=kwargs["option"])
    except RestUtilityException as err:
        return connexion.problem(
            status=403,
            title=f"Request Exception while accessing the URL",
            detail=err.args[0],
        )
    except ResourceServiceNotAvailable as err:
        return connexion.problem(
            status=404,
            title=f"Device {kwargs['site']} not available in TMA",
            detail=err.args[0],
        )
    except Exception as err:
        return connexion.problem(
            status=500,
            title=f"Connector exception raised while sending command to " f"{kwargs['site']}" "to TMA",
            detail=err.args[0],
        )
    else:
        logger.info("Exiting TMA module after sending the response")
        return ConnexionResponse(body=output, status_code=200, content_type="text/html")


def getGrandmaData(**kwargs):  # noqa: N802
    logger.info(f"Entering into Grandma API to fetch details for {kwargs['site']}")
    try:
        custom_obj = CustomService()
        output = custom_obj.read_grandma(site=kwargs["site"])
        csv_output = process_csv(csv_input=output)
        prev_val = 0
        json_dict = {}
        for row in csv_output:
            curr_row = row[1]
            curr_val = int(row[4])
            if row[1] in json_dict:
                total = curr_val + prev_val
                json_dict.update({curr_row: total})
                prev_val = total
            else:
                total = 0
                json_dict.update({curr_row: total})
                prev_val = total
    except RestUtilityException as err:
        return connexion.problem(
            status=403,
            title=f"Request Exception while accessing the URL",
            detail=err.args[0],
        )
    except ResourceServiceNotAvailable as err:
        return connexion.problem(
            status=404,
            title=f"Device {kwargs['site']} not available in Grandma",
            detail=err.args[0],
        )
    except Exception as err:
        return connexion.problem(
            status=500,
            title=f"Connector exception raised while sending command to " f"{kwargs['site']}" "to Grandma",
            detail=err.args[0],
        )
    else:
        logger.info(f"Exiting Grandma module after sending the response {json_dict}")
        return json_dict


def process_csv(csv_input=None):
    cr = csv.reader(csv_input.splitlines(), delimiter=",")
    next(cr)
    return list(cr)
