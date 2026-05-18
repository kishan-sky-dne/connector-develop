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
import functools
import ipaddress
import json
import logging
import random
import re
import string
import time
from typing import Any

# Third Party Library
import connexion
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from jsonschema import Draft201909Validator
from nested_lookup import nested_lookup
from pydantic import ValidationError

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.exceptions import ServiceDBException
from connectors.core.services.itsm.exceptions import DateGeneratorError, DateValidateError, InvalidRequest
from connectors.core.utils.exceptions import (
    ConflictException,
    ConnectorException,
    ConnectorInvalidRequest,
    ResourceServiceNotAvailable,
    RestUtilityException,
    UnauthorizedException,
)

logger = logging.getLogger(__name__)

APP_PATH = config.get(section="internals", key="app_path")
secret_key = config.get(section="internals", key="secret_key")


def generic_secret(length: int = 10) -> str:
    """
    Generates a random string of a given length

    Args:
        length (int, optional): Length of string. Defaults to 10.

    Returns:
        str: Random string of the given length
    """
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def exception_handler(func):  # noqa: C901
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as err:
            logger.exception(err, exc_info=True)
            return connexion.problem(
                status=400,
                title="Data Validation Error",
                detail=err.errors(),
            )
        except UnauthorizedException as err:
            logger.exception(err.args[0], exc_info=True)
            return connexion.problem(
                status=401,
                title=f"Resource system failed with unauthorised exception ",
                detail=err.args[0],
            )
        except ResourceServiceNotAvailable as err:
            logger.exception(err.args[0], exc_info=True)
            return connexion.problem(
                status=404,
                title=f"Resource Service Exception occurred while accessing the URL",
                detail=err.args[0],
            )
        except RestUtilityException as err:
            logger.exception(err.args[0], exc_info=True)
            return connexion.problem(
                status=403,
                title=f"Request Exception while accessing the URL",
                detail=err.args[0],
            )
        except ConnectorException as err:
            logger.exception(err.args[0], exc_info=True)
            return connexion.problem(
                status=500, title=f"Connector exception raised while processing data", detail=err.args[0]
            )
        except ValueError as err:
            logger.exception(err.args[0], exc_info=True)
            return connexion.problem(
                status=400,
                title=f"Error in request body",
                detail=f"`{err.args[0]}` is a required property",
            )
        except (InvalidRequest, ConnectorInvalidRequest) as err:
            logger.exception(err.args[0], exc_info=True)
            return connexion.problem(
                status=400,
                title=f"Invalid Request",
                detail=f"{err.args[0]}",
            )
        except DateGeneratorError as err:
            logger.exception(err.args[0], exc_info=True)
            return connexion.problem(status=400, title=f"Exception occurred while generating date", detail=err.args[0])
        except DateValidateError as err:
            logger.exception(err.args[0], exc_info=True)
            return connexion.problem(
                status=400,
                title=f"Exception occurred while validating date",
                detail=err.__str__(),
            )
        except ConflictException as err:
            logger.exception(err.args[0], exc_info=True)
            return connexion.problem(
                status=409,
                title=f"Conflict exception occurs while processing",
                detail=err.args[0],
            )
        except ServiceDBException as err:
            logger.exception(err.args[0], exc_info=True)
            return connexion.problem(
                status=403,
                title=f"Unable to process the DB Request",
                detail=err.args[0],
            )
        except KeyError as err:
            logger.exception(err.args[0], exc_info=True)
            return connexion.problem(
                status=400,
                title=f"Missing key",
                detail=err.args[0],
            )
        except AttributeError as err:
            logger.exception(err.args[0], exc_info=True)
            return connexion.problem(
                status=400,
                title=f"Method not supported",
                detail=err.args[0],
            )
        except Exception as err:
            logger.exception(err.args[0], exc_info=True)
            return connexion.problem(
                status=500,
                title=f"Internal Server Error occurred",
                detail=err.args[0],
            )

    return wrapper


def validate_json_request_payload(**kwargs):
    """
    Validate json request body
    Request:
        kwargs
    Response:
        Status/Exception
    """
    logger.info(
        f"Entering into validate json request payload " f"module to validate details for {kwargs['usecase']} usecase"
    )
    try:
        request_body = kwargs["body"]
        logger.info(f"Validating {kwargs['usecase']} API params using json schema")
        file_name = f"{APP_PATH}/json_schema/{kwargs['file_path']}.json"
        schema, error_message = load_json_data(file_name, f"{kwargs['usecase']} update details")
        if not schema:
            return False, connexion.problem(
                status=404,
                detail=error_message,
                title="Page Not Found",
            )
        status, detail = validate_json_schema(request_body, schema)
        if not status:
            return False, connexion.problem(
                status=400,
                detail=detail,
                title="Bad Request",
            )
        return status, detail

    except Exception as err:
        message = f"Generic Exception occurred due to {err.args[0]}"
        logger.exception(message, exc_info=True)
        return False, {"errorCategory": "FAILED", "errors": [{"code": "ERR-011-078-1007", "message": message}]}


def validate_json_schema(request_body, schema):
    """
    To validate request body using json schema Draft201909Validator
    """
    error_message = []
    validated_schema = Draft201909Validator(schema)
    errors = sorted(validated_schema.iter_errors(request_body), key=lambda e: e.path)
    for error in errors:
        path = "".join(str(f"[{item}]") for item in error.path)
        if error.context:
            error_message, path = get_suberror(error, error_message, path)
            continue
        error_message.append({error.message: path})
    if errors:
        return False, error_message
    return True, error_message


def get_suberror(error, error_message, path):
    """
    Get the appropriate sub error on json schema validation failure
    Args:
        error:
        error_message:
        path:
    Returns:
        error_message:
        path:
    """
    for suberror in sorted(error.context, key=lambda e: e.schema_path):
        if suberror.context:
            path += "".join(str(f"[{str(item)}]") for item in suberror.path)
            error_message, path = get_suberror(suberror, error_message, path)
            continue
        path += "".join(str(f"[{item}]") for item in suberror.path)
        error_message.append({suberror.message: path})
    return error_message, path


def load_json_data(file_name, use_case):
    """
    To process json file data to dictionary data
    """
    try:
        logger.info(f"Processing json file {file_name} for usecase {use_case}")
        json_schema = open(file_name)
        schema = json.load(json_schema)
        return schema, ""
    except FileNotFoundError as err:
        error_message = f"Json schema file is not available with error: {err}"
        logger.error(error_message)
        return False, error_message


def retry_wrapper(retry_attempts, retry_backoff):
    """
    Retries the wrapped function with given options as long as the function returns False
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retry_attempts):
                if func(*args, **kwargs):
                    if attempt > 0:
                        logger.debug(f"Successfully completed the operation after {attempt+1} attempts")
                    return True
                logger.debug(f"Operation failed. Attempt = {attempt+1}")
                if attempt + 1 != retry_attempts:
                    logger.debug(f"Retrying the last operation after {retry_backoff} seconds.")
                    time.sleep(retry_backoff)
                else:
                    logger.error(f"Operation failed after {retry_attempts} attempts")
                    return False

        return wrapper

    return decorator


def validate_ipv6_prefix(prefix):
    """
        Validates an IPv6 prefix or subnet
    Args:
        prefix
    Returns:
        Boolean
    """
    try:
        ipaddress.IPv6Network(prefix)
        return True
    except ValueError:
        return False


def validate_ipv4_prefix(prefix):
    """
        Validates an IPv4 prefix or subnet
    Args:
        prefix
    Returns:
        Boolean
    """
    try:
        ipaddress.IPv4Network(prefix)
        return True
    except ValueError:
        return False


def create_dict_from_string(input_string):
    """
    Workaround for reported json.loads issue on FC.

    Creates a dictionary from the given input string
    Input string should be comma separated key-values with colons

    Example:
        input_string: "key1:value1,key2:value2,key3:value3"
        returned dict: {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}

    """
    my_dict = {}
    if not input_string:
        return my_dict

    key_value_pairs = input_string.split(",")

    for pair in key_value_pairs:
        key, value = pair.split(":")
        key = key.strip()
        value = value.strip()
        my_dict[key] = value

    return my_dict


def encrypt_password(password: str | None) -> str | None:
    """
        The method encrypts the given password
        Note: Password Size must be 16
    Args:
        password: The password to be encrypted

    Returns:
        STRING (The Base 64 encoded encrypted password)

    """
    if not password:
        return password
    iv = Random.new().read(AES.block_size)
    obj = AES.new(secret_key.encode("utf-8"), AES.MODE_CBC, iv)
    encrypted_password = iv + obj.encrypt(pad(password.encode("utf-8"), AES.block_size))
    return base64.b64encode(encrypted_password).decode("utf-8")


def decrypt_password(password: str | None) -> str | None:
    """
        The method decrypts the given password
        Expectation: Base64 Encoded AES Encrypted Password
    Args:
        password: The password to be decrypted

    Returns:
        STRING (The clear text password)
    """
    if not password:
        return password
    password = base64.b64decode(password)
    iv = password[: AES.block_size]
    obj = AES.new(secret_key.encode("utf-8"), AES.MODE_CBC, iv)
    return unpad(obj.decrypt(password[AES.block_size :]), AES.block_size).decode("utf-8")


def ignore_similar_conflicts_with_pattern(change_req_list: list[dict], pattern: list[str]) -> list[dict]:
    """
    Removes the items from 'change_req_list' that have all 'pattern' list substrings
    in their 'short_description'. Case insensitive.
    """
    if not change_req_list or not pattern:
        return change_req_list

    filtered_list = []
    for item in change_req_list:
        if any(substrings.lower() not in item.get("task.short_description", "").lower() for substrings in pattern):
            filtered_list.append(item)
        else:
            logger.info(f"Ignoring {item} as its short_description matches similar_change_pattern {pattern}")
    return filtered_list


def key_in_dict(
    key: str | int, targe_dict: dict | list, default_value: Any = "", wild: bool = False, with_keys: bool = False
) -> list[int | str | dict | list] | Any:

    """
    Method to parse a key in nested object and return the value
    Args:
        key (str | int): the key you are looking for
        targe_dict (dict | list): the dict you want to search
        default_value (Any, optional): Default value you want to return in case of no key found. Defaults to ''.
        wild (bool, optional): nested_lookup wild search option. Defaults to False.
        with_keys (bool, optional): nested_lookup will return a dict with key and values. Defaults to False.

    Returns:
        list[int|str|dict|list] | Any
    """
    result = nested_lookup(key, targe_dict, wild, with_keys)
    return result if len(result) > 0 else default_value


def generate_hostname(domains: str, hostname: str) -> str:
    """
    Method to generate generic hostname based on the regional domain names provided.

    Args:
        domains: isp.sky.com it.bb.sky.com uk.easynet.net
        hostname: ta0.dev-uk.bllab.isp.sky.com
    Returns:
        ta0.dev-uk.bllab
    """
    return next(
        (re.split(domain, hostname)[0][:-1] for domain in domains.split() if re.search(domain, hostname)),
        hostname,
    )
