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
import re

# Third Party Library
import connexion

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.exceptions import ServiceDBException
from connectors.core.services.service_record.connector import ServiceRecordService
from connectors.core.utils.helpers import exception_handler, load_json_data, validate_json_schema
from connectors.core.utils.serviceDB import ServiceDB

logger = logging.getLogger(__name__)
mongo_use_case_schema_mapper = "usecase-schema-mapper"
APP_PATH = config.get(section="internals", key="app_path")


def validate_payload(request_body: dict, schema_record: dict, error_details: list) -> list:
    """
    Validate the service record payload fields
    Args:
        request_body:
        schema_record:
        error_details:

    Returns:
        error_details
    """
    logger.info(f"Entering into validate payload of service record read for {request_body['service']} service")
    filter_map_values = [
        value
        for data in schema_record[request_body["data"]]["filterMaps"]
        for key, value in data.items()
        if key != "pattern"
    ]
    sort_map_values = [value for data in schema_record[request_body["data"]]["sortMaps"] for key, value in data.items()]
    # Validate filters
    for _filter in request_body["filters"]:
        for filter_map in schema_record[request_body["data"]]["filterMaps"]:
            filter_value = [value for key, value in filter_map.items() if key != "pattern"][0]
            if _filter["param"] == filter_value:
                for value in _filter["values"]:
                    if "$" in value:
                        error_details.append(
                            {
                                "code": "ERR-011-078-1003",
                                "message": f"Provided filter value {value} must not contain $ character",
                            }
                        )
                    if "pattern" in filter_map and not bool(re.match(filter_map["pattern"], value)):
                        error_details.append(
                            {
                                "code": "ERR-011-078-1004",
                                "message": f"Provided filter value {value} did not match with the pattern "
                                f"{filter_map['pattern']}",
                            }
                        )
        if _filter["param"] not in filter_map_values:
            error_details.append(
                {
                    "code": "ERR-011-078-1002",
                    "message": f"Provided filter param {_filter['param']} is not present in schema mapper "
                    f"filterMaps: {filter_map_values}",
                }
            )

    # Validate sort
    for _sort in request_body["sort"]:
        if _sort["param"] not in sort_map_values:
            error_details.append(
                {
                    "code": "ERR-011-078-1005",
                    "message": f"Provided sort param {_sort['param']} is not present in schema mapper "
                    f"sortMaps: {sort_map_values}",
                }
            )
    logger.info(f"Exiting the validate payload of service record read for {request_body['service']} service")
    return error_details


@exception_handler
def get_service_record(**kwargs):
    """
    calling service record module to retrieve the service record - DB data
    kwargs:
        type: query parameter and body response - Mandatory field
    Returns:
            formatted service record data
    Raises:
        Exception

    """
    logger.info(f"Entering into service record read module to fetch details for {kwargs['type']} collection retrieval")
    try:
        request_body = kwargs["body"]
        logger.info("Validating GET services/service/facts API params using json schema")
        file_name = f"{APP_PATH}/json_schema/service_record/{kwargs['type']}/read.json"
        schema, error_message = load_json_data(file_name, f"Service Record Read for type: {kwargs['type']}")
        if not schema:
            return connexion.problem(
                status=404,
                detail=error_message,
                title="Page Not Found",
            )
        status, detail = validate_json_schema(request_body, schema)
        if not status:
            return connexion.problem(
                status=400,
                detail=detail,
                title="Bad Request",
            )

        if kwargs["type"] == "mongo":
            error_details = []
            collection_ref = ServiceDB(mongo_use_case_schema_mapper)
            usecase_schema_record = collection_ref.find_one(query={"usecase": request_body["service"]})
            error_details = validate_payload(request_body, usecase_schema_record, error_details)
            if error_details:
                return {"errorCategory": "FAILED", "errors": error_details}
            record_instance = ServiceRecordService(request_body, usecase_schema_record, include=kwargs.get("_include"))
            return record_instance.get_service_record()
        raise NotImplementedError(f"{kwargs['type']} is not implemented!")

    except ServiceDBException as err:
        message = f"Connector exception raised while retrieving service record due to {err.args[0]}"
        logger.exception(message)
        return {"errorCategory": "FAILED", "errors": [{"code": "ERR-011-078-1001", "message": message}]}
    except (TypeError, KeyError, AttributeError) as err:
        message = f"Exception occurred due to {err.args[0]}"
        logger.exception(message)
        return {"errorCategory": "FAILED", "errors": [{"code": "ERR-011-078-1006", "message": message}]}
    except Exception as err:
        message = f"Generic Exception occurred due to {err.args[0]}"
        logger.exception(message, exc_info=True)
        return {"errorCategory": "FAILED", "errors": [{"code": "ERR-011-078-1007", "message": message}]}
