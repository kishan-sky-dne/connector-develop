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
import re

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.services.lookup.local_hostname_mapping import GROUP_MAPPING, generate_local_mapping
from connectors.core.services.plannet.connector import PlannetService
from connectors.core.utils.exceptions import RestUtilityException

logger = logging.getLogger(__name__)


class Domain:
    """
    Class for network domain related queries and operations
    """

    def __init__(self):
        self.plannet = PlannetService()
        self.plannet_domain_endpoint = config.get(section="plannet", key="network_domain_endpoint")

    def get_network_domain(self, hostname):
        """
        Function to get network domain for a given hostname.
        First tries the plannet API.
        Uses local mapping function as a backup.

        Args:
            hostname (string): hostname to query

        Returns:
            dict: TSR domain of the queried hostname
        """

        response = self.get_plannet_domain(hostname)

        return response or self.get_local_domain(hostname)

    def get_local_domain(self, hostname):
        """
        Function to get network domain for a given hostname using the local mapping file.

        Args:
            hostname (string): hostname to query

        Returns:
            dict: TSR domain of the queried hostname
        """

        group = self.get_local_group(hostname)

        for pattern in generate_local_mapping():
            regex_pattern = pattern.get("regex_pattern")
            if re.search(regex_pattern, hostname):
                domain = pattern["tsr_domain"]
                role = pattern.get("role", "unclassified")
                readable_role = pattern.get("readable_role", "unclassified")
                return {
                    "network-domain": domain,
                    "role": role,
                    "readable_role": readable_role,
                    "sky-group": group,
                    "data-source": "local",
                }
        return None

    def get_local_group(self, hostname):
        """
        Function to get Sky Group for a given hostname using the local mapping file.

        Args:
            hostname (string): hostname to query

        Returns:
            string: Sky group of the queried hostname, defaults to "UK".
        """
        sky_group = "UK"
        for group in GROUP_MAPPING:
            regex_pattern = group.get("regex_pattern")
            if re.search(regex_pattern, hostname):
                sky_group = group.get("group")
                break

        return sky_group

    def get_plannet_domain(self, hostname):
        """
        Function to get network domain for a given hostname using plannet.

        Args:
            hostname (string): hostname to query

        Returns:
            dict: TSR domain of the queried hostname for success, or False for 500 plannet exception.
        """

        if not self.plannet_domain_endpoint:
            return False

        url = f"{self.plannet_domain_endpoint}/{hostname}"
        kwargs = {"url": url}
        logger.debug(f"Connecting to plannet to retrieve TSR domain info for {hostname}")
        try:
            response = self.plannet.get_plannet_details(**kwargs)
            return {
                "network-domain": response.get("network-domain"),
                "sky-group": "UK",
                "data-source": "plannet",
            }
        except RestUtilityException as e:
            code = e.response.status_code
            return (
                False
                if code >= 500
                else {
                    "status": "failure",
                    "errorCategory": "FAILED",
                    "errors": [
                        {"code": "ERR-010-999-0003", "message": f"PlanNet failed to get network domain for {hostname}"}
                    ],
                }
            )
