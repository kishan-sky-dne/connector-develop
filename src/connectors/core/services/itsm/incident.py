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
from connectors.core.utils.rest_api_utility import RestUtility

logger = logging.getLogger(__name__)

cag_base_url = config.get(section="itsm", key="cag_base_url")
api_key = config.get(section="itsm", key="cag_api_key")


class Incident:
    def __init__(self, **kwargs):
        """
        Incident Constructor. Class to generate incident ticket through CAG in SPARK.
        Kwargs:
            alertSummary(string)
            assignTo(string)
            detailedDescription(string)
            severity(string)
            monitoredItem(string)
            affectedArea(string)
            helpURL(string)
            monitoringGroup(string)
            monitoringSystem(string)
            updatable(string)
            orderId(string)
            orderType(string)
            changeTicket(string)
        """
        request_body = kwargs["body"]
        self.alert_summary = request_body.get("alertSummary")
        self.assign_to = request_body.get("assignTo")
        self.detailed_description = request_body.get("detailedDescription")
        self.severity = request_body.get("severity")
        self.monitored_item = request_body.get("monitoredItem")
        self.affected_area = request_body.get("affectedArea")
        self.help_url = request_body.get("helpURL")
        self.monitoring_group = request_body.get("monitoringGroup")
        self.monitoring_system = request_body.get("monitoringSystem")
        self.updatable = request_body.get("updatable")
        self.order_id = request_body.get("orderId")
        self.order_type = request_body.get("orderType")
        self.change_ticket = request_body.get("changeTicket")
        self.rest = RestUtility()

    def create_incident_ticket(self):
        """
        Sends a request to CAG to generate an incident ticket
        after validating the given payload and building one for CAG
        and returns the results
        """
        status, error_message = self._validate_payload()
        if not status:
            return error_message

        payload = self._build_payload()

        try:
            results = self.rest.post(url=f"{cag_base_url}submit", data=json.dumps(payload))
        except RestUtilityException as err:
            logger.exception(f"RestUtility post request to CAG failed with error {err.args[0]}. ")
            return {
                "status": "FAILURE",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-003-999-0002",
                        "message": f"Internal Error Generating Incident Ticket. {err.args[0]}.",
                    }
                ],
            }
        results["status"] = "SUCCESS"
        return results

    def _validate_payload(self):
        """
        Checks if alert_summary is given or could be created
        and returns status and error_message
        """
        if not self.alert_summary:
            if self.order_id and self.order_type and self.change_ticket:
                self.alert_summary = (
                    "Incident raised as part of DNE order "
                    f"{self.order_id} ({self.order_type}) under {self.change_ticket}"
                )
            else:
                return (
                    False,
                    {
                        "status": "FAILURE",
                        "errorCategory": "FAILED",
                        "errors": [
                            {
                                "code": "ERR-003-999-0001",
                                "message": "At least one of the following conditions must be met: "
                                "1.Include 'alertSummary'  "
                                "2.Include all three 'orderId', 'orderType' and 'changeTicket'",
                            }
                        ],
                    },
                )
        return (True, "none")

    def _build_payload(self):
        """
        Creates the payload to be sent to CAG
        """
        payload = {
            "alert_summary": self.alert_summary,
            "assign_to": self.assign_to,
            "detailed_description": self.detailed_description,
            "severity": self.severity,
            "monitored_item": self.monitored_item,
            "apikey": api_key,
        }
        optional_attributes = ["affected_area", "help_url", "monitoring_group", "monitoring_system", "updatable"]
        for attr in optional_attributes:
            value = getattr(self, attr)
            if value is not None:
                payload[attr] = value
        return payload
