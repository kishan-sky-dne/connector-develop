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
from connectors.webserver.cli_command_palette.tasks.read import get_commands

example_kwargs = {"vendor": "cisco", "platform": "iosxr"}


@patch("connectors.webserver.cli_command_palette.tasks.read.CliCommands")
def test_get_commands(cli_commands_mock):
    """
    Test if the landing function calls the CliCommands modules with the given params
    """
    get_commands(**example_kwargs)
    cli_commands_mock.assert_called_once_with(**example_kwargs)
