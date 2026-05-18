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
import base64
import logging

# Third Party Library
import connexion

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.services.itsm.connector import SparkTicketService
from connectors.core.services.itsm.exceptions import (
    DataUnavailable,
    InvalidRequest,
    ResourceServiceNotAvailable,
    SizeLimitExceeded,
)
from connectors.core.utils.exceptions import RestUtilityException

logger = logging.getLogger(__name__)

operation_by = config.get(section="itsm", key="updated_by")
supported_types = config.get(section="itsm", key="supported_types")


def attachment_upload(**kwargs):  # noqa: C901
    """
    Creates Spark Service Now Add/Remove attachment

    Args:
       body = {
                 "ticketNumber": "CTASK0042685",
                 "fileName": "log.txt",
                 "attachment": "InNob3dydW5uaW5nY2",
                 "operation": "add/remove/list"
              }
    Returns:
             {
                "ticketNumber": "CTASK0042685",
                "status": "SUCCESSFUL"
             }

    Raises:

    """
    try:
        ticket = kwargs["body"]
        logger.info(f"Entering into ITSM module to add/remove the attachment for ticket :{ticket['ticketNumber']}")
        logger.debug(f"Request body sent for the creation of ticket: {ticket}")
        filename = ticket["fileName"]
        operation = ticket["operation"]
        ticket_number = ticket["ticketNumber"]
        if operation == "add":
            # Fix for Bug DNE-2584
            if "attachment" not in kwargs:
                logger.error(f"Provided request body does not have an attachment")
                raise InvalidRequest(f"'attachment' is a required property")
            input_file = connexion.request.files.to_dict()
            file_attachment = input_file.get("attachment")
            if file_attachment.content_type not in supported_types:
                # Bug fix for DNE-2582
                logger.error(f"Provided attachment types are not valid")
                return connexion.problem(
                    status=415,
                    title=f"Supported types are {supported_types}",
                    detail=f"{file_attachment.content_type}" f" is not supported",
                )
            attachment = connexion.request.files.get("attachment")
        else:
            attachment = None

        logger.info(
            f"Proceed to prepare the schedule as per the inputs from request body, ticket_number: {ticket_number} , "
            f"Operation: {operation}, operationBy: {operation_by} & filename: {filename} "
        )  # noqa: E123

        data = {
            "ticket_number": ticket_number,
            "filename": filename,
            "operation_by": operation_by,
            "operation": operation,
            "attachment": str(base64.urlsafe_b64encode(attachment.read()), "utf-8").rstrip("=")
            if attachment is not None
            else attachment,  # Fix for Bug DNE-2478
        }  # noqa: E123

        logger.debug(f"Hydration completed successfully and payload to be sent to SPARK is {data}")

        """
        calling spark api for creating the ticket number using service3405
        """

        spark = SparkTicketService()
        spark_response = spark.service3045(**data)
        try:
            result = spark_response["result"]
        except KeyError as err:
            raise ResourceServiceNotAvailable(
                f"Error while getting response from Spark, missing `result` key in " f"payload: {err.args[0]}"
            )  # noqa: E123

        if result:
            # Bug fix for DNE-2585, DNE-2586
            if "error_details" in result:
                raise DataUnavailable(result["error_details"])
            ticket_number = result.get("details").split()[0]
            response = {"status": result.get("details"), "ticketNumber": ticket_number}  # noqa: E123
            logger.info("Exiting ITSM module after sending the response")
            return response
    #  Fix for Bug DNE-2584
    except InvalidRequest as err:
        logger.exception(err, exc_info=True)
        return connexion.problem(
            status=400,
            title=f"Error in request body",
            detail=f"{err.args[0]}",
        )
    except RestUtilityException as err:
        return connexion.problem(
            status=403,
            title=f"Request Exception while accessing the URL",
            detail=err.args[0],
        )
    except ResourceServiceNotAvailable as err:
        return connexion.problem(  # noqa: E123
            status=404,
            title=f"Error while add/remove attachment on Spark",
            detail=f"Problems with `{err.args[0]}`" f" key",
        )  # noqa: E123
    # Fix for BUG DNE-2585
    except DataUnavailable as err:
        logger.exception(err, exc_info=True)
        return connexion.problem(  # noqa: E123
            status=403,
            title=f"Error while add/remove attachment on Spark",
            detail=f"{err.args[0]}",
        )  # noqa: E123
    # Fix for BUG DNE-2588
    except SizeLimitExceeded as err:
        logger.exception(err, exc_info=True)
        return connexion.problem(  # noqa: E123
            status=422,
            title=f"Error while add/remove attachment on Spark",
            detail=f"{err.args[0]}",
        )  # noqa: E123
    except (ValueError, KeyError, TypeError) as err:
        logger.exception(err)
        return connexion.problem(  # noqa: E123
            status=404,
            title=f"Error in request body",
            detail=f"Problems with `{err.args[0]}` key",
        )  # noqa: E123
    except Exception as err:
        logger.exception(err)
        return connexion.problem(  # noqa: E123
            status=500,
            title=f"Connector exception raised while creating the ticket",
            detail=err.args[0],
        )
