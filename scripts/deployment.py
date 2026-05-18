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
# """
# This python script is used to dynamically change the namespace and image tag based on the branch name.
# """
# Standard Library
import logging
import os

# Third Party Library
import yaml

logger = logging.getLogger(__name__)

# registry & branch name & setting environment variables based on the branch name
FC_REGISTRY = os.getenv("FC_REGISTRY")
registry = f"{FC_REGISTRY}/ipnd-dne/connectors"
branch = os.getenv("CI_COMMIT_REF_NAME")
protected_branches = ("develop", "test", "stage", "master")

if branch in protected_branches:
    namespace = f"dne-{branch}"
else:
    namespace = "dne-develop"

logger.info(f"Safe loading the deployment.yaml file")
with open("deployment.yaml", "r") as f:
    deployments = yaml.safe_load_all(f)
    logger.info(f"Getting the service from the deployment.yaml")
    service = deployments.__next__()
    logger.info(f"Getting the deployment from the deployment.yaml")
    deployment = deployments.__next__()

logger.info(f"Updating the service, deployment namespace and container tag as per the branch name {branch}")
service["metadata"]["namespace"] = namespace
deployment["metadata"]["namespace"] = namespace
connector = [
    container for container in deployment["spec"]["template"]["spec"]["containers"] if container["name"] == "connectors"
][0]
connector["image"] = f"{registry}:{branch}"

logger.info(f"Updating the deployment.yaml file")
with open("deployment.yaml", "w") as f:
    yaml.safe_dump_all([service, deployment], f)
