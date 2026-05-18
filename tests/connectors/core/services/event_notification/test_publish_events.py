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
from unittest.mock import ANY, Mock, patch

# Third Party Library
import pytest

# DNE Library
from connectors.core.services.event_notification.publish_events import OrderStatus
from connectors.core.utils.exceptions import ConnectorException

example_payload = {
    "body": {
        "keyId": "BPM-12345",
        "message": {
            "orderNumber": 12345,
            "orderType": "map-t",
            "orderCreatedDate": "2022-07-25 12:04:59",
            "status": "SucceSs",
        },
        "eventTime": "2022-07-25 04:14:52",
        "eventSource": "DNE-BPM",
    }
}


@patch("connectors.core.services.event_notification.publish_events.create_dict_from_string")
@patch("connectors.core.services.event_notification.publish_events.KafkaProducer")
def test_init_exception(producer_mock, create_dict_mock):
    """
    Test exception is raised if topic cannot be mapped using the topic_mapper in config
    """
    create_dict_mock.return_value = {"standard": "dne_order_status"}
    with pytest.raises(ConnectorException):
        OrderStatus(**example_payload)


@patch("connectors.core.services.event_notification.publish_events.create_dict_from_string")
@patch("connectors.core.services.event_notification.publish_events.KafkaProducer")
def test_publush_connectivity_failure(producer_mock, create_dict_mock):
    """
    Test publush returns failure responses when Kafka connection fails
    """
    producer_mock().errors = ["dummy error"]
    order_status = OrderStatus(**example_payload)
    assert order_status.publish() == ({"errorCategory": "FAILED", "errors": ["dummy error"], "status": "FAILURE"}, 500)
    order_status.kafka_producer._connectivity_check.assert_called_once()


@patch("connectors.core.services.event_notification.publish_events.create_dict_from_string")
@patch("connectors.core.services.event_notification.publish_events.KafkaProducer")
def test_publush_produce_failure(producer_mock, create_dict_mock):
    """
    Test publush returns failure response when Kafka error occurs during producing
    """
    producer_mock().errors = []
    order_status = OrderStatus(**example_payload)

    def side_effect():
        producer_mock().errors = ["dummy"]

    order_status._produce_to_kafka = Mock(side_effect=side_effect)
    order_status._prepare_kafka_message = Mock()

    assert order_status.publish() == ({"errorCategory": "FAILED", "errors": ["dummy"], "status": "FAILURE"}, 500)
    order_status.kafka_producer._connectivity_check.assert_called_once()
    order_status._produce_to_kafka.assert_called_once()
    order_status._prepare_kafka_message.assert_called_once()


@patch("connectors.core.services.event_notification.publish_events.create_dict_from_string")
@patch("connectors.core.services.event_notification.publish_events.KafkaProducer")
def test_publush_success(producer_mock, create_dict_mock):
    """
    Test publush returns success as expected
    """
    producer_mock().errors = []
    order_status = OrderStatus(**example_payload)
    assert order_status.publish() == ({"status": "SUCCESS"}, 200)
    order_status.kafka_producer._connectivity_check.assert_called_once()


@patch("connectors.core.services.event_notification.publish_events.create_dict_from_string")
@patch("connectors.core.services.event_notification.publish_events.KafkaProducer")
def test_produce_to_kafka(producer_mock, create_dict_mock):
    """
    Test produce_to_kafka calls the producer's send method twice and flush once
    """
    create_dict_mock.return_value = {"standard": "dne_order_status", "map-t": "dne_mapT_order_status"}
    order_status = OrderStatus(**example_payload)
    order_status._produce_to_kafka()
    assert order_status.kafka_producer.send.call_count == 2
    # using default config value
    order_status.kafka_producer.flush_and_close.assert_called_once_with(6)


@patch("connectors.core.services.event_notification.publish_events.datetime")
@patch("connectors.core.services.event_notification.publish_events.create_dict_from_string")
@patch("connectors.core.services.event_notification.publish_events.KafkaProducer")
def test_prepare_kafka_message(producer_mock, create_dict_mock, datetime_mock):
    """
    Test _prepare_kafka_message adds metadata and other required information to the message
    """
    datetime_mock.datetime.now.return_value = "dummy time"
    order_status = OrderStatus(**example_payload)
    order_status._prepare_kafka_message()
    assert order_status.message == {
        "eventSource": "DNE-BPM",
        "eventTime": "2022-07-25 04:14:52",
        "metadata": {"eventTime": "dummy time", "url": ANY},
        "orderCreatedDate": "2022-07-25 12:04:59",
        "orderEndDate": None,
        "orderNumber": 12345,
        "orderType": "map-t",
        "serviceStatusDetails": None,
        "status": "Success",
    }
