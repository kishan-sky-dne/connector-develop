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
import math
import re
import sys
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import quote

# Third Party Library
import connexion
import pytz
from connexion.lifecycle import ConnexionResponse

# Sky Library
from isp_config import ConfigManagerException

# DNE Library
from connectors.core.config import connectors_config
from connectors.core.exceptions import ServiceDBException
from connectors.core.services.custom.connector import CustomService
from connectors.core.services.itsm.conflictResolver import Resolver
from connectors.core.services.itsm.connector import SparkTicketService
from connectors.core.services.itsm.customValidator import DateConverter
from connectors.core.services.itsm.exceptions import (
    DateGeneratorError,
    DateValidateError,
    InvalidRequest,
    ResourceServiceNotAvailable,
)
from connectors.core.services.itsm.service_mapping import mapper
from connectors.core.services.mailer.exceptions import TemplateDesignerException, TemplateNotFoundException
from connectors.core.services.mailer.templateDesigner import EmailTemplateDesigner
from connectors.core.utils.exceptions import RestUtilityException
from connectors.core.utils.helpers import ignore_similar_conflicts_with_pattern
from connectors.core.utils.serviceDB import ServiceDB
from connectors.webserver.custom.tasks.read import getGrandmaData, getTmaData
from connectors.webserver.itsm.tasks.genericQueryFilter import custom_query, get_adjacent_ci_details
from connectors.webserver.mailer.tasks.sender import email_notifications
from connectors.webserver.plannet.tasks.read import get_circuit_types, get_cis_details, get_interface_links

logger = logging.getLogger(__name__)

try:
    config = connectors_config.ConnectorsConfigManager()
    config.load_config()
except ConfigManagerException:
    sys.exit(1)

external_url = config.get(section="external", key="url")  # Bug fix for 3644
check_duration = config.get(section="itsm", key="check_duration")
attachment_limit = int(config.get(section="itsm", key="ticket_creation_attachment_limit"))
attachment_size_limit = int(config.get(section="itsm", key="ticket_creation_attachment_size_limit"))
max_attachment_size_mb = round(int(attachment_size_limit) / (1024 * 1024), 2)
impact_type_precedence = config.get(section="itsm", key="impact_type_precedence")
third_party_impact_str = config.get(section="itsm", key="third_party_impact")
current_environment = config.get(section="internals", key="environment").lower()
pop_site_list = config.get(section="itsm", key="pop_site_list").split(",")
assigned_to = config.get(section="itsm", key="assigned_to")

timezone = pytz.timezone("Europe/London")
epoch = (
    datetime(1970, 1, 1, 1, 0, 0) if timezone.localize(datetime.now()).dst() else datetime(1970, 1, 1)
)  # Adding 1 hour to handle default epoch in BST
today = (datetime.now() - epoch).total_seconds()

spark = SparkTicketService()
resolver = Resolver()
converter = DateConverter()
tp_mapper = {
    "change": {
        "type": "TPCHG",
        "valid_impact": [
            "Full outage to service",
            "Intermittent service outages",
            "Reduced capacity",
            "Reduced resiliency",
        ],
        "valid_reason": [
            "Delivering new capability",
            "Equipment replacement-fixing faulty equipment",
            "Increasing capacity-bandwidth",
            "Increasing capacity-infrastructure",
            "Maintenance-Sky network Upgrade",
            "Maintenance-Sky work",
            "Maintenance-Third party work",
            "Repair-fix following an incident",
        ],
    }
}
chg_services_without_wait_time = [
    "quattroPrefixSets",
    "serviceIncident",
    "mapTprovisioning",
    "mapTupdate",
    "retrofit",
    "openreachretest",
    "geaOpenReachTest",
    "geaProvisioningV2",
    "maptDelete",
    "portshutunshut",
    "wholesaleEth2",
    "routeServerMappingUpdate",
]  # Fix for Bug DNE-16996
# Added 'portshutunshut' and 'wholesaleEth2' as services that do not require 1 wait day for change window to start

notify_change_window = "notifyChangeWindow"

# MongoDB collection storing default change creation attributes by order type/subtype
itsm_change_creation_db = "itsm_change_creation_data"
misc_collection_db = "misc_collection"


def get_itsm_tagging_types() -> list[str]:
    """Return order types that are opted into the new ITSM tagging behaviour."""
    try:
        logger.info("Loading ITSM tagging configuration from MongoDB")
        collection_ref = ServiceDB(misc_collection_db)
        record = collection_ref.find_one({"service": "itsm_tagging"})
        return record.get("itsm_new_tagging_ordertypes", []) if record else []
    except Exception as err:
        logger.info(
            "Skipping MongoDB-driven ITSM defaults because ServiceDB isn't available (%s)",
            err.args[0] if getattr(err, "args", None) else str(err),
        )
        return []


def _get_change_creation_config(order_type: str) -> dict | None:
    """Fetch change creation config from MongoDB (cached)."""
    try:
        collection_ref = ServiceDB(itsm_change_creation_db)
        return collection_ref.find_one({"orderType": order_type})
    except Exception as err:
        logger.info(
            "Unable to retrieve change creation defaults for orderType=%s due to %s",
            order_type,
            err.args[0] if err.args else str(err),
        )
        return None


def _apply_change_creation_defaults_from_db(ticket: dict) -> None:
    """Hydrate change creation fields from MongoDB based on orderType/orderSubType.

    DB lookup key:
    - orderType comes from ticket['orderType'] (preferred) or ticket['serviceType'].

    DB schema (supported):
    {
        'orderType': '...',
        'default': {'templateName': '...', 'shortDescription': '...', 'tag': '[TAG]'},
        'orderSubType': {'sub': {... overrides ...}}
    }

    Only sets fields that are missing in the ticket payload.
    """
    order_type = (ticket.get("serviceType") or "").strip()
    order_sub_type = (ticket.get("orderSubType") or "").strip()

    db_record = _get_change_creation_config(order_type)
    if not db_record:
        logger.debug("No DB config found for orderType=%s", order_type)
        return

    # base config
    config = db_record.get("default", {}).copy()  # copy to avoid mutating cached config

    # subtype override
    if subtype_cfg := db_record.get("orderSubType", {}).get(order_sub_type, {}):
        logger.debug(
            "Applying subtype override orderType=%s orderSubType=%s",
            order_type,
            order_sub_type,
        )
        config.update(subtype_cfg)

    if not config:
        return

    if template := config.get("templateName"):
        ticket["templateName"] = template
    # shortDescription tagging
    default_db_short_desc = (config.get("shortDescription") or "").strip()
    db_tag = (config.get("tag") or "").strip()

    if not default_db_short_desc or not db_tag:
        return

    if default_db_short_desc.startswith("[DNE]"):
        ticket["shortDescription"] = default_db_short_desc.replace("[DNE]", db_tag)
    else:
        ticket["shortDescription"] = f"{db_tag} {default_db_short_desc}"
    logger.info(
        "Applied DB defaults for orderType=%s orderSubType=%s shortDescription=%s",
        order_type,
        order_sub_type,
        ticket["shortDescription"],
    )


def check_valid_attachments(attachment_list):
    logger.info(f"Check for number of files in attachment and the max allowed size for attachments ")
    if len(attachment_list) > attachment_limit:
        logger.error(
            f"Attachments exceed the configured count limit - current count "
            f"is {len(attachment_list)} which exceeds set limit of "
            f"{attachment_limit}"
        )
        raise InvalidRequest(
            f"Problem with no of attachments, current count is {len(attachment_list)} "
            f"and which exceeds the set limit of {attachment_limit}"
        )
    logger.info(f"Check for files attachment aggregate size with the configured max allowed size")
    total_file_size = 0
    for attachment in attachment_list:
        file_content_size = sys.getsizeof(attachment["fileContent"])
        total_file_size += file_content_size
    if total_file_size > attachment_size_limit:
        # Fix for Bug DNE-2575
        total_file_size_mb = round(int(total_file_size) / (1024 * 1024), 2)
        logger.error(
            f"Attachments exceeds the configured size limit - attachments size "
            f"is {total_file_size_mb}MB which exceeds the set limit of {max_attachment_size_mb}MB"
        )
        raise InvalidRequest(
            f"Problem with total size of attachments in `attachmentList` key, attachments size is "
            f"{total_file_size_mb}MB which exceeds the set limit of {max_attachment_size_mb}MB"
        )


def get_plannet_cid(**kwargs):
    # sourcery skip: low-code-quality
    oghp_cid = []
    wholesale_cid = []
    other_cid = []
    oghp_cids = []
    wholesale_cids = []
    wholesale_ifnl_cids = []
    other_cids = []
    oghp_cis = []
    wholesale_cis = []
    other_cis = []
    circuit_type_mapper = {
        "wholesale": ["Wholesale Access"],
        "ogcp": ["GEA cablelink"],
        "other": ["DSLAM", "ISAM-B", "ISAM-V", "MSAN", "Stinger"],
    }

    ticket = kwargs["ticket"]
    circuit_types = get_circuit_types(limit=100, offset=0)

    for result in circuit_types.get("results", []):
        if result["name"] in circuit_type_mapper["wholesale"]:
            wholesale_cid.extend([str(result["id"])])
        elif result["name"] in circuit_type_mapper["ogcp"]:
            oghp_cid.extend([str(result["id"])])
        elif result["name"] in circuit_type_mapper["other"]:
            other_cid.extend([str(result["id"])])

    logger.info(f"Wholesale: {wholesale_cid}, OGHP: {oghp_cid}, Others: {other_cid}")

    filtered_cis = [
        host["ciName"] for host in ticket.get("affectedCIs") if re.search(r"^(as|ma|me)(\d+\.)", host["ciName"])
    ]

    immediate_ci_as = []
    for ci in filtered_cis:
        circuit_link = get_interface_links(linkType="Ethernet Bearer", onHostName=ci, limit=100, offset=0)
        for link in circuit_link.get("results", []):
            if link["circuit"] and re.search("^as", link["ne_2"]["name"]):
                immediate_ci_as.append(link["ne_2"]["name"])
            elif link["circuit"]:
                oghp_cids.extend(
                    [
                        {"ciName": link["circuit"]["cid"], "impactType": "Full Outage"}
                        for item in oghp_cid
                        if item in link["circuit"]["type"]
                    ]
                )
                oghp_cis.extend([link["circuit"]["cid"] for item in oghp_cid if item in link["circuit"]["type"]])
                wholesale_cids.extend(
                    [
                        {"ciName": link["circuit"]["cid"], "impactType": "Full Outage"}
                        for item in wholesale_cid
                        if item in link["circuit"]["type"] and not link["circuit"]["cid"].startswith("EBCL")
                    ]
                )
                wholesale_cis.extend(
                    [link["circuit"]["cid"] for item in wholesale_cid if item in link["circuit"]["type"]]
                )
                wholesale_ifnl_cids.extend(
                    [
                        {
                            "ciName": link["circuit"]["cid"].split("-")[0]
                            + "/"
                            + link["circuit"].get("parent_ref", ""),
                            "impactType": "Full Outage",
                        }
                        for item in wholesale_cid
                        if (item in link["circuit"]["type"])
                        and link["circuit"]["cid"].startswith("EBCL")
                        and link["circuit"]["parent_ref"]
                    ]
                )

                # wholesale_ifnl_cis.extend(
                #     [link["circuit"]["cid"] for item in wholesale_ifnl_cid if item in link["circuit"]["type"]]
                # )
                other_cids.extend(
                    [
                        {"ciName": link["ne_2"]["name"], "impactType": "Full Outage"}
                        for item in other_cid
                        if item in link["circuit"]["type"]
                    ]
                )
                other_cis.extend([link["ne_2"]["name"] for item in other_cid if item in link["circuit"]["type"]])

    wholesale_cids.extend(wholesale_ifnl_cids)
    uniq_immediate_as_cis = list(set(immediate_ci_as) - set(filtered_cis))
    for ci in uniq_immediate_as_cis:
        circuit_link = get_interface_links(linkType="Ethernet Bearer", onHostName=ci, limit=100, offset=0)
        for link in circuit_link["results"]:
            if link["circuit"]:
                other_cids.extend([{"ciName": link["ne_2"]["name"], "impactType": "Full Outage"}])
                other_cis.extend([link["ne_2"]["name"]])

    # Calling TMA to add the devics which is missed from Plannet as workaround
    logger.info(f"Exchange to be called TMA Spark Helper are {list(set(kwargs['exchanges']))}")
    input_tma_cis = {"sparkid": kwargs["ticket_number"], "txproc": "false"}
    custom_obj = CustomService()
    tma_cis_list = []
    exchanges_without_pop = list(set(kwargs["exchanges"]) - set(pop_site_list))
    logger.info(f"Exchanges without pop {exchanges_without_pop}")

    for exchange_itr in exchanges_without_pop:
        input_tma_cis["tmael"] = exchange_itr
    output_tma_cis = custom_obj.post_tma_cis_from_sparkid(**input_tma_cis)
    tma_cis_list = list(output_tma_cis["devs"].keys())
    logger.info(f"CIs from TMA Spark Helper: {tma_cis_list}")

    # Removing Duplicate CIDs to reduce the Spark Calls while attaching CIs

    uniq_oghp_cids = [dict(i) for i in {tuple(ids.items()) for ids in oghp_cids}]
    uniq_wholesale_cids = [dict(i) for i in {tuple(ids.items()) for ids in wholesale_cids}]
    uniq_other_cids = [dict(i) for i in {tuple(ids.items()) for ids in other_cids}]

    final_plannet_cis = wholesale_cis + oghp_cis + other_cis
    logger.info(f"Consolidated Plannet CIDs: {final_plannet_cis}")
    missing_ci = list(set(tma_cis_list) - set(final_plannet_cis))
    missing_cis = [{"ciName": item, "impactType": "Full Outage"} for item in missing_ci]
    logger.info(
        f"Wholesale CIDs: {uniq_wholesale_cids}, OGHP CIDs: {uniq_oghp_cids}, Other CIDs: {uniq_other_cids},"
        f"Missing CIs: {missing_cis}"
    )

    # Sorting the results to ensure UT always pass
    return (
        sorted(uniq_oghp_cids, key=lambda i: i["ciName"]),
        sorted(uniq_wholesale_cids, key=lambda i: i["ciName"]),
        sorted(uniq_other_cids, key=lambda i: i["ciName"]),
        missing_cis,
    )  # noqa: E251, E501


def create_standard_ticket(**kwargs: dict) -> any:  # noqa: C901 # sourcery skip
    """
    Creates Spark Service Now Standard Change

    Args:
       body = {
               "affectedCIs": [{
                   "ciName": "ma0.test.bllab.it.bb.sky.com",
                   "impactType": "No Service Impact"
               }],
               "changeType": "normal",
               "createdBy": "vsh18",
               "endDate": 1572794340,
               "shortDescription": "12345",
               "startDate": 1572794340,
               "templateName" : "UK: IPND - STD2371 - CORE Plug-up and Circuit test (IP T&D)",
               "attachments": [
               {
               "fileName": "NIP.doc",
               "fileContent": "base64 encoded"
               },
               {
               "fileName": "PatchingRequest.xls",
               "fileContent": "base64 encoded"
               }
               ],
               "reScheduledInfo": {
               "prevTktNumber": "CHG0092700",
               "justification": "Reasons for previous failure"
               }
           }

    Returns:
       {
         "endDate": "1572794340",
         "startDate": "1572794340",
         "status": "CREATED",
         "ticketNumber": "CHG123456789"
       }

    """
    try:
        ticket = kwargs["body"]

        tagging_service_types = get_itsm_tagging_types()
        if ticket.get("serviceType") in tagging_service_types:
            _apply_change_creation_defaults_from_db(ticket)

        offset = ticket.get("offset", 0)
        affected_ci_list = []
        cmdbci = []
        final_affected_ci_list = []
        wholesale = []
        result_ci = None
        justification = ticket.get("justification", "")
        implementation_plan = ticket.get("implementationPlan", "")
        logger.info(f"Entering into ITSM module for normal/standard ticket creation with ticket :{ticket}")
        is_dummy = ticket.get("isDummy")
        is_change_on_holiday = ticket.get("isChgOnHoliday", False)
        is_change_on_freeze = ticket.get("isChgOnFreeze", False)
        skip_conflict = ticket.get("skipConflict", False)

        change_freeze_response = []
        if ticket.get("attachments"):
            check_valid_attachments(ticket["attachments"])
        try:
            service_map = mapper[ticket["serviceType"]]["create"]
        except KeyError as err:
            raise ResourceServiceNotAvailable(
                f"Standard ticket creation not supported for the service {ticket['serviceType']}: {err.args[0]}"
            )
        config_group = service_map["config_group"]
        similar_change_pattern = service_map.get("extra_args", {}).get("similar_change_pattern", [])
        start_date = ticket["startDate"]
        end_date = ticket["endDate"]
        logger.info(
            f"Proceed to prepare the schedule as per the inputs from request body, StartDate: {start_date} , "
            f"EndDate: {end_date}"
        )  # noqa: E123
        start_date_in_epoch, end_date_in_epoch = start_date, end_date
        if (start_date >= (datetime.today() - epoch).total_seconds()) and (start_date < end_date):  # noqa: E226
            # Change window unit is hours & wait time unit is No of Days
            change_window = round(end_date_in_epoch - start_date_in_epoch) / (60 * 60)  # noqa: E226
            date_today = datetime.today().date()
            date_start = (
                datetime.fromtimestamp(start_date_in_epoch).date()
                if timezone.localize(datetime.fromtimestamp(start_date_in_epoch)).dst()
                else datetime.utcfromtimestamp(start_date_in_epoch).date()
            )
            start_date_midnight = (date_start - epoch.date()).total_seconds()
            start_date_offset = (start_date_in_epoch - start_date_midnight) / (60 * 60)
            offset += start_date_offset
            logger.info(
                f"Offset with {timezone.localize(datetime.fromtimestamp(start_date_in_epoch)).dst()} : {offset}"
            )
            wait_time = (date_start - date_today).days
            if not wait_time and ticket["serviceType"] not in chg_services_without_wait_time:
                wait_time += 1
        else:
            logger.error(
                f"Start Date {start_date_in_epoch} is a past time compared today {today} or "
                f"Start Date is greater than End Date"
            )
            raise InvalidRequest(f"Either Start Date is in past or Start Date is greater than End Date")
        start_date_in_epoch, end_date_in_epoch = converter.convert(
            change_window_duration=change_window,
            days_to_wait=wait_time,
            offset=offset,
            is_change_on_holiday=is_change_on_holiday,
        )  # noqa: E123
        total_duration = (end_date_in_epoch - start_date_in_epoch) / (60 * 60 * 24)
        if int(total_duration) > int(check_duration) * 7:
            logger.error(f"End date does not fall under max configured date {total_duration}")
            raise InvalidRequest(
                f"Change duration start date and end date are not falling under " f"{check_duration} weeks"
            )
        """
        checking if any open changes exist for CIs
        """

        affected_ci_list = [hostname for hostname in ticket["affectedCIs"]]
        if not is_dummy:
            cmdbci = [hostname["ciName"] for hostname in ticket["affectedCIs"]]
            interim_start_date = (
                datetime.fromtimestamp(start_date_in_epoch)
                if timezone.localize(datetime.fromtimestamp(start_date_in_epoch)).dst()
                else datetime.utcfromtimestamp(start_date_in_epoch)
            )
            interim_end_date = interim_start_date + timedelta(weeks=int(check_duration))
            slot_end_date_in_epoch = int((interim_end_date - epoch).total_seconds())

            final_change_req_list = []
            if not skip_conflict:
                logger.info(f"Retrieving any open changes exists for {cmdbci}")

                chunk_size = 25  # Fix for Bug DNE-41292
                cmdbci_temp = [hostname["ciName"] for hostname in ticket["affectedCIs"]]

                ci_lists_temp = split_ci_list(cmdbci_temp, chunk_size)
                for ci in ci_lists_temp:  # Fix for Bug DNE-18911
                    change_req_list = spark.service3800(
                        db_table="task_ci",
                        affected_cis=ci,
                        ci_filter="ci_item",
                        start_date=start_date_in_epoch,
                        end_date=slot_end_date_in_epoch,
                        short_description=True,
                        short_description_value=str(ticket.get("shortDescription", "")),
                    )

                    if similar_change_pattern:
                        change_req_list = ignore_similar_conflicts_with_pattern(
                            change_req_list=change_req_list, pattern=similar_change_pattern
                        )
                    final_change_req_list.extend(change_req_list)

                logger.info(f"Retrieved {len(final_change_req_list)} open changes completed successfully")
                logger.debug(f"Retrieved {final_change_req_list} open changes completed successfully")
            else:
                logger.info(f"Open changes are not checked as skip_conflict flag is True")

            """
                checking conflicts for the given start and end date
            """
            logger.info(
                f"Checking if any change restrictions exists for {start_date_in_epoch} & {slot_end_date_in_epoch}"
            )
            if not is_change_on_freeze:
                change_freeze_response = spark.service3020(
                    start_date=start_date_in_epoch, end_date=slot_end_date_in_epoch
                )
            logger.info(f"change_freeze_response {change_freeze_response}")
            change_freeze_list = []
            if change_freeze_response:
                if "ITA" in config_group:  # Fix as part of Regression Testing - DNE-11250
                    config_group = "".join(config_group.split("-")[:2]).strip().replace("  ", " ")
                for index, change_freeze in enumerate(change_freeze_response):  # Fix as part of Metro
                    if config_group in change_freeze["condition"]:
                        change_freeze_list.append(change_freeze)
            logger.info(f"Checks for change restrictions completed successfully with {len(change_freeze_list)}")
            logger.info(f"change_freeze_list {change_freeze_list}")
            if final_change_req_list or change_freeze_list:
                status, start_date_in_epoch, end_date_in_epoch = resolver.standard_find_time_slot(
                    change_request=final_change_req_list,
                    start_date=start_date_in_epoch,
                    change_window=change_window,
                    change_freeze=change_freeze_list,
                    slot_end_date=slot_end_date_in_epoch,
                    is_change_on_holiday=is_change_on_holiday,
                )  # noqa: E501

                if not status:
                    response = {
                        "status": "UNSUCCESSFUL",
                        "errorCategory": "FAILED",
                        "errors": [
                            {
                                "code": "ERR-003-999-0001",
                                "message": f"No slots available in the next {check_duration} weeks from "
                                f"{interim_start_date}",
                            }
                        ],
                    }  # noqa: E123
                    return response

        if ticket.get("reScheduledInfo"):
            reschedule_info = ticket["reScheduledInfo"]
            try:
                implementation_plan = reschedule_info["prevTktNumber"]
                justification = reschedule_info["justification"]
            except KeyError as err:
                raise ResourceServiceNotAvailable(
                    f"Error while fetching required parameters for reScheduledInfo key in " f"payload: {err.args[0]}"
                )  # noqa: E123
        if "implementationPlanDtls" in ticket:
            implementation_plan_dtl = ticket["implementationPlanDtls"]
            implementation_plan_types = [
                implementation_plan_dtl.get("freeText"),
                implementation_plan_dtl.get("templatedText"),
            ]
            if all(implementation_plan_types) or not any(implementation_plan_types):
                logger.error(
                    "freeText and templatedText, both or none of the attributes are present. Only one of "
                    "them is required."
                )
                raise InvalidRequest(
                    "freeText and templatedText, both or none of the attributes are present. Only one of them is "
                    "required."
                )

            if "freeText" in implementation_plan_dtl:
                implementation_plan = implementation_plan_dtl["freeText"]
            else:
                template_name = implementation_plan_dtl["templatedText"]["templateName"]
                template_attribute = implementation_plan_dtl["templatedText"]["templateAttribute"]
                template_language = "en"
                """
                Calling Jinja2 template engine to render j2 template
                """
                email_template = EmailTemplateDesigner()
                logger.info(f"Proceed to prepare content using HTML templates")
                implementation_plan = email_template.design("j2", template_name, template_language, template_attribute)
                logger.debug(f"Response from EmailDesigner template for HTML template is {implementation_plan}")
                logger.info(f"Content creation using j2 templates completed successfully")

        data_normal = {
            "templateName": quote(ticket["templateName"]),
            "createdBy": quote(ticket["createdBy"]),
            "start_date": str(start_date_in_epoch),
            "end_date": str(end_date_in_epoch),
            "short_description": quote(str(ticket.get("shortDescription"))),
            "justification": quote(justification),
            "implementation_plan": quote(implementation_plan),
            "configuration_item": quote(ticket.get("configurationItem", "")),
            "assigned_to": quote(ticket.get("assignedTo", "")) or assigned_to,
        }
        logger.info(f"Hydration completed for service 3401 and payload to be sent to SPARK is {data_normal}")
        spark_response = spark.service3401(**data_normal)
        result = spark_response["result"]
        # Fix for Bug DNE-2477
        if any(key in result for key in ("error", "error_details", "conflict_details")):
            response = {
                "status": "UNSUCCESSFUL",
                "conflictDetails": result.get("conflict_details"),
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-003-999-0002",
                        "message": result.get("error_details") or result.get("error"),
                    }
                ],
            }  # noqa: E123
            return response
        else:
            ticket_number = result.get("details").split()[0]
            response = {
                "status": "SUCCESSFUL",
                "ticketNumber": ticket_number,
                "startDate": start_date_in_epoch,
                "endDate": end_date_in_epoch,
                "templateName": ticket["templateName"],
            }  # noqa: E123
        # Trigger email notification if created change start/end time is different from user given start/end time
        if start_date != start_date_in_epoch or end_date != end_date_in_epoch:
            notify_cw_change(ticket, ticket_number, start_date_in_epoch)
        logger.info(f"Entering into ITSM module to add the attachment for ticket : {ticket_number}")
        if ticket.get("attachments"):
            attachment_status = attach_files(ticket, ticket_number)
            if attachment_status:
                response["status"] = attachment_status["status"]
                response["attachmentError"] = attachment_status["attachmentError"]
            logger.info(f"Finished getting response from service 3045 in ITSM module for create ticket: {response}")

        # Adding assignmentGroup info to the created change
        if assignment_group := ticket.get("assignmentGroup"):
            logger.info(f"Entering into ITSM module to update the assignment group for ticket : {ticket_number}")
            assignment_status = update_assignment_group(ticket_number, assignment_group)
            if assignment_status and assignment_status.get("status") != "SUCCESSFUL":
                response["status"] = assignment_status.get("status")
                response["assignmentGroupError"] = assignment_status.get("assignmentGroupError")
            logger.info(
                f"Finished getting response from service 3042 in ITSM module for assignment group update: {response}"
            )

        if ticket.get("serviceType") == "metroServiceMigration":  # Bug fix for DNE-32901
            logger.info(f"Entering int process custom scripts for : {ticket_number}")
            if current_environment not in ["development", "test", "stage"]:
                process_custom_scripts(ticket_number=ticket_number, ticket=ticket)
        if ticket.get("serviceType") in ["metroMigration"]:
            logger.info(f"Entering int process custom scripts for : {ticket_number}")
            if current_environment not in ["development", "test", "stage"]:
                process_custom_scripts(ticket_number=ticket_number, ticket=ticket)
            for affectedci in affected_ci_list:
                if re.search(r"^(ta|br)(\d+)", affectedci["ciName"]):
                    affectedci["impactType"] = "At Risk"
            # Extracting exchange details
            exchanges = []
            for ci in cmdbci:
                if re.search(r"^(as|ma|me)(\d+\.)", ci):
                    exchanges.append(ci.split(".")[1])
            ohcp, wholesale, other, missing_cis = get_plannet_cid(
                **kwargs,
                affected_ci_list=affected_ci_list,
                ticket=ticket,
                ticket_number=ticket_number,
                exchanges=exchanges,
            )
            affected_ci_list.extend(ohcp)
            affected_ci_list.extend(wholesale)
            affected_ci_list.extend(other)
            affected_ci_list.extend(missing_cis)
            final_affected_ci_list = [dict(i) for i in {tuple(ids.items()) for ids in affected_ci_list}]

        result_ci = spark.service3040(
            ticket=ticket_number,
            ci_list=(final_affected_ci_list if ticket.get("serviceType") in ["metroMigration"] else affected_ci_list),
            impact_start=str(start_date_in_epoch),
            impact_end=str(end_date_in_epoch),
            operation="add",
            operation_by=quote(ticket["createdBy"]),
        )

        if not result_ci:
            logger.error(f"Ticket {ticket} raised but unable to add one or more CIs {affected_ci_list}")
            response["ciAddError"] = affected_ci_list
            response.update({"status": "UNSUCCESSFUL"})  # Fix for Bug DNE-4853
            # return response
        logger.info(f"Exiting ITSM module after getting the response from service 3040 : {result_ci}")

        if ticket.get("thirdPartyTicket"):
            # Downstream ci code start
            ws_cis = {}
            for ws in wholesale:
                ws_cis.setdefault(ws.get("ciName"), ws)
            for host, ws_kwargs in ticket.get("wholesaleCIs", {}).items():
                ws_cis.setdefault(host, {"ciName": host, "impactType": ws_kwargs.get("impactType")})
            wholesale = ws_cis.values()
            # Downstream ci code end
            third_party_response = third_party_ticket_creation(
                affected_ci_list=wholesale, ticket=ticket, ticket_number=ticket_number
            )
            # if third_party_response.get("errors"): Need to be removed after 7653 testing
            #     return connexion.problem(
            #         status=403,
            #         title=f"Error occured in Third party ticket creation",
            #         detail=third_party_response.get("errors"),
            #         ext=response,
            #     )
            if third_party_response.get("successResponse"):
                response["thirdParty"] = third_party_response

            if third_party_response.get("failedResponse") or third_party_response.get("errors"):
                response["thirdParty"] = third_party_response
                response.update({"status": "PARTIAL-SUCCESS"})  # Fix for Bug DNE-7653
        logger.info(f"Exiting ITSM module after getting the response from service 3030 : {result_ci}")
        return response
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
    except Exception as err:
        logger.error(f"exception caused with error info as {err.args[0]}")
        raise


def process_custom_scripts(ticket_number=None, ticket=None):
    # sourcery skip: extract-method, for-append-to-extend, remove-redundant-exception, simplify-single-exception-tuple
    """
    Input:
        ticket_number=CHG12345
        ticket = {Spark successful response}
    Ouput:
        True or False
    """
    logger.info(f"Entering into ITSM module to attach the TMA Output : {ticket_number}")
    try:
        exchange_affected_cis = [
            host["ciName"].split(".")[1]
            for host in ticket.get("affectedCIs")
            if re.search(r"^(as|ma|me)(\d+\.)", host["ciName"])  # Fix for TMA to pick exact exchange
        ]
        exchanges = list(set(exchange_affected_cis))
        exchanges = list(set(exchanges) - set(pop_site_list))
        logger.info(f"Processing exchanges {exchanges} for Grandma and TMA")
        tma_file_attachments = []
        for exchange in exchanges:
            html_content = getTmaData(site=f"{exchange}", option="-f")
            file_name = f"{exchange}.html"
            tma_file_attachments.append(
                {
                    "fileName": file_name,
                    "fileContent": str(base64.urlsafe_b64encode(html_content.body), "utf-8").rstrip("="),
                }
            )  # noqa: E128
        if tma_file_attachments:
            ticket.update({"attachments": tma_file_attachments})
            response = attach_files(ticket, ticket_number)
            logger.info(f"Finished getting response from service 3045 in ITSM module for TMA: {response}")

        logger.info("Entering into ITSM module to process Grandma")
        interoute_cis = []
        for exchange in exchanges:
            grandma_response = getGrandmaData(site=f"{exchange.upper()}")
            for key, value in grandma_response.items():
                if value > 0:
                    interoute_cis.append({key: value})
        logger.info(f"Finished getting response from Grandma with {interoute_cis}")
        if interoute_cis:
            interoute_body = {
                "parentTicket": ticket_number,
                "ticketType": "change",
                "customerName": ["Interoute"],
                "impact": "Full outage to service",
                "reason": "Maintenance-Sky network Upgrade",
            }
            response = create_third_party_ticket(body=interoute_body)
            logger.info(f"Completed grandma processing with {response}")
        logger.info("Successfully completed processing TMA and Grandma")
        return True
    except (KeyError, AttributeError, ValueError, Exception) as err:
        logger.exception(err)
        return False


def third_party_ticket_creation(**kwargs):
    response = {}
    ticket = kwargs["ticket"]
    third_party_ticket_type = "change"
    third_party_ticket_impact = ticket["thirdPartyTicket"].get("thirdpartyImpact")
    third_party_ticket_reason = ticket["thirdPartyTicket"].get("thirdpartyImpactReason")
    affected_cis = [host["ciName"] for host in kwargs["affected_ci_list"]]
    customer_names = custom_query(table="cmdb_circuit", ci_list=affected_cis, filter="ci_list")
    third_party_ticket_customer_name = [
        c_name.get("u_customer").get("displayValue") for c_name in customer_names.get("result")
    ]
    third_party_ticket_parent_ticket = kwargs["ticket_number"]
    third_party_ticket = {
        "parentTicket": third_party_ticket_parent_ticket,
        "ticketType": third_party_ticket_type,
        "customerName": third_party_ticket_customer_name,
        "impact": third_party_ticket_impact,
        "reason": third_party_ticket_reason,
    }
    logger.info(f"inside third_party_ticket_creation third_party_ticket {third_party_ticket}")
    result = create_third_party_ticket(body=third_party_ticket)

    if (not isinstance(result, dict) and result.status_code == 400) or (
        isinstance(result, dict) and result.get("errors")
    ):
        response["errors"] = result.get("errors") if isinstance(result, dict) else result.body.get("detail")
    else:
        response = result
    logger.info(f"Exit third_party_ticket_creation response {response}")
    return response


def calculate_wait_time_offset(start_date):
    """
    Method to calculate wait_time and offset.
    offset - drift from 12:00 midnight
    wait_time - (start_date - current date) in days
    Args:
        start_date: in epoch
    Returns:
        offset, wait_time
    """
    logger.debug(f"Inside method to calculate wait_time and offset drift from 12 midnight")
    if start_date < today:
        raise InvalidRequest(f"Start Date is in past")
    offset = 0
    date_today = datetime.today().date()
    date_start = datetime.utcfromtimestamp(start_date).date()
    start_date_midnight = (date_start - epoch.date()).total_seconds()
    start_date_offset = (start_date - start_date_midnight) / (60 * 60)
    offset += start_date_offset
    wait_time = (date_start - date_today).days
    return offset, wait_time


def hydrate_cis(**kwargs) -> bool:
    """
    Method to hydrate CIs from PlanNet.
     - drift from 12:00 midnight
    wait_time - (start_date - current date) in days

    Args:
        req_body: input payload
    Returns:
        List of CIs
    """
    ticket = kwargs["body"]
    if ticket.get("serviceType") == "bngFailover":
        hostnames: list = [host["ciName"] for host in ticket["affectedCIs"]]
        hydrated_ci_list: list = get_adjacent_ci_details(hostnames, ticket["serviceType"])
        ticket["affectedCIs"].extend(
            (
                {"ciName": ci, "impactType": "Reduced Resiliency" if ci.startswith("br") else "No Service Impact"}
                for ci in hydrated_ci_list
                if ci not in hostnames
            )
        )
        return True
    if not ticket["serviceType"] in ["serviceIncident"] and ticket.get("isCIPullRequired"):
        raise InvalidRequest(
            f"Currently, support of fetching affetced CIs from PlanNet is supported for only "
            f"serviceIncident service type. Therefore, value must be set to false for other service type."
        )
    """
    Currently, serviceIncident has all CIs listed in input payload itself. we do not need to fetch
    from PlanNet
    """
    if ticket["serviceType"] in ["serviceIncident"] and ticket.get("isCIPullRequired"):
        raise InvalidRequest(
            f"Currently, support of fetching affetced CIs from PlanNet is Not supported for "
            f"serviceIncident service type. Therefore, value must be set to false."
        )
    return True


def fetch_ma_switches(downstream_cis, service_types):
    cis = []
    if "ALL" in service_types:
        cis = downstream_cis.get("nes", {}).get("mas", []) + downstream_cis.get("nes", {}).get("switches", [])
    return cis


def fetch_um(downstream_cis, service_types):
    cis = []
    if len({"UM", "ALL"} - set(service_types)) < 2:
        cis = downstream_cis.get("nes", {}).get("exchangeMgmtNes", []) + downstream_cis.get("nes", {}).get("llus", [])
    return cis


def fetch_voice(downstream_cis, service_types):
    result_cis = []
    if len({"VOICE", "ALL"} - set(service_types)) < 2:
        cis = downstream_cis.get("nes", {}).get("exchangeMgmtNes", []) + downstream_cis.get("nes", {}).get("llus", [])
        result_cis = [ci for ci in cis if ci.startswith(("vm", "ar", "wbm"))]
    return result_cis


def fetch_ubb(downstream_cis, service_types):
    result_cis = []
    if len({"UBB", "ALL"} - set(service_types)) < 2:
        cis = downstream_cis.get("nes", {}).get("llus", [])
        result_cis = (
            downstream_cis.get("circuits", {}).get("geas", [])
            + downstream_cis.get("nes", {}).get("wapNNI", [])
            + [ci for ci in cis if ci.startswith(("bm", "cr"))]
        )
    return result_cis


def fetch_wse(downstream_cis, service_types):
    cis = []
    if len({"WSE", "ALL"} - set(service_types)) < 2:
        cis = downstream_cis.get("circuits", {}).get("wholesale", [])
    return cis


def fetch_downstream_cis_with_type(downstream_cis, impact_type, hydrated_cis_with_type, service_types):
    """_summary_

    Args:
        downstream_cis (_type_): _description_
        impact_type (_type_): _description_
        hydrated_cis_with_type (_type_): _description_
        service_types (_type_): _description_

    Returns:
        _type_: _description_
    """
    logger.info(
        f"Inside fetch_downstream_cis_with_type downstream_cis {downstream_cis}, "
        f"impact_type {impact_type}, hydrated_cis_with_type {hydrated_cis_with_type}, "
        f"service_types {service_types}"
    )
    fetched_cis = {
        "ma_switches": fetch_ma_switches(downstream_cis, service_types),
        "UM": fetch_um(downstream_cis, service_types),
        "VOICE": fetch_voice(downstream_cis, service_types),
        "UBB": fetch_ubb(downstream_cis, service_types),
        "WSE": fetch_wse(downstream_cis, service_types),
    }
    for type, cis in fetched_cis.items():
        for ci in cis:
            hydrated_cis_with_type.setdefault(type, {}).setdefault(
                ci, {"impactType": impact_type, "serviceTypes": service_types}
            )
    logger.info(f"Exit fetch_downstream_cis_with_type hydrated_cis_with_type {hydrated_cis_with_type}")
    return hydrated_cis_with_type


def fetch_downstream_cis(ticket):
    """_summary_

    Args:
        ticket (_type_): _description_

    Returns:
        _type_: _description_
    """
    logger.info(f"Inside fetch_downstream_cis ticket {ticket}")
    down_cis = {}
    for downstream_cis in ticket.get("addDownstreamCIs"):
        downstream_ci_details = get_cis_details(host=downstream_cis.get("hostname"))
        logger.info(f"downstream_ci_details {downstream_ci_details}")
        downstream_ci_details = {key: ci_details for key, ci_details in downstream_ci_details.items() if ci_details}
        down_cis = fetch_downstream_cis_with_type(
            downstream_ci_details, downstream_cis.get("impactType"), down_cis, downstream_cis.get("serviceTypes")
        )
    logger.info(f"Exit fetch_downstream_cis down_cis {down_cis}")
    return down_cis


def get_downstream_cis(kwargs):
    """_summary_

    Args:
        ticket (_type_): _description_
        kwargs (_type_): _description_

    Returns:
        _type_: _description_
    """
    logger.info(f"Inside get_downstream_cis kwargs {kwargs}")
    impact_type_precedence_list = [value.strip() for value in impact_type_precedence.split(",")]
    third_party_impact_map = {
        third_party_impact_list.split(":")[0].strip(): third_party_impact_list.split(":")[1].strip()
        for third_party_impact_list in third_party_impact_str.split(",")
    }
    logger.info(
        f"get_downstream_cis impact_type_precedence_list {impact_type_precedence_list}, "
        f"third_party_impact_map {third_party_impact_map}"
    )
    ticket = kwargs.get("body", {})
    affected_cis_host = {}

    for affected_cis in kwargs.get("body", {}).get("affectedCIs", []):
        affected_cis_host.setdefault(affected_cis.get("ciName"), affected_cis)

    for downstream_cis in ticket.get("addDownstreamCIs", [])[:]:
        affected_cis_host[downstream_cis.get("hostname")] = {
            "ciName": downstream_cis.get("hostname"),
            "impactType": next(
                (
                    impact_type_precedence_value
                    for impact_type_precedence_value in impact_type_precedence_list
                    if impact_type_precedence_value
                    in [
                        downstream_cis.get("impactType"),
                        affected_cis_host.get(downstream_cis.get("hostname"), {}).get("impactType"),
                    ]
                ),
                downstream_cis.get("impactType"),
            ),
        }
        downstream_cis["impactType"] = next(
            (
                impact_type_precedence_value
                for impact_type_precedence_value in impact_type_precedence_list
                if impact_type_precedence_value
                in [
                    downstream_cis.get("impactType"),
                    affected_cis_host.get(downstream_cis.get("hostname"), {}).get("impactType"),
                ]
            ),
            downstream_cis.get("impactType"),
        )

    downstream_cis = fetch_downstream_cis(ticket)
    for key, down_cis in downstream_cis.items():
        for host, value in down_cis.items():
            affected_cis_host[host] = {
                "ciName": host,
                "impactType": next(
                    (
                        impact_type_precedence_value
                        for impact_type_precedence_value in impact_type_precedence_list
                        if impact_type_precedence_value
                        in [value.get("impactType"), affected_cis_host.get(host, {}).get("impactType")]
                    ),
                    value.get("impactType"),
                ),
            }
    logger.info(f"affected_ci_host {affected_cis_host}")
    kwargs["body"]["affectedCIs"] = list(affected_cis_host.values())
    # kwargs.get("body",{}).get("affectedCIs",affected_cis_host.values())
    for type, wse_cis in downstream_cis.get("WSE", {}).items():
        # IF impactType=at Risk then thirdpartyImpact=reduce resiliency
        # otherwise thirdpartyImpact=Full outage to service
        ticket.setdefault("thirdPartyTicket", {})["thirdpartyImpact"] = third_party_impact_map.get(
            wse_cis.get("impactType"), "Full outage to service"
        )
        ticket.setdefault("thirdPartyTicket", {}).setdefault(
            "thirdpartyImpactReason", "Maintenance-Sky network Upgrade"
        )
        kwargs.get("body", {}).setdefault("wholesaleCIs", {}).setdefault(type, wse_cis)
    logger.info(f"Exit get_downstream_cis ticket {ticket} kwargs {kwargs}")
    return ticket, kwargs


def create_ticket(**kwargs: dict) -> dict[str, Any] | ConnexionResponse:  # noqa: C901 # sourcery skip
    """
    Creates Spark Service Now Minor Change

    Args:
       body = {
                 "affectedCIs": [
                   {
                     "ciName": "Sample CI",
                     "impactType": "impactType 1"
                   }
                 ],
                 "changeWindow": 6,
                 "createdBy": "rky08",
                 "endDate": "1572794340",
                 "serviceType": "ethernetSegment",
                 "shortDescription": "Configuration of Ethernet Segment for ma0 and ma1",
                 "parentChange": "CHG1234567",
                 "startDate": "1572794340",
                 "waitTime": 1
               }

    Returns:
       {
         "endDate": "1572794340",
         "startDate": "1572794340",
         "status": "CREATED",
         "ticketNumber": "CHG123456789"
       }

    Raises:

    """
    try:
        ticket = kwargs["body"]
        short_desc_prefix = "[DNE]" if not ticket.get("shortDescription").startswith("[DNE]") else ""
        ticket["shortDescription"] = f"{short_desc_prefix}{ticket.get('shortDescription')}"

        """
        If isCIPullRequired set to True, Invoke to hydrate list of affected CIs from Planet.
        """
        if ticket.get("isCIPullRequired"):
            hydrate_cis(**kwargs)
        # Fix for Bug DNE-2558
        # downstream cis start
        if ticket.get("addDownstreamCIs"):
            ticket, kwargs = get_downstream_cis(kwargs)
            logger.info(f"calling function get_downstream_cis body {kwargs.get('body')} ticket {ticket}")
        # downstream cis end
        change_type = ticket.get("changeType") or "minor"
        if (change_type == "standard") or (change_type == "normal"):
            response = create_standard_ticket(**kwargs)
            return response
        logger.info(f"Entering into ITSM module for ticket generation with serviceType as :{ticket['serviceType']}")
        logger.debug(f"Request body sent for the creation of ticket: {ticket}")
        affected_cis = ticket["affectedCIs"]
        cmdbci = [hostname["ciName"] for hostname in ticket["affectedCIs"]]
        try:
            service_map = mapper[ticket["serviceType"]]["create"]
        except KeyError as err:
            raise ResourceServiceNotAvailable(
                f"Minor ticket creation not supported for the service {ticket['serviceType']}: {err.args[0]}"
            )

        description = service_map["description"]
        description += f"{' , '.join(ci for ci in cmdbci)}"
        # Bug fix for 3644
        description += (
            f" to get more details go to {external_url} --> order tracking --> "
            f"open the order {ticket.get('shortDescription') or 'None'} "
            f"--> expand technical information"
        )
        description = ticket.get("description") or description
        parent_change = ticket.get("parentChange") or service_map["parent_change"]
        assignment_group = ticket.get("assignmentGroup") or service_map["assignment_group"]
        # Fix for  Bug DNE-2482
        short_description = service_map.get("short_description") + ticket["shortDescription"]
        start_date = ticket.get("startDate")
        end_date = ticket.get("endDate")
        wait_time = ticket.get("waitTime")
        change_window = ticket.get("changeWindow")
        offset = ticket.get("offset", 0)
        config_group = service_map["config_group"]
        max_chg_window = service_map["extra_args"].get("max_change_window", 6)

        logger.info(f"ITSM Factory has mapped the configured values successfully")
        # Fix for Bug DNE-2480
        if not (start_date and end_date) and not (change_window and wait_time):
            raise InvalidRequest(
                f"Combination of Start Date & End Date or "
                f"Change Window & Wait time should be given and greater than 0"
            )

        logger.info(
            f"Proceed to prepare the schedule as per the inputs from request body, StartDate: {start_date} , "
            f"EndDate: {end_date}, changeWindow: {change_window} & waitTime: {wait_time} "
        )  # noqa: E123

        if ticket["serviceType"] in [
            "metroMigration",
            "ubbMigration",
            "newSwitchInstall",
            "retrofit",  # Bug fix for DNE-39597,
        ]:  # Bug fix for DNE-15465
            data = {
                "cmdbci": affected_cis
                if ticket["serviceType"] == "retrofit"
                else [],  # Redacting the CI list for MetroMigration
                "createdBy": quote(ticket["createdBy"]),
                "start_date": str(start_date),
                "end_date": str(end_date),
                "assignment_group": quote(assignment_group),
                "parent_change": quote(parent_change),
                "short_description": quote(short_description),
                "description": quote(service_map["description"]),
                "config_group": quote(config_group),
            }  # noqa: E123
        else:
            data = prepare_payload_for_spark(
                affected_cis,
                quote(ticket["createdBy"]),
                start_date,
                end_date,
                assignment_group,
                parent_change,
                short_description,
                description,
                config_group,
                cmdbci,
                change_window,
                wait_time,
                offset,
                ticket.get("serviceType"),
                max_chg_window,
                ticket.get("isChgOnHoliday", False),
            )

        logger.info(f"Hydration completed successfully and payload to be sent to SPARK is {data}")

        """
        calling spark api for creating the ticket number using service3405
        """
        spark_response = spark.service3405(**data)
        try:
            result = spark_response["result"]
        except KeyError as err:
            raise ResourceServiceNotAvailable(
                f"Error while getting response from Spark, missing `result` key in " f"payload: {err.args[0]}"
            )  # noqa: E123

        if any(key in result for key in ("error_details", "conflict_details")):  # Fix for DNE-7606
            # Fix for bug 3173
            err = result["error_details"] if result.get("error_details") else result["conflict_details"]
            if "parent" in err:
                err = f"{err}, parent ticket# {parent_change}"
            response = {
                "status": "UNSUCCESSFUL",
                "error": err,
                "conflictDetails": result.get("conflict_details"),
            }  # noqa: E123
        else:
            ticket_number = result.get("details").split()[0]
            response = {
                "status": "SUCCESSFUL",
                "ticketNumber": ticket_number,
                "startDate": int(data["start_date"]),
                "endDate": int(data["end_date"]),
            }  # noqa: E123

            # Fix for Bug DNE-2513, DNE-3912
            if ticket.get("attachments"):
                check_valid_attachments(ticket["attachments"])
                logger.info(f"Entering into ITSM module to add the attachment for ticket : {ticket_number}")
                attachment_status = attach_files(ticket, ticket_number)
                if attachment_status:
                    response["status"] = attachment_status["status"]
                    response["attachmentError"] = attachment_status["attachmentError"]

                logger.info("Finished getting response from service 3045 in ITSM module for create ticket: {response}")
            if start_date and (start_date != int(data.get("start_date")) or end_date != int(data.get("end_date"))):
                notify_cw_change(ticket, ticket_number, int(data.get("start_date")))
        logger.info("Exiting ITSM module after sending the response")
        return response

    except (DateGeneratorError, DateValidateError) as err:
        return connexion.problem(  # noqa: E123
            status=400,
            title=f"Error in preparing startDate, endDate, waitTime or changeWindow",
            detail=err.args[0],
        )  # noqa: E123
    except RestUtilityException as err:
        return connexion.problem(
            status=403,
            title=f"Request Exception while accessing the URL",
            detail=err.args[0],
        )
    except ResourceServiceNotAvailable as err:
        return connexion.problem(  # noqa: E123
            status=404,
            title=f"Error while creating the ticket on Spark",
            detail=f"Problems with `{err.args[0]}` key",
        )  # noqa: E123
    except (ValueError, KeyError, TypeError) as err:
        logger.exception(err)
        return connexion.problem(  # noqa: E123
            status=400,
            title=f"Error in request body",
            detail=f"`{err.args[0]}` is a required property",
        )  # noqa: E123
    except InvalidRequest as err:
        logger.exception(err, exc_info=True)
        return connexion.problem(  # noqa: E123
            status=400,
            title=f"Invalid Request",
            detail=f"{err.args[0]}",
        )  # noqa: E123
    except Exception as err:
        logger.exception(err)
        return connexion.problem(  # noqa: E123
            status=500,
            title=f"Connector exception raised while creating the ticket",
            detail=err.args[0],
        )  # noqa: E123


# Fix for Bug DNE-2513
def attach_files(ticket, ticket_number):
    failed_files = []
    add_status = False
    for files in ticket["attachments"]:
        attachment = files["fileContent"]
        filename = quote(files["fileName"])
        operation_by = quote(ticket["createdBy"])
        data = {
            "ticket_number": ticket_number,
            "filename": filename,
            "operation_by": operation_by,
            "operation": "add",
            "attachment": attachment,
        }  # noqa: E123
        logger.debug(f"Payload to be sent to itsm/attachment is {data} for Service 3045")
        spark_response = spark.service3045(**data)
        result = spark_response["result"]
        if any(key in result for key in ("error_details", "conflict_details")):  # Fix for DNE-7606
            failed_files.append(
                {
                    "fileName": filename,
                    "errorMessage": (
                        result["error_details"] if result.get("error_details") else result["conflict_details"]
                    ),
                }
            )  # Fix for BUG DNE-4433
        else:
            add_status = True
    if failed_files:
        return {
            "status": "PARTIAL-SUCCESS" if add_status else "FAILURE",
            "attachmentError": failed_files,
        }


def update_assignment_group(ticket_number: str, assignment_group: str) -> dict:
    """
    Method to update assignment group for a given ticket number using service 3045

    Args:
        ticket_number: str : Ticket number for which assignment group needs to be updated
        assignment_group: str : Assignment group name to be updated in the ticket
    Returns:
        dict: A dictionary containing the status of the update operation and error details if any
    """
    logger.info(f"Entering into ITSM module for assignment group update for ticket : {ticket_number}")
    data = {
        "ticket_number": ticket_number,
        "updated_by": "SVC-APP-DNE",
        "assignment_group": quote(assignment_group),
    }
    spark_response = spark.service3402(**data)
    result = spark_response["result"]
    assignment_status = {}
    if any(key in result for key in ("error_details", "conflict_details")):  # Fix for DNE-7606
        assignment_status = {
            "status": "UNSUCCESSFUL",
            "assignmentGroupError": (
                result["error_details"] if result.get("error_details") else result["conflict_details"]
            ),
        }
        logger.debug(f"Error in updating assignment group with response {result} for ticket {ticket_number}")
    else:
        assignment_status = {"status": "SUCCESSFUL"}
        logger.debug(f"Success status in updating assignment group with response {result} for ticket {ticket_number}")
    logger.info(
        f"Finished getting response from service 3042 in ITSM module for assignment group update: {assignment_status}"
    )
    return assignment_status


def create_third_party_ticket(**kwargs):
    """
    Creates Spark Service Now third party ticket

    kwargs:
       body = {
                 "parentTicket": "CHG123456789",
                 "ticketType": "change",
                 "customerName": ["Entanet", "Amdocs"],
                 "impact": "Full outage to service",
                 "reason": "Maintenance-sky network upgrade"
               }

    Returns:
        [
        {
         "status": "TPCHG12345 (WHOLESALE PORTAL TASK CREATED)",
         "customer": "Entanet"
         },
         {
         "error_details": "cannot create wholesale portal task",
         "customer": "Amdocs"
         }
       ]

    Raises:
        RestUtilityException
        ResourceServiceNotAvailable
        ValueError, KeyError, TypeError
        InvalidRequest
        Exception

    """
    try:
        logger.info(f"Entering into ITSM module for third party ticket generation")
        ticket_request_body = kwargs["body"]
        status, error = _validate_third_party_inputs(ticket_request_body)
        if not status:
            return connexion.problem(
                status=400,
                title=f"Request Body validation failed",
                detail=error,
            )
        logger.debug(f"Request body to sent for the creation of ticket: {ticket_request_body}")
        # Preparing data_model for service 3030 spark Api
        data_model = [
            {
                "ticket_type": tp_mapper[ticket_request_body["ticketType"]]["type"],
                "ticket_number": ticket_request_body["parentTicket"],
                "third_party": customer,
                "impact": ticket_request_body["impact"],
                "reason": ticket_request_body["reason"],
            }
            for customer in list(set(ticket_request_body["customerName"]))  # Fix for DNE-7526
        ]
        # Initiating for loop for all customers as spark process only one customer at a time
        sprk_response = {"successResponse": [], "failedResponse": []}
        for data in data_model:
            spark_response = spark.service3030(**data)
            logger.debug(f"spark data received: {spark_response}")
            result = spark_response["result"]
            if any(key in result for key in ("error", "error_details", "conflict_details")):
                sprk_response["failedResponse"].append(
                    {
                        "code": "ERR-003-999-0002",
                        "message": result.get("error") or result.get("error_details") or result.get("conflict_details"),
                        "customer": data.get("third_party"),
                    }
                )
                logger.debug(f"Error in spark response {result} for customer {data.get('third_party')}")
            else:
                logger.debug(f"Success status {result.get('details')} for customer {data.get('third_party')}")
                sprk_response["successResponse"].append(
                    {"message": result.get("details"), "customer": data.get("third_party")}
                )
        if len(sprk_response["successResponse"]) == len(list(set(ticket_request_body["customerName"]))):
            sp_response = {"successResponse": sprk_response["successResponse"]}
        elif len(sprk_response["successResponse"]) == 0:
            sp_response = {
                "status": "PARTIAL-SUCCESS",
                "failedResponse": sprk_response["failedResponse"],
                "successResponse": [],
            }
        else:
            sp_response = {
                "status": "PARTIAL-SUCCESS",
                "successResponse": sprk_response["successResponse"],
                "failedResponse": sprk_response["failedResponse"],
            }
        logger.info(f"Exiting after completing process for third party ticket creation")
        return sp_response
    except RestUtilityException as err:
        logger.exception(err, exc_info=True)
        return connexion.problem(
            status=403,
            title=f"Request Exception while accessing the URL",
            detail=err.args[0],
        )
    except ResourceServiceNotAvailable as err:
        logger.exception(err, exc_info=True)
        return connexion.problem(  # noqa: E123
            status=404,
            title=f"Error while creating the ticket on Spark",
            detail=f"Problems with `{err.args[0]}` key",
        )  # noqa: E123
    except (ValueError, KeyError, TypeError) as err:
        logger.exception(err, exc_info=True)
        return connexion.problem(  # noqa: E123
            status=400,
            title=f"Error in request body",
            detail=f"`{err.args[0]}` is a required property",
        )  # noqa: E123
    except Exception as err:
        logger.exception(err, exc_info=True)
        return connexion.problem(  # noqa: E123
            status=500,
            title=f"Connector exception raised while creating the ticket",
            detail=err.args[0],
        )  # noqa: E123


def _validate_third_party_inputs(data):
    """
    Validate input data for third party tickets

    kwargs:
       data = {
                 "parentTicket": "CHG123456789",
                 "ticketType": "change",
                 "customerName": ["Entanet", "Amdocs"],
                 "impact": "Full outage to service",
                 "reason": "Maintenance-sky network upgrade"
               }
    Returns:
        status: True if no error else False
        error: list of errors if any or []
    """
    status = True
    errors = []
    if data["ticketType"] == "change":
        if data["impact"] not in tp_mapper[data["ticketType"]]["valid_impact"]:
            status = False
            errors.append(
                (
                    f"`{data['impact']}` is not valid impact for ticketType `{data['ticketType']}`. "
                    f"Please provide valid impact from list {tp_mapper[data['ticketType']]['valid_impact']}"
                )
            )
        if data["reason"] not in tp_mapper[data["ticketType"]]["valid_reason"]:
            status = False
            errors.append(
                (
                    f"`{data['reason']}` is not valid reason for ticketType `{data['ticketType']}`. "
                    f"Please provide valid reason from list {tp_mapper[data['ticketType']]['valid_reason']}"
                )
            )
    return status, errors


def prepare_payload_for_spark(
    affected_cis,
    created_by,
    start_date,
    end_date,
    assignment_group,
    parent_change,
    short_description,
    description,
    config_group,
    cmdbci,
    change_window,
    wait_time,
    offset,
    service_type,
    max_chg_window,
    is_change_on_holiday,
):  # sourcery skip
    """
    Placing intelligence to find the slot
    """
    """
    computing change window and wait time with the given start and end date
    """
    if start_date and end_date:
        start_date_in_epoch, end_date_in_epoch = start_date, end_date
        # Bug fix for DNE-2476
        if start_date < today or start_date >= end_date:  # Sourcery related suggestion
            raise InvalidRequest(f"Either Start Date is in past or Start Date is greater than End Date")

        # Change window unit is hours & wait time unit is No of Days
        change_window = round(
            (end_date_in_epoch - start_date_in_epoch) / (60 * 60)
        )  # noqa: E226 # BUG fix for DNE-3911
        wait_time = math.floor((start_date_in_epoch - today) / (60 * 60 * 24))  # noqa: E226
        calc_time_offset_mapper = {
            "calc_offset": {"serviceType": ["geaProvisioning"], "function": calculate_wait_time_offset}
        }
        for check_type, check in calc_time_offset_mapper.items():
            if service_type in check["serviceType"]:
                offset, wait_time = check["function"](start_date_in_epoch)
                logger.info(
                    f"Minor ticket with serviceType {service_type} provided offset is {offset} "
                    f"wait_time is {wait_time} and max_possible_change_window {max_chg_window}"
                )

    """
    limiting the change window parameter to fall within 6 hours
    """
    if change_window > max_chg_window or change_window < 1:
        raise InvalidRequest(
            f"Minimum and  Maximum allowed change window after round-off "
            f"should be between 1 hour to {max_chg_window} hours"
        )
    elif change_window == 0 or wait_time == 0:
        raise InvalidRequest(f"Change Window & Wait time should be greater than 0")
    """
    calling custom validator to hydrate the startDate and endDate before calling SPARK API
    """
    start_date_in_epoch, end_date_in_epoch = converter.convert(
        change_window_duration=change_window,
        days_to_wait=wait_time,
        offset=offset,
        is_change_on_holiday=is_change_on_holiday,
    )  # noqa: E123
    """
    checking if any open changes exist for CIs
    """
    interim_start_date = (
        datetime.fromtimestamp(start_date_in_epoch)
        if timezone.localize(datetime.fromtimestamp(start_date_in_epoch)).dst()
        else datetime.utcfromtimestamp(start_date_in_epoch)
    )
    interim_end_date = interim_start_date + timedelta(weeks=int(check_duration))
    slot_end_date_in_epoch = int((interim_end_date - epoch).total_seconds())
    logger.info(f"Retrieving any open changes exists for {cmdbci}")
    change_req_list = spark.service3800(
        db_table="task_ci",
        affected_cis=cmdbci,
        ci_filter="ci_item",
        start_date=start_date_in_epoch,
        end_date=slot_end_date_in_epoch,
    )
    logger.info(f"Retrieved {len(change_req_list)} open changes completed successfully")

    """
    checking conflicts for the given start and end date
    """
    logger.info(f"Checking if any change restrictions exists for {start_date_in_epoch} & {slot_end_date_in_epoch}")
    change_freeze_response = spark.service3020(start_date=start_date_in_epoch, end_date=slot_end_date_in_epoch)
    change_freeze_list = []
    config_group_bkp = config_group
    if change_freeze_response:
        if "ITA" in config_group:  # Fix as part of Regression Testing - DNE-11250
            config_group = "".join(config_group.split("-")[:2]).strip().replace("  ", " ")
        for index, change_freeze in enumerate(change_freeze_response):  # Fix as part of Metro
            if config_group in change_freeze["condition"]:
                change_freeze_list.append(change_freeze)
    logger.info(f"Checks for change restrictions completed successfully with {len(change_freeze_list)}")

    """
    Find a slot considering both change freeze and change requests
    """
    midnight_start_date = None
    midnight_end_date = None
    if change_req_list or change_freeze_list:
        status, midnight_start_date, midnight_end_date = resolver.find_time_slot(
            change_request=change_req_list,
            start_date=start_date_in_epoch,
            change_window=change_window,
            change_freeze=change_freeze_list,
            slot_end_date=slot_end_date_in_epoch,
            service_type=service_type,
        )  # noqa: E501

        if not status:
            return {
                "status": "UNSUCCESSFUL",
                "error": f"No slots available in the next {check_duration} weeks from " f"{interim_start_date}",
            }
    return {
        "cmdbci": affected_cis,
        "createdBy": quote(created_by),
        "start_date": str(midnight_start_date or start_date_in_epoch),
        "end_date": str(midnight_end_date or end_date_in_epoch),
        "assignment_group": quote(assignment_group),
        "parent_change": quote(parent_change),
        "short_description": quote(short_description),
        "description": quote(description),
        "config_group": quote(config_group_bkp),
    }  # noqa: E123


def notify_cw_change(ticket, ticket_number, start_date_in_epoch):
    """
    sends email notification to the users when the change window is not honored
    kwargs:
       ticket: user given payload details
       ticket_number: generated ticket number
       start_date_in_epoch: spark ticket created date time
    Returns:
         True if no error else False
    """
    try:
        response = ""
        logger.info("Inside method to send email notification as the ticket change window not honored")
        service_type = ticket.get("serviceType")
        collection_ref = ServiceDB(notify_change_window)
        service_record = collection_ref.find_one(query={})
        logger.info(f"service collection: {service_record}")
        if not service_record or not service_record.get("notifychangewindow"):
            logger.info(f"service collection {notify_change_window} record doesn't exist in DB..")
            return False
        record = [
            service.get(service_type)
            for service in service_record.get("notifychangewindow")
            if service.get(service_type)
        ]
        record = record[0] if record else {}
        notify_change = record.get("notifyChg")
        notify_ctask = record.get("notifyCtask")
        order_number = ticket.get("orderNumber")
        email_recipients = record.get("emailRecipients", {})
        to_list = email_recipients.get("toList")
        cc_list = email_recipients.get("ccList")
        bcc_list = email_recipients.get("bccList")
        requested_start_time = (
            datetime.fromtimestamp(ticket.get("startDate"))
            if timezone.localize(datetime.fromtimestamp(ticket.get("startDate"))).dst()
            else datetime.utcfromtimestamp(ticket.get("startDate"))
        )
        actual_start_time = (
            datetime.fromtimestamp(start_date_in_epoch)
            if timezone.localize(datetime.fromtimestamp(start_date_in_epoch)).dst()
            else datetime.utcfromtimestamp(start_date_in_epoch)
        )
        json_data = {
            "toList": to_list,
            "bccList": bcc_list,
            "ccList": cc_list,
            "language": "en",
            "mailTemplate": "SparkDateUpdated",
            "parameters": {
                "orderNumber": order_number or "NA",
                "orderType ": service_type,
                "ticketNumber": ticket_number,
                "requestedStartTime": requested_start_time,
                "actualStartTime": actual_start_time,
                "url": "https://dne.cf.sky.com/",
            },
        }
        if notify_change and ticket.get("changeType") in ["standard", "normal"]:
            logger.info(f"notify change - Initiating email sender with the json data {json_data}")
            response = email_notifications(body=json_data)
        elif notify_ctask and ticket.get("changeType") not in ["standard", "normal"]:
            logger.info(f"notify ctask - Initiating email sender with the json data {json_data}")
            response = email_notifications(body=json_data)
        if isinstance(response, ConnexionResponse):
            msg = response.body.get("detail")
            logger.info(f"Failed to send email notification due to: {msg}")
            return False
        logger.info(f"Email sender response: {response}")
        return True
    except ServiceDBException as err:
        message = f"Connector exception raised while retrieving service record due to {err.args[0]}"
        logger.info(message)


def split_ci_list(ci_list, chunk_size):
    return [ci_list[index : index + chunk_size] for index in range(0, len(ci_list), chunk_size)]
