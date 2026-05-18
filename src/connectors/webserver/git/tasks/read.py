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
import sys
from urllib.parse import quote_plus

# Sky Library
from isp_config import ConfigManagerException

# DNE Library
from connectors.core.config import connectors_config
from connectors.core.services.git.connector import GitService
from connectors.core.utils.helpers import exception_handler

logger = logging.getLogger(__name__)

try:
    config = connectors_config.ConnectorsConfigManager()
    config.load_config()
except ConfigManagerException:
    sys.exit(1)

"""
Git Parameters
"""
base_url = config.get(section="git", key="base_url")
token = config.get(section="git", key="token")
# Instantiating git object
git_obj = GitService()


@exception_handler
def get_file(**kwargs):
    """
    Landing function to fetch repository details from Git inventory
    kwargs:

    returns:

    """
    logger.info("Entering into get_file method to fetch repository details from Git inventory")
    project_id = kwargs.get("projectId")
    file_path = quote_plus(kwargs.get("filePath"))
    kwargs["url"] = f"{base_url}v4/projects/{project_id}/repository/files/{file_path}/raw"
    kwargs["headers"] = {"PRIVATE-TOKEN": token}
    data = git_obj.get_repository_details(**kwargs)
    logger.debug(f"Fetched repository details from git inventory: {data}")
    return data if isinstance(data, dict) else data.text
