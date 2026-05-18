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
from connectors.core.services.itsm.connector import SparkTicketService
from connectors.core.services.itsm.exceptions import InvalidRequest, ResourceServiceNotAvailable
from connectors.core.utils.exceptions import RestUtilityException

logger = logging.getLogger(__name__)


def attachment_list(**kwargs):  # noqa: C901
    """
    Creates Spark Service Now List attachment

    Args:
       ticket_number: Change Ticket Number

    Returns:
       {
         "result": [
           {
             "fileName": "precheck.txt",
             "state": "available",
             "createdOn": "2020-05-22 23:42:32",
             "updatedOn": "2020-05-22 23:42:32"
           }
         ]
       }

    Raises:

    """
    try:
        ticket_number = kwargs["ticketNumber"]
        logger.info(f"Entering into ITSM module to list the attachment for ticket :{ticket_number}")
        # Bug fix for DNE-2579
        if not ticket_number:
            raise InvalidRequest("'ticketNumber' is a required property")

        """
        calling spark api for creating the ticket number using service3405
        """

        spark = SparkTicketService()
        spark_response = spark.service3045(ticket_number=ticket_number, operation="list")
        try:
            results = spark_response["result"]
        except KeyError as err:
            raise ResourceServiceNotAvailable(
                f"Error while getting response from Spark, missing `result` key in " f"payload: {err.args[0]}"
            )  # noqa: E123

        output = {"results": []}

        # Bug fix for DNE-2579
        if "error_details" in results:
            raise InvalidRequest(f"Ticket {ticket_number} is invalid")
        for result in results:
            response = {
                "fileName": result.get("file_name"),
                "createdOn": result.get("sys_created_on"),
                "updatedOn": result.get("sys_updated_on"),
                "state": result.get("state"),
            }
            output["results"].append(response)
        logger.info("Exiting ITSM module after sending the response")
        return output
    except InvalidRequest as err:
        logger.exception(err)
        return connexion.problem(
            status=400,
            title=f"Error in request body",
            detail=f"{err.args[0]}",
        )
    except (ValueError, KeyError, TypeError) as err:
        logger.exception(err)
        return connexion.problem(
            status=404, title=f"Error in response from Spark or ticket not found", detail=err.args[0]
        )
    except RestUtilityException as err:
        return connexion.problem(
            status=403,
            title=f"Request Exception while accessing the URL",
            detail=err.args[0],
        )
    except ResourceServiceNotAvailable as err:
        logger.exception(err)
        return connexion.problem(status=404, title=f"Error in accessing Spark ticketing system", detail=err.args[0])
    except Exception as err:
        logger.exception(err)
        return connexion.problem(
            status=500, title=f"Connector exception raised while creating the ticket", detail=err.args[0]
        )
