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
# from unittest.mock import AsyncMock, MagicMock, patch
#
# # Third Party Library
# import pytest
# from aiohttp import ClientSession
#
# # DNE Library
# from connectors.core.services.itsm import aio_connector
#
# # from connectors.core.utils.exceptions import GenericConnectorsException
#
#
# # class AsyncMock(MagicMock):
# #     async def __call__(self, *args, **kwargs):
# #         return super(AsyncMock, self).__call__(*args, **kwargs)
#
#
# @patch("connectors.core.services.itsm.aio_connector.SparkTicketService._srv3800_get_ci_relationship")
# @pytest.mark.parametrize("db_table", ["cmdb_rel_ci"])
# @pytest.mark.parametrize("ci_filter", ["child", "parent", "abcd"])
# @pytest.mark.parametrize("ci_list", ["ma0.bllabd1", "me1.bllabd2", "UK - Core Network - Transport Aggregation (TA)"])
# @pytest.mark.asyncio
# async def test_service3800_success(mock_srv3800_ci_rel, db_table, ci_filter, ci_list):
#     """
#     positive test case to validate service3800 success scenario
#     """
#     await mock_srv3800_ci_rel(ci_list=ci_list, ci_role=ci_filter)
#     expected_response = [
#         {
#             "parentCI": "None",
#             "childCI": "ma0.bllabd4",
#             "relationshipType": "NA",
#             "relationshipStatus": "CI not found or there are no relationships",
#         },
#         {
#             "parentCI": "None",
#             "childCI": "ma0.bllabd5",
#             "relationshipType": "NA",
#             "relationshipStatus": "CI not found or there are no relationships",
#         },
#         {
#             "parentCI": "UK - Wholesale Ethernet - Entanet Ethernet",
#             "childCI": "me0.mypon.isp.sky.com",
#             "relationshipType": "Depends on::Used by",
#             "relationshipStatus": "present",
#         },
#         {
#             "parentCI": "ONEA45266093",
#             "childCI": "me0.mypon.isp.sky.com",
#             "relationshipType": "Depends on::Used by",
#             "relationshipStatus": "present",
#         },
#     ]
#     mock_srv3800_ci_rel.return_value = expected_response
#     spark = aio_connector.SparkTicketService()
#     spark_response = await spark.service3800(table=db_table, ci_list=ci_list, filter=ci_filter)
#     assert spark_response == expected_response
#
#
# @patch("connectors.core.services.itsm.aio_connector.SparkTicketService._srv3800_get_ci_relationship")
# @pytest.mark.parametrize("db_table", ["abcd"])
# @pytest.mark.parametrize("ci_filter", ["child", "parent", "abcd"])
# @pytest.mark.parametrize("ci_list", ["ma0.bllabd1", "me1.bllabd2", "UK - Core Network - Transport Aggregation (TA)"])
# @pytest.mark.asyncio
# async def test_service3800_not_supported_table(mock_srv3800_ci_rel, db_table, ci_filter, ci_list):
#     """
#     Negative test case to validate service3800 failure scenario
#     """
#     await mock_srv3800_ci_rel(ci_list=ci_list, ci_role=ci_filter)
#     expected_response = f"The given {db_table} is currently not supported"
#     mock_srv3800_ci_rel.return_value = expected_response
#     spark = aio_connector.SparkTicketService()
#     spark_response = await spark.service3800(table=db_table, ci_list=ci_list, filter=ci_filter)
#     assert spark_response == expected_response
#
#
# @patch("connectors.core.services.itsm.aio_connector.SparkTicketService.spark_request")
# @pytest.mark.asyncio
# async def test_srv3800_get_ci_relationship_case1(mock_spark_request):
#     """
#     positive test case to validate srv3800_get_ci_relationship success scenario
#     """
#     dummy_url = "https://sparkproxyuat.azure-api.net/service3800/"
#     await mock_spark_request(method="post", session=ClientSession(), url=dummy_url, headers=None)
#     ci_list = ["ma0.bllabd1"]
#     ci_filter = "child"
#     spark = aio_connector.SparkTicketService()
#
#     base_url = "https://sparkproxyuat.azure-api.net//service3800/"
#     expected_response = {'result': [
#         {
#             "parentCI": None,
#             "childCI": "ma0.bllabd1",
#             # "relationshipType": None,
#             "relationshipStatus": "CI not found or there are no relationships or resource not found",
#             "getUrlPath": f"{base_url}request?db_table=cmdb_rel_ci&query_filter=child.name%3Dma0.bllabd1",
#             "action": "read"
#         }
#     ]}
#     mock_spark_request.return_value = expected_response
#     spark_response = await spark._srv3800_get_ci_relationship(
#     ci_list=ci_list, ci_role=ci_filter
#     )
#     # POP 'error': <AsyncMock name='mock.get()' id='140529561037648> as this a dynamic Mock instance
#     #spark_response["result"][0].pop("error")
#     assert spark_response == expected_response
#
# spark_request_response1 = [
#     {
#         "parentCI": "UK - Metro Network - Metro Aggregation (MA)",
#         "relationshipType": "Depends on::Used by",
#         "childCI": "me0.mypon.isp.sky.com",
#         "action": "add",
#         "relationshipStatus": (
#             "Created relationship for 'UK - Metro Network - Metro Aggregation (MA) <<>> me0.mypon.isp.sky.com"
#         ),
#     }
# ]
#
# spark_request_response2 = [
#     {
#         "parentCI": "UK - Metro Network - Metro Aggregation (MA)",
#         "relationshipType": "Depends on::Used by",
#         "childCI": "me0.mypon.isp.sky.com",
#         "action": "remove",
#         "relationshipStatus": (
#             "Removed relationship 'UK - Metro Network - Metro Aggregation (MA) <<>> me0.mypon.isp.sky.com"
#         ),
#     }
# ]
#
# srv_builder_response1 = [
#     {
#         "parentCI": "UK - Metro Network - Metro Aggregation (MA)",
#         "relationshipType": "Depends on::Used by",
#         "childCI": "me0.mypon.isp.sky.com",
#         "action": "add",
#         "relationshipStatus": (
#             "Created relationship for 'UK - Metro Network - Metro Aggregation (MA) <<>> me0.mypon.isp.sky.com"
#         ),
#     }
# ]
#
# srv_builder_response2 = [
#     {
#         "action": "remove",
#         "childCI": "me0.mypon.isp.sky.com",
#         "parentCI": "UK - Metro Network - Metro Aggregation (MA)",
#         "relationshipType": "Depends on::Used by",
#         "relationshipStatus": (
#             "Removed relationship 'UK - Metro Network - Metro Aggregation (MA) <<>> me0.mypon.isp.sky.com"
#         ),
#     }
# ]
#
#
# @patch("connectors.core.services.itsm.aio_connector.SparkTicketService.spark_request")
# @pytest.mark.asyncio
# async def test_service3605_case1(mock_spark_request):
#     """
#     positive test case to validate service3605 success scenario
#     """
#     dummy_url = "https://sparkproxyuat.azure-api.net/service3605/"
#     await mock_spark_request(method="post", session=ClientSession(), url=dummy_url, headers=None)
#     payload = {"ciRelationships": []}
#     spark = aio_connector.SparkTicketService()
#     expected_response = {'results': {'failure': [], 'success': []}, 'status': 'SUCCESS'}
#     mock_spark_request.retrun_value = expected_response
#     spark_response = await spark.service3605(body=payload)
#     assert spark_response == expected_response
#
#
# @patch("connectors.core.services.itsm.aio_connector.SparkTicketService.spark_request")
# @patch("connectors.core.services.itsm.aio_connector.SparkTicketService._srv3605_response_builder")
# @pytest.mark.asyncio
# async def test_service3605_case2(mock_spark_request, mock_srv3605_response):
#     """
#     positive test case 2 to validate service3605 success scenario
#     """
#     payload = {
#         "ciRelationships": [
#             {
#                 "parentCI": "UK - Metro Network - Metro Aggregation (MA)",
#                 "relationshipType": "Depends on::Used by",
#                 "childCI": "me0.mypon.isp.sky.com",
#                 "action": "add",
#             }
#         ]
#     }
#     spark = aio_connector.SparkTicketService()
#     expected_response = {
#         "results": {"failure": [],
#                     "success": [
#                         {
#                             "action": "add",
#                             "childCI": "me0.mypon.isp.sky.com",
#                             "parentCI": "UK - Metro Network - Metro Aggregation (MA)",
#                             "relationshipType": "Depends on::Used by",
#                             "relationshipStatus": (
#                                 "Created relationship for 'UK - Metro Network - Metro Aggregation (MA) <<>> "
#                                 "me0.mypon.isp.sky.com"
#                             ),
#                         }
#                     ]
#                     },
#         "status": "SUCCESS",
#     }
#     mock_spark_request.return_value = spark_request_response1, [], "SUCCESS"
#     mock_srv3605_response.return_value = srv_builder_response1, [], "SUCCESS"
#     spark_response = await spark.service3605(body=payload)
#     assert spark_response == expected_response
#
#
# @patch("connectors.core.services.itsm.aio_connector.SparkTicketService.spark_request")
# @patch("connectors.core.services.itsm.aio_connector.SparkTicketService._srv3605_response_builder")
# @pytest.mark.asyncio
# async def test_service3605_case3(mock_spark_request, mock_srv3605_response):
#     """
#     positive test case 3 to validate service3605 success scenario
#     """
#     payload = {
#         "ciRelationships": [
#             {
#                 "parentCI": "UK - Metro Network - Metro Aggregation (MA)",
#                 "relationshipType": "Depends on::Used by",
#                 "childCI": "me0.mypon.isp.sky.com",
#                 "action": "remove",
#             }
#         ]
#     }
#     spark = aio_connector.SparkTicketService()
#     spark.aio_rest = AsyncMock()
#     expected_response = {
#         "results": {"failure": [],
#                     "success": [
#                         {
#                             "action": "remove",
#                             "childCI": "me0.mypon.isp.sky.com",
#                             "parentCI": "UK - Metro Network - Metro Aggregation (MA)",
#                             "relationshipType": "Depends on::Used by",
#                             "relationshipStatus": (
#                                 "Removed relationship 'UK - Metro Network - Metro Aggregation (MA) "
#                                 "<<>> me0.mypon.isp.sky.com"
#                             ),
#                         }
#                     ],
#                     },
#         "status": "SUCCESS",
#     }
#     mock_spark_request.return_value = spark_request_response2, [], "SUCCESS"
#     mock_srv3605_response.return_value = srv_builder_response2, [], "SUCCESS"
#     spark_response = await spark.service3605(body=payload)
#     assert spark_response == expected_response
#
#
# @pytest.mark.asyncio
# async def test_service3605_case4():
#     """
#     Negative test case to validate service3605 failure scenario
#     """
#     payload = {
#         "ciRelationships": [
#             {
#                 "parentCI": "UK - Metro Network - Metro Aggregation (MA)",
#                 "relationshipType": "Depends on::Used by",
#                 "childCI": "me0.mypon.isp.sky.com",
#                 "action": "add",
#             }
#         ]
#     }
#     spark = aio_connector.SparkTicketService()
#     spark.aio_rest = AsyncMock()
#     expected_response = {
#         "results": [
#             {
#                 "parentCI": "UK - Metro Network - Metro Aggregation (MA)",
#                 "relationshipType": "Depends on::Used by",
#                 "childCI": "me0.mypon.isp.sky.com",
#                 "action": "remove",
#             }
#         ]
#     }
#     spark_response = await spark.service3605(body=payload)
#     assert spark_response != expected_response
#
#
# @patch("connectors.core.services.itsm.aio_connector.SparkTicketService.spark_request")
# @patch("connectors.core.services.itsm.aio_connector.SparkTicketService._srv3605_response_builder")
# @pytest.mark.asyncio
# async def test_service3605_raises_exception(mock_spark_request, mock_srv3605_response):
#     """
#     positive test case 3 to validate service3605 success scenario
#     """
#     payload = {
#         "ciRelationships": [
#             {
#                 "parentCI": "UK - Metro Network - Metro Aggregation (MA)",
#                 "relationshipType": "Depends on::Used by",
#                 "childCI": "me0.mypon.isp.sky.com",
#                 "action": "remove",
#             }
#         ]
#     }
#     spark = aio_connector.SparkTicketService()
#     spark.aio_rest = AsyncMock()
#     expected_response = {'errorCategory': 'FAILED',
#                          'errors': [
#                              {'code': 'ERR-002-999-0001', 'message': "cannot unpack non-iterable Exception object"}
#                          ]
#                          }
#     mock_spark_request.return_value = Exception("dummy error")
#     mock_srv3605_response.side_effect = Exception("dummy error")
#     spark_response = await spark.service3605(body=payload)
#     assert spark_response == expected_response
#
#
# async def test_srv3605_response_builder_case1():
#     """
#     positive test case to validate srv3605_response_builder success scenario
#     """
#     ci_relationships = [
#         {
#             "action": "add",
#             "childCI": "me0.mypon.isp.sky.com",
#             "parentCI": "UK - Metro Network - Metro Aggregation (MA)",
#             "relationshipType": "Depends on::Used by",
#         }
#     ]
#     list_of_urls = [
#         "https://sparkproxyuat.azure-api.net//service3605/request?action=remove&parent_ci=UK - "
#         "Metro Network - Metro Aggregation (MA)&child_ci=me0.mypon.isp.sky.com&relationship_type"
#         "=Depends on::Used by"
#     ]
#     response_json = {
#         "details": ("Created relationship for 'UK - Metro Network - Metro Aggregation (MA) "
#                     "<<>> me0.mypon.isp.sky.com"),
#     }
#     mock_client_obj = AsyncMock()
#     response = MagicMock(result=response_json)
#     mock_client_obj.api_response.return_value = response
#     # expected_response = [
#     #     {
#     #         "action": "add",
#     #         "childCI": "me0.mypon.isp.sky.com",
#     #         "parentCI": "UK - Metro Network - Metro Aggregation (MA)",
#     #         "relationshipType": "Depends on::Used by",
#     #     }
#     # ]
#     spark = aio_connector.SparkTicketService()
#     success_resp, failure_resp, status = await spark._srv3605_response_builder(ci_relationships, mock_client_obj,
#                                                                                list_of_urls)
#     assert success_resp == []
#     assert failure_resp == []
