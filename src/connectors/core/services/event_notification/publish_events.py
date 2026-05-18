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
import logging

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.utils.exceptions import ConnectorException
from connectors.core.utils.helpers import create_dict_from_string
from connectors.core.utils.kafka import KafkaProducer
from connectors.models.order_status import Payload

logger = logging.getLogger(__name__)

order_status_delivery_timeout = int(config.get(section="kafka", key="order_status_delivery_timeout"))
order_status_connectivity_timeout = int(config.get(section="kafka", key="order_status_connectivity_timeout"))
order_status_flush_timeout = int(config.get(section="kafka", key="order_status_flush_timeout"))
topic_mapper = config.get(section="orderStatus", key="topic_mapper")
url = config.get(section="orderStatus", key="url")


class OrderStatus:
    def __init__(self, **kwargs):
        """
        Order Status Constructor. Class to publish DNE order status to Kafka.
        Kwargs:
            keyId(string)
            message(dict)
            eventTime(int)
            eventSource(string)
        """
        request_body = kwargs["body"]
        # validate the payload
        payload = Payload(**request_body)
        self.key_id = payload.keyId
        self.message = dict(payload.message)
        self.event_time = payload.eventTime
        self.event_source = payload.eventSource
        self.topic_mapper = create_dict_from_string(topic_mapper)
        self.kafka_producer = KafkaProducer(
            delivery_timeout=order_status_delivery_timeout, ignore_delivery_failures=self.topic_mapper["standard"]
        )
        try:
            self.use_case_topic = self.topic_mapper[self.message.get("orderType")]
            self.standard_topic = self.topic_mapper["standard"]  # This should always be present
        except KeyError as err:
            logger.exception(f"Topic not found in the relevant environment variable {err.args[0]}")
            raise ConnectorException("Invalid orderType") from err

    def publish(self):
        """
        Orchestrates the execution of order_status publication
        and returns the response
        """
        self.kafka_producer._connectivity_check(order_status_connectivity_timeout)
        if self.kafka_producer.errors:
            return self.kafka_error_message

        self._prepare_kafka_message()

        self._produce_to_kafka()
        if self.kafka_producer.errors:
            return self.kafka_error_message

        return {"status": "SUCCESS"}, 200

    def _produce_to_kafka(self):
        """
        Sends the message to both the standard and the usecase specific topics
        and makes a flush call immediately
        """
        self.kafka_producer.send(topic=self.use_case_topic, key=self.key_id, value=self.message)
        self.kafka_producer.send(topic=self.standard_topic, key=self.key_id, value=self.message)
        # flush timeout is expected to be greater than the producer's delivery timeout per message
        # to ensure delivery reports are captured before terminating the producer
        self.kafka_producer.flush_and_close(order_status_flush_timeout)

    def _prepare_kafka_message(self):
        """
        Appends metadata and other required information to the message
        """
        self.message["eventTime"] = self.event_time
        self.message["eventSource"] = self.event_source
        self.message["metadata"] = {
            "eventTime": str(datetime.datetime.now(datetime.timezone.utc)),
            "url": url + str(self.message["orderNumber"]),
        }

    @property
    def kafka_error_message(self):
        return {"status": "FAILURE", "errorCategory": "FAILED", "errors": self.kafka_producer.errors}, 500
