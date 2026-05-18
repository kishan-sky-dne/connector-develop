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
# # Standard Library
# from unittest.mock import AsyncMock, patch
#
# # DNE Library
# from connectors.core.services.itsm.exceptions import ResourceServiceNotAvailable
# from connectors.core.utils.exceptions import RestUtilityException
# from connectors.webserver.itsm.tasks.ciRelationshipUpdater import update_ci_relationships
#
#
# payload = {
#         "ciRelationships": [
#             {
#                 "parentCI": "UK - Metro Network - Metro Aggregation (MA)",
#                 "relationshipType": "Depends on::Used by",
#                 "childCI": "me0.mypon.isp.sky.com",
#                 "action": "add",
#             }
#         ]
#     }
#
#
# @patch("connectors.core.services.itsm.aio_connector.SparkTicketService.service3605")
# def test_ci_relationship_update_case1(mock_aio_srvc3605):
#     """
#     Test to check update_ci_relationships() function success scenario 1
#     """
#     payload = {"ciRelationships": []}
#     expected_return_value = []
#     mock_aio_srvc3605.return_value = expected_return_value
#     response = update_ci_relationships(body=payload)
#     assert response == expected_return_value
#
#
# @patch("connectors.core.services.itsm.aio_connector.SparkTicketService.service3605")
# def test_ci_relationship_update_case2(mock_aio_srvc3605):
#     """
#     Test to check update_ci_relationships() function success scenario 2
#     """
#     expected_return_value = [payload["ciRelationships"][0]]
#     mock_aio_srvc3605.return_value = expected_return_value
#     response = update_ci_relationships(body=payload)
#     assert response == expected_return_value
#
#
# @patch("connectors.core.services.itsm.aio_connector.SparkTicketService.service3605")
# def test_update_ci_relationships_generic_exception(mock_srvc_3800):
#     """
#     Test to check if update_ci_relationships() function causes generic exception
#     """
#     mock_srvc_3800.side_effect = Exception("dummy error")
#     response = update_ci_relationships(body=payload)
#     assert response.body["status"] == 500
#
#
# @patch("connectors.core.services.itsm.aio_connector.SparkTicketService.service3605")
# def test_update_ci_relationships_rest_utility_exception(mock_srvc_3800):
#     """
#     Test to check if update_ci_relationships() function raises rest utility exception.
#     """
#     response = AsyncMock()
#     response.status_code.return_value = 403
#     mock_srvc_3800.side_effect = RestUtilityException("error", response=response)
#     response = update_ci_relationships(body=payload)
#     assert response.body["status"] == 403
#
#
# @patch("connectors.core.services.itsm.aio_connector.SparkTicketService.service3605")
# def test_update_ci_relationships_resource_service_not_available_exception(mock_srvc_3800):
#     """
#     Test to check if update_ci_relationships() function raises ResourceServiceNotAvailable exception
#     """
#     mock_srvc_3800.side_effect = ResourceServiceNotAvailable("dummy error")
#     response = update_ci_relationships(body=payload)
#     assert response.body["status"] == 404
