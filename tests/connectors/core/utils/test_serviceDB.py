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
from unittest.mock import patch

# Third Party Library
import pytest
from pymongo.database import Collection, Database
from pymongo.errors import PyMongoError

# DNE Library
from connectors.core.utils import serviceDB
from connectors.core.utils.serviceDB import MongoClient, ServiceDB, ServiceDBException


@patch.object(serviceDB, "username", return_value="dummy_user")
@patch.object(serviceDB, "password", return_value="dummy_pass")
@patch.object(Database, "list_collection_names", return_value=["xxx", "xyx"])
def test_db_connection_initialization(db_mock, pass_mock, user_mock):
    """
    test service db initialization
    """
    db_conn = ServiceDB(collection="xxx")
    assert isinstance(db_conn.client, MongoClient)
    assert isinstance(db_conn.database, Database)
    assert isinstance(db_conn.collection, Collection)


@patch.object(serviceDB, "username", return_value="dummy_user")
@patch.object(serviceDB, "password", return_value="dummy_pass")
@patch.object(Database, "list_collection_names", return_value=["super", "xyx"])
def test_db_connection_initialization_no_collection(db_mock, pass_mock, user_mock):
    """
    negative test service db initialization
    """
    with pytest.raises(ServiceDBException):
        ServiceDB(collection="xxx")


@patch.object(serviceDB, "username", return_value="dummy_user")
@patch.object(serviceDB, "password", return_value="dummy_pass")
@patch.object(Database, "list_collection_names", return_value=["xxx", "xyx"])
@patch.object(Collection, "find_one", side_effect=PyMongoError)
def test_db_find_one_exception_pymongo(mock_find_one, db_mock, pass_mock, user_mock):
    """
    negative test to check service db find_one handles pymongo error and raises service Db Exception
    """
    db_conn = ServiceDB(collection="xxx")
    with pytest.raises(ServiceDBException):
        query = {"query": "dummy_query"}
        db_conn.find_one(query)


@patch.object(serviceDB, "username", return_value="dummy_user")
@patch.object(serviceDB, "password", return_value="dummy_pass")
@patch.object(Database, "list_collection_names", return_value=["xxx", "xyx"])
@patch.object(Collection, "find_one", return_value=None)
def test_db_find_one_no_record(mock_find_one, db_mock, pass_mock, user_mock):
    """
    negative test to check service db find_one raises exception when no record found
    """
    db_conn = ServiceDB(collection="xxx")
    with pytest.raises(ServiceDBException):
        query = {"query": "dummy_query"}
        db_conn.find_one(query)


@patch.object(serviceDB, "username", return_value="dummy_user")
@patch.object(serviceDB, "password", return_value="dummy_pass")
@patch.object(Database, "list_collection_names", return_value=["xxx", "xyx"])
@patch.object(Collection, "find_one", return_value={"record": "dummy record"})
def test_db_find_one(mock_find_one, db_mock, pass_mock, user_mock):
    """
    positive test to check service db find_one utility
    """
    db_conn = ServiceDB(collection="xxx")
    query = {"query": "dummy_query"}
    assert db_conn.find_one(query) == {"record": "dummy record"}


@patch.object(serviceDB, "username", return_value="dummy_user")
@patch.object(serviceDB, "password", return_value="dummy_pass")
@patch.object(Database, "list_collection_names", return_value=["xxx", "xyx"])
@patch.object(Collection, "insert_one", side_effect=PyMongoError)
def test_db_insert_exception_pymongo(insert_mock, db_mock, pass_mock, user_mock):
    """
    negative test to check service db insert handles pymongo error and raises service Db Exception
    """
    db_conn = ServiceDB(collection="xxx")
    with pytest.raises(ServiceDBException):
        model = {"model": "dummy_model"}
        db_conn.insert(model)


@patch.object(serviceDB, "username", return_value="dummy_user")
@patch.object(serviceDB, "password", return_value="dummy_pass")
@patch.object(Database, "list_collection_names", return_value=["xxx", "xyx"])
@patch.object(Collection, "insert_one")
def test_db_insert(insert_mock, db_mock, pass_mock, user_mock):
    """
    positive test to check service db insert utility
    """
    db_conn = ServiceDB(collection="xxx")
    dummy = {"record": "dummy record"}
    insert_mock.return_value.acknowledged = True
    assert db_conn.insert(dummy)


@patch.object(serviceDB, "username", return_value="dummy_user")
@patch.object(serviceDB, "password", return_value="dummy_pass")
@patch.object(Database, "list_collection_names", return_value=["xxx", "xyx"])
@patch.object(Collection, "insert_one")
def test_db_insert_failed(insert_mock, db_mock, pass_mock, user_mock):
    """
    negative test to check service db insert utility
    """
    db_conn = ServiceDB(collection="xxx")
    dummy = {"record": "dummy record"}
    insert_mock.return_value.acknowledged = False
    with pytest.raises(ServiceDBException):
        db_conn.insert(dummy)


@patch.object(serviceDB, "username", return_value="dummy_user")
@patch.object(serviceDB, "password", return_value="dummy_pass")
@patch.object(Database, "list_collection_names", return_value=["xxx", "xyx"])
@patch.object(Collection, "update_one", side_effect=PyMongoError)
def test_db_update_exception_pymongo(update_mock, db_mock, pass_mock, user_mock):
    """
    negative test to check service db update handles pymongo error and raises service Db Exception
    """
    db_conn = ServiceDB(collection="xxx")
    with pytest.raises(ServiceDBException):
        query = {"query": "dummy"}
        params = {"model": "dummy_model"}
        db_conn.update(query, params)


@patch.object(serviceDB, "username", return_value="dummy_user")
@patch.object(serviceDB, "password", return_value="dummy_pass")
@patch.object(Database, "list_collection_names", return_value=["xxx", "xyx"])
@patch.object(Collection, "update_one")
@patch("connectors.core.utils.serviceDB.time")
def test_db_update(time_mock, update_mock, db_mock, pass_mock, user_mock):
    """
    positive test to check service db update utility
    """
    update_mock.return_value.matched_count = 1
    update_mock.return_value.modified_count = 1
    db_conn = ServiceDB(collection="xxx")
    dummy = {"record": "dummy record"}
    assert db_conn.update(query=dummy, params=dummy)


@patch.object(serviceDB, "username", return_value="dummy_user")
@patch.object(serviceDB, "password", return_value="dummy_pass")
@patch.object(Database, "list_collection_names", return_value=["xxx", "xyx"])
@patch.object(Collection, "update_one")
@patch("connectors.core.utils.serviceDB.time")
def test_db_update_failed(time_mock, update_mock, db_mock, pass_mock, user_mock):
    """
    negative test to check service db update utility
    """
    update_mock.return_value.matched_count = 0
    update_mock.return_value.modified_count = 0
    db_conn = ServiceDB(
        collection="xxx",
    )
    dummy = {"record": "dummy record"}
    with pytest.raises(ServiceDBException):
        db_conn.update(query=dummy, params=dummy)
