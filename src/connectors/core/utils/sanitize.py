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
from copy import deepcopy

# Third Party Library
from nested_lookup import nested_alter

# DNE Library
from connectors.core.utils.helpers import encrypt_password

logger = logging.getLogger(__name__)


def sanitize_response(api_response):
    """
    This function removes the sensitive data from the api response if present
    params:
        api_response - api response json object - type dictionary
    returns:
        text format of response object without sensitive data
    """
    try:
        if api_response.get("tacacs_secret", None):  # Fix for DNE-8457
            resp = deepcopy(api_response)
            del resp["tacacs_secret"]
            return str(resp)
        else:
            return str(api_response)
    except (KeyError, TypeError, AttributeError):
        return api_response


def encrypt_sensitive_data(data, keys=None):
    """Takes a dict and encrypts all instances of the specified keys.

    Args:
        data (dict): The dict to encrypt from
        key (list, optional): The keys to encrypt their values. Defaults to ["tacacs_secret", "tacacs_group"].
    Returns:
        dict: the updated dictionary
    """

    if keys is None:
        keys = ["tacacs_secret", "tacacs_group"]
    logger.debug(f"Encrypting the values for {keys}")
    for key in keys:
        nested_alter(data, key, encrypt_password, in_place=True)
    return data
