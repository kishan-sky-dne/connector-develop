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
from unittest.mock import patch

# DNE Library
from connectors.core.utils.sanitize import encrypt_sensitive_data, sanitize_response

api_resp = {
    "device_type": "CiscoNCS",
    "hostname": "xyz.test.bllab",
    "ipaddr": "2.120.0.21",
    "location": "BLLAB",
    "model": "",
    "model_family": "",
    "os": "",
    "os_version": "7.1.2",
    "tacacs_secret": "fdskfslfkslad",
}

sanitized_resp = {
    "device_type": "CiscoNCS",
    "hostname": "xyz.test.bllab",
    "ipaddr": "2.120.0.21",
    "location": "BLLAB",
    "model": "",
    "model_family": "",
    "os": "",
    "os_version": "7.1.2",
}


def test_sanitize_response():
    assert sanitize_response(api_resp) == str(sanitized_resp)
    assert sanitize_response(sanitized_resp) == str(sanitized_resp)
    assert sanitize_response("response") == "response"


@patch("connectors.core.utils.sanitize.encrypt_password")
def test_encrypt_sensitive_data_default_keys(encryption_mock):
    """
    Test the encrypt_sensitive_data function with default keys (tacacs_secret and tacacs_group).
    It should mask the specified keys in the input dictionary at any level.
    """
    encryption_mock.return_value = "xxxxx"
    data = {
        "device_type": "CiscoNCS",
        "hostname": "xyz.test.bllab",
        "tacacs_secret": "top_secret",
        "tacacs_group": "admin",
        "inner_dict": {"tacacs_secret": "top_secret"},
    }
    assert encrypt_sensitive_data(data) == {
        "device_type": "CiscoNCS",
        "hostname": "xyz.test.bllab",
        "tacacs_secret": "xxxxx",
        "tacacs_group": "xxxxx",
        "inner_dict": {"tacacs_secret": "xxxxx"},
    }


@patch("connectors.core.utils.sanitize.encrypt_password")
def test_encrypt_sensitive_data_custom_keys(encryption_mock):
    """
    Test the encrypt_sensitive_data function with custom keys.
    It should mask the specified keys in the input dictionary.
    """
    encryption_mock.return_value = "xxxxx"
    data = {
        "password": "super_secret",
        "tacacs_secret": "top_secret",
        "tacacs_group": "admin",
        "other_secret": "hidden",
    }
    assert encrypt_sensitive_data(data, keys=["tacacs_secret", "other_secret"]) == {
        "password": "super_secret",
        "tacacs_secret": "xxxxx",
        "tacacs_group": "admin",
        "other_secret": "xxxxx",
    }


@patch("connectors.core.utils.sanitize.encrypt_password")
def test_encrypt_sensitive_data_no_keys(encryption_mock):
    """
    Test the encrypt_sensitive_data function with no keys.
    It should not modify the input dictionary since no keys are specified.
    """
    data = {"password": "super_secret", "tacacs_secret": "top_secret", "tacacs_group": "admin"}
    assert encrypt_sensitive_data(data, keys=[]) == {
        "password": "super_secret",
        "tacacs_secret": "top_secret",
        "tacacs_group": "admin",
    }


@patch("connectors.core.utils.sanitize.encrypt_password")
def test_encrypt_sensitive_data_empty_dict(encryption_mock):
    """
    Test the encrypt_sensitive_data function with an empty dictionary.
    It should return an empty dictionary since there are no keys to mask.
    """
    assert encrypt_sensitive_data({}) == {}


def test_encrypt_sensitive_data_no_tacacs_value():
    """
    Test the encrypt_sensitive_data function with None and empty values
    It should not modify the input dictionary.
    """
    data = {"tacacs_secret": "", "tacacs_group": None}
    assert encrypt_sensitive_data(data) == {"tacacs_secret": "", "tacacs_group": None}


def test_encrypt_sensitive_data_no_tacacs_key():
    """
    Test the encrypt_sensitive_data function with no tacacs key in data.
    It should not modify the input dictionary.
    """
    data = {"tacacs_group": None}
    assert encrypt_sensitive_data(data) == {"tacacs_group": None}
