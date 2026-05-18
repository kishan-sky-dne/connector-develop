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


def get_ticket(**kwargs):  # noqa: N802
    """
    Get Spark Service Now ticket details.

    Args:
       ticket_number: Change Ticket Number
       parentChange: optional bool type

    Returns:
       {
         "result": [
           {
             "approvalStatus": "APPROVED",
             "chgtktNumber": "CHG123456789",
             "endDate": "1572794340",
             "startDate": "1572794340"
           }
         ]
       }

    Raises:

    """
    try:
        tickets = set(kwargs["ticketNumber"])
        parent_change = kwargs.get("parentChange")
        default_fields = [
            "number",
            "state",
            "u_minor_change_state",
            "type",
            "assignment_group",
            "u_owner_group",
            "start_date",
            "u_planned_start_date",
            "u_planned_end_date",
            "end_date",
            "short_description",
        ]
        return_fields = set(default_fields + kwargs.get("return_fields", []))
        return_fields = ",".join(return_fields)

        logger.info(f"Entering into ITSM module to retrieve ticket details for :{tickets}")
        output = {"results": []}

        for ticket in tickets:
            """
            calling spark api for retrieving the details of  the ticket number using service3400
            """
            # Bug fix for DNE-2523
            state = None
            start_date = None
            end_date = None
            parent_ticket = None
            if not ticket:
                raise InvalidRequest("Mandatory key `ticket` missing from the payload")
            spark = SparkTicketService()
            spark_response = spark.service3400(ticket_number=ticket, return_fields=return_fields)

            results = spark_response["result"]
            if results and "error_details" not in results:  # Fix for Bug DNE-2481
                result = results[0]
                start_date = result.get("start_date") or result.get("u_planned_start_date")
                end_date = result.get("end_date") or result.get("u_planned_end_date")
                state = result.get("u_minor_change_state") or result.get("state")
                parent_ticket = result.get("change_request", {}).get("display_value")

            response = {
                "chgtktNumber": ticket,
                "state": state,
                "startDate": start_date,
                "endDate": end_date,
            }
            if return_fields and "u_related_ci_list" in return_fields:
                response["related_ci"] = [
                    related_ci.lstrip() for related_ci in result.get("u_related_ci_list").split(",") if related_ci
                ]
            if parent_change and "ctask" in ticket.lower():  # BUGFIX DNE-10047 applicable only for CTASK
                response["parentTicketNumber"] = parent_ticket

            output["results"].append(response)

        logger.info("Exiting ITSM module after sending the response")
        return output

    except (ValueError, KeyError, TypeError) as err:
        logger.exception(err)
        return connexion.problem(
            status=404, title="Error in response from Spark or ticket not found", detail=err.args[0]
        )
    except InvalidRequest as err:
        logger.exception(err)
        return connexion.problem(status=400, title="Error in request for ticket details", detail=err.args[0])
    except RestUtilityException as err:
        return connexion.problem(
            status=403,
            title="Request Exception while accessing the URL",
            detail=err.args[0],
        )
    except ResourceServiceNotAvailable as err:
        logger.exception(err)
        return connexion.problem(status=404, title="Error in accessing Spark ticketing system", detail=err.args[0])
    except Exception as err:
        logger.exception(err)
        return connexion.problem(
            status=500, title="Connector exception raised while creating the ticket", detail=err.args[0]
        )
