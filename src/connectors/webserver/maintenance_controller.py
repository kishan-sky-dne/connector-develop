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
import os

# Third Party Library
import connexion

# DNE Library
from connectors.core.config.connectors_config import config

APP_PATH = config.get(section="internals", key="app_path")


def maintenance_healthcheck():
    try:
        path = os.path
        container_name = os.environ.get("HOSTNAME")
        service_port = os.environ.get("K8S_ISSUE_SERVICE_PORT")
        if path.isfile(f"{APP_PATH}/maintenance"):
            return connexion.problem(
                status=503,
                title="Service unavailable as maintenance file is found",
                detail=f"Container name {container_name} running with service port {service_port}",
            )
        else:
            return {
                "status": "OK",
                "container_name": os.environ.get("HOSTNAME"),
                "servicePort": os.environ.get("K8S_ISSUE_SERVICE_PORT"),
            }
    except Exception as err:
        return connexion.problem(
            status=404,
            title="Exception while handling the file",
            detail=f"Problems with `{err.args[0]}`",
        )
