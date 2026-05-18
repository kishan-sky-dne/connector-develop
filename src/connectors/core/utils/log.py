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
import sys
from datetime import datetime

# Third Party Library
from connexion import request
from dateutil import tz
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname
        if not log_record.get("timestamp"):
            now = datetime.now(tz.gettz("Europe/London")).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            log_record["timestamp"] = now

        """
        Assigning request headers values to custom logging format to enable tracing only when request
        context is available
        """
        if request:
            request_json = log_request_info()
            log_record["X-Request-ID"] = request_json["request_id"]
            log_record["X-Forwarded-For"] = request_json["forwarded_for"]
            log_record["X-Forwarded-Host"] = request_json["forwarded_host"]
            log_record["X-Forwarded-Proto"] = request_json["protocol"]
            log_record["remote-address"] = request_json["remote_address"]


def setup_logger(logger):
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    formatter = CustomJsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(X-Request-ID)s %(X-Forwarded-For)s "
        "%(X-Forwarded-Host)s %(X-Forwarded-Proto)s %(remote-address)s %(message)s %(pathname)s %(funcName)s %(lineno)s"
    )
    ch.setFormatter(formatter)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)


def log_request_info():
    request_id = request.headers.get("X-Request-ID")
    forwarded_for = request.headers.get("X-Forwarded-For")
    remote_address = request.remote_addr
    forwarded_host = request.host.split(":", 1)[0]
    protocol = request.headers.get("X-Forwarded-Proto")
    return {
        "request_id": request_id,
        "forwarded_for": forwarded_for,
        "remote_address": remote_address,
        "forwarded_host": forwarded_host,
        "protocol": protocol,
    }
