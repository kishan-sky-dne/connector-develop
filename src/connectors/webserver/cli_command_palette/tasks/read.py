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
from connectors.core.services.cli_command_palette.cli_command_palette import CliCommands
from connectors.core.utils.helpers import exception_handler

logger = logging.getLogger(__name__)


@exception_handler
def get_commands(**kwargs):
    """
    calls cli_command_palette module to retrieve device specific cli commands
    kwargs:
        vendor(string)
        model(string)
        platform(string)
        version(string)
    Returns:
        List of CLI commands
    """
    vendor = kwargs["vendor"]
    platform = kwargs["platform"]
    model = kwargs.get("model")
    version = kwargs.get("version")
    logger.info(
        "Entering into cli_command_palette module to fetch cli commands for device "
        f"vendor:{vendor}, model:{model}, platform:{platform}, version:{version}"
    )
    commands = CliCommands(**kwargs).get_commands()
    logger.info("Exiting cli_command_palette module")
    return commands
