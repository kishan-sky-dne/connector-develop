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
from unittest.mock import ANY, Mock, patch

# Third Party Library
import pytest
from confluent_kafka import KafkaError, KafkaException

# DNE Library
from connectors.core.utils.kafka import KafkaConsumer, KafkaProducer


@patch("connectors.core.utils.kafka.json")
@patch("connectors.core.utils.kafka.Consumer")
def test_init(consumer_mock, json_mock):
    """
    Test stop event is assigned and topic is subscribed in init.
    """
    json_mock.loads.return_value = "dummy_config"
    kafka_consumer = KafkaConsumer("dummy_topic", "dummy_gp_id", "dummy_event")
    assert kafka_consumer.stop_event == "dummy_event"
    kafka_consumer.consumer.subscribe.called_once_with("dummy_topic")


@patch("connectors.core.utils.kafka.KafkaConsumer.consume")
@patch("connectors.core.utils.kafka.json")
@patch("connectors.core.utils.kafka.Consumer")
def test_start(consumer_mock, json_mock, consume_mock):
    """
    Test Consumer is instantiated with and subscribed to given config and topic
    """
    event = Mock()
    event.is_set.return_value = True
    kafka_consumer = KafkaConsumer("dummy_topic", "dummy_gp_id", event)
    list(kafka_consumer.start())
    consume_mock.assert_not_called()


@patch("connectors.core.utils.kafka.json")
@patch("connectors.core.utils.kafka.Consumer")
def test_consume_calls(consumer_mock, json_mock, caplog):
    """
    Test consume method makes the intended calls and logs general errors
    """
    kafka_consumer = KafkaConsumer("dummy_topic", "dummy_gp_id", "dummy_event")
    kafka_consumer.consume()
    kafka_consumer.consumer.subscribe.assert_called_once_with("dummy_topic")
    kafka_consumer.consumer.poll.assert_called_once()
    assert "Error while consuming messages" in caplog.text


@patch("connectors.core.utils.kafka.json")
@patch("connectors.core.utils.kafka.Consumer")
def test_consume_none_message(consumer_mock, json_mock):
    """
    Test consume method returns False when consumed message is None
    """
    consumer_mock().poll.return_value = None
    kafka_consumer = KafkaConsumer("dummy_topic", "dummy_gp_id", "dummy_event")
    assert kafka_consumer.consume() == ({}, None)


@patch("connectors.core.utils.kafka.json")
@patch("connectors.core.utils.kafka.Consumer")
def test_consume_error_codes(consumer_mock, json_mock, caplog):
    """
    Test consume method logs errors and returns False
    when errors are raised during message consumption
    """
    event = Mock()
    kafka_consumer = KafkaConsumer("dummy_topic", "dummy_gp_id", event)
    consumer_mock().poll().error().code.return_value = KafkaError._PARTITION_EOF
    assert kafka_consumer.consume() == ({}, ANY)
    assert "Reached end at offset" in caplog.text

    consumer_mock().poll().error().code.return_value = KafkaError.UNKNOWN_TOPIC_OR_PART
    assert kafka_consumer.consume() == ({}, ANY)
    assert "Topic does not exist" in caplog.text


@patch("connectors.core.utils.kafka.KafkaConsumer._process_message")
@patch("connectors.core.utils.kafka.json")
@patch("connectors.core.utils.kafka.Consumer")
def test_consume_message_return(consumer_mock, json_mock, processor_mock):
    """
    Test consume method returns False when consumed message is None
    """
    consumer_mock().poll().error.return_value = False
    processor_mock.return_value = "dummy response"
    kafka_consumer = KafkaConsumer("dummy_topic", "dummy_gp_id", "dummy_event")
    assert kafka_consumer.consume() == ("dummy response", ANY)


@patch("connectors.core.utils.kafka.KafkaConsumer._process_message")
@patch("connectors.core.utils.kafka.json")
@patch("connectors.core.utils.kafka.Consumer")
def test_consume_irregular_message(consumer_mock, json_mock, processor_mock):
    """
    Test erros or events other than a regular message are not processed
    """
    consumer_mock().poll().error.return_value = False
    consumer_mock().poll().value.return_value = None
    kafka_consumer = KafkaConsumer("dummy_topic", "dummy_gp_id", "dummy_event")
    kafka_consumer.consume()
    processor_mock.assert_not_called()


@patch("connectors.core.utils.kafka.json")
@patch("connectors.core.utils.kafka.Consumer")
def test_consume_exception(consumer_mock, json_mock, caplog):
    """
    Test consume method logs Kafka Exceptions and raises them
    """
    consumer_mock().poll.side_effect = KafkaException
    kafka_consumer = KafkaConsumer("dummy_topic", "dummy_gp_id", "dummy_event")
    with pytest.raises(KafkaException):
        kafka_consumer.consume()
        assert "Kafka Execption Raised" in caplog.text


@patch("connectors.core.utils.kafka.Consumer")
def test_process_message_json(consumer_mock):
    """
    Test process json messages
    """
    message = Mock()
    message.value.return_value = '{"key":"value"}'
    kafka_consumer = KafkaConsumer("dummy_topic", "dummy_gp_id", Mock())
    result = kafka_consumer._process_message(message)
    assert result == {"key": "value"}


@patch("connectors.core.utils.kafka.Consumer")
def test_process_message_string(consumer_mock):
    """
    Test process string messages
    """
    message = Mock()
    message.value.return_value = b"string"
    kafka_consumer = KafkaConsumer("dummy_topic", "dummy_gp_id", Mock())
    result = kafka_consumer._process_message(message)
    assert result == "string"


@patch("connectors.core.utils.kafka.json")
@patch("connectors.core.utils.kafka.Consumer")
def test_stop_negative(consumer_mock, json_mock):
    """
    Test consumer close method is not called when consumer is None
    """
    json_mock.loads.return_value = "dummy_config"
    kafka_consumer = KafkaConsumer("dummy_topic", "dummy_gp_id", Mock())
    kafka_consumer.consumer = None
    kafka_consumer.stop()
    consumer_mock.close.assert_not_called()


@patch("connectors.core.utils.kafka.json")
@patch("connectors.core.utils.kafka.Consumer")
def test_stop_positive(consumer_mock, json_mock):
    """
    Test consumer close method is called when consumer is not None
    """
    json_mock.loads.return_value = "dummy_config"
    kafka_consumer = KafkaConsumer("dummy_topic", "dummy_gp_id", Mock())
    kafka_consumer.consumer = Mock()
    kafka_consumer.stop()
    kafka_consumer.consumer.close.assert_called_once()


@patch("connectors.core.utils.kafka.Consumer")
def test_connectivity_check_succuess(consumer_mock, caplog):
    """
    Test _connectivity_check logs success message when list_topics returns a response
    """
    kafka_consumer = KafkaConsumer("dummy_topic", "dummy_gp_id", Mock())
    kafka_consumer.consumer = Mock()

    kafka_consumer.consumer.list_topics.return_value = "dummy"
    with caplog.at_level(logging.INFO):
        kafka_consumer.connectivity_check()
        assert "Successfully connected to Kafka cluster" in caplog.text


@patch("connectors.core.utils.kafka.Consumer")
def test_connectivity_check_failure(consumer_mock, caplog):
    """
    Test _connectivity_check logs failure message when list_topics raises exception
    """
    kafka_consumer = KafkaConsumer("dummy_topic", "dummy_gp_id", Mock())
    kafka_consumer.consumer = Mock()

    kafka_consumer.consumer.list_topics.side_effect = KafkaException
    with caplog.at_level(logging.ERROR):
        kafka_consumer.connectivity_check()
        assert "Failed to connect to Kafka cluster" in caplog.text


@patch.object(KafkaProducer, "_connectivity_check")
@patch("connectors.core.utils.kafka.Producer")
def test_producer_init(producer_mock, cc_mock):
    """
    Check the Producer constructor sets the producer with the intended object.
    """
    producer_mock.return_value = "dummy"
    kafka_producer = KafkaProducer()
    assert kafka_producer.producer == "dummy"


@patch.object(KafkaProducer, "_connectivity_check")
@patch.object(KafkaProducer, "_process_message", return_value=b'{"key": "value"}')
@patch.object(KafkaProducer, "__init__", return_value=None)
def test_send(init_mock, serilize_mock, cc_mock):
    """
    Check the Producer produce and poll methods were called with the expected arguments.
    """
    kafka_producer = KafkaProducer()
    kafka_producer.producer = Mock()

    key = {"key": "value"}
    value = {"key": "value"}

    kafka_producer.send(key, value)
    init_mock.assert_called_once()

    kafka_producer.producer.produce.assert_called_once_with(
        topic=ANY, key=b'{"key": "value"}', value=b'{"key": "value"}', callback=ANY
    )

    kafka_producer.producer.poll.assert_called_once_with(0)


@patch.object(KafkaProducer, "_connectivity_check")
@patch.object(KafkaProducer, "_process_message", return_value=b'{"key": "value"}')
@patch.object(KafkaProducer, "__init__", return_value=None)
def test_send_with_partition(init_mock, serilize_mock, cc_mock):
    """
    Check the Producer produce and poll methods were called with the expected arguments.
    """
    kafka_producer = KafkaProducer()
    kafka_producer.producer = Mock()

    key = {"key": "value"}
    value = {"key": "value"}

    kafka_producer.send(key, value, partition=1)
    init_mock.assert_called_once()

    kafka_producer.producer.produce.assert_called_once_with(
        topic=ANY, key=b'{"key": "value"}', value=b'{"key": "value"}', partition=1, callback=ANY
    )

    kafka_producer.producer.poll.assert_called_once_with(0)


@patch.object(KafkaProducer, "_process_message", return_value=b'{"key": "value"}')
@patch("connectors.core.utils.kafka.Producer", autospec=True)
def test_send_exception(producer_mock, serilize_mock, caplog):
    """
    Check Kafka exception is captured and logged and error added
    """
    kafka_producer = KafkaProducer()
    kafka_producer.producer.produce = Mock(side_effect=KafkaException)

    value = {"key": "value"}
    kafka_producer.send("dummy_topic", value)
    assert "Kafka Execption Raised" in caplog.text
    assert kafka_producer.errors == [
        {"code": "ERR-016-999-0002", "message": "Unexpected error while publishing message"}
    ]


@patch.object(KafkaProducer, "_process_message", return_value=b'{"key": "value"}')
@patch("connectors.core.utils.kafka.Producer", autospec=True)
def test_send_exception_ignore_topic_failure(producer_mock, serilize_mock, caplog):
    """
    Check Kafka exception is captured and logged but no error added
    """
    kafka_producer = KafkaProducer(ignore_delivery_failures="dummy_topic")
    kafka_producer.producer.produce = Mock(side_effect=KafkaException)

    value = {"key": "value"}
    kafka_producer.send("dummy_topic", value)
    assert "Kafka Execption Raised" in caplog.text
    assert kafka_producer.errors == []


@patch("connectors.core.utils.kafka.Producer", autospec=True)
def test_delivery_callback(producer_mock, caplog):
    """
    Check the _delivery_callback method logs intended messages
    """
    kafka_producer = KafkaProducer()
    message = Mock()

    kafka_producer._delivery_callback(err="dummy", msg=message)
    assert "Failed to deliver message" in caplog.text
    assert kafka_producer.errors == [{"code": "ERR-016-999-0003", "message": "Failed to publish the message"}]

    with caplog.at_level(logging.DEBUG):
        kafka_producer._delivery_callback(err=None, msg=message)
        assert "delivered to " in caplog.text


@patch("connectors.core.utils.kafka.Producer", autospec=True)
def test_delivery_callback_failure_ignore(producer_mock, caplog):
    """
    Check the _delivery_callback method logs intended messages
    But doesn't add it to errors when topic is ignored
    """
    kafka_producer = KafkaProducer(ignore_delivery_failures="dummy_topic")
    message = Mock()
    message.topic.return_value = "dummy_topic"

    kafka_producer._delivery_callback(err="dummy", msg=message)
    assert "Failed to deliver message" in caplog.text
    assert kafka_producer.errors == []


@patch("connectors.core.utils.kafka.Producer", autospec=True)
def test_flush_and_close_success(producer_mock, caplog):
    """
    Check the producer flush_and_close method sets producer to None and does not log any errors
    """
    kafka_producer = KafkaProducer()
    kafka_producer.producer.flush.return_value = 0
    kafka_producer.flush_and_close(0)
    with caplog.at_level(logging.ERROR):
        assert "Producer terminating with 1 messages still in queue or transit" not in caplog.text
    assert kafka_producer.producer is None


@patch("connectors.core.utils.kafka.Producer", autospec=True)
def test_flush_and_close_failure(producer_mock, caplog):
    """
    Check the producer flush_and_close method sets producer to None and logs errors
    """
    kafka_producer = KafkaProducer()
    kafka_producer.producer.flush.return_value = 1
    kafka_producer.flush_and_close(0)
    with caplog.at_level(logging.ERROR):
        assert "Producer terminating with 1 messages still in queue or transit" in caplog.text
    assert kafka_producer.producer is None


@patch.object(KafkaProducer, "_connectivity_check")
@patch.object(KafkaProducer, "__init__", return_value=None)
def test_producer_process_message(init_mock, cc_mock):
    """
    Test _process_message returns string or JSON string
    """
    producer = KafkaProducer()
    assert producer._process_message(1) == "1"
    assert producer._process_message("dummystring") == "dummystring"
    assert producer._process_message({"key": "value"}) == '{"key": "value"}'


@patch.object(KafkaProducer, "__init__", return_value=None)
def test_producer_connectivity_check_success(producer_mock, caplog):
    """
    Test _connectivity_check logs success message when list_topics returns a response
    """
    kafka_producer = KafkaProducer()
    kafka_producer.producer = Mock()

    kafka_producer.producer.list_topics.return_value = "dummy"
    with caplog.at_level(logging.INFO):
        kafka_producer._connectivity_check(1)
        assert "Successfully connected to Kafka cluster" in caplog.text


@patch.object(KafkaProducer, "__init__", return_value=None)
def test_producer_connectivity_check_failure(producer_mock, caplog):
    """
    Test _connectivity_check logs failure message when list_topics raises exception
    """
    kafka_producer = KafkaProducer()
    kafka_producer.producer = Mock()
    kafka_producer.errors = []

    kafka_producer.producer.list_topics.side_effect = KafkaException
    with caplog.at_level(logging.ERROR):
        kafka_producer._connectivity_check(1)
        assert "Failed to connect to Kafka server with timeout" in caplog.text
    assert kafka_producer.errors == [
        {"code": "ERR-016-999-0001", "message": "Failed to connect to Kafka server with timeout 1."}
    ]
