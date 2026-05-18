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

# DNE Library
from connectors.core.services.cli_command_palette.cli_command_palette import CliCommands

example_kwargs = {"vendor": "cisco", "platform": "iosxr"}


@patch("connectors.core.services.cli_command_palette.cli_command_palette.PostgresSingletonManager")
def test_execute_query(db_mock):
    """
    Test to check query results are converted into a list
    """
    session = Mock()
    session.execute.return_value = [
        {
            "count_sum": 6,
            "command": "show version",
            "target_routers": "ma0.test.bllab.it.bb.sky.com, ma0.test.bllab.it.bb.sky.com",
        }
    ]
    results = CliCommands(**example_kwargs)._execute_query(session)
    assert results == ["show version"]


@patch("connectors.core.services.cli_command_palette.cli_command_palette.PostgresSingletonManager")
def test_get_commands(db_mock):
    """
    Test to check get_commands returns the right response
    """
    cli_commands = CliCommands(**example_kwargs)
    cli_commands._execute_query = Mock(return_value=["show version", "show running-config", "show install active"])
    results = cli_commands.get_commands()
    assert results == ["show version", "show running-config", "show install active"]
    cli_commands._execute_query = Mock(return_value=[])
    results = cli_commands.get_commands()
    assert results.body["title"] == "Data Not Found"


@patch("connectors.core.services.cli_command_palette.cli_command_palette.PostgresSingletonManager")
def test_process_results(db_mock):
    """
    Test to check if hostname is not in target_routers, variables are replaced with <VAR>
    """
    example_kwargs = {"vendor": "cisco", "platform": "iosxr", "hostname": "ta0.test.bllab.it.bb.sky.com"}
    example_results = [
        {
            "count_sum": 6,
            "command": "show int te0/0/0/1",
            "target_routers": "ma0.test.bllab.it.bb.sky.com, ma1.test.bllab.it.bb.sky.com",
        }
    ]
    CliCommands(**example_kwargs)._process_results(example_results)
    assert example_results == [
        {
            "count_sum": 6,
            "command": "show int <VAR>",
            "target_routers": "ma0.test.bllab.it.bb.sky.com, ma1.test.bllab.it.bb.sky.com",
        }
    ]


@patch("connectors.core.services.cli_command_palette.cli_command_palette.PostgresSingletonManager")
def test_process_results_no_change(db_mock):
    """
    Test to check if hostname is in target_routers, results do not change
    """
    example_kwargs = {"vendor": "cisco", "platform": "iosxr", "hostname": "ma0.test.bllab.it.bb.sky.com"}
    example_results = [
        {
            "count_sum": 6,
            "command": "show int te0/0/0/1",
            "target_routers": "ma0.test.bllab.it.bb.sky.com, ma1.test.bllab.it.bb.sky.com",
        }
    ]
    CliCommands(**example_kwargs)._process_results(example_results)
    assert example_results == [
        {
            "count_sum": 6,
            "command": "show int te0/0/0/1",
            "target_routers": "ma0.test.bllab.it.bb.sky.com, ma1.test.bllab.it.bb.sky.com",
        }
    ]
