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

# DNE Library
from connectors.core.services.radius.connector import error_updation, ipv6_validate, pre_value_update
from connectors.core.utils.helpers import exception_handler

logger = logging.getLogger(__name__)


@exception_handler
@ipv6_validate
@pre_value_update
def get_bmr_by_ip(**kwargs):
    """_summary_

    Returns:
        _type_: _description_
    """
    logger.info(f"Inside get_bmr_by_ip kwargs {kwargs}")
    new_response = None
    status_code = ""
    return_value = None
    if not kwargs.get("status"):
        message = "Failed to fetch BMR records: "
        kwargs["message"] = message + kwargs.get("message", "")
        return_value, status_code = error_updation(kwargs)
    else:
        radius = kwargs.get("radius_obj")
        response_value = radius.get_bmr_details(**kwargs)
        if str(response_value.get("status_code")) == "200":
            status_code = (response_value and response_value.get("status_code", 200)) or 200
            if response_value and response_value.get("message"):
                response_msg = response_value.get("message")
                new_response = {
                    "rule_ipv6_prefix": response_msg.get("ruleipv6prefix"),
                    "rule_ipv4_prefix": response_msg.get("ruleipv4prefix"),
                    "psid_length": response_msg.get("psid_length"),
                    "psid_offset": response_msg.get("psid_offset"),
                    "ea_length": response_msg.get("ea_length"),
                    "seqid": response_msg.get("seqid"),
                    "timestamp": response_msg.get("timestamp"),
                    "objtype": response_msg.get("objtype"),
                }
            return_value = {"bmrRecord": new_response}
        else:
            kwargs = kwargs | (response_value if isinstance(response_value, dict) else {}) | {"status": False}
            return_value, status_code = get_bmr_by_ip(**kwargs)
    logger.info(f"Exit get_bmr_by_ip kwargs {return_value}")
    return return_value, 200


@exception_handler
@pre_value_update
def sync_bmr_by_seq_id(**kwargs):
    """_summary_

    Returns:
        _type_: _description_
    """
    logger.info(f"Inside sync_bmr_by_seq_id kwargs {kwargs}")
    status_code = ""
    return_value = None
    synchronised_value = False
    if not kwargs.get("status"):
        message = "Failed to fetch BMR status: "
        kwargs["message"] = message + kwargs.get("message", "")
        return_value, status_code = error_updation(kwargs)
    else:
        status_code = 200
        radius = kwargs.get("radius_obj")
        logger.info(f"access_token {kwargs.get('access_token')}")
        response = radius.sync_bmr_details(**kwargs)
        if response and str(response.get("status_code")) == "200":
            if (
                response
                and response.get("message", {}).get("BMRStatus", {}).get("synchronised")
                and response.get("message", {}).get("BMRStatus", {}).get("sync_seqid")
                and int(response.get("message", {}).get("BMRStatus", {}).get("sync_seqid")) >= int(kwargs.get("seqid"))
            ):
                synchronised_value = True
            try:
                current_seq_id = response.get("message", {}).get("BMRStatus", {}).get("sync_seqid")
                sync_timestamp = (
                    response.get("message", {})
                    .get("BMRStatus", {})
                    .get("bmr_status_detail", [])[0]
                    .get("timestamp", "")
                )
            except Exception as e:
                logger.exception(f"Exception fetching from api {str(e)}")
                current_seq_id = None
                sync_timestamp = None
            return_value = {
                "synchronised": synchronised_value,
                "requested_sync_seqid": kwargs.get("seqid"),
                "current_sync_seqid": current_seq_id,
                "timestamp": sync_timestamp,
            }
        else:
            kwargs = kwargs | (response if isinstance(response, dict) else {}) | {"status": False}
            return_value, status_code = sync_bmr_by_seq_id(**kwargs)
    logger.info(f"Exit sync_bmr_by_seq_id return_value {return_value}")
    return return_value, 200
