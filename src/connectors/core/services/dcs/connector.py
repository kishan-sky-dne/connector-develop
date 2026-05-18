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
import math
from json import dumps
from typing import Any

# Third Party Library
import requests

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.exceptions import ConnectorsException
from connectors.core.services.dcs.exceptions import DisallowedOperation
from connectors.core.utils.exceptions import ConflictException, ResourceServiceNotAvailable, RestUtilityException
from connectors.core.utils.rest_api_utility import RestUtility

logger = logging.getLogger(__name__)


class DeviceConfigurationService:
    def __init__(self, hostname: str | None, username: str, password: str, **kwargs) -> None:
        """calling dcs

        Retrieves the details of the given hostname from DCS

        :param hostname: The hostname - Path parameter
        :type hostname: str
        :param username: The cauth username
        :type username: str
        :param password: The cauth password
        :type password: str
        :rtype: None
        """
        logger.debug("Initializing Device Configuration Service")
        self.username = username
        self.rest = RestUtility(username=username, password=password)
        self.hostname = hostname
        self.kwargs = kwargs
        self.base_url = config.get(section="dcs", key="url")
        self.device_list: list = []

    def device(self) -> Any:
        """
        Retrieves the details of the given hostname from DCS # noqa: E501
        """
        device_url = self.hostname
        try:
            logger.info(f"Fetching device information from DCS with username {self.username}")
            return self.rest.get(self.base_url + device_url)
        except (ValueError, TypeError, AttributeError) as err:
            raise ConnectorsException(f" {err.args[0]}")
        except RestUtilityException as err:
            if err.response.status_code == requests.codes.not_found:  # Checks the response code is 404
                raise ResourceServiceNotAvailable(f"{err.args[0]}")
            else:
                logger.exception(f"Response Code from the response: {err.response.status_code}")
                raise RestUtilityException(f"{err.args[0]}", err.response)

    def add_device(self):
        """
        Add device with given hostname to DCS

        Args:
        user_model

        Returns:
            Status, msg

        Raises:
            Problem in adding the device data in DCS
        """
        try:
            logger.info(f"Adding device {self.hostname} in DCS system")
            return self.rest.post(self.base_url, data=dumps(self.kwargs["data"]))
        except (ValueError, TypeError, AttributeError, KeyError) as err:
            raise ConnectorsException(f" {err.args[0]}")
        except RestUtilityException as err:
            if err.response.status_code == requests.codes.conflict:  # Checks the response code is 409
                raise ConflictException(f"{err.args[0]}")
            else:
                logger.exception(f"Response Code from the response: {err.response.status_code}")
                raise RestUtilityException(f"{err.args[0]}", err.response)

    def update_device(self) -> dict:
        """
        Update device data in DCS

        Args:
        user_model

        Returns:
            Status, msg

        Raises:
            Problem in updating the device data in DCS
        """
        device_url = self.hostname
        try:
            logger.info(f"Updating device {self.hostname} in DCS system with data {self.kwargs['data']}")
            self.rest.patch(self.base_url + device_url, data=dumps(self.kwargs["data"]))  # Fix for Bug DNE-18853
            return {"status": "SUCCESS"}
        except (ValueError, TypeError, AttributeError, KeyError) as err:
            raise ConnectorsException(f" {err.args[0]}")
        except RestUtilityException as err:
            if err.response == requests.codes.not_found:  # Checks the response code is 404
                raise ResourceServiceNotAvailable(f"{err.args[0]}")
            if err.response == requests.codes.unprocessable_entity:  # Checks the response code is 422
                raise DisallowedOperation(f"{err.args[0]}")
            logger.exception(f"Response Code from the response: {err.response}")
            raise RestUtilityException(f"{err.args[0]}", err.response)

    def all_devices(self) -> dict:
        """
        Retrieves all devices from DCS
        """
        try:
            logger.info(f"Fetching all devices from DCS with username {self.username}")
            return self.rest.get(self.base_url, log_results=False)
        except Exception as err:
            logger.exception(f"Exception fetching all devices from DCS: {err.args[0]}")
            raise ConnectorsException(f"{err.args[0]}") from err

    def get_all_device_details(self, expand: list | None = None) -> dict:
        """
        Retrieves the details of all devices from DCS
        """
        if expand is None:
            expand = ["attribs", "ports"]
        query = ""
        try:
            logger.info(f"Fetching device information from DCS with username {self.username}")
            operator_mapper = {"eq": "==", "regex": "~=", "gt": ">", "gte": ">=", "lt": "<", "lte": "<=", "ne": "!="}
            relational_mapper = {"ne": " and "}
            filter_data = self.kwargs["filters"]
            limit = self.kwargs["limit"]
            page_number = self.kwargs["page_number"]
            offset = self.kwargs["offset"]
            for count, _filters in enumerate(filter_data):
                values = _filters["values"]
                if _filters["operator"] == "regex":
                    query += " or ".join(
                        f'{_filters["param"]}{operator_mapper[_filters["operator"]]} {value}' for value in values
                    )
                else:
                    query += relational_mapper.get(_filters["operator"], " or ").join(
                        f'{_filters["param"]}{operator_mapper[_filters["operator"]]}' f'"{value}"' for value in values
                    )
                if count != len(filter_data) - 1:
                    query += f" {_filters.get('logicalOperator', 'and')} "
            if query:
                url = f"{self.base_url}?expand={','.join(expand)}&data_filter={query}"
            else:
                url = f"{self.base_url}?expand={','.join(expand)}"
            device_response = self.rest.get(url, log_results=False)
            self.device_list = device_response
            total_pages = math.ceil(len(device_response) / limit)
            if not device_response:
                return {
                    "pageNumber": page_number,
                    "totalPages": total_pages,
                    "offset": offset,
                    "limit": limit,
                    "results": device_response,
                }
            if len(device_response) <= offset:
                return {
                    "errorCategory": "FAILED",
                    "errors": [
                        {
                            "code": "ERR-011-999-1001",
                            "message": "Given offset is exceeding than total response",
                        }
                    ],
                }
            if not total_pages >= page_number:
                return {
                    "errorCategory": "FAILED",
                    "errors": [
                        {
                            "code": "ERR-011-999-1001",
                            "message": "Given page number is exceeding than total page",
                        }
                    ],
                }
            start_index = (page_number - 1) * limit + offset
            end_index = start_index + limit
            results = device_response[start_index:end_index]
            return {
                "pageNumber": page_number,
                "totalPages": total_pages,
                "offset": offset,
                "limit": limit,
                "results": results,
            }
        except RestUtilityException as err:
            logger.exception(f"RestUtility Error Response: {err.response}")
            raise RestUtilityException(f"{err.args[0]}", err.response) from err
        except Exception as err:
            return {
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-011-999-1001",
                        "message": f"Getting device details from DCS failed:{err}",
                    }
                ],
            }

    def find_all_vendors(self) -> dict:
        """
        Finds all vendors of devices currently in DCS

        Returns:
            dict: Names of all vendors
        """
        all_vendors = self._find_all_values_in_dcs_response("vendor")
        logger.debug(f"All vendors found in DCS are: {all_vendors}")
        return {"vendors": all_vendors}

    def find_all_platforms(self, vendor: str) -> dict:
        """
        Finds all platforms under a given vendor in DCS

        Args:
            vendor (str): Given vendor to search for all platforms

        Returns:
            dict: Names of all platforms under given vendor
        """

        self.kwargs["filters"] = [self._generate_dcs_filter(vendor, "vendor")]

        all_platforms = self._find_all_values_in_dcs_response("os")
        logger.debug(f"All platforms under vendor {vendor} found in DCS are: {all_platforms}")
        return {"platforms": all_platforms}

    def find_all_os_versions(self, vendor: str, platform: str) -> dict:
        """
        Finds all os versions of devices under given vendor AND platform

        Args:
            vendor (str): vendor to search for os versions
            platform (str): platform to search for os versions

        Returns:
            dict: Names of all os versions
        """
        self.kwargs["filters"] = [
            self._generate_dcs_filter(vendor, "vendor"),
            self._generate_dcs_filter(platform, "os"),
        ]
        all_os_versions = self._find_all_values_in_dcs_response("os_version")
        logger.debug(
            f"All os versions under vendor {vendor} and platform {platform} found in DCS are: {all_os_versions}"
        )
        return {"os_versions": all_os_versions}

    def find_all_chassis(self, vendor: str, platform: str, os_version: str) -> dict:
        """
        Finds all chassis of devices under given vendor AND platform AND os version

        Args:
            vendor (str): vendor to search for chassis
            platform (str): platform to search for chassis
            os_version (str): os version to search for chassis

        Returns:
            dict: Names of all chassis
        """
        self.kwargs["filters"] = [
            self._generate_dcs_filter(vendor, "vendor"),
            self._generate_dcs_filter(platform, "os"),
            self._generate_dcs_filter(os_version, "os_version"),
        ]
        all_chassis = self._find_all_values_in_dcs_response("model")
        logger.debug(
            f"All chassis under vendor {vendor}, platform {platform}, "
            "and os_version {os_version} found in DCS are: {all_chassis}"
        )
        return {"chassis": all_chassis}

    def _generate_dcs_filter(self, dcs_value: str, dcs_param: str) -> dict:
        return {
            "logicalOperator": "and",
            "operator": "eq",
            "param": dcs_param,
            "values": sorted(list({dcs_value.lower(), dcs_value.upper(), dcs_value.capitalize(), dcs_value})),
        }

    def _find_all_values_in_dcs_response(self, param_to_find: str) -> list[str]:
        """
        Finds all values of a given param in the dcs response

        Args:
            param_to_find (str): Parameter to find all values of e.g. model, vendor

        Returns:
            set: Set of all values
        """
        self.get_all_device_details(expand=["attribs"])
        all_values = {device[param_to_find] for device in self.device_list if device[param_to_find]}
        return sorted(list(all_values))

    def send_dcs_fetch_request(self) -> dict:
        """
        Sends config fetch request for the given hostname from DCS

        Returns:
            Status for dcsfetch request.
        """
        device_url = f"{self.hostname}/collect"
        try:
            logger.info(f"Sending DCS fetch request with URL: {self.base_url + device_url}")
            return self.rest.put(self.base_url + device_url, data={})
        except (ValueError, TypeError, AttributeError) as err:
            raise ConnectorsException(f" {err.args[0]}") from err
        except RestUtilityException as err:
            if err.response.status_code == requests.codes.not_found:  # Checks the response code is 404
                raise ResourceServiceNotAvailable(f"{err.args[0]}") from err
            logger.exception(f"Response Code from the response: {err.response.status_code}")
            raise RestUtilityException(f"{err.args[0]}", err.response) from err
        except Exception as err:
            return {
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-011-999-1001",
                        "message": f"Sending DCSFetch request failed with error: {err}",
                    }
                ],
            }
