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
import re
from unittest.mock import patch

# Third Party Library
import pytest

# DNE Library
from connectors.core.services.lookup.local_hostname_mapping import (
    GROUP_MAPPING,
    HOSTNAME_MAPPING,
    generate_local_mapping,
    validate_tsr_envvar_entry,
)


def test_all_hostname_entries_satisfy_regex():
    """
    Test that every pattern in the `HOSTNAME_MAPPING` list is valid regex.
    """
    for pattern in HOSTNAME_MAPPING:
        try:
            re.compile(pattern["regex_pattern"])
        except re.error:
            pytest.fail(f"Pattern {pattern['regex_pattern']} is not valid regex")


def test_all_entries_are_correctly_formatted():
    """
    Test that each entry in the local mapping file is in the form:
    (<str>, {"readable_pattern": <str>, "tsr_domain": <str>})

    Where "tsr_domain" must be in ["core", "metro", "access", "voice", "mobile", "legacy"]
    """
    for pattern in HOSTNAME_MAPPING:

        if not isinstance(pattern, dict):
            pytest.fail(f"Pattern {pattern} is not correctly formatted")

        if any(x not in pattern.keys() for x in ["readable_pattern", "tsr_domain", "regex_pattern"]):
            pytest.fail(f"Entry {pattern} does not contain the required key-values")

        if any(not isinstance(pattern[x], str) for x in ["readable_pattern", "tsr_domain", "regex_pattern"]):
            pytest.fail(f"Entry {pattern[1]} values are not strings")


def test_all_group_entries_satisfy_regex():
    """
    Test that every pattern in the `GROUP_MAPPING` list is valid regex.
    """
    for pattern in GROUP_MAPPING:
        try:
            re.compile(pattern["regex_pattern"])
        except re.error:
            pytest.fail(f"Pattern {pattern['regex_pattern']} is not valid regex")


@patch("connectors.core.config.connectors_config.config")
def test_generate_local_mapping_no_envvar(config_mock):
    """
    Test that `generate_local_mapping` returns HOSTNAME_MAPPING if no env var given
    """

    config_mock.get.return_value = None

    assert generate_local_mapping() == HOSTNAME_MAPPING


@patch("connectors.core.services.lookup.local_hostname_mapping.config")
@patch("connectors.core.services.lookup.local_hostname_mapping.validate_tsr_envvar_entry")
@patch("connectors.core.services.lookup.local_hostname_mapping.ast.literal_eval")
def test_generate_local_mapping_calls_validate_tsr_envvar_entry(eval_mock, validate_mock, config_mock):
    """
    Test that `generate_local_mapping` calls `validate_tsr_envvar_entry` for each env var entry
    """

    config_mock.get.return_value = True  # "[{'test'}, {'test2'}]"
    eval_mock.return_value = [{}, {}]
    generate_local_mapping()

    assert validate_mock.call_count == 2


@patch("connectors.core.services.lookup.local_hostname_mapping.config")
@patch("connectors.core.services.lookup.local_hostname_mapping.ast.literal_eval")
def test_generate_local_mapping_failure_1(eval_mock, config_mock):
    """
    Test that `generate_local_mapping` returns HOSTNAME_MAPPING if validation fails for env vars.
    """

    config_mock.get.return_value = "[{'test'}, {'test2'}]"
    eval_mock.side_effect = SyntaxError

    assert generate_local_mapping() == HOSTNAME_MAPPING


@patch("connectors.core.services.lookup.local_hostname_mapping.config")
@patch("connectors.core.services.lookup.local_hostname_mapping.ast.literal_eval")
def test_generate_local_mapping_failure_2(eval_mock, config_mock):
    """
    Test that `generate_local_mapping` returns HOSTNAME_MAPPING if validation fails for env vars.
    """

    config_mock.get.return_value = "[{'test'}, {'test2'}]"
    eval_mock.return_value = "string"

    assert generate_local_mapping() == HOSTNAME_MAPPING


@patch("connectors.core.services.lookup.local_hostname_mapping.config")
@patch("connectors.core.services.lookup.local_hostname_mapping.validate_tsr_envvar_entry")
@patch("connectors.core.services.lookup.local_hostname_mapping.ast.literal_eval")
def test_generate_local_mapping_validate_failure(eval_mock, validate_mock, config_mock):
    """
    Test that `generate_local_mapping` returns HOSTNAME_MAPPING if validation fails for env vars.
    """

    config_mock.get.return_value = "[{'test'}, {'test2'}]"
    eval_mock.return_value = [{}, {}]
    validate_mock.return_value = False
    assert generate_local_mapping() == HOSTNAME_MAPPING


@patch("connectors.core.services.lookup.local_hostname_mapping.config")
@patch("connectors.core.services.lookup.local_hostname_mapping.validate_tsr_envvar_entry")
@patch("connectors.core.services.lookup.local_hostname_mapping.ast.literal_eval")
def test_generate_local_mapping_inserts_at_top(eval_mock, validate_mock, config_mock):
    """
    Test that `generate_local_mapping` inserts the env var at the top of the list if requested.
    """

    config_mock.get.return_value = "[{'test'}, {'test2'}]"
    eval_mock.return_value = [{"regex_pattern": "test", "tsr_domain": "test_domain", "insert_at": "top"}]
    validate_mock.return_value = True
    assert generate_local_mapping()[0] == {"regex_pattern": "test", "tsr_domain": "test_domain", "insert_at": "top"}


@patch("connectors.core.services.lookup.local_hostname_mapping.config")
@patch("connectors.core.services.lookup.local_hostname_mapping.validate_tsr_envvar_entry")
@patch("connectors.core.services.lookup.local_hostname_mapping.ast.literal_eval")
def test_generate_local_mapping_inserts_at_bottom(eval_mock, validate_mock, config_mock):
    """
    Test that `generate_local_mapping` inserts the env var at the bottom of the list by default
    """

    config_mock.get.return_value = "[{'test'}, {'test2'}]"
    eval_mock.return_value = [{"regex_pattern": "test", "tsr_domain": "test_domain"}]
    validate_mock.return_value = True
    assert generate_local_mapping()[-1] == {"regex_pattern": "test", "tsr_domain": "test_domain"}


cases = [
    ("test_string", False),
    ({"regex_patern": "value", "tsr_domain": "metro"}, False),
    ({"regex_pattern": "value", "tsrr_domain": "core"}, False),
    ({"regex_pattern": "value", "tsr_domain": "bad_domain"}, False),
    ({"regex_pattern": "(bad_regex", "tsr_domain": "core"}, False),
    ({"regex_pattern": r"^good_regex\.", "tsr_domain": "core"}, True),
]


@pytest.mark.parametrize("input, expected", cases)
def test_validate_tsr_envvar_entry(input, expected):
    """
    Test that `validate_tsr_envvar_entry` returns True or False for various validation examples.
    """

    assert validate_tsr_envvar_entry(input) == expected
