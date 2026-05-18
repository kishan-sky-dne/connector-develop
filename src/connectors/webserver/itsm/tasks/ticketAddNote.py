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
from urllib.parse import quote

# Third Party Library
import connexion

# Sky Library
from isp_config import ConfigManagerException

# DNE Library
from connectors.core.config import connectors_config
from connectors.core.services.itsm.connector import SparkTicketService
from connectors.core.services.itsm.exceptions import InvalidRequest, ResourceServiceNotAvailable
from connectors.core.services.mailer.exceptions import TemplateDesignerException, TemplateNotFoundException
from connectors.core.services.mailer.templateDesigner import EmailTemplateDesigner
from connectors.core.utils.exceptions import RestUtilityException

logger = logging.getLogger(__name__)

try:
    config = connectors_config.ConnectorsConfigManager()
    config.load_config()
except ConfigManagerException:
    sys.exit(1)

updated_by = config.get(section="itsm", key="updated_by")
template_category = config.get(section="itsm", key="template_category")


def add_note(**kwargs):  # noqa: C901
    """
    Creates Spark Service Now to Add Worknotes

    Args:
       body = {
                 "chgtktNumber": "CHG123456789",
                 "workNotes": "This is 1st note",
                 "comments": "This is a comment"
                 "templatedWorkNote": {
                    "templateName": "metroLink",
                    "serviceName": "Metro Link",
                    "templateAttributes": [
                        {
                            "aEnd": "ma0.stage-uk.bllab",
                            "bEnd": "ta0.stage-uk.bllab",
                            "circuitId": "OGHP00806240",
                            "status": "Provisioned"
                        }
                    ]
                 }
              }
    Returns:
             {
                "status": "success"
             }

    Raises:

    """
    try:
        ticket = kwargs["body"]
        logger.info(f"Entering into ITSM module to add worknotes for ticket :{ticket['chgtktNumber']}")
        logger.debug(f"Request body sent for the creation of ticket: {ticket}")
        ticket_number = ticket["chgtktNumber"]
        spark = SparkTicketService()

        if "templatedWorkNote" in ticket and "workNotes" not in ticket:
            logger.info(f"Entering into ITSM module to add templated work notes")
            work_note = add_templated_note(ticket["templatedWorkNote"], template_category)

        elif "workNotes" not in ticket:
            logger.info(f"workNotes or templatedWorkNote none of the attributes are present.")
            raise InvalidRequest(
                f"workNotes or templatedWorkNote none of the attributes are present. "
                f"At least one of them is required."
            )
        else:
            work_note = list([quote(ticket["workNotes"])])

        for i, note in enumerate(work_note):
            logger.info(
                f"Proceed to prepare the schedule as per the inputs from request body, ticket_number: {ticket_number},"
                f" operationBy: {updated_by} & worknote: {note} "
            )  # noqa: E123

            data = {"ticket_number": ticket_number, "work_notes": note, "updated_by": updated_by}  # noqa: E123
            if kwargs.get("comments"):
                data.update({"comments": quote(kwargs["comments"])})
            logger.debug(f"Hydration completed successfully and payload to be sent to SPARK is {data}")

            """
            calling spark api for adding Worknote to the ticket number using service3050
            """

            spark_response = spark.service3050(**data)
            result = spark_response["result"]  # KeyError exception implemented in service3050 function
            logger.info(f"Response from spark service 3050 is {result}")
            if result:
                # Bug fix for DNE-2578
                if "error_details" in result:
                    raise InvalidRequest(f"Ticket {ticket_number} is invalid")
                response = {"status": result.get("details")}
                if i == len(work_note) - 1:  # Fix for DNE-5488
                    logger.info("Exiting ITSM module after sending the response")
                    return response

    except InvalidRequest as err:
        logger.exception(err)
        return connexion.problem(
            status=400,
            title=f"Error in request body",
            detail=f"{err.args[0]}",
        )
    except TemplateNotFoundException as err:
        logger.exception(err)
        return connexion.problem(
            status=404,
            title=f"Template not found",
            detail=err.args[0],
        )
    except TemplateDesignerException as err:
        logger.exception(err)
        return connexion.problem(
            status=400,
            title=f"Error in preparing the design template for J2:",
            detail=err.args[0],
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
            title=f"Error while adding Worknotes on Spark",
            detail=f"Problems with `{err.args[0]}`" f" key",
        )
        # noqa: E123
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
            title=f"Connector exception raised while adding the Worknote",
            detail=err.args[0],
        )


def split_data(data, max_limit):
    """
    Logically splits the URL encoded work notes data
    as Spark Proxy API restricts to 4000 characters of worknote

    Args:
        data = URL encoded data
        max_limit = 4000

    Returns:
        lst = ["data1", "data2", ..]

    """
    lst = []
    if max_limit <= len(data):
        data_slice = data[:max_limit]
        last_line = data_slice.split("%0A")[-1]
        mod_limit = max_limit - len(last_line) if last_line else max_limit
        lst.extend([data[:mod_limit]])
        lst.extend(split_data(data[mod_limit:], max_limit))
    elif len(data) > 0:
        lst.extend([data])
    return lst


def add_templated_note(templated_work_note, itsm_template_category):
    """
    Formats received templatedWorkNote data as per TemplateName

    Args:
        "templated_work_note = {
                                    "templateName": "metroLink",
                                    "serviceName": "Metro Link",
                                    "templateAttributes": [
                                        {
                                            "aEnd": "ma0.stage-uk.bllab",
                                            "bEnd": "ta0.stage-uk.bllab",
                                            "circuitId": "OGHP00806240",
                                            "status": "Provisioned"
                                        }
                                    ]
                                }
        itsm_template_category = list of templates supported
    Returns:
        list of logically divided URL encoded work note data

    """

    category = list(set(itsm_template_category.split(",")))

    logger.info(f"Supported Categories: {category}")

    if templated_work_note["templateName"].strip() not in category:
        raise InvalidRequest(
            f"Given template is not supported by DNE team currently "
            f"Please raise a request for templateName: {templated_work_note['templateName']} "
            f"as the supported templates are {itsm_template_category}. "
        )

    for line in templated_work_note["templateAttributes"]:
        if "circuitId" in line and "bEnd" not in line:
            logger.debug(f"Required bEnd attribute missing in Line detail {line}")
            raise InvalidRequest(f"Required bEnd attribute missing in Line Detail {line}")

    logger.info(f"Proceed to prepare content using Jinja template {templated_work_note['templateName']}")
    work_note_template = EmailTemplateDesigner()
    """   Calling Jinja template to render templated work note """
    templated_work_notes = (
        work_note_template.design("j2", templated_work_note["templateName"], "en", templated_work_note) + "\n"
    )

    logger.debug(f"Logically split the templated Work note data")
    try:
        return split_data(quote(templated_work_notes), 4000)

    except RecursionError as err:
        logger.exception(err)
        return connexion.problem(  # noqa: E123
            status=500,
            title=f"Connector exception raised while adding the Worknote",
            detail=err.args[0],
        )
