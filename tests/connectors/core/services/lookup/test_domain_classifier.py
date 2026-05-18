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
from unittest.mock import Mock, patch

# Third Party Library
import pytest

# DNE Library
from connectors.core.services.lookup.domain_classifier import Domain
from connectors.core.utils.exceptions import RestUtilityException


@patch("connectors.core.services.lookup.domain_classifier.Domain.get_plannet_domain")
def test_get_network_domain_plannet_success(plannet_mock):
    domain = Domain()
    plannet_mock.return_value = "response"

    assert domain.get_network_domain("test") == "response"
    assert plannet_mock.called_with("test")


@patch("connectors.core.services.lookup.domain_classifier.Domain.get_plannet_domain")
@patch("connectors.core.services.lookup.domain_classifier.Domain.get_local_domain")
def test_get_network_domain_plannet_failure(local_mock, plannet_mock):
    domain = Domain()
    plannet_mock.return_value = None
    local_mock.return_value = "local_response"

    assert domain.get_network_domain("test") == "local_response"
    assert plannet_mock.called_with("test")
    assert local_mock.called_with("test")


@patch("connectors.core.services.lookup.domain_classifier.generate_local_mapping")
def test_get_local_domain(mapping_mock):

    mapping_mock.return_value = [
        {"regex_pattern": r"^me\d\.", "readable_pattern": "me#", "tsr_domain": "metro", "role": "metro"},
        {"regex_pattern": r"^me\d\d\.", "readable_pattern": "me##", "tsr_domain": "metro", "role": "metro"},
    ]
    domain = Domain()
    domain.get_local_group = Mock(return_value="test-group")
    domain.get_local_domain("me20.bllabd2")

    assert mapping_mock.called
    assert domain.get_local_group.called


@patch("connectors.core.services.lookup.domain_classifier.generate_local_mapping")
def test_get_local_domain_no_match(mapping_mock):

    mapping_mock.return_value = [
        {"regex_pattern": r"^me\d\.", "readable_pattern": "me#", "tsr_domain": "metro", "role": "metro"},
        {"regex_pattern": r"^me\d\d\.", "readable_pattern": "me##", "tsr_domain": "metro", "role": "metro"},
    ]
    domain = Domain()
    domain.get_local_group = Mock(return_value="test-group")
    assert domain.get_local_domain("bad_hostname") is None


cases = [
    ("ma0.bllab", "UK"),
    ("ma0.bllab.it.bb.sky.com", "IT"),
]


@pytest.mark.parametrize("input, expected", cases)
def test_get_local_group(input, expected):
    """
    Test `get_local_group` returns the expected value
    """
    domain = Domain()

    assert domain.get_local_group(input) == expected


def test_get_plannet_domain_no_url():
    """
    Test `get_plannet_domain`
    """

    domain = Domain()
    domain.plannet_domain_endpoint = ""

    assert domain.get_plannet_domain("test") is False


def test_get_plannet_domain_calls_plannet_success():
    """
    Test `get_plannet_domain`
    """

    domain = Domain()
    domain.plannet = Mock()
    domain.plannet_domain_endpoint = "/test_endpoint"
    domain.plannet.get_plannet_details.return_value = {"network-domain": "domain"}

    assert domain.get_plannet_domain("test") == {
        "data-source": "plannet",
        "network-domain": "domain",
        "sky-group": "UK",
    }


class Response:
    def __init__(self, status_code):
        self.status_code = status_code


def test_get_plannet_domain_calls_plannet_failure_1():
    """
    Test `get_plannet_domain`
    """
    test_response = Response(500)
    domain = Domain()
    domain.plannet = Mock()
    domain.plannet_domain_endpoint = "/test_endpoint"
    domain.plannet.get_plannet_details.side_effect = RestUtilityException("", response=test_response)

    assert domain.get_plannet_domain("test") is False


def test_get_plannet_domain_calls_plannet_failure_2():
    """
    Test `get_plannet_domain`
    """
    test_response = Response(400)
    domain = Domain()
    domain.plannet = Mock()
    domain.plannet_domain_endpoint = "/test_endpoint"
    domain.plannet.get_plannet_details.side_effect = RestUtilityException("", response=test_response)

    assert domain.get_plannet_domain("test") == {
        "status": "failure",
        "errorCategory": "FAILED",
        "errors": [{"code": "ERR-010-999-0003", "message": "PlanNet failed to get network domain for test"}],
    }
