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
from typing import Type

# Third Party Library
from confluent_kafka import Message

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.utils.elastic_search import ElasticsearchClient
from connectors.core.utils.helpers import retry_wrapper
from connectors.core.utils.kafka import KafkaConsumer
from connectors.core.utils.sqldb.model import SkybridgeCommands, SkybridgeTransactions
from connectors.core.utils.sqldb.sqlDB import PostgreSQLDB

logger = logging.getLogger(__name__)

retry_attempts = config.get(section="auditnow", key="retry_attempts") or 5
retry_backoff = config.get(section="auditnow", key="retry_backoff") or 3
group_id = config.get(section="auditnow", key="consumer_group_id")


class AuditNowThread(threading.Thread):

    _instance = None
    _lock = threading.Lock()

    def __new__(cls: Type["AuditNowThread"], *_) -> "AuditNowThread":
        """
        Ensures a thread safe singleton instance of the class.
        """
        with cls._lock:
            if not cls._instance:
                logger.debug("No AuditNowThread instance found. Creating a new instance.")
                cls._instance = super().__new__(cls)

            else:
                logger.debug("Reusing existing AuditNowThread instance.")
            return cls._instance

    def __init__(self, topic: str, stop_event: threading.Event) -> None:
        """
        Initializes the AuditNowThread with instances of KafkaConsumer, Elasticsearch and PostgreSQL clients.
        Tracks the stop condition using the shared stop_event attribute.
        """
        if getattr(self, "_initialized", False):
            # Skip __init__ if already initialized
            return
        logger.info(f"Creating AuditNow thread for {topic}")
        threading.Thread.__init__(self, daemon=True)
        self.stop_event = stop_event
        self.topic = topic
        self.kafka_consumer = KafkaConsumer(topic=[self.topic], group_id=group_id, stop_event=self.stop_event)
        self.es_client = ElasticsearchClient()
        self.postgres_instance = PostgreSQLDB()
        self._initialized = True  # Flag to prevent reinitialization

    @classmethod
    def clear(cls: Type["AuditNowThread"]) -> None:
        """
        Clears the instance of this class
        """
        cls._instance = None

    def run(self) -> None:
        """
        This method overrides the run method of threading.Thread.
        It listens to Kafka and stores messages in Elasticsearch and PostgreSQL.

        The thread continues running until the stop event is set.
        """
        try:
            self.check_connections()

            for processed_message, msg in self.kafka_consumer.start():

                if logged := self._audit_logged(processed_message, msg):
                    self.kafka_consumer.consumer.commit(msg)
                    # Here to avoid re-running this when message is not committed
                    self._update_command_palette(processed_message)
                else:
                    logger.error(
                        f"The message with topic {msg.topic()} at offset {msg.offset()} in partition {msg.partition()} "
                        "will be lost once a new message is successfully logged."
                    )
                logger.debug(f"Message logging status {logged}")
        except Exception as err:
            logger.exception(f"Exception occurred in AuditThread: {str(err)}")
        finally:
            self.stop()

    def _elasticsearch_index(self, processed_message: dict, msg: Message) -> bool:
        """
        Indexes the processed_message in Elasticsearch. Returns True if succeeds else False.
        """
        if not self.es_client.index_document(index_name=self.topic, document=processed_message):
            logger.error(
                f"Failed to index message with topic {msg.topic()} at offset {msg.offset()} "
                f"in partition {msg.partition()} to Elasticsearch. Index: {self.topic}"
            )
            return False
        return True

    def _postgres_insert(self, processed_message, msg):
        """
        Inserts the processed_message into PostgreSQL. Returns True if succeeds else False.
        """
        with self.postgres_instance.transactional_session() as session:
            try:
                results = session.execute(
                    self.postgres_instance.get_insert_json_query(SkybridgeTransactions, json_data=processed_message)
                )
                logger.debug(
                    f"Record {processed_message} successfully inserted "
                    f"to skybridge_transanctions table with id {results.inserted_primary_key}."
                )
            except Exception as err:
                logger.error(
                    f"Failed to insert message with topic {msg.topic()} at offset {msg.offset()} "
                    f"in partition {msg.partition()} to skybridge_transanctions table in PostgreSQL database. {err}"
                )
                return False
            return True

    @retry_wrapper(retry_attempts=int(retry_attempts), retry_backoff=int(retry_backoff))
    def _audit_logged(self, processed_message, msg):
        """
        Calls the methods to write to Elasticsearch and PostgreSQL. Returns False if both fail else True.
        The retry wrapper will retry this method if it returns false.
        """
        logged_in_elasticsearch = self._elasticsearch_index(processed_message, msg)
        logged_in_postgres = self._postgres_insert(processed_message, msg)
        logged = logged_in_elasticsearch or logged_in_postgres
        if not logged:
            logger.error(
                "Failed to log the message with "
                f"topic {msg.topic()} at offset {msg.offset()} in partition {msg.partition()} "
                f"in any of the servers. Retrying for {retry_attempts} times"
            )
        return logged

    def check_connections(self):
        """
        Checks Kafka, Elasticsearch and Postgres servers' connections.
        Only for logging purposes.
        """
        self.kafka_consumer.connectivity_check()
        self.es_client.connect()
        self.postgres_instance.is_server_responsive()

    def stop(self) -> None:
        """
        Stops and closes connections for ElasticSearch client and KafkaConsumer
        """
        self.es_client.close()
        self.kafka_consumer.stop()
        self.postgres_instance.dispose_engine()
        AuditNowThread.clear()

    def _update_command_palette(self, processed_message):
        """
        Updates Skybridge command palette using a subset of each log
        """
        record = {
            k: processed_message.get(k)
            for k in (
                "username",
                "device_vendor",
                "device_os_type",
                "device_os_version",
                "device_model",
                "target_router",
                "command",
                "output",
            )
        }
        record["command"] = record["command"].strip()
        with self.postgres_instance.transactional_session() as session:
            try:
                # not matching record["output"]
                q = session.query(SkybridgeCommands).filter(
                    SkybridgeCommands.username == record["username"],
                    SkybridgeCommands.device_vendor == record["device_vendor"],
                    SkybridgeCommands.device_os_type == record["device_os_type"],
                    SkybridgeCommands.device_os_version == record["device_os_version"],
                    SkybridgeCommands.device_model == record["device_model"],
                    SkybridgeCommands.target_router == record["target_router"],
                    SkybridgeCommands.command == record["command"],
                )
                if session.query(q.exists()).scalar():
                    # updating output to reflect any new blocked commands
                    q.update({"count": SkybridgeCommands.count + 1, "output": record["output"]})
                    logger.debug(f"Record {record} successfully updated in skybridge_commands table")
                else:
                    record["count"] = 1
                    results = session.execute(
                        self.postgres_instance.get_insert_json_query(SkybridgeCommands, json_data=record)
                    )
                    logger.debug(
                        f"Record {record} successfully inserted "
                        f"to skybridge_commands table with id {results.inserted_primary_key}."
                    )
            except Exception as err:
                logger.error(f"Failed to insert/update record {record} in skybridge_commands table. {err}")
