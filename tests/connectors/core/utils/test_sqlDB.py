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
import threading
from unittest.mock import Mock, patch

# Third Party Library
import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql.dml import Insert

# DNE Library
from connectors.core.utils.sqldb.sqlDB import MySQLDB, PostgreSQLDB, PostgresSingletonManager


@patch("connectors.core.utils.sqldb.sqlDB.create_engine")
@patch("connectors.core.utils.sqldb.sqlDB.sessionmaker")
def test_postgresdb_initialization(sessionmaker_mock, create_engine_mock):
    """
    Test PostgreSQLDB initialization
    """
    create_engine_mock.return_value = "dummy engine"
    postgres_instance = PostgreSQLDB()
    create_engine_mock.assert_called_once()
    sessionmaker_mock.assert_called_once_with(bind="dummy engine")
    assert postgres_instance.database == "PostgreSQL"


@patch("connectors.core.utils.sqldb.sqlDB.create_engine")
@patch("connectors.core.utils.sqldb.sqlDB.sessionmaker")
def test_mysqldb_initialization(sessionmaker_mock, create_engine_mock):
    """
    Test MySQLDB initialization
    """
    create_engine_mock.return_value = "dummy engine"
    mysql_instance = MySQLDB()
    create_engine_mock.assert_called_once()
    sessionmaker_mock.assert_called_once_with(bind="dummy engine")
    assert mysql_instance.database == "MySQL"


@patch("connectors.core.utils.sqldb.sqlDB.scoped_session")
@patch("connectors.core.utils.sqldb.sqlDB.create_engine")
@patch("connectors.core.utils.sqldb.sqlDB.sessionmaker")
def test_transactional_session_success(sessionmaker_mock, create_engine_mock, scoped_session_mock):
    """
    Test transactional_session success
    """
    sessionmaker_mock.return_value = "dummy sessionFactory"
    mysql_instance = MySQLDB()
    with mysql_instance.transactional_session() as session:
        scoped_session_mock.assert_called_once_with("dummy sessionFactory")
    session.commit.assert_called_once()
    session.close.assert_called_once()


@patch("connectors.core.utils.sqldb.sqlDB.scoped_session")
@patch("connectors.core.utils.sqldb.sqlDB.create_engine")
@patch("connectors.core.utils.sqldb.sqlDB.sessionmaker")
def test_transactional_session_failure(sessionmaker_mock, create_engine_mock, scoped_session_mock):
    """
    Test transactional_session rollback
    """
    sessionmaker_mock.return_value = "dummy sessionFactory"
    scoped_session_mock.return_value.commit.side_effect = Exception("dummmy")
    mysql_instance = MySQLDB()
    with pytest.raises(Exception):
        with mysql_instance.transactional_session() as session:
            scoped_session_mock.assert_called_once_with("dummy sessionFactory")
    session.commit.assert_called_once()
    session.rollback.assert_called_once()
    session.close.assert_called_once()


@patch("connectors.core.utils.sqldb.sqlDB.create_engine")
@patch("connectors.core.utils.sqldb.sqlDB.sessionmaker")
def test_get_insert_json_query(sessionmaker_mock, create_engine_mock):
    """
    Test get_insert_json_query returns a sqlalchemy Insert type
    """
    mysql_instance = MySQLDB()
    assert isinstance(mysql_instance.get_insert_json_query(Mock(), {"dummy": "json"}), Insert)


@patch("connectors.core.utils.sqldb.sqlDB.create_engine")
@patch("connectors.core.utils.sqldb.sqlDB.sessionmaker")
def test_is_server_responsive_positive(sessionmaker_mock, create_engine_mock):
    """
    Test is_server_responsive returns True when SELECT 1; doesn't fail
    """
    mysql_instance = MySQLDB()
    assert mysql_instance.is_server_responsive()
    create_engine_mock.return_value.execute.assert_called_once_with("SELECT 1;")


@patch("connectors.core.utils.sqldb.sqlDB.create_engine")
@patch("connectors.core.utils.sqldb.sqlDB.sessionmaker")
def test_is_server_responsive_negative(sessionmaker_mock, create_engine_mock):
    """
    Test is_server_responsive returns False when SELECT 1; fails
    """
    mysql_instance = MySQLDB()
    create_engine_mock.return_value.execute.side_effect = OperationalError("dummy", "dummy", "dummy")
    assert not mysql_instance.is_server_responsive()


@patch("connectors.core.utils.sqldb.sqlDB.create_engine")
@patch("connectors.core.utils.sqldb.sqlDB.sessionmaker")
def test_dispose_engine(sessionmaker_mock, create_engine_mock):
    """
    Test dispose_engine calls engine's dispose method
    """
    mysql_instance = MySQLDB()
    mysql_instance.dispose_engine()
    mysql_instance.engine.dispose.assert_called_once()


@patch("connectors.core.utils.sqldb.sqlDB.create_engine")
@patch("connectors.core.utils.sqldb.sqlDB.sessionmaker")
def test_postgres_singleton_manager_creates_new_instance(sessionmaker_mock, create_engine_mock):
    """
    Test PostgresSingletonManager creates a new instance
    """
    instance = PostgresSingletonManager()
    assert isinstance(instance, PostgreSQLDB)
    assert PostgresSingletonManager._instance is not None


@patch("connectors.core.utils.sqldb.sqlDB.create_engine")
@patch("connectors.core.utils.sqldb.sqlDB.sessionmaker")
def test_postgres_singleton_manager_reuses_existing_instance(sessionmaker_mock, create_engine_mock):
    """
    Test PostgresSingletonManager reuses existing instance
    """
    instance1 = PostgresSingletonManager()
    instance2 = PostgresSingletonManager()
    assert instance1 is instance2


@patch("connectors.core.utils.sqldb.sqlDB.create_engine")
@patch("connectors.core.utils.sqldb.sqlDB.sessionmaker")
def test_postgres_singleton_manager_thread_safe_postgres_creation(sessionmaker_mock, create_engine_mock):
    """
    Test PostgresSingletonManager is thread safe
    """
    # Create instances in multiple threads
    with threading.Lock():
        instances = [PostgresSingletonManager() for _ in range(5)]
    # All instances should be the same, as the lock ensures only one instance is created
    assert all(instance is instances[0] for instance in instances)
