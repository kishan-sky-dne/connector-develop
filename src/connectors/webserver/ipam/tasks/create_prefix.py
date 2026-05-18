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
from connectors.core.services.ipam.connector import CreatePrefix
from connectors.core.utils.exceptions import ConnectorException, ResourceServiceNotAvailable, RestUtilityException

logger = logging.getLogger(__name__)


def create_netbox_prefix(**kwargs):
    """
    Method to create the prefix in netbox and get the status
    Args:
        kwargs: prefix, site, vrf, tenant, role, is_pool, description, tags, custom_fields
    Returns:
            status as success if prefix is created successfully
            status as failure with error details if creation fails
    """

    logger.info(f"Creating the provided prefix in netbox {kwargs['body']['prefix']}")

    try:
        status_obj = CreatePrefix(kwargs["body"])
        return status_obj.create_prefix()
    except ResourceServiceNotAvailable as err:
        return connexion.problem(
            status=404,
            title=f"Requested resource is not found",
            detail=err.args[0],
        )
    except RestUtilityException as err:
        return connexion.problem(
            status=403,
            title=f"Request Exception while accessing the URL",
            detail=err.args[0],
        )
    except ConnectorException as err:
        return connexion.problem(
            status=400,
            title=f"Connector exception during prefix validations",
            detail=err.args[0],
        )
    except Exception as err:
        logger.exception(f"{err.args[0]} while reserving the provided IP")
        connexion.problem(
            status=500,
            title=f"Creating the provided prefix failed",
            detail=f"Exception raised while creating the provided prefix",
        )
