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
import json
import logging
from datetime import datetime, timezone

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.utils.exceptions import ConnectorException, ConnectorInvalidRequest
from connectors.core.utils.rest_api_utility import RestUtility
from connectors.core.utils.rsa import RSA
from connectors.core.utils.sqldb.model import Tokens
from connectors.core.utils.sqldb.sqlDB import MySQLDB

logger = logging.getLogger(__name__)


class HorizonService:

    HORIZON_ENDPOINT = config.get(section="horizon", key="endpoint")
    HORIZON_DNE_EMAIL = config.get(section="horizon", key="email")

    def __init__(self):
        """
        Calling Horizon Service

        Retrieves and updates deliverables in Horizon

        """
        logger.info("Initializing Horizon Service")
        self._token: str = ""
        self._rest_util: RestUtility | None = None
        self.dne_horizon_deliverable_id_map: dict = {}
        self._sql_instance: MySQLDB | None = None
        self.warnings = []

    @property
    def horizon_token(self) -> str:
        """
        Fetches the horizon token from SQL DB if not already present in the object

        Raises:
            ConnectorException: If token cannot be found in the DB
            ConnectorException: If the token has expired

        Returns:
            str: horizon token
        """
        if not self._token:
            with self.sql_instance.transactional_session() as session:
                logger.debug("Querying SQL DB for horizon token")
                token_details = (
                    session.query(Tokens.token, Tokens.expiry_at)
                    .filter(Tokens.system == "horizon")
                    .order_by(Tokens.id.desc())
                    .limit(1)
                    .all()
                )
                if len(token_details) != 1:
                    raise ConnectorException(f"Expecting to find 1 horizon token but found {len(token_details)}")
                token = token_details[0].token
                token_expiry_date = token_details[0].expiry_at
                date_diff = token_expiry_date - datetime.now(timezone.utc).date()
                days_to_expire = date_diff.days
                if days_to_expire <= 1:
                    raise ConnectorException("Horizon token found in DB is expired")
                self._token = self._decrypt_token(token)
                logger.debug(f"Last 3 characters of token being used are {self._token[-3:]}")
        return self._token

    def _decrypt_token(self, token: str) -> str:
        logger.debug(f"Last 3 characters of encrypted token are {token[-3:]}")
        try:
            return RSA().decrypt(bytes(token, "utf-8").decode("unicode_escape").encode("latin1"))
        except Exception as err:
            logger.debug("Exception raised when decrypting horizon token so using plaintext taken from DB")
            logger.debug(f"Exception type is {type(err)}")
            logger.exception(f"Exception is {err}")
            return token

    @property
    def rest_util(self) -> RestUtility:
        """
        Creates a rest util object if not already created and adds the horizon token to the headers

        Returns:
            RestUtility: rest util object with horizon token as auth
        """
        if not self._rest_util:
            logger.debug("Creating rest util object and setting authorization in headers")
            self._rest_util = RestUtility()
            self.rest_util.headers["Authorization"] = f"Token {self.horizon_token}"
        return self._rest_util

    @property
    def sql_instance(self) -> MySQLDB:
        """
        Creates a MySQLDB object if not already created

        Returns:
            MySQLDB: MySQLDB object
        """
        if not self._sql_instance:
            logger.debug("Creating MySQLDB object")
            self._sql_instance = MySQLDB(database_name="dne_core")
        return self._sql_instance

    def get_horizon_deliverable(self, order_id: str | None = None, unique_reference: str | None = None) -> dict:
        """
        Gets the horizon deliverable data corresponding to the passed order id

        Args:
            order_id (str): DNE order ID

        Returns:
            dict: details of horizon deliverable
        """
        url = f"{self.HORIZON_ENDPOINT}api/base/deliverable"
        if order_id:
            params = {"remote_order_reference": order_id}
        elif unique_reference:
            params = {"deliverable_reference": unique_reference}
        else:
            params = None
        response = self.rest_util.get(url=url, params=params)
        logger.debug(f"Response from Horizon with given parameters {params} is: {response}")
        if response["count"] == 0 and unique_reference:
            params = {"deliverable_reference": unique_reference}
            response = self.rest_util.get(url=url, params=params)
            logger.debug(f"Response from Horizon with given parameters {params} is: {response}")
        return response, params

    def _get_horizon_deliverable_id(self, dne_order_id: str, unique_reference: str | None = None) -> tuple[int, int]:
        """
        Gets the horizon deliverable id corresponding to the passed order id

        Args:
            dne_order_id (str): DNE order ID

        Returns:
            str: horizon deliverable id
        """
        logger.debug(f"Getting the horizon id corresponding to the dne order id {dne_order_id}")
        horizon_deliverable_details, params = self.get_horizon_deliverable(dne_order_id, unique_reference)
        self._check_response_count(horizon_deliverable_details["count"], params, dne_order_id, unique_reference)
        horizon_deliverable_id = horizon_deliverable_details.get("results", [])[0]["id"]
        horizon_deliverable_type_id = horizon_deliverable_details.get("results", [])[0]["status"]["deliverable_type"]
        self.dne_horizon_deliverable_id_map[dne_order_id] = horizon_deliverable_id
        return horizon_deliverable_id, horizon_deliverable_type_id

    def _check_response_count(
        self, count: int, params: dict, id_searched_for: str, unique_reference: str | None = None
    ) -> None:
        """
        Raises an exception if the horizon response has more or less than one result

        Args:
            count (int): count from horizon response
            id_searched_for (str): The id passed to the api call

        Raises:
            ConnectorInvalidRequest: If the count is more or less than one
        """
        if count > 1:
            if params.get("remote_order_reference"):
                raise ConnectorInvalidRequest(
                    f"Duplicate deliverables found in Horizon with order ID '{id_searched_for}'. "
                    f"The total number of deliverables found is '{count}'."
                )
            elif params.get("deliverable_reference"):
                raise ConnectorInvalidRequest(
                    f"No deliverables found in Horizon with order ID '{id_searched_for}', "
                    f"and '{count}' duplicate deliverables found with unique reference '{unique_reference}'."
                )
        elif count == 0:
            if params.get("remote_order_reference"):
                raise ConnectorInvalidRequest(f"No deliverables found in Horizon with order ID '{id_searched_for}'.")
            elif params.get("deliverable_reference"):
                raise ConnectorInvalidRequest(
                    f"No deliverables found in Horizon with order ID '{id_searched_for}' "
                    f"or unique reference '{unique_reference}'."
                )

    def _get_status_id(self, status: str, horizon_deliverable_type_id: int) -> str:
        """
        Gets the horizon id of a given status

        Args:
            status (str): Readable status message e.g. In Progress

        Returns:
            str: Horizon id of the status
        """
        logger.debug(f"Finding the id of status {status}")
        url = f"{self.HORIZON_ENDPOINT}api/base/status/deliverable_type_id/{horizon_deliverable_type_id}"
        response = self.rest_util.get(url=url)
        if isinstance(response, dict):
            response = [response]
        for item in response:
            if item.get("name") == status:
                logger.info(f"Fetched status ID for '{status}' with given deliver type: {item.get('id')}")
                return item.get("id")

        logger.error(f"Failed to fetch corresponding ID for status {status} from Horizon. Horizon response: {response}")
        raise ConnectorInvalidRequest(f"Failed to fetch corresponding ID for status {status} from Horizon.")

    def _update_horizon_details(
        self,
        horizon_deliverable_id: int,
        horizon_deliverable_type_id: int,
        completion_date: str | None = None,
        estimated_completion_date: str | None = None,
        original_required_by_date: str | None = None,
        status: str | None = None,
        **kwargs,
    ) -> dict:
        """
        Updates the horizon deliverable details

        Args:
            horizon_deliverable_id (int): Id of horizon deliverable
            horizon_deliverable_type_id (int): Id of horizon deliverable type
            completion_date (str, optional): completion data. Defaults to None.
            estimated_completion_date (str, optional): estimated completion date. Defaults to None.
            original_required_by_date (str, optional): original required by date. Defaults to None.
            status (str, optional): horizon status id. Defaults to None.

        Returns:
            dict: details of updated deliverable
        """
        logger.debug(f"Updating horizon deliverable {horizon_deliverable_id}")
        url = f"{self.HORIZON_ENDPOINT}api/base/deliverable/{horizon_deliverable_id}"
        status_id = (
            self._get_status_id(status, horizon_deliverable_type_id) if status and horizon_deliverable_type_id else None
        )
        body = {
            "completion_date": completion_date,
            "estimated_completion_date": estimated_completion_date,
            "original_required_by_date": original_required_by_date,
            "status": status_id,
        }
        for key, value in list(body.items()):
            if value is None:
                del body[key]
        if status != "Complete" and body.get("completion_date"):
            del body["completion_date"]
            self.warnings.append("Not updating completion date as status is not Complete")
        return self.rest_util.patch(url=url, data=json.dumps(body))

    def update_deliverable_details(self, **kwargs) -> dict:
        """
        Updates a horizon deliverable corresponding to a dne order id

        Raises:
            ConnectorInvalidRequest: If no details are passed to update

        Returns:
            dict: status and id of horizon deliverable
        """
        body = kwargs.get("body", {})
        if not body:
            raise ConnectorInvalidRequest("Must pass at least on parameter to update on horizon deliverable")
        if body["status"] == "Complete" and not body.get("completion_date"):
            raise ConnectorInvalidRequest("When updating status to complete must provide completion_date")
        order_id = kwargs["order_id"]
        unique_reference = body.get("unique_reference")
        logger.debug(f"Updating horizon deliverable for dne order id {order_id}")
        horizon_deliverable_id, horizon_deliverable_type_id = self._get_horizon_deliverable_id(
            order_id, unique_reference
        )
        logger.debug(
            f"horizon_deliverable_id: {horizon_deliverable_id},"
            f"horizon_deliverable_type_id: {horizon_deliverable_type_id}"
        )
        self._update_horizon_details(horizon_deliverable_id, horizon_deliverable_type_id, **body)
        return {"status": "SUCCESS", **({"warnings": self.warnings} if self.warnings else {})}
