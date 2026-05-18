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
import asyncio
import logging
import re
from datetime import date

# Third Party Library
import connexion
from nested_lookup import nested_lookup

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.services.itsm.aio_connector import SparkTicketService as AioSparkTicketService
from connectors.core.services.itsm.connector import SparkTicketService
from connectors.core.services.itsm.exceptions import InvalidRequest, ResourceServiceNotAvailable
from connectors.core.services.itsm.service_mapping import mapper
from connectors.core.utils.exceptions import ConnectorException
from connectors.core.utils.exceptions import ResourceServiceNotAvailable as serviceDown
from connectors.core.utils.exceptions import RestUtilityException
from connectors.core.utils.helpers import ignore_similar_conflicts_with_pattern
from connectors.webserver.plannet.tasks.read import get_interface_links, get_nes_details

current_environment: str = config.get(section="internals", key="environment").lower()

logger = logging.getLogger(__name__)


def custom_query(**kwargs) -> list:
    """
    Get Spark Service Now ticket details.

    Args:
       table: Table name
       start_date: start date to filter the records
       end_date: end date to filter the records
       filter: field needs to be searched for

    Returns:
       {}

    Raises:

    """
    try:

        db_table = (
            "task_ci"
            if kwargs["table"] == "change_request"
            else "u_cmdb_ci_circuit"
            if kwargs["table"] == "cmdb_circuit"
            else kwargs["table"]
        )
        start_date_in_epoch = kwargs.get("start_date")
        end_date_in_epoch = kwargs.get("end_date")
        ci_filter = kwargs["filter"]
        affected_cis: list = kwargs.get("ci_list", [])
        service_type: str = kwargs.get("service_type")
        hydrated_ci_list: list = get_adjacent_ci_details(affected_cis, service_type)
        affected_cis.extend(hydrated_ci_list)
        short_description = kwargs.get("shortDescription")
        ticket_number = kwargs.get("ticket_number")

        logger.info(f"Entering into ITSM module to retrieve details for table :{db_table}")
        """
        calling spark api for retrieving the details of  the ticket number using service3800
        """
        spark = SparkTicketService()
        spark_response = spark.service3800(
            db_table=f"{db_table}",
            affected_cis=affected_cis,
            ci_filter=f"{ci_filter}",
            start_date=start_date_in_epoch,
            end_date=end_date_in_epoch,
            short_description=short_description,
            ticket_number=ticket_number,
            hostname=kwargs.get("hostname"),
        )
        if service_type and short_description:
            logger.debug(f"Checking if similar change conflicts should be ignored for '{service_type}'")
            if (
                similar_change_pattern := mapper.get(service_type, {})
                .get("create", {})
                .get("extra_args", {})
                .get("similar_change_pattern", [])
            ):
                logger.debug(f"Found similar_change_pattern: '{similar_change_pattern}' for '{service_type}'")
                spark_response = ignore_similar_conflicts_with_pattern(
                    change_req_list=spark_response, pattern=similar_change_pattern
                )

        logger.info("Exiting ITSM module after sending the response")
        return spark_response

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
        return connexion.problem(status=404, title="Error in accessing Spark ticketing system", detail=err.args[0])
    except Exception as err:
        logger.exception(err)
        return connexion.problem(
            status=500, title="Connector exception raised while running custom query", detail=err.args[0]
        )


def aio_custom_query(**kwargs):
    """
    Run Asynchronous Spark Custom Query
    kwargs:
      table: Table name
      filter: fields needs to be searched for
      ci_list: Ci name or list of CIs
    Returns:
        {"results": []}
    """
    logger.info(f"Entering into ITSM module to retrieve details for table: {kwargs['table']}")
    spark_service_instance = AioSparkTicketService()
    try:
        response = asyncio.run(spark_service_instance.service3800(**kwargs))
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


def get_adjacent_ci_details(ci_list: list, service_type: str) -> list:
    """
    Call PlanNet API to get adjacent CIs. e.g. for BNG Failover use case,
    it will fetch peer & ta/pr devices
    Args:
        ci_list(list):Contains the CI List
        service_type(str):Mentions the servicetype
    Returns:
          Modified ci list
    """
    hydrated_ci_details: set = set()
    ne_details: list = []

    if service_type != "bngFailover":
        return []

    logger.info(f"Entering method to get adjacent cis for CI {ci_list} for service {service_type}")
    adjacent_host_pattern_mapper: dict = {"bngFailover": ("ta%", "pr%")}
    to_ne_names: tuple = adjacent_host_pattern_mapper.get(service_type)
    ne_names_pattern_mapper: dict = {"bngFailover": "(ta|pr)"}

    for ci in ci_list:
        nes_data: dict = get_nes_details(name=ci, limit=50, offset=0, searchLiveDate=date.today())
        logger.debug(f"nes_data for {ci} is {nes_data}")
        validate_nes_response(nes_data)
        params: dict = {"limit": 50, "offset": 0, "searchLiveDate": date.today()}
        if current_environment in ("development", "test", "stage"):
            params["parent"] = nes_data.get("results")[0].get("parent")["id"]
        else:
            params["parents"] = nes_data.get("results")[0].get("parent")["id"]
        nes_response: dict = get_nes_details(**params)
        logger.debug(f"nes_response for parent id {nes_data.get('results')[0].get('parent')['id']} is {nes_response}")
        results: list = nes_response.get("results", [])
        new_ci_list: list = [name.get("name") for name in results]
        hydrated_ci_details.update(new_ci_list)

        ne_names_list: set = set()
        for name in new_ci_list:
            intf_link_responses: list = [
                get_interface_links(
                    linkType="Ethernet Bearer",
                    date=date.today(),
                    limit=100,
                    fromHostName=name,
                    toHostName=pattern,
                    offset=0,
                )
                for pattern in to_ne_names
            ]

            for intf_link_response in intf_link_responses:
                ne_1_details: list = nested_lookup("ne_2", intf_link_response)
                ne_2_details: list = nested_lookup("ne_1", intf_link_response)
                ne_details.extend(ne_1_details)
                ne_details.extend(ne_2_details)
                ne_names_list: set = {
                    detail.get("name")
                    for detail in ne_details
                    if re.search(
                        f"^{ne_names_pattern_mapper.get(service_type)}",
                        detail.get("name"),
                    )
                }
                hydrated_ci_details.update(ne_names_list)

        logger.info(f"Adjacent CI details {hydrated_ci_details} for service {service_type}")
        if not hydrated_ci_details or not ne_names_list:
            raise ConnectorException(f"Adjacent devices not present for the device {ci}")
    return list(hydrated_ci_details)


def validate_nes_response(nes_data: dict) -> None:
    """
    Validates nes response and returns error message if connector response has error
    Args:
        nes_data(dict): nes_device_response
    Returns:
        None
    """
    for error in nes_data.get("errors", []):
        if "ResourceServiceNotAvailable" in error.get("message", ""):
            raise serviceDown("Unable to get BNG details - PlanNet is not reachable.")
        else:
            raise ConnectorException(error.get("message"))
    if not nes_data or not nes_data.get("results") or not nes_data.get("results")[0].get("parent"):
        raise ConnectorException("Unable to get BNG details")
