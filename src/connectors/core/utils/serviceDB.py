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
import time

# Third Party Library
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Sky Library
from isp_config import ConfigManagerException

# DNE Library
from connectors.core.config import connectors_config
from connectors.core.exceptions import ServiceDBException

try:
    config = connectors_config.ConnectorsConfigManager()
    config.load_config()
except ConfigManagerException:
    sys.exit(1)

port = config.get(section="serviceDB", key="port")
username = config.get(section="serviceDB", key="username")
password = config.get(section="serviceDB", key="password")
instances = config.get(section="serviceDB", key="instances").split(",")
replicaset = config.get(section="serviceDB", key="replicaSet")
readpreference = config.get(section="serviceDB", key="readPreference")
localthresholdms = config.get(section="serviceDB", key="localThresholdMs")
ca_cert_path = config.get(section="internals", key="ca_certs")
max_time_ms = int(config.get(section="serviceDB", key="maxTimeMS"))


logger = logging.getLogger(__name__)


class ServiceDB:
    def __init__(self, collection: str) -> None:
        """
        Initializes MongoDB Client
        """
        logger.debug(f"Initializing ServiceDB with instances: {instances}, port: {port}, username: {username}")
        self.url = (
            f"mongodb://{username}:{password}@{instances[0]}:{port},{instances[1]}:{port},"
            f"{instances[2]}:{port}/Dial"
        )
        self.client = MongoClient(
            self.url,
            replicaset=replicaset,
            readPreference=readpreference,
            localThresholdMS=localthresholdms,
            ssl=True,
            ssl_ca_certs=ca_cert_path,
        )
        self.database = self.client["Dial"]
        if collection in self.database.list_collection_names(filter={"name": collection}):
            self.collection = self.database[collection]
            logger.info(f"collection identified {collection}")
        else:
            raise ServiceDBException(f"Collection {collection} not found in ServiceDB")

    def insert(self, model):
        """
        Method to insert to db
        Args:
            model : db/user/service model
        Returns:
            status: True
        Raises:
            Exception
        """
        try:
            insert = self.collection.insert_one(model)
            if insert.acknowledged:
                logger.debug(f"model has been inserted with the id {insert.inserted_id}")
                return True
            else:
                raise ServiceDBException(f"PyMongo error while inserting the model model into db")
        except PyMongoError as err:
            raise ServiceDBException(err)

    def update(self, query, params):
        """
        Method to update to db
        Args:
            query: update query
            params: parameters
        Returns:
            status: True
        Raises:
            Exception
        """
        try:
            body = {"$set": params}
            logger.info(f"Update data in DB, {query, params}")
            update = self.collection.update_one(query, body, upsert=True)
            time.sleep(5)
            if update.matched_count == 1 and update.modified_count == 1:
                return True
            else:
                raise ServiceDBException(f"Entry for {query} not found in ServiceDB")
        except PyMongoError as err:
            raise ServiceDBException(err)

    def find_one(self, query):
        """
        Method to find_one in db
        Args:
        query: find query
         Returns:
              record
         Raises:
             Exception
        """

        try:
            record = self.collection.find_one(query, max_time_ms=max_time_ms)
            logger.debug(f"record fetched for query {query}")
            if record:
                return record
            logger.debug(f"Record not found for query {query}")
            raise ServiceDBException(f"record not found for query {query}")
        except PyMongoError as err:
            raise ServiceDBException(err) from err

    def find(self, query):
        """
        Method to find in db
        Args:
             query: find query
        Returns:
             record
        Raises:
            Exception
        """
        try:
            return list(self.collection.find(query))
        except PyMongoError as err:
            raise ServiceDBException(err) from err

    def aggregate(self, query, **kwargs):
        """
        Method to fire aggregate query
        Args:
             query: list of dictionary
             kwargs: optional parameters
        Returns:
             records
        Raises:
            Exception
        """
        if not isinstance(query, list):
            raise ServiceDBException("Query must contain list of operations (Pipeline) Eg: [{'$match':{}}]")
        try:
            return list(self.collection.aggregate(query, **{**kwargs, "maxTimeMS": max_time_ms}))
        except PyMongoError as err:
            raise ServiceDBException(err) from err
