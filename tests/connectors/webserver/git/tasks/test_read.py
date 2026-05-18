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
from collections import namedtuple
from unittest.mock import Mock, patch

# DNE Library
from connectors.core.services.git.connector import GitService
from connectors.webserver.git.tasks import read

MyStruct = namedtuple("MyStruct", "text")
git_response = MyStruct(text="This is a response")

kwargs = {"projectId": 1, "filePath": "test.txt"}


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_get_files(get_mocked):
    """
    Test to check the functionality of get_inca_details()
    """
    git_file = GitService()
    get_mocked.return_value = git_response
    git_file.get_repository_details = Mock(return_value=git_response)
    output = read.get_file(**kwargs)
    assert output == "This is a response"
