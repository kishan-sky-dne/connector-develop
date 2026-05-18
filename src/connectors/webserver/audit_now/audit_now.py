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
import threading

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.utils.audit_now import AuditNowThread

logger = logging.getLogger(__name__)

stop_event = threading.Event()

topic = config.get(section="auditnow", key="topic")
AUDITNOW_THREAD_NAME = "AuditNowThread"


def start_audit_now() -> dict:
    """
    Starts AuditNow thread for Skybridge transactions.
    """
    logger.info(f"Received request to start the AuditNow thread with topic {topic}.")
    stop_event.clear()
    audit_now_thread = AuditNowThread(topic, stop_event)
    if audit_now_thread.is_alive():
        logger.info("The AuditNow thread is already running.")
        return {"info": "AuditNow is already running."}
    audit_now_thread.name = AUDITNOW_THREAD_NAME

    audit_now_thread.start()
    logger.info("Started the AuditNow thread.")
    return {"info": "Started AuditNow."}


def stop_audit_now() -> dict:
    """
    Stops AuditNow thread.
    """
    logger.info("Received request to stop the AuditNow thread.")
    for thread in threading.enumerate():
        if thread.name == AUDITNOW_THREAD_NAME:
            logger.info("Setting the stop event to terminate the AuditNow thread.")
            stop_event.set()
            return {"info": "Stopped AuditNow."}
    logger.info("The AuditNow thread is not running.")
    return {"info": "AuditNow is not running."}


def audit_now_status() -> dict:
    """
    Checks AuditNow thread status.
    """
    for thread in threading.enumerate():
        if thread.name == AUDITNOW_THREAD_NAME:
            logger.info("AuditNow is running.")
            return {"info": "AuditNow is running."}
    logger.info("AuditNow is not running.")
    return {"info": "AuditNow is not running."}
