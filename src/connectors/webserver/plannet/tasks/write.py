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
import json
import logging

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.services.plannet.connector import PlannetService
from connectors.core.services.plannet.exceptions import InvalidRequest
from connectors.core.utils.exceptions import ConnectorException
from connectors.core.utils.helpers import exception_handler

# from connectors.core.utils.oauth import azure_ad_token_generator

logger = logging.getLogger(__name__)

base_url = config.get(section="plannet", key="base_url")
username = config.get(section="plannet", key="username")
password = config.get(section="plannet", key="password")
token = config.get(section="plannet", key="access_token")


@exception_handler
def udpate_card_details(**kwargs):
    body = kwargs["body"]
    hostname = body["hostname"]
    slot_name = body["slot_name"]
    new_card_type = body.get("card_type")
    new_part_number = body.get("part_number")
    logger.info(f"Entering into PlanNet module to update card details for {body['hostname']}.")
    if not new_card_type and not new_part_number:
        raise InvalidRequest("Invalid request. Must supply either the 'card_type' or 'part_number' attribute.")
    # token = azure_ad_token_generator(ad_username=username, ad_password=password)
    card_id = get_card_id(hostname, slot_name, token)
    if not card_id:
        raise ConnectorException(f"Could not identify card id for slot {slot_name} on {hostname}.")
    new_card_type_id = (
        get_card_type_id(new_card_type, token, match_key="name")
        if new_card_type
        else get_card_type_id(new_part_number, token, match_key="part_number")
    )
    if not new_card_type_id:
        raise ConnectorException(f"Could not identify card type id for {new_card_type or new_part_number}")
    request = {
        "url": f"api/dcim/cards/{card_id}/",
        "headers": {"Content-Type": "application/json", "Authorization": f"Token {token}"},
        "payload": json.dumps({"card_type": new_card_type_id}),
    }
    plannet = PlannetService()
    return plannet.patch_plannet_details(**request)


def get_card_id(hostname, slot_name, token):
    plannet = PlannetService()
    search_url = f"api/dcim/cards?search_ne={hostname}"
    headers = {"Content-Type": "application/json", "Authorization": f"Token {token}"}
    cards = plannet.get_plannet_details(url=search_url, headers=headers)
    return next(
        (card["id"] for card in cards["results"] if card["slot"]["name"] == slot_name and hostname in card["name"]),
        None,
    )


def get_card_type_id(match_value, token, match_key="name"):
    plannet = PlannetService()
    search_url = f"api/dcim/card-types?{match_key}={match_value}"
    headers = {"Content-Type": "application/json", "Authorization": f"Token {token}"}
    card_types = plannet.get_plannet_details(url=search_url, headers=headers)
    return next((card_type["id"] for card_type in card_types["results"] if card_type[match_key] == match_value), None)


@exception_handler
def update_transition_group(**kwargs):
    """
    Update the transition group info

    Returns:
        dict: New transition group info
    """
    body: dict = kwargs["body"]
    tg_id: int = kwargs["id"]
    tg_id = tg_id.lower().replace("tg", "")
    logger.info(f"Entering into PlanNet module to update transition group details for {tg_id}.")
    request: dict = {
        "url": f"api/dcim/tgs/{tg_id}/",
        "headers": {"Content-Type": "application/json", "Authorization": f"Token {token}"},
        "payload": json.dumps(body),
    }
    plannet = PlannetService()
    return plannet.patch_plannet_details(**request)
