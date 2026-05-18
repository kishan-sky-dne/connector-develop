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
import threading
from contextlib import contextmanager

# Third Party Library
from sqlalchemy import create_engine, insert
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import scoped_session, sessionmaker

# Sky Library
from isp_config import ConfigManagerException

# DNE Library
from connectors.core.config import connectors_config

try:
    config = connectors_config.ConnectorsConfigManager()
    config.load_config()
except ConfigManagerException:
    sys.exit(1)

# mysql
port = config.get(section="mysqlDB", key="port")
username = config.get(section="mysqlDB", key="username")
password = config.get(section="mysqlDB", key="password")
host = config.get(section="mysqlDB", key="host")
driver = config.get(section="mysqlDB", key="driver")
database_name = config.get(section="mysqlDB", key="database_name")

# postgres
postgres_port = config.get(section="postgresDB", key="port")
postgres_username = config.get(section="postgresDB", key="username")
postgres_password = config.get(section="postgresDB", key="password")
postgres_host = config.get(section="postgresDB", key="host")
postgres_database_name = config.get(section="postgresDB", key="database_name")

logger = logging.getLogger(__name__)


class SqlDB:
    """
    Usage:
    sql_instance = SqlDB()
    with sql_instance.transactional_session() as session:
        session.query()
    """

    def __init__(self, database, url, connect_args):
        self.database = database
        logger.info(f"Initializing {self.database} client.")
        self.engine = create_engine(url, echo=True, pool_recycle=3600, connect_args=connect_args)
        self.SessionFactory = sessionmaker(bind=self.engine)

    @contextmanager
    def transactional_session(self):
        """Provide a transactional scope around a series of operations."""
        session = scoped_session(self.SessionFactory)
        logger.debug("Transactional scope started for a series of operations")
        try:
            yield session
            # added for bug DNE_31568
            logger.info("committing the transactional session")
            session.commit()
        except Exception as err:
            # added for bug DNE_31568
            logger.exception(f"Exception in transaction session {err.__class__.__name__} with {err}")
            session.rollback()
            raise
        finally:
            # added for bug DNE_31568
            logger.info("closing the transaction session")
            session.close()

    def get_insert_json_query(self, relation_object, json_data):
        """
        Return the query to insert json_data to the given relation
        """
        return insert(relation_object).values(json_data)

    def is_server_responsive(self):
        """
        Check if the server is responsive and log results
        """
        try:
            self.engine.execute("SELECT 1;")
            logger.info(f"Connected to {self.database}.")
            return True
        except OperationalError:
            logger.error(f"Failed to connect to {self.database}.")
            return False

    def dispose_engine(self):
        """
        Closes all connections associated with the engine and releases any acquired resources.
        """
        logger.info(f"Disposing the engine {self.engine}.")
        self.engine.dispose()


class MySQLDB(SqlDB):
    def __init__(self, **kwargs):
        """
        Initialize MySQL database client.
        """
        database = "MySQL"
        mysql_database_name = kwargs.get("database_name", database_name)
        url = f"{driver}+pymysql://{username}:{password}@{host}:{int(port)}/{mysql_database_name}"
        connect_args = {"ssl": {"ca": "/etc/ssl/certs/ca-certificates.crt"}}
        super().__init__(database, url, connect_args)


class PostgreSQLDB(SqlDB):
    def __init__(self, **kwargs):
        """
        Initialize PostgreSQL database client.
        """
        database = "PostgreSQL"
        database_name = kwargs.get("postgres_database_name", postgres_database_name)
        url = (
            "postgresql://"
            f"{postgres_username}:{postgres_password}@{postgres_host}:{int(postgres_port)}/{database_name}"
        )
        connect_args = {"sslmode": "prefer"}  # TODO Config SSL
        super().__init__(database, url, connect_args)


class PostgresSingletonManager:
    """
    A thread-safe Singleton class for Postgres.
    """

    _instance = None
    _lock = threading.Lock()

    @classmethod
    def __new__(cls, *args):
        with cls._lock:
            if not cls._instance:
                logger.debug("No PostgreSQLDB instance found. Creating a new instance.")
                cls._instance = PostgreSQLDB()
            else:
                logger.debug("Reusing existing PostgreSQLDB instance.")
            return cls._instance
