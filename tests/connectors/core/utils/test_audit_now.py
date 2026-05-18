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
from unittest.mock import Mock, patch

# Third Party Library
import pytest

# DNE Library
from connectors.core.utils.audit_now import AuditNowThread


@patch("connectors.core.utils.audit_now.PostgreSQLDB")
@patch("connectors.core.utils.audit_now.ElasticsearchClient")
@patch("connectors.core.utils.audit_now.KafkaConsumer")
def test_init(kafka_mock, es_mock, postgres_mock):
    """
    Test AuditNowThread is initialized with instances of
    KafkaConsumer and ElasticsearchClient and PostgreSQLDB.
    """
    audit_now_thread = AuditNowThread("dummy", Mock())
    AuditNowThread.clear()

    kafka_mock.assert_called_once()
    es_mock.assert_called_once()
    postgres_mock.assert_called_once()

    assert audit_now_thread.kafka_consumer == kafka_mock()
    assert audit_now_thread.es_client == es_mock()
    assert audit_now_thread.postgres_instance == postgres_mock()
    assert audit_now_thread._instance is None


@patch("connectors.core.utils.audit_now.PostgreSQLDB")
@patch("connectors.core.utils.audit_now.ElasticsearchClient")
@patch("connectors.core.utils.audit_now.KafkaConsumer")
def test_run_positive(kafka_mock, es_mock, postgres_mock):
    """
    Test run method commits the offset of each consumed message from Kafka
    that is written to at least one of Elasticsearch and Postgres servers
    and makes intended callls
    """
    mock_message = Mock()
    kafka_mock().start.return_value = [("dummy_message", mock_message)]
    audit_now_thread = AuditNowThread("dummy_topic", Mock())
    audit_now_thread._update_command_palette = Mock()
    audit_now_thread.check_connections = Mock()
    audit_now_thread._audit_logged = Mock(return_value=True)
    audit_now_thread.run()
    audit_now_thread._update_command_palette.assert_called_once_with("dummy_message")
    audit_now_thread._audit_logged.assert_called_once_with("dummy_message", mock_message)
    audit_now_thread.check_connections.assert_called_once()
    audit_now_thread.kafka_consumer.consumer.commit.assert_called_once_with(mock_message)
    assert audit_now_thread._instance is None


@patch("connectors.core.utils.audit_now.PostgreSQLDB")
@patch("connectors.core.utils.audit_now.ElasticsearchClient")
@patch("connectors.core.utils.audit_now.KafkaConsumer")
def test_run_negative(kafka_mock, es_mock, postgres_mock, caplog):
    """
    Test run method does not commit the offset of each consumed message from Kafka
    that is not written to any of Elasticsearch or Postgres servers, logs error
    and makes intended calls

    """
    mock_message = Mock()
    kafka_mock().start.return_value = [("dummy_message", mock_message)]
    audit_now_thread = AuditNowThread("dummy_topic", Mock())
    audit_now_thread._audit_logged = Mock(return_value=False)
    audit_now_thread.check_connections = Mock()
    audit_now_thread.run()
    assert "will be lost once a new message is successfully logged" in caplog.text
    audit_now_thread._audit_logged.assert_called_once_with("dummy_message", mock_message)
    audit_now_thread.check_connections.assert_called_once()
    audit_now_thread.kafka_consumer.consumer.commit.assert_not_called()
    assert audit_now_thread._instance is None


@patch("connectors.core.utils.audit_now.PostgreSQLDB")
@patch("connectors.core.utils.audit_now.ElasticsearchClient")
@patch("connectors.core.utils.audit_now.KafkaConsumer")
def test_run_exception(kafka_mock, es_mock, postgres_mock, caplog):
    """
    Test run method does not commit the offset of each consumed message from Kafka
    that is not written to any of Elasticsearch or Postgres servers, logs error
    and makes intended callls

    """
    kafka_mock().start.side_effect = Exception("dummy")
    audit_now_thread = AuditNowThread("dummy_topic", Mock())
    audit_now_thread.check_connections = Mock()
    audit_now_thread.run()
    assert "Exception occurred in AuditThread" in caplog.text
    audit_now_thread.check_connections.assert_called_once()
    audit_now_thread.kafka_consumer.consumer.commit.assert_not_called()
    assert audit_now_thread._instance is None


@patch("connectors.core.utils.audit_now.PostgreSQLDB")
@patch("connectors.core.utils.audit_now.ElasticsearchClient")
@patch("connectors.core.utils.audit_now.KafkaConsumer")
def test_stop(kafka_mock, es_mock, postgres_mock):
    """
    Test stop method calls Elasticseach, Kafka and Postgres close methods.
    """
    audit_now_thread = AuditNowThread("dummy", Mock())
    audit_now_thread.stop()
    es_mock().close.assert_called_once()
    kafka_mock().stop.assert_called_once()
    postgres_mock().dispose_engine.assert_called_once()
    assert audit_now_thread._instance is None


@patch("connectors.core.utils.audit_now.PostgreSQLDB")
@patch("connectors.core.utils.audit_now.ElasticsearchClient")
@patch("connectors.core.utils.audit_now.KafkaConsumer")
def test_check_connections(kafka_mock, es_mock, postgres_mock):
    """
    Test check_connections method calls Elasticseach, Kafka and Postgres connectivity check methods.
    """
    audit_now_thread = AuditNowThread("dummy", Mock())
    audit_now_thread.check_connections()
    AuditNowThread.clear()
    es_mock().connect.assert_called_once()
    kafka_mock().connectivity_check.assert_called_once()
    postgres_mock().is_server_responsive.assert_called_once()
    assert audit_now_thread._instance is None


@pytest.mark.parametrize(
    "es_res, postgres_res, log_res",
    [(True, True, True), (True, False, True), (False, True, True), (False, False, False)],
)
@patch("connectors.core.utils.audit_now.PostgreSQLDB")
@patch("connectors.core.utils.audit_now.ElasticsearchClient")
@patch("connectors.core.utils.audit_now.KafkaConsumer")
def test_audit_logged(kafka_mock, es_mock, postgres_mock, es_res, postgres_res, log_res):
    """
    Test _audit_logged method returns True if at least one of es or postgres write methods returns True
    """
    mock_message = Mock()
    audit_now_thread = AuditNowThread("dummy", Mock())
    audit_now_thread._elasticsearch_index = Mock(return_value=es_res)
    audit_now_thread._postgres_insert = Mock(return_value=postgres_res)
    assert (
        audit_now_thread._audit_logged.__wrapped__(audit_now_thread, processed_message="dummy_msg", msg=mock_message)
        == log_res
    )
    audit_now_thread._elasticsearch_index.assert_called_once_with("dummy_msg", mock_message)
    audit_now_thread._postgres_insert.assert_called_once_with("dummy_msg", mock_message)
    AuditNowThread.clear()
    assert audit_now_thread._instance is None


@pytest.mark.parametrize("index_document_res, elasticsearch_index_res", [(True, True), (False, False)])
@patch("connectors.core.utils.audit_now.PostgreSQLDB")
@patch("connectors.core.utils.audit_now.ElasticsearchClient")
@patch("connectors.core.utils.audit_now.KafkaConsumer")
def test_elasticsearch_index(kafka_mock, es_mock, postgres_mock, index_document_res, elasticsearch_index_res):
    """
    Test _elasticsearch_index returns False and logs error when index_document() returns false
    And returns True otherwise
    """
    mock_message = Mock()
    audit_now_thread = AuditNowThread("dummy", Mock())
    audit_now_thread.es_client.index_document = Mock(return_value=index_document_res)
    assert audit_now_thread._elasticsearch_index("dummy_msg", mock_message) == elasticsearch_index_res
    AuditNowThread.clear()
    assert audit_now_thread._instance is None


@patch("connectors.core.utils.audit_now.PostgreSQLDB")
@patch("connectors.core.utils.audit_now.ElasticsearchClient")
@patch("connectors.core.utils.audit_now.KafkaConsumer")
def test_postgres_insert_positive(kafka_mock, es_mock, postgres_mock, caplog):
    """
    Test _postgres_insert returns True when message is successfully written to Postgres
    """
    mock_message = Mock()
    audit_now_thread = AuditNowThread("dummy", Mock())
    caplog.set_level(logging.DEBUG)
    assert audit_now_thread._postgres_insert("dummy_msg", mock_message)
    assert "successfully inserted" in caplog.text
    AuditNowThread.clear()
    assert audit_now_thread._instance is None


@patch("connectors.core.utils.audit_now.PostgreSQLDB")
@patch("connectors.core.utils.audit_now.ElasticsearchClient")
@patch("connectors.core.utils.audit_now.KafkaConsumer")
def test_postgres_insert_negative(kafka_mock, es_mock, postgres_mock, caplog):
    """
    Test _postgres_insert returns False and logs error when message is not successfully written to Postgres
    """
    mock_message = Mock()
    audit_now_thread = AuditNowThread("dummy", Mock())
    audit_now_thread.postgres_instance.get_insert_json_query.side_effect = Exception("dummy error")
    assert not audit_now_thread._postgres_insert("dummy_msg", mock_message)
    assert "Failed to insert message" in caplog.text
    AuditNowThread.clear()
    assert audit_now_thread._instance is None


@patch("connectors.core.utils.audit_now.PostgreSQLDB")
@patch("connectors.core.utils.audit_now.ElasticsearchClient")
@patch("connectors.core.utils.audit_now.KafkaConsumer")
def test_update_command_palette(kafka_mock, es_mock, postgres_mock, caplog):
    """
    Test _update_command_palette updates the skybridge_commands table
    if intended record exists
    """
    mock_message = Mock()
    audit_now_thread = AuditNowThread("dummy", Mock())
    caplog.set_level(logging.DEBUG)
    audit_now_thread._update_command_palette(mock_message)
    assert "successfully updated in skybridge_commands table" in caplog.text
    AuditNowThread.clear()
    assert audit_now_thread._instance is None


@patch("connectors.core.utils.audit_now.PostgreSQLDB")
@patch("connectors.core.utils.audit_now.ElasticsearchClient")
@patch("connectors.core.utils.audit_now.KafkaConsumer")
def test_update_command_palette_new_record(kafka_mock, es_mock, postgres_mock, caplog):
    """
    Test _update_command_palette inserts new record in the skybridge_commands table
    if intended record does not exists
    """
    mock_message = Mock()
    postgres_mock().transactional_session().__enter__().query().scalar.return_value = False
    audit_now_thread = AuditNowThread("dummy", Mock())
    caplog.set_level(logging.DEBUG)
    audit_now_thread._update_command_palette(mock_message)
    assert "successfully inserted " in caplog.text
    AuditNowThread.clear()
    assert audit_now_thread._instance is None


@patch("connectors.core.utils.audit_now.PostgreSQLDB")
@patch("connectors.core.utils.audit_now.ElasticsearchClient")
@patch("connectors.core.utils.audit_now.KafkaConsumer")
def test_update_command_palette_exception(kafka_mock, es_mock, postgres_mock, caplog):
    """
    Test _update_command_palette logs the execption if update/insert fails
    """
    mock_message = Mock()
    postgres_mock().transactional_session().__enter__().query.side_effect = Exception("dummy")
    audit_now_thread = AuditNowThread("dummy", Mock())
    audit_now_thread._update_command_palette(mock_message)
    assert "Failed to insert/update record " in caplog.text
    AuditNowThread.clear()
    assert audit_now_thread._instance is None


@patch("connectors.core.utils.audit_now.PostgreSQLDB")
@patch("connectors.core.utils.audit_now.ElasticsearchClient")
@patch("connectors.core.utils.audit_now.KafkaConsumer")
def test__new__(kafka_mock, es_mock, postgres_mock):
    """
    Test AuditNowThread__new__ lcreates a new instance
    """
    audit_now_thread = AuditNowThread("dummy", Mock())
    assert audit_now_thread._instance is not None
    AuditNowThread.clear()
    assert audit_now_thread._instance is None


@patch("connectors.core.utils.audit_now.PostgreSQLDB")
@patch("connectors.core.utils.audit_now.ElasticsearchClient")
@patch("connectors.core.utils.audit_now.KafkaConsumer")
def test__new__singleton(kafka_mock, es_mock, postgres_mock):
    """
    Test AuditNowThread reuses existing instance
    """
    instance1 = AuditNowThread("dummy", Mock())
    instance2 = AuditNowThread("dummy", Mock())
    assert instance1 is instance2
    AuditNowThread.clear()
    assert instance1._instance is None
    assert instance2._instance is None


@patch("connectors.core.utils.audit_now.PostgreSQLDB")
@patch("connectors.core.utils.audit_now.ElasticsearchClient")
@patch("connectors.core.utils.audit_now.KafkaConsumer")
def test__new__thread_safe(kafka_mock, es_mock, postgres_mock):
    """
    Test AuditNowThread is thread safe
    """
    with threading.Lock():
        instances = [AuditNowThread("dummy", Mock()) for _ in range(5)]
    # All instances should be the same, as the lock ensures only one instance is created
    assert all(instance is instances[0] for instance in instances)
    AuditNowThread.clear()
    assert instances[0]._instance is None
