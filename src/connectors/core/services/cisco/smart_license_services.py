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
import datetime
import json
import logging
import sys
from typing import Any

# Sky Library
from isp_config import ConfigManagerException

# DNE Library
from connectors.core.config import connectors_config
from connectors.core.services.cisco.cisco_smart_license_operations import CiscoSmartOperations
from connectors.core.utils.exceptions import GenericConnectorsException
from connectors.core.utils.rest_api_utility import RestUtility

logger = logging.getLogger(__name__)

try:
    config = connectors_config.ConnectorsConfigManager()
    config.load_config()
except ConfigManagerException:
    sys.exit(1)

client_id = config.get(section="ciscoSmartAccount", key="client_id")
client_secret = config.get(section="ciscoSmartAccount", key="client_secret")
username = config.get(section="ciscoSmartAccount", key="username")
password = config.get(section="ciscoSmartAccount", key="password")


class CiscoSmartLicense:
    def get_latest_token(self) -> None | Any | tuple[Any, Any] | Any | KeyError | ValueError | AttributeError:
        """
        Get the token from the DB,
        if no tokens:
            return None
        if token is expired or token will be expired in next one day:
            return None
        return Data
        Returns: Token
        """
        try:
            logger.info("Fetching the latest valid token")
            csmo = CiscoSmartOperations()
            operation_result = csmo.get_smart_token_operations()
            if type(operation_result) is not tuple:
                return operation_result

            token = operation_result[0]
            token_expiry_date = operation_result[1]
            date_diff = token_expiry_date - datetime.datetime.now(datetime.timezone.utc)
            return None if date_diff.days <= 1 else token
        except (KeyError, ValueError, AttributeError) as error:
            logger.error("fetching the latest token from DB failed due to {error.args[0]}")
            logger.exception(f"{error.args[0]} while fetching the latest token from DB", exc_info=True)
            return error

    def add_token(
        self, token_from_cisco_smart: str, expiry_date: str, export_control: str, created_by: str
    ) -> Any | None | Any | KeyError | ValueError | AttributeError:
        """
        Returns: Token_id
        """
        try:
            logger.info(f"Adding the token")
            csmo = CiscoSmartOperations(
                token=token_from_cisco_smart,
                expiry_date=expiry_date,
                export_control=export_control,
                created_by=created_by,
            )
            return csmo.add_token_operations()
        except (KeyError, ValueError, AttributeError) as error:
            logger.error(f"Adding token to DB failed due to {error.args[0]}")
            logger.exception(f"{error.args[0]} while Adding token to DB", exc_info=True)
            return error

    def fetch_authorization_token(self) -> Any:
        """
        Fetch the bearer token using the client secret from the cisco smart account
        Returns:
        """
        try:
            logger.info(f"Fetching the bearer token using the client secret from the cisco smart account")
            rest = RestUtility(authorization_via_tokens=False, username=client_id, password=client_secret)
            return rest.post(
                "https://cloudsso.cisco.com/as/token.oauth2",
                headers={"Content-type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "password",
                    "username": username,
                    "password": password,
                },
            )

        except (ValueError, TypeError, AttributeError) as error:
            logger.error(
                f"Fetching the bearer token using the client secret from the cisco smart account failed"
                f" due to {error.args[0]}"
            )
            logger.exception(
                f"{error.args[0]} while fetching the bearer token by using the client secret from the"
                f"cisco smart account",
                exc_info=True,
            )
            raise GenericConnectorsException(f"oAuth bearer token request failed due to : {error.args[0]}")

    def fetch_smart_license_from_cisco(self) -> Any:
        """
        Returns: response from smart cisco device
        """
        try:
            logger.info("Fetching the token from the cisco smart account")
            bearer_token = self.fetch_authorization_token()["access_token"]
            return RestUtility(authorization_via_tokens=False).post(
                "https://apx.cisco.com/services/api/smart-accounts-and-licensing/v1/"
                "accounts/sky.uk/virtual-accounts/Telco/tokens",
                headers={"Authorization": f"Bearer {bearer_token}", "Content-Type": "application/json"},
                data=json.dumps({"description": "", "expiresAfterDays": 365, "exportControlled": "Allowed"}),
            )
        except (KeyError, ValueError, TypeError, AttributeError) as error:
            logger.error(
                f"fetching the token from the cisco smart account failed due to {error.args[0]},"
                f"token not found, expired or invalid"
            )
            logger.exception(
                f"{error.args[0]} while fetching the token from the cisco smart account, "
                f"token not found, expired or invalid ",
                exc_info=True,
            )
            raise GenericConnectorsException(
                f"fetching the token from the cisco smart account Exception: {error.args[0]},"
                f"token not found, expired or invalid "
            ) from error

    def get_smart_token(self) -> dict[str, Any] | dict[str, str] | Any:
        """
        This method adds the token to the db fetched from the smart cisco device
         if the latest token from db has expired or doesn't exists
        Returns: Token
        """
        try:
            logger.info("Fetching the cisco smart token")
            token_from_db = self.get_latest_token()
            if type(token_from_db) == str:
                result = {"status": "SUCCESS", "token": token_from_db}
            if token_from_db is None:
                token_dict = self.fetch_smart_license_from_cisco()
                if token_dict.get("status") == "SUCCESS":
                    token_from_cisco_smart = token_dict["tokenInfo"]["token"]
                    expiry_date = token_dict["tokenInfo"]["expirationDate"]
                    created_by = token_dict["tokenInfo"]["createdBy"]
                    export_control = token_dict["tokenInfo"]["exportControl"]
                    token = self.add_token(
                        token_from_cisco_smart=token_from_cisco_smart,
                        expiry_date=expiry_date,
                        export_control=export_control,
                        created_by=created_by,
                    )
                    result = {"status": "SUCCESS", "token": token}
            if type(token_from_db) != str and token_from_db:
                result = {
                    "status": "FAILURE",
                    "errorCategory": "FAILED",
                    "errors": [
                        {"code": "ERR-008-012-1001", "message": "Failed to generate token" + str(token_from_db)}
                    ],
                }
            return result
        except (KeyError, ValueError, AttributeError, GenericConnectorsException) as error:
            logger.error(
                f"Failed to generate cisco smart token due to {error.args[0]}," f"token not found, expired or invalid"
            )
            logger.exception(
                f"{error.args[0]} while fetching the cisco smart token, " f"token not found, expired or invalid",
                exc_info=True,
            )
            return error.args[0]
