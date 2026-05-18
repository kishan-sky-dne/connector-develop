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
from connectors.core.services.radius.connector import error_updation, ipv4_validate, ipv6_validate, pre_value_update
from connectors.core.utils.helpers import exception_handler

logger = logging.getLogger(__name__)


@ipv4_validate
@ipv6_validate
@exception_handler
@pre_value_update
def create_bmr(**kwargs):
    """_summary_

    Returns:
        _type_: _description_
    """
    logger.info(f"Inside create_bmr kwargs {kwargs}")
    status_code = ""
    return_value = None
    if not kwargs.get("status"):
        message = "Failed to Create BMR record: "
        kwargs["message"] = message + kwargs.get("message", "")
        return_value, status_code = error_updation(kwargs)
    else:
        status_code = 200
        radius = kwargs.get("radius_obj")
        response_value = radius.add_bmr_details(**kwargs)
        logger.info(f"response_value {response_value}")
        if response_value and str(response_value.get("status_code")) == "200":
            return_value = {"status": "SUCCESS", "seqid": response_value.get("seqid")}
        else:
            kwargs = kwargs | (response_value if isinstance(response_value, dict) else {}) | {"status": False}
            return_value, status_code = create_bmr(**kwargs)
    logger.info(f"Exit create_bmr return_value {return_value}")
    return return_value, 200


@ipv6_validate
@exception_handler
@pre_value_update
def delete_bmr_by_ip(**kwargs):
    """_summary_

    Returns:
        _type_: _description_
    """
    logger.info(f"Inside delete_bmr_by_ip kwargs {kwargs}")
    status_code = ""
    return_value = None
    if not kwargs.get("status"):
        message = f"Failed to delete BMR record for prefix '{kwargs.get('ipv6Prefix')}': "
        kwargs["message"] = message + kwargs.get("message", "")
        return_value, status_code = error_updation(kwargs)
    else:
        radius = kwargs.get("radius_obj")
        response_value, status_code = radius.delete_bmr_details(**kwargs)
        logger.info(f"response {response_value}")
        if str(status_code) == "200":
            return_value = {"status": "SUCCESS", "seqid": response_value.get("seqid", "")}
        else:
            kwargs = kwargs | (response_value if isinstance(response_value, dict) else {}) | {"status": False}
            return_value, status_code = delete_bmr_by_ip(**kwargs)
    logger.info(f"Exit delete_bmr_by_ip return_value {return_value}")
    return return_value, 200
