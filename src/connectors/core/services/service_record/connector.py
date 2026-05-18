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

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.exceptions import ServiceDBException
from connectors.core.utils.serviceDB import ServiceDB

logger = logging.getLogger(__name__)

# GLOBALS
RECORDS_PER_PAGE = int(config.get(section="service_record", key="records_per_page"))
MAX_TIME_MS = int(config.get(section="service_record", key="max_time_ms"))


class ServiceRecordService:
    def __init__(self, request_body: dict, use_case_schema_record: dict, include: str | None = None) -> None:
        """
        Retrieves the service record details by making aggregate db query
        """
        logger.info("Initializing Service Record Service")
        self.request_body = request_body
        self.use_case_schema_record = use_case_schema_record
        self.include = include

    def get_service_record(self) -> dict:
        """
        Calls _get_service_record to retrieve service record details and handles db exceptions
        """
        logger.info("Inside fetch service record method to get service record details")
        try:
            return self._get_service_record()
        except ServiceDBException as err:
            message = f"Exception occurred due to {err.args[0]}"
            logger.exception(message)
            raise ServiceDBException(message) from err

    def _get_service_record(self) -> dict:
        """
        Retrieves the service record details from DB
        """
        # Construct query for aggregation
        request_records_per_page = self.request_body.get("recordsPerPage", 10)
        request_page_number = self.request_body.get("pageNumber", 1)
        records_per_page = request_records_per_page if RECORDS_PER_PAGE <= 50 else 50

        # Initialize specific service collection ref
        service_mapper = {
            "service": {
                "skyTalk": "sky-talk-lifecycle",
                "unifiedManagement": "unified-management-lifecycle",
                "deltaBase": "me-to-ma-data",
                "metroLink": "metro-link-lifecycle",
                "metroRR": "metro-rr-lifecycle",
                "ubb": "ubb-service",
                "wholesale": "wholesale-lifecycle",
                "dia": "dia-create-lifecycle",
            },
            "audit": {
                "skyTalk": "sky-talk-audit-log",
                "unifiedManagement": "unified-management-audit-log",
                "deltaBase": "me-to-ma-audit-log",
                "metroLink": "metro-link-audit-log",
                "metroRR": "metro-rr-audit-log",
                "ubb": "ubb-audit-log",
                "wholesale": "wholesale-audit-log",
                "verify-l2circuit": "verify-l2circuit-audit-log",
                "dia": "audit",
            },
        }

        service_collection_ref = ServiceDB(service_mapper[self.request_body["data"]][self.request_body["service"]])
        match_query = self.get_match_query()
        total_records = self.get_total_records(service_collection_ref, match_query)
        end_page_index = 0
        start_page_index = 0
        records = []
        if total_records:
            final_query = [
                {"$match": match_query},
                {"$sort": self.get_sort_query()},
                {
                    "$project": (
                        self.use_case_schema_record[self.request_body["data"]]["responseMapBrief"]
                        if self.include == "brief"
                        else self.use_case_schema_record[self.request_body["data"]]["responseMap"]
                    )
                },
                {"$skip": (request_page_number - 1) * records_per_page},
                {"$limit": records_per_page},
            ]
            records = service_collection_ref.aggregate(final_query, maxTimeMS=MAX_TIME_MS)
            # Start Index of the record in this page. Based on pageNumber and recordsPerPage
            start_page_index = (request_page_number - 1) * records_per_page + 1
            next_end_page_index = request_page_number * request_records_per_page
            # End index of the record in this page Based on pageNumber, recordsPerPage and number of records
            end_page_index = (
                next_end_page_index
                if next_end_page_index <= total_records[0]["totalRecords"]
                else start_page_index + (total_records[0]["totalRecords"] % records_per_page) - 1
            )
        return {
            "totalRecords": total_records[0]["totalRecords"] if total_records else len(total_records),
            "recordsPerPage": request_records_per_page if records else 0,
            "pageNumber": request_page_number if records else 0,
            "pageStartIndex": start_page_index,
            "pageEndIndex": end_page_index,
            "data": records,
        }

    def get_match_query(self):
        """
        Construct the match query for the provided filters
        Args:
        Returns:
            combined_query
        """
        combined_query = {}
        prev_operator = ""
        for filter_req in self.request_body["filters"]:
            value = filter_req["values"] if filter_req["operator"] in ["in", "nin"] else filter_req["values"][0]
            query = {filter_req["param"]: {f"${filter_req['operator']}": value}}
            operator = filter_req.get("filterLogicalOperator")
            if not operator and not combined_query:
                combined_query = query
            elif not combined_query:
                combined_query = {f"${operator}": [query]}
            elif f"${prev_operator}" in combined_query:
                combined_query[f"${prev_operator}"].append(query)
            else:
                combined_query = {f"${prev_operator}": [combined_query, query]}
            prev_operator = operator
        return combined_query

    def get_sort_query(self):
        """
        Construct the sorting param
        Args:
        Returns:
            sort_query
        """
        sort_query_mapper = {"asc": 1, "dsc": -1}
        return {_sort["param"]: sort_query_mapper[_sort["order"]] for _sort in self.request_body["sort"]}

    @staticmethod
    def get_total_records(service_collection_ref, match_query):
        total_record_query = [
            {"$match": match_query},
            {"$count": "totalRecords"},
        ]
        return service_collection_ref.aggregate(total_record_query, maxTimeMS=MAX_TIME_MS)
