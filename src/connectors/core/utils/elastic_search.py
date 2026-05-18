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

# Third Party Library
from elasticsearch import Elasticsearch, exceptions

# DNE Library
from connectors.core.config.connectors_config import config

logger = logging.getLogger(__name__)

nodes = config.get(section="elasticsearch", key="nodes").split(",")
username = config.get(section="elasticsearch", key="username")
password = config.get(section="elasticsearch", key="password")


class ElasticsearchClient:
    def __init__(self):
        """
        Initialize ElasticsearchClient.
        """
        logger.info(f"Initializing Elasticsearch client. Nodes {nodes}")
        self.es = None
        self.es = Elasticsearch(
            nodes,
            # TODO secure connection
            # ca_certs="docker/connectors/sky_internal_cas.crt",
            http_auth=(username, password),
            ca_certs="/etc/ssl/certs/ca-certificates.crt",
        )

    def connect(self):
        """
        Connect to Elasticsearch with nodes given in config and log errors.
        """
        try:
            if self.es.ping():
                logger.info("Connected to Elasticsearch.")
                return True
            logger.error("Failed to connect to Elasticsearch.")
        except exceptions.ConnectionError:
            logger.error("ConnectionError while pinging Elasticsearch")
        return False

    def create_index(self, index_name):
        """
        Create an index in Elasticsearch if it doesn't already exist.

        Args:
            index_name (str): The name of the index.
        """
        try:
            # ignore the index creation request if the index already exists
            if not self.es.indices.exists(index=index_name):
                logger.debug(f"Creating Elasticsearch index: {index_name}")
                self.es.indices.create(index=index_name)
            else:
                logger.debug(f"Elasticsearch index {index_name} already exists")
            return True
        except exceptions.RequestError:
            logger.error(f"RequestError while creating Elasticsearch index: {index_name}")
        except exceptions.ElasticsearchException:
            logger.exception(f"ElasticsearchException while creating Elasticsearch index: {index_name}")
        return False

    def index_document(self, index_name, document):
        """
        Index a document in Elasticsearch and log errors.

        Args:
            index_name (str): The name of the index.
            document: The document to be indexed.
        """
        processed_document = self._process_document(document)
        try:
            result = self.es.index(index=index_name, body=processed_document)
            if result["result"] == "created":
                logger.debug(f"Document {processed_document} indexed successfully. Index: {index_name} ")
                return True
            else:
                logger.error(f"Failed to index document: {result} Index: {index_name}")
        except exceptions.RequestError:
            logger.error(f"RequestError while indexing document. Index: {index_name}, document: {processed_document}")
        except exceptions.ElasticsearchException:
            logger.exception(
                f"ElasticsearchException while indexing document. Index: {index_name}, document: {processed_document}"
            )
        return False

    def _process_document(self, document):
        """
        Process the document and return the correponding dictionary.
        """
        return document if isinstance(document, dict) else {"content": document}

    def close(self):
        """
        Close the connection to Elasticsearch and release resources.
        """
        if self.es:
            logger.info("Closing Elasticsearch client")
            self.es.transport.close()
            self.es = None
