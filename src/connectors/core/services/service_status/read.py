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

# Third Party Library
import connexion

# DNE Library
from connectors.core.exceptions import ServiceDBException
from connectors.core.utils.serviceDB import ServiceDB

logger = logging.getLogger(__name__)


class ServiceStatus:
    def __init__(self, **kwargs):
        """
        Service Status Constructor. Class to retrieve the status for the required services
        Kwargs:
            orderId(string)
            serviceType(string)
            operationType(string)
        """
        self.order_id = kwargs.get("orderId")
        self.service_type = kwargs.get("serviceType")
        self.operation_type = kwargs.get("operationType")
        self.errors = []
        logger.info(
            f"Initializing Service Status with {self.service_type} service(s) "
            f"'{self.order_id}' order ID and '{self.operation_type}' operation"
        )
        self.service_status_db_instance = self._instantiate_service_db("service-status")
        self.service_status_details = {}
        self.schema_record = {}
        # deltaBase specific states: "VERIFIED", "CONFIGURING", "CONFIGURED"
        # "ROLLBACK-VERIFIED", "ROLLBACK", "ROLLBACK-INITIATE"
        self.state_mapper = {
            "create": {
                "success": ["ACTIVE", "VERIFIED"],
                "in_progerss": ["PLANNED", "PROVISIONING", "PROVISIONED", "CONFIGURING", "CONFIGURED"],
            },
            "delete": {
                "success": ["INACTIVE", "ROLLBACK-VERIFIED"],
                "in_progerss": ["PLANNED", "DECOMMISSIONING", "DECOMMISSIONED", "ROLLBACK", "ROLLBACK-INITIATE"],
            },
        }

    def get_service_status(self):
        """
        Retrieves the service status details for all the given services.
        Returns:
            Dict: Formatted service status details.
        """
        if not self.service_status_db_instance:
            return connexion.problem(
                status=500,
                title="Failed to connect to the serviceDB.",
                detail=", ".join(self.errors),
            )
        for service_type in self.service_type:
            service_type = service_type.strip()
            self.schema_record = self._get_schema_record(service_type)
            if not self.schema_record:
                return connexion.problem(
                    status=500,
                    title="Failed to fetch record from service status collection",
                    detail=", ".join(self.errors),
                )
            if not self._validate_service_status_schema_record():
                return connexion.problem(
                    status=500,
                    title=f"Service Status Read Schema is not valid for {service_type}",
                    detail=", ".join(self.errors),
                )
            service_db_instance = self._instantiate_service_db(self.schema_record["collection"])
            if not service_db_instance:
                return connexion.problem(
                    status=500,
                    title="Failed to connect to the serviceDB.",
                    detail=", ".join(self.errors),
                )
            data = service_db_instance.aggregate(self._build_query())
            self._check_not_attempted_service(data, service_type)
            self._check_in_progress_state(data, service_type)
            if service_type not in self.service_status_details:
                self._check_success_failure_states(data, service_type)
        return {"orderId": self.order_id, "serviceStatusDtls": self.service_status_details}

    def _check_not_attempted_service(self, data, service_type):
        """
        Checks if any service record is found, and removes invalid records, if any.
        """
        if not data:
            self.service_status_details[service_type] = "Not Attempted"

    def _check_in_progress_state(self, data, service_type):
        """
        Checks if any of the service records is in 'In Progress' state.
        """
        for service in data:
            if service["record"]["state"] in self.state_mapper[self.operation_type]["in_progerss"]:
                self.service_status_details[service_type] = "In Progress"
                break

    def _check_success_failure_states(self, data, service_type):
        """
        Checks whether the service is in Success or Failure state.
        """
        services_in_success_state, services_in_failure_state = self._segregate_active_inactive_records(data)
        if not services_in_success_state:
            self.service_status_details[service_type] = "Failure"
            if self.schema_record["returnKeys"] != "NA":
                self.service_status_details[f"{str(service_type)}Dtls"] = {
                    "failure": [service for service in services_in_failure_state if service]
                }
        elif not services_in_failure_state:
            self.service_status_details[service_type] = "Success"
            if self.schema_record["returnKeys"] != "NA":
                self.service_status_details[f"{str(service_type)}Dtls"] = {
                    "success": [service for service in services_in_success_state if service]
                }
        else:
            self.service_status_details[service_type] = "Partial Success"
            if self.schema_record["returnKeys"] != "NA":
                self.service_status_details[f"{str(service_type)}Dtls"] = {
                    "success": [service for service in services_in_success_state if service],
                    "failure": [service for service in services_in_failure_state if service],
                }

    def _segregate_active_inactive_records(self, data):
        """
        Segregates active and inactive records.
        """
        services_in_success_state = []
        services_in_failure_state = []
        for service in data:
            if service["record"]["state"] in self.state_mapper[self.operation_type]["success"]:
                services_in_success_state.append(service["record"])
            else:
                services_in_failure_state.append(service["record"])
            del service["record"]["state"]
        return services_in_success_state, services_in_failure_state

    def _instantiate_service_db(self, collection):
        """
        Connects to the serviceDB and selects the given collection.

        Returns:
            ServiceDB: The serviceDB object for the given collection.
        """
        try:
            return ServiceDB(collection)
        except ServiceDBException as err:
            logger.exception(err.args[0])
            self.errors.append(err.args[0])
        return None

    def _validate_service_status_schema_record(self):
        """
        Validates the fetched schema record.

        Returns:
            Boolean: False if error found else true.
        """
        if "collection" not in self.schema_record:
            return self._capture_schema_error("'collection' key not found in schema")
        if "uniqueKeys" not in self.schema_record:
            return self._capture_schema_error("'uniqueKeys' key not found in schema")
        if "returnKeys" not in self.schema_record:
            return self._capture_schema_error("'returnKeys' key not found in schema")
        if not isinstance(self.schema_record["uniqueKeys"], str):
            return self._capture_schema_error("'uniqueKeys' in schema must have string type")
        return (
            True
            if isinstance(self.schema_record["returnKeys"], dict) or self.schema_record["returnKeys"] == "NA"
            else self._capture_schema_error("'returnKeys' in schema must have object type or be 'NA'")
        )

    def _capture_schema_error(self, arg0):
        """
        Captures error in schema.

        Returns:
            Boolean: False.
        """
        logger.exception(arg0)
        self.errors.append(arg0)
        return False

    def _get_schema_record(self, service_type):
        """
        Queries the service-status collection with the service_type parameter.

        Returns:
            Dict: The schema record for the service.
        """
        try:
            return self.service_status_db_instance.find_one(query={"service": service_type})
        except ServiceDBException as err:
            logger.exception(err.args[0])
            self.errors.append(err.args[0])
        return None

    def _build_query(self):
        """
        Builds a serviceDB query based on the request parameters
        and the stored keys in the db for the requested service.

        Returns:
            List: ServiceDB aggregate query.
        """
        return [
            {"$match": {"orderId": self.order_id, "state": {"$exists": True}}},
            {"$sort": {"createdDate": -1}},
            {
                "$group": {
                    "_id": self._process_unique_keys(),
                    "createdDate": {"$max": "$createdDate"},
                    "document": {"$push": "$$CURRENT"},
                }
            },
            {"$project": {"_id": 0, "record": {"$arrayElemAt": ["$document", 0]}}},
            {"$project": {"record": self._process_return_keys()}},
        ]

    def _process_unique_keys(self):
        """
        Processes the stored unique keys in serviceDB for the current requested service.

        Returns:
            dict: The formatted unique keys to be used in the query.
        """
        if self.schema_record["uniqueKeys"] == "NA":
            return {"orderId": "$orderId"}
        unique_keys_list = self.schema_record["uniqueKeys"].split(",")
        return {unique_keys.strip().replace(".", ""): f"${unique_keys.strip()}" for unique_keys in unique_keys_list}

    def _process_return_keys(self):
        """
        Processes the stored return keys in serviceDB for the current requested service.

        Returns:
            dict: The formatted return keys to be used in the query projection.
        """
        if self.schema_record["returnKeys"] == "NA":
            return {"record": {"_id": 0}}
        processed_return_keys = self.schema_record["returnKeys"]
        processed_return_keys["state"] = 1
        return processed_return_keys
