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
from datetime import datetime
from urllib.parse import quote

# Third Party Library
import connexion
import pytz

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.services.itsm.connector import SparkTicketService
from connectors.core.services.itsm.exceptions import (
    DataUnavailable,
    InvalidRequest,
    InvalidStateRequest,
    ResourceServiceNotAvailable,
)
from connectors.core.utils.exceptions import ConnectorException, RestUtilityException

logger = logging.getLogger(__name__)

assigned_to = config.get(section="itsm", key="assigned_to")

# Define the epoch
EPOCH = pytz.utc.localize(datetime(1970, 1, 1))
logger.debug(f"Epoch information: {EPOCH}")


def update_ticket(**kwargs: dict) -> any:  # noqa: C901
    # sourcery skip: low-code-quality
    """
    Update Spark Ticket

    Returns:
       response: JSON Schema with the ticket update details

    Raises:
      Exception

    """
    try:
        ticket = kwargs["body"]
        spark = SparkTicketService()
        logger.info(f"Entering into ITSM module to update ticket details for {ticket['ticketNumber']}")
        if (ticket["ticketNumber"]).startswith("CHG"):
            logger.debug(f"Update ticket called for Standard ticket {ticket['ticketNumber']}")
            data = {"ticket_number": ticket["ticketNumber"], "updated_by": ticket["updatedBy"]}
            if all(key not in ticket for key in ("state", "assignmentGrp", "assignedTo")):
                logger.error("One out of state or assignment group or assigned to at least is mandatory")
                # Fix for Bug DNE-2515
                raise InvalidRequest(
                    "For updating Normal tickets " "state or assignment group or assigned to is mandatory"
                )
            if ticket.get("state"):
                data["state"] = ticket["state"]
            if ticket.get("assignedTo"):
                data["assigned_to"] = ticket["assignedTo"]
            if ticket.get("assignmentGrp"):
                data["assignment_group"] = quote(ticket["assignmentGrp"])
            if ticket.get("state") == "Post Implementation Review":
                spark_response: dict = spark.service3400(
                    ticket_number=ticket["ticketNumber"],
                    return_fields=["start_date", "u_planned_start_date", "u_planned_end_date", "end_date"],
                )
                if "error_details" in spark_response["result"]:
                    raise DataUnavailable(spark_response["result"]["error_details"])
                _post_implementation_review(ticket, data, spark_response)
            if ticket.get("state", "").lower() == "closed":
                if not ticket.get("workNotes"):
                    raise InvalidRequest("Work notes is mandatory when the state is being updated to closed")
                data["work_notes"] = ticket.get("workNotes", "")
            if ticket.get("reschedule"):
                data["reschedule"] = ticket.get("reschedule")
                data["reschedule_reason"] = quote(ticket.get("rescheduleReason", ""))
                data["new_start_date"] = ticket.get("newStartDate")
                data["new_end_date"] = ticket.get("newEndDate")
            """
                calling spark api for creating the ticket number using service3402
            """
            logger.info(f"Calling service3402 from ITSM module with data : {data}")
            response = spark.service3402(**data)
            if ("error_details" or "conflict_details") in response["result"]:
                # Bug fix for DNE-2490
                raise DataUnavailable(response["result"]["error_details"] or response["result"]["conflict_details"])
            if ticket.get("workNotes") and ticket.get("state", "").lower() != "closed":
                data = {
                    "ticket_number": ticket["ticketNumber"],
                    "work_notes": quote(ticket["workNotes"]),
                    "updated_by": ticket["updatedBy"],
                }
                """
                   calling spark api for adding workNotes to the ticket number using service3050
                """
                response = spark.service3050(**data)
            logger.info("Exiting ITSM module after sending the response for Update ticket")
            return response

        logger.debug(f"Update ticket called for Minor ticket {ticket['ticketNumber']}")
        data = {
            "ticket_number": quote(ticket["ticketNumber"]),  # Bug Fix for 3156
            "updated_by": quote(ticket["updatedBy"]),  # Bug Fix for 3156
            "work_notes": quote(ticket["workNotes"]),  # Bug Fix for 3156
        }
        if ticket.get("state"):
            data.update(assigned_to=quote(ticket.get("assignedTo") or assigned_to), state=quote(ticket.get("state")))
            """
            calling spark api for creating the ticket number using service3406
            """
            logger.info(f"Updating the worknotes and state for the ticket{ticket['ticketNumber'] }")
            response = spark.service3406(**data)
        else:
            """
            calling spark api for creating the ticket number using service3050
            """
            logger.info(f"Updating the worknotes for the ticket{ticket['ticketNumber'] }")
            response = spark.service3050(**data)
        logger.info("Exiting ITSM module after sending the response")
        return response

    except DataUnavailable as err:
        logger.exception(err, exc_info=True)
        return connexion.problem(
            status=403,
            title="Error while updating the ticket state on Spark",
            detail=f"{err.args[0]}",
        )
    except InvalidRequest as err:
        logger.exception(err, exc_info=True)
        return connexion.problem(
            status=400,
            title="Error in request body",
            detail=f"{err.args[0]}",
        )
    except ResourceServiceNotAvailable as err:
        logger.exception(err)
        return connexion.problem(
            status=404,
            title="Error in accessing Spark ticketing system",
            detail=err.args[0],
        )
    except InvalidStateRequest as err:
        logger.exception(err)
        return connexion.problem(
            status=400,
            title="Invalid State transfer",
            detail=err.args[0],
        )
    except RestUtilityException as err:
        return connexion.problem(
            status=403,
            title="Request Exception while accessing the URL",
            detail=err.args[0],
        )
    except (ValueError, KeyError, TypeError) as err:
        logger.exception(err)
        return connexion.problem(
            status=400,
            title="Error in request body",
            detail=f"`{err.args[0]}` is a required property",
        )
    except Exception as err:
        logger.exception(err)
        return connexion.problem(
            status=500,
            title="Connector exception raised while creating the ticket",
            detail=err.args[0],
        )


def _post_implementation_review(ticket: dict, data: dict, spark_response: dict) -> None:
    """
    Function for Post Implementation Review ticket

    Args:
        ticket (dict)
        data (dict)

    Raises:
        InvalidRequest: If StartDate and EndDate are not in the past also,
                    EndDate is not greater than StartDate.
    """
    logger.debug("In _post_implementation_review, reviewing the ticket post implementation.")
    data["implementation_code"] = ticket["implementationCode"]
    implementation_details = ticket.get("implementationDetails")
    ticket["implementationDetails"] = (
        f"[DNE]{implementation_details}" if implementation_details else implementation_details
    )
    data["implementation_detail"] = quote(ticket["implementationDetails"])
    current_date_timestamp: int = int((datetime.now(pytz.utc) - EPOCH).total_seconds())
    logger.debug(f"Current day since epoch: {current_date_timestamp}")
    update_data_datetime(ticket, data, spark_response, current_date_timestamp)
    logger.debug("In _post_implementation_review and dateTime validation passed.")

    if data["implementation_code"].lower() == "unsuccessful":
        # Fix for bug DNE-2516, DNE-2549
        data["unsuccessful_reason"] = quote(ticket["failureDescp"])
        data["cause_of_failure"] = quote(ticket["causeOfFailure"])
        data["backed_out"] = (
            "Fully Backed Out" if str(ticket["backedOut"]).lower() == "yes" else str(ticket["backedOut"])
        )
        data["corrected_plan"] = quote(ticket["correctedPlan"])


def update_data_datetime(ticket: dict, data: dict, spark_response: dict, current_date_timestamp: int) -> None:
    """
    Validates the date and time information in the provided ticket.

    Args:
        ticket (dict): The ticket containing date and time information.
        data (dict): Additional data related to the ticket.
        spark_response (dict): The The ticket information from Spark
        current_date_timestamp (int): The timestamp representing the current date and time.
    """
    logger.debug(f"In update_data_datetime with ticket: {ticket} , data: {data} and spark_response: {spark_response}")
    bpm_start_date_timestamp: int = ticket["startDate"]
    bpm_end_date_timestamp: int = ticket["endDate"]

    if bpm_start_date_timestamp > bpm_end_date_timestamp:
        raise InvalidRequest(
            f"The EndDate ({bpm_end_date_timestamp}) should be later than the StartDate ({bpm_start_date_timestamp})."
        )

    spark_results: list = spark_response["result"]
    spark_start_date_timestamp: int = _extract_date_timestamp(spark_results, "start_date", "u_planned_start_date")
    spark_end_date_timestamp: int = _extract_date_timestamp(spark_results, "end_date", "u_planned_end_date")
    logger.debug(
        f"In update_data_datetime with BPM startDate timestamp ({bpm_start_date_timestamp}) "
        f"and Spark startDate timestamp ({spark_start_date_timestamp})"
    )
    logger.debug(
        f"In update_data_datetime with BPM endDate timestamp ({bpm_end_date_timestamp}) "
        f"and Spark endDate timestamp ({spark_end_date_timestamp})"
    )
    # Validation
    data["start_date"] = max(bpm_start_date_timestamp, spark_start_date_timestamp)
    if bpm_end_date_timestamp <= current_date_timestamp and bpm_end_date_timestamp <= spark_end_date_timestamp:
        # Adding a -2 second buffer
        data["end_date"] = bpm_end_date_timestamp - 2
        return
    data["end_date"] = min(current_date_timestamp, spark_end_date_timestamp) - 2  # Adding a -2 second buffer


def _extract_date_timestamp(spark_results: list, date: str, u_planned_date: str) -> int:
    """
    Extracts GMT timestamp from a datetime string in a Spark result set.

    Args:
        spark_results (list): A list containing Spark query results.
        date (str): The key representing the datetime value in the Spark result set.

    Returns:
        int: GMT timestamp corresponding to the given datetime string.
    """
    logger.debug(f"In _extract_date_timestamp for {date} and u_planned_date: {u_planned_date}")
    spark_date: str = spark_results[0].get(date) or spark_results[0].get(u_planned_date)
    if not spark_date:
        logger.debug(
            f"In _extract_date_timestamp with spark_date: {spark_date}; Spark {date} is not available in Spark"
        )
        if date == "start_date":
            return 0
        else:
            raise ConnectorException(f"Spark {date} is not available in Spark")
    # Convert string to datetime object
    result = datetime.strptime(spark_date, "%d/%m/%Y %H:%M:%S")
    # Convert datetime object to GMT timestamp
    return int(pytz.utc.localize(result).timestamp())
