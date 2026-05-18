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

# Third Party Library
import pytest

# DNE Library
from connectors.core.exceptions import ServiceDBException
from connectors.core.services.itsm.exceptions import DateGeneratorError, DateValidateError, InvalidRequest
from connectors.core.utils import helpers
from connectors.core.utils.exceptions import (
    ConflictException,
    ConnectorException,
    ResourceServiceNotAvailable,
    RestUtilityException,
    UnauthorizedException,
)
from connectors.core.utils.helpers import (
    create_dict_from_string,
    decrypt_password,
    encrypt_password,
    exception_handler,
    generic_secret,
    ignore_similar_conflicts_with_pattern,
)


@pytest.mark.parametrize(
    "args, expected",
    [
        ([], 10),
        ([50], 50),
        ([0], 0),
    ],
)
def test_generic_secret(args, expected):
    assert len(generic_secret(*args)) == expected


secret = generic_secret()


class ResponseRest400:
    def __init__(self):
        self.status_code = 400


class ResponseRest404:
    def __init__(self):
        self.status_code = 404


@exception_handler
def func1():
    raise UnauthorizedException()


@exception_handler
def func2():
    raise ResourceServiceNotAvailable()


@exception_handler
def func3():
    raise ConnectorException()


@exception_handler
def func4():
    raise ValueError(f"ValueError")


@exception_handler
def func5():
    raise RestUtilityException("Rest Api error")


@exception_handler
def func6():
    raise InvalidRequest("invalid request")


@exception_handler
def func7():
    raise DateGeneratorError("date_generation_issue")


@exception_handler
def func8():
    raise DateValidateError("date_validation_issue")


@exception_handler
def func9():
    raise ConflictException("Conflict_issue")


@exception_handler
def func10():
    raise ServiceDBException("service db exception")


@exception_handler
def func11():
    raise KeyError(f"KeyError")


@exception_handler
def func12():
    raise AttributeError(f"AttributeError")


@exception_handler
def func13():
    raise Exception(f"other Exception")


def test_exception_handler_case1():
    assert func1().status_code == 401
    assert func2().status_code == 404
    assert func3().status_code == 500
    assert func4().status_code == 400
    assert func5().status_code == 403
    assert func6().status_code == 400
    assert func7().status_code == 400
    assert func8().status_code == 400
    assert func9().status_code == 409
    assert func10().status_code == 403
    assert func11().status_code == 400
    assert func12().status_code == 400
    assert func13().status_code == 500


def test_create_dict_from_string():
    """
    test the intended dictionary is created using the input string
    """
    input_string = "key1:value1,key2:value2,key3:value3"
    expected_dictionary = {"key1": "value1", "key2": "value2", "key3": "value3"}
    assert create_dict_from_string(input_string) == expected_dictionary


def test_encrypt_decrypt():
    """
    Test if decrypted password is generated in the original plain text password.
    """
    helpers.secret_key = "MyVeryDummyKeyyy"
    password = secret
    token = encrypt_password(password)
    assert password != token
    assert password == decrypt_password(token)


def test_encrypt_decrypt_none():
    """
    Test if encrypt and decrypt do not change a None value
    """
    password = None
    encrypted = encrypt_password(password)
    assert password == encrypted
    assert password == decrypt_password(encrypted)


def test_encrypt_decrypt_empty():
    """
    Test if encrypt and decrypt do not change an empty value
    """
    password = ""
    encrypted = encrypt_password(password)
    assert password == encrypted
    assert password == decrypt_password(encrypted)


def test_ignore_similar_conflicts_with_pattern_no_pattern_match():
    """
    No modification when not all pattern substrings exist in short_description
    """
    change_req_list = [
        {
            "task.short_description": "[DNE]Draining MAP-T Prefix 2a05:3419:e120::/43 under DNE Order BPM-168459",
            "otherkeys": "dummy",
        },
        {"task.short_description": "A different DNE Order ticket"},
    ]
    pattern = ["WAP Provisioning", "DNE Order"]

    result = ignore_similar_conflicts_with_pattern(change_req_list, pattern)

    assert result == change_req_list


def test_ignore_similar_conflicts_with_pattern_with_pattern_matches():
    """
    Remove item from the list if all substrings (case insensitive) exist in short_description
    """
    change_req_list = [
        {
            "task.short_description": "[DNE]Draining MAP-T Prefix 2a05:3419:e120::/43 under DNE Order BPM-168459",
            "otherkeys": "dummy",
        },
        {"task.short_description": "A different DNE Order ticket"},
        {"task.short_description": "dummy description"},
    ]
    pattern = ["draining map-t", "dne order"]

    result = ignore_similar_conflicts_with_pattern(change_req_list, pattern)

    assert result == [
        {"task.short_description": "A different DNE Order ticket"},
        {"task.short_description": "dummy description"},
    ]


def test_ignore_similar_conflicts_with_pattern_empty_list():
    """
    No list no change
    """
    change_req_list = []
    pattern = ["Draining MAP-T", "DNE Order"]
    assert ignore_similar_conflicts_with_pattern(change_req_list, pattern) == []


def test_ignore_similar_conflicts_with_pattern_empty_pattern():
    """
    No pattern no change
    """
    change_req_list = [
        {
            "task.short_description": "[DNE]Draining MAP-T Prefix 2a05:3419:e120::/43 under DNE Order BPM-168459",
            "otherkeys": "dummy",
        },
        {"task.short_description": "A different DNE Order ticket"},
    ]
    pattern = []
    result = ignore_similar_conflicts_with_pattern(change_req_list, pattern)
    assert result == change_req_list


def test_ignore_similar_conflicts_with_pattern_empty_list_and_pattern():
    """
    No list or pattern no change
    """
    change_req_list = []
    pattern = []
    result = ignore_similar_conflicts_with_pattern(change_req_list, pattern)
    assert result == []


def test_ignore_similar_conflicts_with_pattern_no_short_description_and_pattern():
    """
    No short description no change
    """
    change_req_list = [
        {"otherkeys": "dummy"},
    ]
    pattern = []
    result = ignore_similar_conflicts_with_pattern(change_req_list, pattern)
    assert result == change_req_list


def test_ignore_similar_conflicts_with_pattern_no_short_description():
    """
    No short description no change
    """
    change_req_list = [
        {"otherkeys": "dummy"},
    ]
    pattern = ["Some pattern"]
    result = ignore_similar_conflicts_with_pattern(change_req_list, pattern)
    assert result == change_req_list
