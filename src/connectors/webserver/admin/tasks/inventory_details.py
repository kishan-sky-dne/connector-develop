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

# Third Party Library
import connexion

# DNE Library
from connectors.core.services.admin.inventory_details import InventoryDetails
from connectors.core.utils.exceptions import GenericConnectorsException

logger = logging.getLogger(__name__)


def get_inventory_details(**kwargs):
    """
    Method to get inventory details
        Args:
           kwargs: request body
        Returns:
            status as success and details and status failure with error category, message and code
            incase of failure
    """
    try:
        logger.info("Entering into admin module to get inventory details")
        logger.info(kwargs)
        include = kwargs.get("_include")
        if (include is not None) and ("osState" in include):
            include = list(map(lambda x: x.replace("osState", "currentState"), include))
        if not include:
            include = ["deviceVendor", "deviceModel", "region", "deviceRole", "currentState", "packageType", "fileType"]

        inventory_details_obj = InventoryDetails(
            include,
        )
        return inventory_details_obj.get_inventory_details()
    except GenericConnectorsException as err:
        return connexion.problem(
            status=500, title="Connector exception raised while getting inventory details", detail=err.args[0]
        )
