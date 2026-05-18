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
from connectors.core.services.git.connector import GitService
from connectors.core.utils.helpers import generic_secret

secret = generic_secret()

# This is a random token for testing purposes
access_token = secret
kwargs = {"url": "v4/projects/1/repository/files/test.tct/raw", "headers": {"PRIVATE-TOKEN": access_token}}

git_response = "This is a response"


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
@patch("connectors.core.utils.oauth.token_generator")
def test_get_repository_details(mock_token_generator, get_mocked):
    """
    Test to check the functionality of get_repository_details()
    """
    git_file = GitService()
    get_mocked.return_value = git_response
    output = git_file.get_repository_details(**kwargs)
    assert output == git_response
