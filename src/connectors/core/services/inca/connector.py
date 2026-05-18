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

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.utils.exceptions import RestUtilityException
from connectors.core.utils.helpers import generate_hostname
from connectors.core.utils.rest_api_utility import RestUtility

logger = logging.getLogger(__name__)

base_url = config.get(section="inca", key="base_url")
DOMAINS = config.get(section="internals", key="regional_domain")


class IncaService:
    def __init__(self):
        """calling INCA

        Retrieves the details of the given type of circuits from INCA Inventory

        :kwargs: {
            type: Type of circuit,
            state=state of circuit,
            limit=limit the output records
            }
        """
        logger.info("Initializing INCA Inventory Service")
        self.rest = RestUtility()

    def get_details(self, **kwargs):
        """
        Retrieves the details of the gea from INCA
        Args:
        Returns:
            dict formatted data
        """
        logger.info(f"Inside Inca method to get {kwargs['type']} inca details from the INCA Inventory")
        try:
            inca_url = base_url + kwargs["url"]
            logger.debug(f"Fetching {kwargs['type']} information from INCA url {kwargs['url']}")
            return self.rest.get(url=inca_url, headers=kwargs["headers"])
        except RestUtilityException as err:
            logger.exception(f"Response Code from the response: {err.response.status_code}")
            raise RestUtilityException(f"{err.args[0]}", err.response)

    @staticmethod
    def _get_hostnames_for_fqdn_removed(devices: list[dict]) -> list[dict]:
        """
        Returns device names with FQDN part removed

        Args:
            devices: List of hostnames

        Returns:
            List of hostnames of FQDN part removed.
        """
        for device in devices:
            device["hostname"] = generate_hostname(DOMAINS, device["hostname"])
        return devices

    def update_inca_device_decommissioned(self, **kwargs) -> dict:
        """
        Updates the device decommissioned status in INCA
        Args:
        Returns:
            dict formatted data
        """
        logger.info("Inside Inca method to update device decommissioned status")
        try:
            type_url = base_url + kwargs["url"]
            logger.debug(
                f"Update device decommissioned state for devices " f"{kwargs['body']} from INCA url {type_url}"
            )
            req_payload = {
                "mdfId": kwargs["body"].get("mdfId"),
                "devices": self._get_hostnames_for_fqdn_removed(kwargs["body"].get("devices")),
            }
            logger.info(f"Inca Device Decomm Update Payload: {req_payload}")
            inca_response = self.rest.put(
                url=type_url, data=json.dumps(req_payload), timeout=20, headers=kwargs["headers"]
            )
            logger.info(f"Response received from INCA is {inca_response}")
            if inca_response.get("result").lower() == "ok":
                return {"result": "OK", "status": "SUCCESS"}
            else:
                return {
                    "status": "FAILURE",
                    "errorCategory": "FAILED",
                    "result": "Update Device to Decomm status in Inca is Failed",
                    "errors": [
                        {
                            "code": "ERR-011-999-0008",
                            "message": f"Update Device to Decomm status in Inca is Failed: "
                            f"{inca_response.get('result')}",
                        }
                    ],
                }
        except Exception as err:
            logger.exception(f"Exception occurred while updating INCA device decomm status: {err}")
            return {
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "result": "Update Device to Decomm status in Inca is Failed",
                "errors": [
                    {
                        "code": "ERR-011-999-0009",
                        "message": f"Update Device to Decomm status in Inca is Failed: " f"{err}",
                    }
                ],
            }

    def update_inca_type_details(self, **kwargs):
        """
        Retrieves the details of the gea from INCA
        Args:
        Returns:
            dict formatted data
        """
        logger.info(f"Inside Inca method to update {kwargs['type']} circuit status details")
        called_function = {
            "gea": self.gea_inca_update_status,
            "newMetroSwitch": self.new_metro_switch_inca_update_status,
        }
        update_response = called_function[kwargs["type"]](kwargs)
        logger.info(f"Response received from update inca: {update_response}")
        return update_response

    def get_inca_update_status(self, **kwargs) -> dict:
        """
        Retrieves the details of the gea from INCA
        Args:
        Returns:
            dict formatted data
        """
        logger.info(f"Inside Inca method to get {kwargs['job_id']} circuit status details")
        query_url = f"?id={kwargs['job_id'].replace('GC-', '').replace('BU-', '')}"
        try:
            type_url = base_url + kwargs["url"]
            logger.debug(f"Fetching {kwargs['job_id']} information from INCA url {type_url+query_url}")
            output = self.rest.get(url=type_url + query_url, timeout=20, headers=kwargs["headers"])
            logger.debug(f"output from get api is: {output}")
            if not isinstance(output, dict):
                return {
                    "jobId": kwargs["job_id"],
                    "status": "FAILURE",
                    "errorCategory": "FAILED",
                    "errors": [
                        {
                            "code": "ERR-011-999-0001",
                            "message": (
                                "Unexpected response from INCA: "
                                + (output.text if hasattr(output, "text") else str(output))
                            ),
                        }
                    ],
                }
            return self._job_state_response(output, kwargs)
        except RestUtilityException as err:
            logger.exception(f"Response Code from the response: {err.response.status_code}")
            raise RestUtilityException(f"{err.args[0]}", err.response) from err

    @staticmethod
    def _job_state_response(output: dict, kwargs: dict) -> dict:
        # sourcery skip
        """
        Static Method to analyse job and return response
        """
        logger.debug("Inside job state response formatting method")
        if not isinstance(output.get("results"), list) and output.get("results", "na").lower() == "no new message.":
            return {"jobId": kwargs["job_id"], "status": "IN-PROGRESS"}
        elif isinstance(output.get("results"), list) and "error" not in output.keys():
            result_data = {"jobId": kwargs["job_id"], "status": "FAILURE", "metadata": {}}
            circuit_list = []
            error_list = []
            for item in output.get("results"):
                circuit_data = {}
                circuit_data.update(
                    circuitId=item.get("or_cablelink_reference")
                    if "GC-" in kwargs["job_id"]
                    else item.get("cablelink_ref"),
                    status="success" if item.get("response").lower() == "ok" else "failure",
                )
                circuit_list.append(circuit_data)
                if item.get("response").lower() != "ok":
                    error_list.append(
                        {
                            "code": "ERR-011-999-0004",
                            "message": (
                                f"State update failed for gea circuitId {item.get('or_cablelink_reference')}: "
                                f"{item.get('response')}"
                                if "GC-" in kwargs["job_id"]
                                else f"Request failed for Id {item.get('cablelink_ref')}: {item.get('response')}"
                            ),
                        }
                    )
            if not error_list:
                result_data.update(status="SUCCESS")
            elif len(error_list) == len(output.get("results")):
                result_data.update(errorCategory="FAILED", errors=error_list)
            else:
                result_data.update(status="PARTIAL-SUCCESS", errorCategory="FAILED", errors=error_list)
            result_data["metadata"].update(circuitsStatus=circuit_list)
            return result_data
        elif "error" in output.keys():
            error = output.get("error").replace("statusDetail", "circuitDetails")
            return {
                "jobId": kwargs["job_id"],
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-011-999-0001",
                        "message": f"Request Validation failed for jobId {kwargs['job_id']} with error: " f"{error}",
                    }
                ],
            }
        else:
            return {
                "jobId": kwargs["job_id"],
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-011-999-0001",
                        "message": (
                            f"Request Validation failed for jobId {kwargs['job_id']} with error: "
                            f"{output.get('results')}"
                        ),
                    }
                ],
            }

    def gea_inca_update_status(self, kwargs: dict) -> dict:
        """
        Sends update request to INCA with built payload
        """
        formatted_body = {
            "status_details": [
                {
                    "or_cablelink_reference": item.get("circuitId"),
                    "status": item.get("configStatus"),
                    "config_date": item.get("configDate"),
                    **(
                        {"circuit_state": item.get("circuitState")}
                        if item.get("circuitState") in ["Ready-For-Config", "GEA-CEASE"]
                        else {}
                    ),
                    **({"spark_ref": item.get("sparkReference")} if item.get("sparkReference") else {}),
                    **({"test_ref": item.get("testRef")} if item.get("testRef") else {}),
                    **({"comments": item.get("comments")} if item.get("comments") else {}),
                    **({"dne_order_ref": item.get("orderRef")} if item.get("orderRef") else {}),
                    **({"config_cease_date": item.get("configCeaseDate")} if item.get("configCeaseDate") else {}),
                    **({"or_cease_date": item.get("orCeaseDate")} if item.get("orCeaseDate") else {}),
                    **({"or_cease_ref": item.get("orCeaseRef")} if item.get("orCeaseRef") else {}),
                    **(
                        {"order_reference": item.get("circuitCeaseOrderRef")}
                        if item.get("circuitCeaseOrderRef")
                        else {}
                    ),
                    **(
                        {"cease_submitted_date": item.get("ceaseSubmittedDate")}
                        if item.get("ceaseSubmittedDate")
                        else {}
                    ),
                }
                for item in kwargs["body"]["circuitDetails"]
            ]
        }
        type_url = base_url + kwargs["url"]
        logger.debug(f"Fetching {kwargs['type']} information from INCA url {type_url}")
        logger.info(f"Fetching {kwargs['type']} information from INCA request BODY {formatted_body}")
        inca_response = self.rest.post(
            url=type_url, data=json.dumps(formatted_body), timeout=20, headers=kwargs["headers"]
        )
        logger.info(f"Response received from INCA is {inca_response}")
        if inca_response.get("result").lower() == "ok":
            return {"jobId": "GC-" + inca_response.get("id")}
        else:
            return {
                "errorCategory": "RETRY" if "too many" in inca_response.get("result").lower() else "FAILED",
                "errors": [
                    {
                        "code": "ERR-011-999-0003",
                        "message": f"Failed to generate jobId with error: {inca_response.get('result')}",
                    }
                ],
            }

    def new_metro_switch_inca_update_status(self, kwargs):
        """
        Method implemented as a part of newMetroSwitch changes will trigger INCA api with hostname provided
        Returns formatted response for:
            case 1:
                Success Scenario: result is "ok"
            case 2:
                Record does not exist: result contains "no matching request found"
            case 3:
                permission denied: result contains "status does not permit rfs update"
        """
        input_body = {"hostname": kwargs["body"]["hostname"]}
        try:
            type_url = base_url + kwargs["url"]
            logger.info(
                f"Fetching {kwargs['type']} information from INCA url {type_url} and INCA request " f"BODY {input_body}"
            )
            inca_response = self.rest.put(
                url=type_url, data=json.dumps(input_body), timeout=20, headers=kwargs["headers"]
            )

            if inca_response.get("result", "").lower() == "ok":
                logger.info(f"New Switch RFS status is updated successfully for hostname {input_body['hostname']}")
                return {"status": "SUCCESS", "result": "OK", "metadata": {"hostname": input_body["hostname"]}}
        except RestUtilityException as err:
            logger.exception(f"Response Code from the response: {err.response.status_code}")
            error_msg = json.loads(err.response._content)
            error_msg = error_msg["result"] if isinstance(error_msg, dict) and "result" in error_msg else str(error_msg)
            inca_error_response = {
                "No matching request found": {
                    "metadata": {"hostname": input_body["hostname"]},
                    "result": "No matching request found",
                    "error_msg": {
                        "code": "ERR-011-999-0007",
                        "message": f"No matching request found for hostname {input_body['hostname']}",
                    },
                },
                "New Switch Request status does not permit RFS Update": {
                    "metadata": {"hostname": input_body["hostname"]},
                    "result": "New Switch Request status does not permit RFS Update",
                    "error_msg": {
                        "code": "ERR-011-999-0008",
                        "message": (
                            f"New Switch Request status does not permit RFS Update for hostname "
                            f"{input_body['hostname']}"
                        ),
                    },
                },
                "default": {
                    "metadata": {"hostname": input_body["hostname"]},
                    "result": "New Switch Request status failed",
                    "error_msg": {
                        "code": "ERR-011-999-0009",
                        "message": f"New Switch Request status failed for hostname {input_body['hostname']}",
                    },
                },
            }
            return {
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "result": inca_error_response.get(error_msg, inca_error_response["default"]).get("result"),
                "metadata": inca_error_response.get(error_msg, inca_error_response["default"]).get("metadata"),
                "errors": [inca_error_response.get(error_msg, inca_error_response["default"]).get("error_msg")],
            }

    def update_wholesale_details(self, **kwargs):
        """
        Update the circuit request details in the INCA
        Request:
          kwargs:
               url
               formatted_body
               requestType
               serviceType
               headers
        Response:
               Status/Exception
        """
        logger.info(
            f"Inside Inca module to update for wholesale {kwargs['serviceType']}:{kwargs['requestType']} details"
        )
        try:
            formatted_body = kwargs["formatted_body"]
            unique_request_identifier_key = {
                "uni": formatted_body.get("asset_Ref"),
                "interconnect": formatted_body.get("companyCode"),
                "partner": formatted_body.get("nniCode"),
            }
            logger.info(
                f"Inside Inca module to update wholesale {kwargs['serviceType']}:{kwargs['requestType']}"
                f" {unique_request_identifier_key[kwargs['serviceType']]}"
            )
            type_url = base_url + kwargs["url"]
            logger.info(f"Fetching {kwargs['requestType']} information from INCA url {type_url}")
            logger.debug(f"Fetching {kwargs['requestType']} information from INCA request BODY {formatted_body}")
            http_method = {
                "uni": {"new": "put", "update": "put", "cease": "put"},
                "partner": {"new": "post", "cease": "put"},
                "interconnect": {"new": "post", "update": "put", "cease": "put"},
            }
            inca_response = getattr(self.rest, http_method[kwargs["serviceType"]][kwargs["requestType"]])(
                url=type_url, data=json.dumps(formatted_body), headers=kwargs.get("headers")
            )
            logger.debug(
                f"Response received from INCA for wholesale"
                f" {kwargs['serviceType']}:{kwargs['requestType']} is {inca_response}"
            )
            if inca_response.get("result") == "OK":
                return {"status": "SUCCESS"}
        except RestUtilityException as err:
            logger.exception(f"Response Code from the response: {err.response.status_code}")
            error_msg = json.loads(err.response._content)
            error_msg = error_msg["result"] if isinstance(error_msg, dict) and "result" in error_msg else str(error_msg)
            inca_error_response = {
                "No matching request found": {
                    "code": "ERR-011-999-0007",
                    "message": "No matching request found for given Asset ID",
                },
                "Wholesale Request status does not permit Updates": {
                    "code": "ERR-011-999-0009",
                    "message": "Wholesale request update is not allowed",
                },
                "default": {
                    "code": "ERR-011-999-0010",
                    "message": f"Wholesale validation failed for parameter: `{error_msg}`",
                },
                "Company Code must be unique": {
                    "code": "ERR-011-999-0011",
                    "message": "Partner code already exists in INCA",
                },
                "Company Name must be unique": {
                    "code": "ERR-011-999-0012",
                    "message": "Partner name already exists in INCA",
                },
                "NNI Code must be unique": {
                    "code": "ERR-011-999-0012",
                    "message": "NNI Asset ID already exists",
                },
                "Company Code not found in INCA": {
                    "code": "ERR-011-999-0015",
                    "message": "Partner code not found in INCA",
                },
                "Remote BB PE hostname not found in INCA": {
                    "code": "ERR-011-999-0014",
                    "message": "Remote NNI-PE hostname not found in INCA",
                },
                "Company Code not found": {
                    "code": "ERR-011-999-0015",
                    "message": "Partner code is not found in INCA",
                },
                "nniCode not found in INCA": {
                    "code": "ERR-011-999-0016",
                    "message": "NNI Asset ID is not found in INCA",
                },
            }
            return {
                "status": "FAILED",
                "errorCategory": "FAILED",
                "errors": [inca_error_response.get(error_msg, inca_error_response["default"])],
            }

    def cease_circuit(self, **kwargs) -> dict:
        """
        method to cease a existing gea circuit
        Args:
        Returns:
            dict formatted data
        """
        logger.info(f"Inside Inca method to cease {kwargs['type']} circuit")
        function_map = {"gea": self.cease_gea_circuit}
        response = function_map[kwargs.get("type")](**kwargs)
        logger.info(f"Response received from write inca: {response}")
        return response

    def cease_gea_circuit(self, **kwargs) -> dict:
        """
        Sends write request to INCA with built payload
        """
        cit_data = kwargs.get("body", {}).get("geaCeaseDetails", {})
        formatted_body = {
            "request_date": cit_data.get("requestDate"),
            "exchange": cit_data.get("exchange"),
            "tg_reference": cit_data.get("tgReference"),
            "required_by_date": cit_data.get("requiredByDate"),
            "bt_switch": cit_data.get("btSwitch"),
            "order_reference": cit_data.get("circuitCeaseOrderRef"),
            "cablelink_ref": cit_data.get("cablelinkRef"),
            "message_type": cit_data.get("messageType"),
        }
        type_url = base_url + kwargs["url"]
        logger.debug(f"Fetching {kwargs['type']} {kwargs.get('requestType')} information from INCA url {type_url}")
        logger.info(
            f"Fetching {kwargs['type']} {kwargs.get('requestType')} information from INCA "
            f"request BODY {formatted_body}"
        )
        inca_response = self.rest.post(
            url=type_url, data=json.dumps(formatted_body), timeout=20, headers=kwargs["headers"]
        )
        logger.info(f"Response received from INCA is {inca_response}")
        if inca_response.get("result").lower() == "ok":
            return {"jobId": "BU-" + inca_response.get("id")}
        else:
            return {
                "errorCategory": "RETRY" if "too many" in inca_response.get("result").lower() else "FAILED",
                "errors": [
                    {
                        "code": "ERR-011-999-0003",
                        "message": (
                            f"GEA Cease request: Failed to generate jobId with error: {inca_response.get('result')}"
                        ),
                    }
                ],
            }
