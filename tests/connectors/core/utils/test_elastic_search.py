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

# from elasticsearch.exceptions import ConnectionError
from unittest.mock import Mock, patch

# Third Party Library
from elasticsearch import exceptions

# DNE Library
from connectors.core.utils.elastic_search import ElasticsearchClient


@patch("connectors.core.utils.elastic_search.Elasticsearch")
def test_connect_success(es_mock):
    """
    Test connect returns True upon successful connection
    """
    es_mock().ping.return_value = True
    elasticsearch = ElasticsearchClient()
    assert elasticsearch.connect()


@patch("connectors.core.utils.elastic_search.Elasticsearch")
def test_connect_failure(es_mock):
    """
    Test connect returns False upon unsuccessful connection
    """
    es_mock().ping.return_value = False
    elasticsearch = ElasticsearchClient()
    assert not elasticsearch.connect()


@patch("connectors.core.utils.elastic_search.Elasticsearch")
def test_connect_exception(es_mock, caplog):
    """
    Test connect returns False upon unsuccessful connection and logs error
    """
    es_mock().ping.side_effect = exceptions.ConnectionError
    elasticsearch = ElasticsearchClient()
    assert not elasticsearch.connect()
    assert "ConnectionError while pinging Elasticsearch" in caplog.text


def test_create_index_positive():
    """
    Test create_index calls indices.create when index does not exist and returns True
    """
    elasticsearch = ElasticsearchClient()
    elasticsearch.es = Mock()
    elasticsearch.es.indices.exists.return_value = False
    assert elasticsearch.create_index("dummy_index")
    elasticsearch.es.indices.create.assert_called_once_with(index="dummy_index")


def test_create_index_negative():
    """
    Test create_index does not call indices.create when index exists and returns True
    """
    elasticsearch = ElasticsearchClient()
    elasticsearch.es = Mock()
    elasticsearch.es.indices.exists.return_value = True
    assert elasticsearch.create_index("dummy_index")
    elasticsearch.es.indices.create.assert_not_called()


def test_create_index_error(caplog):
    """
    Test create_index logs request errors and returns False
    """
    elasticsearch = ElasticsearchClient()
    elasticsearch.es = Mock()
    elasticsearch.es.indices.exists.side_effect = exceptions.RequestError
    assert not elasticsearch.create_index("dummy_index")
    assert "RequestError while creating Elasticsearch index" in caplog.text


def test_create_index_exception(caplog):
    """
    Test create_index logs exceptions and returns False
    """
    elasticsearch = ElasticsearchClient()
    elasticsearch.es = Mock()
    elasticsearch.es.indices.exists.side_effect = exceptions.ElasticsearchException
    assert not elasticsearch.create_index("dummy_index")
    assert "ElasticsearchException while creating Elasticsearch index" in caplog.text


@patch("connectors.core.utils.elastic_search.ElasticsearchClient._process_document")
def test_index_document_positive(process_mock, caplog):
    """
    Test index_document logs success message and returns True
    """
    caplog.set_level(logging.DEBUG)
    process_mock.return_value = "dummy_proccessed_document"
    elasticsearch = ElasticsearchClient()
    elasticsearch.es = Mock()
    elasticsearch.es.index.return_value = {"result": "created"}
    assert elasticsearch.index_document("dummy_index", "dummy_document")
    assert "dummy_proccessed_document indexed successfully. Index: dummy_index" in caplog.text


@patch("connectors.core.utils.elastic_search.ElasticsearchClient._process_document")
def test_index_document_negative(process_mock, caplog):
    """
    Test index_document logs failure message and returns False
    """
    process_mock.return_value = "dummy_proccessed_document"
    elasticsearch = ElasticsearchClient()
    elasticsearch.es = Mock()
    elasticsearch.es.index.return_value = {"result": "dummy"}
    assert not elasticsearch.index_document("dummy_index", "dummy_document")
    assert "Failed to index document: {'result': 'dummy'} Index: dummy_index" in caplog.text


@patch("connectors.core.utils.elastic_search.ElasticsearchClient._process_document")
def test_index_document_error(process_mock, caplog):
    """
    Test index_document logs request error and returns False
    """
    process_mock.return_value = "dummy_proccessed_document"
    elasticsearch = ElasticsearchClient()
    elasticsearch.es = Mock()
    elasticsearch.es.index.side_effect = exceptions.RequestError
    assert not elasticsearch.index_document("dummy_index", "dummy_document")
    assert (
        "RequestError while indexing document. Index: dummy_index, document: dummy_proccessed_document" in caplog.text
    )


@patch("connectors.core.utils.elastic_search.ElasticsearchClient._process_document")
def test_index_document_exception(process_mock, caplog):
    """
    Test index_document logs exception and returns False
    """
    process_mock.return_value = "dummy_proccessed_document"
    elasticsearch = ElasticsearchClient()
    elasticsearch.es = Mock()
    elasticsearch.es.index.side_effect = exceptions.ElasticsearchException
    assert not elasticsearch.index_document("dummy_index", "dummy_document")
    assert (
        "ElasticsearchException while indexing document. Index: dummy_index, document: dummy_proccessed_document"
        in caplog.text
    )


def test_process_document_with_dict():
    """
    Test _process_document returns given dictionary as it is
    """
    elasticsearch = ElasticsearchClient()
    document = {"key": "value"}
    result = elasticsearch._process_document(document)
    assert result == document


def test_process_document_with_non_dict():
    """
    Test _process_document still returns a dict when the given document is not a dict
    """
    elasticsearch = ElasticsearchClient()
    document = "Some text"
    expected_result = {"content": document}
    result = elasticsearch._process_document(document)
    assert result == expected_result


def test_close_positive(caplog):
    """
    Test close sets es to None
    """
    caplog.set_level(logging.INFO)
    elasticsearch = ElasticsearchClient()
    elasticsearch.es = Mock()
    elasticsearch.close()
    assert elasticsearch.es is None
    assert "Closing Elasticsearch client" in caplog.text


def test_close_negative(caplog):
    """
    Test close does not call transport.close() when es is None
    """
    caplog.set_level(logging.INFO)
    elasticsearch = ElasticsearchClient()
    elasticsearch.es = None
    elasticsearch.close()
    assert "Closing Elasticsearch client" not in caplog.text
