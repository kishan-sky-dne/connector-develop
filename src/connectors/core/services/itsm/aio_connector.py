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
import asyncio
import logging
from random import shuffle

# Third Party Library
import aiohttp
import backoff
from aiohttp.client_exceptions import ClientConnectionError, ClientError, ClientResponseError

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.utils.aiohttp_adapter import AioRestUtility

logger = logging.getLogger(__name__)

itsm_url = config.get(section="itsm", key="url")
itsm_keys = config.get(section="itsm", key="subscription_key").split(",")
error_codes = config.get(section="session", key="error_codes")
error_codes = list(int(i) for i in error_codes.split(","))
backoff_factor = config.get(section="session", key="backoff_factor")
max_retries = config.get(section="session", key="max_retries")
verify = config.get(section="session", key="verify")
backoff_max_time = config.get(section="session", key="backoff_max_time")
backoff_jitter = None
backoff_retry_after = config.get(section="session", key="backoff_retry_after")


def retry_for_these_error_codes():
    error_codes.append(429)
    return error_codes


class SparkTicketService:
    def __init__(self, **kwargs):
        logger.info("Initializing Spark service Now")
        self.aio_rest = AioRestUtility()
        self.base_url = itsm_url
        self.headers = {"accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
        shuffle(itsm_keys)
        self.api_keys = iter(itsm_keys)
        self.headers["ocp-apim-subscription-key"] = next(self.api_keys)
        self.timeout = kwargs.get("timeout", 300)
        self.ssl_verify = kwargs.get("ssl_verify", True)
        self.max_retries = max_retries

    @backoff.on_predicate(
        backoff.runtime,
        predicate=lambda response: response.status in retry_for_these_error_codes(),
        value=lambda response: int(response.headers.get("Retry-After", backoff_retry_after)),
        jitter=backoff_jitter,
        max_time=backoff_max_time,
    )
    async def spark_request(self, method, session, url, headers=None, **kwargs):
        """
        Helper method to wrap calls to Spark (via the AioRestUtility) and
        automatically rotate keys.
        Args:
           - method (str): HTTP verb in lowercase
           - session (object): aiohttp ClientSession object
           - url (str): Full request URL
        Returns:
           - response from Spark
        Raises:
            Exception
        """
        try:
            response = await getattr(self.aio_rest, method)(session, url, headers=self.headers, **kwargs)
            return response
        except Exception as error:
            logger.exception(error)
            raise

    async def service3800(self, **kwargs):
        """
        Calling Asynchronous Spark Service Now 3800 service to retrieve spark details
        Args:
            kwargs:
              db_table: Table name
              ci_filter: fields needs to be searched for - parent/child
              ci_list: Ci name or list of CIs
        Returns:
            query_response_data
        """
        servicenum = "service3800"
        logger.info(f"Entering into ITSM {servicenum} (Generic Custom Query)")
        db_table = kwargs.get("table")
        ci_filter = kwargs.get("filter")
        ci_list = kwargs.get("ci_list")
        if db_table == "cmdb_rel_ci":
            query_response_data = await self._srv3800_get_ci_relationship(ci_list=ci_list, ci_role=ci_filter)
        else:
            return f"The given {db_table} is currently not supported"
        logger.info(f"Exciting Asynchronous {servicenum} call")
        return query_response_data

    async def _srv3800_get_ci_relationship(self, ci_list, ci_role):
        """
        Asynchronous get CI relationshiop data from Spark
        Args:
            ci_list: list of CIs
            ci_role: child/parent
        Returns:
            query_response_data
        """
        logger.info(f"Entering into ITSM module to retrieve {ci_role} ci relationships for CIs {ci_list}")
        servicenum = "service3800"
        tasks = []
        result = {"result": []}
        list_of_get_urls = [
            f"{self.base_url}/{servicenum}/request?db_table=cmdb_rel_ci&query_filter={ci_role}.name%3D{item}"
            for item in ci_list
        ]
        # 1 - Create a list of target_urls
        # 2 - Create a list of an async get spark_request instances(session.get(url=url, headers=headers)
        # 3 - Gather results for all the tasks asynchronously
        # 4 - The index of the response_data will always match the input task/url list.
        #     The index is how the request and responses are mapped.
        logger.info(f"The request sent to Spark Service Now for {servicenum} is: {list_of_get_urls}")
        async with aiohttp.ClientSession() as session:
            tasks.extend(
                self.spark_request(method="get", session=session, url=url, headers=self.headers)
                for url in list_of_get_urls
            )
            response_data = await asyncio.gather(*tasks, return_exceptions=True)
            try:
                response = await self._srv3800_ci_rel_response_builder(
                    api_response_data=response_data, list_of_get_urls=list_of_get_urls, ci_list=ci_list, ci_role=ci_role
                )
                result["result"] = response
                return result
            except Exception as err:
                logger.exception(err)
                return {"errorCategory": "FAILED", "errors": [{"code": "ERR-003-999-0001", "message": f"{err}"}]}

    async def _srv3800_ci_rel_response_builder(self, api_response_data, list_of_get_urls, ci_list, ci_role):
        """
        Function to build a generic response for CI relationships
        Args:
          - api_response_data: spark service ci relationships status information
          - list_of_get_urls: list of urls/queries sent to the spark service
          - ci_list: list of ci's
          - ci_role: query filter
        Returns:
          - response: list of dictionary items containing ci relationship status information
        """
        logger.info(f"Spark service CI relationships api response: {api_response_data}")
        formatted_response = []
        for idx, get_resp in enumerate(api_response_data):
            try:
                per_call_response = await get_resp.json()
                logger.info(
                    f"Spark service CI relationships per call api response for url {list_of_get_urls[idx]}: "
                    f"{per_call_response}"
                )
                if "result" in per_call_response:
                    if len(per_call_response["result"]) != 0:
                        for item in per_call_response["result"]:
                            response_schema = {
                                "parentCI": item["parent"]["display_value"],
                                "childCI": item["child"]["display_value"],
                                "relationshipType": item["type"]["display_value"],
                                "relationshipStatus": "active",
                                "action": "read",
                                "getUrlPath": list_of_get_urls[idx],
                            }
                            formatted_response.append(response_schema)
                    else:
                        response_schema = {
                            "parentCI": ci_list[idx] if ci_role == "parent" else None,
                            "childCI": ci_list[idx] if ci_role == "child" else None,
                            "relationshipStatus": ("CI not found or there are no relationships or resource not found"),
                            "action": "read",
                            "getUrlPath": list_of_get_urls[idx],
                        }
                        formatted_response.append(response_schema)
            except Exception as err:
                logger.exception(err)
                response_schema = {"getUrlPath": list_of_get_urls[idx], "action": "read"}
                if isinstance(get_resp, (ClientResponseError, ClientError)):
                    response_schema["error"] = {"message": get_resp.message, "statusCode": get_resp.status}
                else:
                    response_schema[
                        "relationshipStatus"
                    ] = "CI not found or there are no relationships or resource not found"
                    response_schema["parentCI"] = ci_list[idx] if ci_role == "parent" else None
                    response_schema["childCI"] = ci_list[idx] if ci_role == "child" else None
                formatted_response.append(response_schema)
        return formatted_response

    async def service3605(self, **kwargs):
        """
        Calling Asynchronous Spark Service Now 3605 service to create/remove the ciRelationships
        Args:
            kwargs:
              body: user payload/ciRelationships
        Returns:
            ciRelationships_response_data
        """
        servicenum = "service3605"
        logger.info(f"Entering into {servicenum} capability with kwargs: {kwargs.get('body')}")
        ci_relationship_data = kwargs.get("body").get("ciRelationships")
        list_of_urls = [
            f"{self.base_url}/{servicenum}/request?action={item.get('action')}&parent_ci={item.get('parentCI')}"
            f"&child_ci={item.get('childCI')}&relationship_type={item.get('relationshipType', 'Depends on::Used by')}"
            for item in ci_relationship_data
        ]
        logger.info(f"The request sent to Spark Service Now for {servicenum} is: {list_of_urls}")
        result = {"results": {"success": [], "failure": []}, "status": None}
        async with aiohttp.ClientSession() as session:
            response_data = await asyncio.gather(
                *(
                    self.spark_request(method="post", session=session, url=url, headers=self.headers)
                    for url in list_of_urls
                ),
                return_exceptions=True,
            )
            try:
                success_list, failure_list, status = await self._srv3605_response_builder(
                    ci_relationships=ci_relationship_data, api_response_data=response_data, list_of_urls=list_of_urls
                )
                result["results"]["success"] = success_list
                result["results"]["failure"] = failure_list
                result["status"] = status
                return result
            except Exception as err:
                logger.exception(f"An exception occurred while updating the CI relationships: {err}")
                return {"errorCategory": "FAILED", "errors": [{"code": "ERR-002-999-0001", "message": f"{err}"}]}

    async def _srv3605_response_builder(self, ci_relationships, api_response_data, list_of_urls):
        """
        Function to build a generic response for CI relationships
        Args:
          - ci_relationships: user payload data
          - api_response_data: spark service ci relationships status information
          - list_of_urls: list of urls/queries sent to the spark service
        Returns:
          - response: list of dictionary items containing ci relationship status information
        """
        try:
            logger.info(f"Spark service CI relationships api response: {api_response_data}")
            success, partial_success, status = "", "", ""
            success_list, failure_list = [], []
            for idx, post_resp in enumerate(api_response_data):
                per_call_response = (
                    await post_resp.json()
                    if not isinstance(
                        post_resp,
                        (
                            NameError,
                            UnboundLocalError,
                            AttributeError,
                            ClientConnectionError,
                            ClientError,
                            ClientResponseError,
                        ),
                    )
                    else {}
                )
                logger.info(
                    f"Spark service CI relationships per call api response for url {list_of_urls[idx]}: "
                    f"{per_call_response}"
                )
                if "error_details" in per_call_response.get("result", {}):
                    ci_relationships[idx]["postUrlPath"] = list_of_urls[idx]
                    ci_relationships[idx]["error"] = {
                        "message": per_call_response["result"]["error_details"],
                        "statusCode": "ERR-003-999-" + str(post_resp.status),
                    }  # Bug fix for DNE-22533
                    partial_success = True
                    failure_list.append(ci_relationships[idx])
                elif "details" in per_call_response.get("result", {}):
                    ci_relationships[idx]["relationshipStatus"] = str(per_call_response["result"]["details"])
                    ci_relationships[idx]["postUrlPath"] = list_of_urls[idx]
                    success = True
                    success_list.append(ci_relationships[idx])
                elif isinstance(post_resp, (ClientError, ClientResponseError)):
                    ci_relationships[idx]["postUrlPath"] = list_of_urls[idx]
                    ci_relationships[idx]["error"] = {
                        "message": post_resp.message,
                        "statusCode": "ERR-003-999-" + str(post_resp.status),
                    }
                    partial_success = True
                    failure_list.append(ci_relationships[idx])
                elif isinstance(post_resp, (NameError, UnboundLocalError, AttributeError, ClientConnectionError)):
                    ci_relationships[idx]["postUrlPath"] = list_of_urls[idx]
                    ci_relationships[idx]["error"] = {"message": "connection error", "statusCode": None}
                    partial_success = True
                    failure_list.append(ci_relationships[idx])
            status = ("PARTIAL_SUCCESS" if success else "FAILURE") if partial_success else "SUCCESS"
            return success_list, failure_list, status
        except Exception as err:
            logger.exception(err)
            raise err
