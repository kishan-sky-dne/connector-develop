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
from collections.abc import Generator

# Third Party Library
from confluent_kafka import Consumer, KafkaError, KafkaException, Message, Producer

# DNE Library
from connectors.core.config.connectors_config import config

logger = logging.getLogger(__name__)

bootstrap_servers = config.get(section="kafka", key="bootstrap_servers")
reset = config.get(section="kafka", key="reset")
commit = config.get(section="kafka", key="commit") or False
sasl_username = config.get(section="kafka", key="sasl_username")
sasl_password = config.get(section="kafka", key="sasl_password")
sasl_username_write = config.get(section="kafka", key="sasl_username_write")
sasl_password_write = config.get(section="kafka", key="sasl_password_write")


class KafkaConsumer:
    def __init__(self, topic, group_id, stop_event):
        """
        Initializes Kafka consumer with the configuration specified in environment variables.
        Args:
            topic (str): The Kafka topic to consume from.
            stop_event (Event): The threading event to break the loop.
        """
        logger.info("Initializing Kafka Consumer")
        config = {
            "bootstrap.servers": bootstrap_servers,
            "auto.offset.reset": reset,
            "group.id": group_id,
            "enable.auto.commit": commit,
            "security.protocol": "SASL_SSL",
            # "ssl.ca.location": "/etc/ssl/certs/ca-certificates.crt",
            "enable.ssl.certificate.verification": False,
            "sasl.mechanism": "SCRAM-SHA-256",
            "sasl.username": sasl_username,
            "sasl.password": sasl_password,
        }

        self.consumer = Consumer(config)
        self.topic = topic
        self.stop_event = stop_event
        self.consumer.subscribe(self.topic)
        logger.debug(f"Kafka Consumer subscribing to {self.topic}")

    def start(self) -> Generator[tuple[dict, Message], None, None]:
        """
        Starts consuming messages and yields new messages.
        """
        while not self.stop_event.is_set():
            message, msg = self.consume()
            if message:
                yield message, msg

    def consume(self) -> tuple[dict, Message]:
        """
        Consumes and returns messages from Kafka topic
        """
        try:
            # Consumes a single message. Timeout in one second.
            msg = self.consumer.poll(1.0)

            # prevent the loop from being blocked when there are no new messages
            if msg is None:
                return {}, msg
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.error(
                        f"topic {msg.topic()} in partition {msg.partition()} Reached end at offset {msg.offset()}"
                    )
                elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                    logger.error(f"Topic does not exist: {self.topic}")
                else:
                    logger.error(f"Error while consuming messages: {msg.error()}")
                return {}, msg
            elif msg.value() is not None:
                processed_message = self._process_message(msg)
                logger.debug(f"Consumed message: {processed_message} from topic: {msg.topic()}")
                return processed_message, msg

        except KafkaException as exception:
            logger.exception(f"Kafka exception raised while consuming messages: {str(exception)}")
            raise

    def _process_message(self, message: Message) -> dict | str:
        """
        Parses a Kafka message by decoding it as JSON or string.
        """
        try:
            return json.loads(message.value())
        except json.decoder.JSONDecodeError:
            return message.value().decode()

    def stop(self) -> None:
        """
        Stops the Kafka consumer.
        """
        logger.info("Closing Kafka consumer")
        if self.consumer is not None:
            self.consumer.close()

    def connectivity_check(self) -> None:
        """
        Tests Kafka Consumer connectivity by requesting metadata from the cluster.
        """
        try:
            self.consumer.list_topics(timeout=2)
            logger.info("Successfully connected to Kafka cluster")
        except KafkaException as exception:
            logger.error(f"Failed to connect to Kafka cluster. {exception}")


class KafkaProducer:
    def __init__(self, delivery_timeout=0, ignore_delivery_failures=""):
        """
        Initializes a Kafka producer with the specified bootstrap servers in environment variables.
        """
        logger.info("Creating a new Producer instance")
        config = {
            "bootstrap.servers": bootstrap_servers,
            "delivery.timeout.ms": delivery_timeout,
            "security.protocol": "SASL_SSL",
            "ssl.ca.location": "/etc/ssl/certs/ca-certificates.crt",
            "enable.ssl.certificate.verification": False,
            "sasl.mechanism": "SCRAM-SHA-256",
            "sasl.username": sasl_username_write,
            "sasl.password": sasl_password_write,
        }
        logger.debug(
            f"Configuring Kafka Producer with bootstrap_servers: {bootstrap_servers} "
            f"delivery_timeout: {delivery_timeout}"
        )
        self.errors = []
        self.producer = Producer(config)
        self.ignore_delivery_failures = ignore_delivery_failures

    def send(self, topic, value, key=None, partition=None):
        """
        Sends a message to the specified topic in Kafka.

        Args:
            key: The key of the message.
            topic: The kafka destination topic.
            value: The value of the message.
            partition: The target partition for the message.
        """
        try:
            if partition:
                self.producer.produce(
                    topic=topic,
                    key=self._process_message(key),
                    value=self._process_message(value),
                    partition=partition,
                    callback=self._delivery_callback,
                )
            # partition based on a hash of the key (if provided) else round-robin
            else:
                self.producer.produce(
                    topic=topic,
                    key=self._process_message(key),
                    value=self._process_message(value),
                    callback=self._delivery_callback,
                )
            self.producer.poll(0)
        except KafkaException as exception:
            logger.error(f"Kafka Execption Raised: {exception}")
            if topic != self.ignore_delivery_failures:
                self.errors.append({"code": "ERR-016-999-0002", "message": "Unexpected error while publishing message"})

    def _delivery_callback(self, err, msg):
        """
        Handles delivery reports from the Kafka broker.

        Args:
            err (KafkaError): An object containing any errors that occurred while delivering the message.
            msg (Message): An object representing the delivered message.
        """
        if err is not None:
            logger.error(
                f"Failed to deliver message with topic {msg.topic()}, key {msg.key()}, value {msg.value()}: {err}"
            )
            if msg.topic() != self.ignore_delivery_failures:
                self.errors.append({"code": "ERR-016-999-0003", "message": "Failed to publish the message"})
        else:
            logger.debug(
                f"Message {msg.value()} delivered to topic {msg.topic()} "
                f"partition [{msg.partition()}] at offset {msg.offset()}"
            )

    def flush_and_close(self, timeout=None):
        """
        Checks if all the queued, in-flight or outstanding messages are delivered
        and releases resources used by producer instance.
        Ensures delivery failure is logged if any produced message is not acknowledged.

        Args:
            timeout (int): Maximum amount of time (seconds) to wait for all messages to be delivered.
        """
        # Can block the program flow if no timeout period is given
        undelivered_messages = self.producer.flush(timeout) if timeout else self.producer.flush()
        if undelivered_messages > 0:
            logger.error(f"Producer terminating with {undelivered_messages} messages still in queue or transit")

        self.producer = None
        logger.debug("Closing Producer instance")

    def _process_message(self, obj):
        """
        Serializes an object as a JSON string or converts it to a string representation.
        """
        if isinstance(obj, dict):
            return json.dumps(obj)
        return obj if obj is None else str(obj)

    def _connectivity_check(self, connectivity_check_timeout):
        """
        Tests Kafka Producer connectivity by requesting metadata from the cluster.
        """
        try:
            self.producer.list_topics(timeout=float(connectivity_check_timeout))
            logger.info("Successfully connected to Kafka cluster")
        except KafkaException as exception:
            logger.error(f"Failed to connect to Kafka server with timeout {connectivity_check_timeout}. {exception}")
            self.errors.append(
                {
                    "code": "ERR-016-999-0001",
                    "message": f"Failed to connect to Kafka server with timeout {connectivity_check_timeout}.",
                }
            )
