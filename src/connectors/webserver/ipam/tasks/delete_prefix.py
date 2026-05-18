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
from connectors.core.services.ipam.connector import DeletePrefix
from connectors.core.utils.exceptions import ConnectorException, RestUtilityException

logger = logging.getLogger(__name__)


def delete_netbox_prefix(**kwargs):
    """
    Method to delete the provided prefix
    Args:
        kwargs: ID
    Returns:
            status as success and for status failure have error code with message
    """
    logger.info(f"Entering into IPAM module to delete prefix for {kwargs['ID']}")
    try:
        ipam = DeletePrefix(kwargs)
        return ipam.delete_prefix()
    except RestUtilityException as err:
        return connexion.problem(
            status=403,
            title=f"Request Exception while accessing the URL",
            detail=err.args[0],
        )
    except ConnectorException as err:
        return connexion.problem(
            status=403,
            title=f"Error while accessing response",
            detail=err.args[0],
        )
    except Exception as err:
        logger.exception(f"{err.args[0]} while deleting the provided prefix")
        connexion.problem(
            status=500,
            title=f"Deleting the provided prefix failed",
            detail=f"Exception raised while deleting the provided Prefix",
        )
