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
import io
import os
from unittest.mock import patch

# Third Party Library
import flask
import pytest
from werkzeug.datastructures import FileStorage

# DNE Library
from connectors.webserver.itsm.tasks.ticketAttachmentList import attachment_list
from connectors.webserver.itsm.tasks.ticketAttachmentUpload import attachment_upload

abs_dir = os.path.abspath(os.path.dirname(__file__))

data = {"body": {"operation": "remove", "ticketNumber": "CHG0108229", "fileName": "fileName.txt"}}
#  Fix for Bug DNE-2584
data1 = {
    "body": {
        "operation": "add",
        "ticketNumber": "CHG0108229",
        "fileName": "fileName.txt",
    },
    "attachment": FileStorage(open(abs_dir + "/../../../../requirements.txt", "r"), content_type="application/msword"),
}
data2 = {"ticketNumber": "CHG0108229"}
#  Fix for Bug DNE-2584
data3 = {
    "body": {
        "operation": "add",
        "ticketNumber": "CHG0108229",
        "fileName": "fileName.txt",
    },
    "attachment": FileStorage(open(abs_dir + "/test_attachments.py", "r"), content_type="application/octet-stream"),
}

data4 = {
    "body": {
        "operation": "add",
        "ticketNumber": "CHG0108229",
        "fileName": "fileName.txt",
    },
}
data5 = {"ticketNumber": None}

app = flask.Flask(__name__)
test_file = "trial_data".encode(encoding="utf-8")


@pytest.mark.parametrize("kwargs", [data1])
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("base64.b64encode")
def test_attachment1(encode_mock, service3045_mock, kwargs):
    encode_mock.return_value = b"YmFzZTY0IGVuY29kZWQgc3RyaW5n"
    with app.test_request_context(
        method="POST",
        data={
            "attachment": FileStorage(
                stream=io.BytesIO(test_file),
                filename="requirements.txt",
                content_type="application/msword",
            )
        },
        content_type="multipart/form-data",
    ):

        service3045_mock.return_value = {"result": {"details": "CHG0108229 (ATTACHMENT ADDED)"}}
        result = attachment_upload(**kwargs)
        assert result == {"status": "CHG0108229 (ATTACHMENT ADDED)", "ticketNumber": "CHG0108229"}


@pytest.mark.parametrize("kwargs", [data2])
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
def test_attachment2(service3045_mock, kwargs):
    service3045_mock.return_value = {
        "result": [
            {
                "size_bytes": "584790",
                "file_name": "fileName.txt",
                "sys_mod_count": "1",
                "average_image_color": "",
                "image_width": "",
                "sys_updated_on": "2020-07-06 14:38:10",
                "sys_tags": "",
                "table_name": "change_request",
                "sys_id": "4b1ced5adb7550509ae2ae4cd3961909",
                "image_height": "",
                "sys_updated_by": "system",
                "content_type": "text/plain",
                "sys_created_on": "2020-07-06 14:38:10",
                "size_compressed": "343459",
                "u_linked_sys_id": "",
                "compressed": "true",
                "state": "available",
                "table_sys_id": "bc0fa79bdbfcdc5024c9a235ca961930",
                "chunk_size_bytes": "700000",
                "hash": "0a7154dc4493101199015a907dbbd2b7a3b1b961e7331fb14d181e09f44ceef7",
                "sys_created_by": "spark_proxy_INTEGRATION",
            },
            {
                "size_bytes": "1487934",
                "file_name": "precheck2.doc",
                "sys_mod_count": "1",
                "average_image_color": "",
                "image_width": "",
                "sys_updated_on": "2020-06-29 14:46:41",
                "sys_tags": "",
                "table_name": "change_request",
                "sys_id": "53eaa50cdb3554509ae2ae4cd39619e9",
                "image_height": "",
                "sys_updated_by": "system",
                "content_type": "application/msword",
                "sys_created_on": "2020-06-29 14:46:39",
                "size_compressed": "1413442",
                "u_linked_sys_id": "",
                "compressed": "true",
                "state": "available",
                "table_sys_id": "bc0fa79bdbfcdc5024c9a235ca961930",
                "chunk_size_bytes": "700000",
                "hash": "4554a9a0a61af205f36bbdb537b50aedb3a265bfb6c6f8487cbd7e968c612f6a",
                "sys_created_by": "spark_proxy_INTEGRATION",
            },
            {
                "size_bytes": "1487934",
                "file_name": "precheck4.doc",
                "sys_mod_count": "1",
                "average_image_color": "",
                "image_width": "",
                "sys_updated_on": "2020-06-30 12:18:35",
                "sys_tags": "",
                "table_name": "change_request",
                "sys_id": "8ca2961cdb7998509ae2ae4cd3961949",
                "image_height": "",
                "sys_updated_by": "system",
                "content_type": "application/msword",
                "sys_created_on": "2020-06-30 12:18:35",
                "size_compressed": "1413442",
                "u_linked_sys_id": "",
                "compressed": "true",
                "state": "available",
                "table_sys_id": "bc0fa79bdbfcdc5024c9a235ca961930",
                "chunk_size_bytes": "700000",
                "hash": "4554a9a0a61af205f36bbdb537b50aedb3a265bfb6c6f8487cbd7e968c612f6a",
                "sys_created_by": "spark_proxy_INTEGRATION",
            },
        ]
    }
    result = attachment_list(**kwargs)
    assert result == {
        "results": [
            {
                "createdOn": "2020-07-06 14:38:10",
                "fileName": "fileName.txt",
                "state": "available",
                "updatedOn": "2020-07-06 14:38:10",
            },
            {
                "createdOn": "2020-06-29 14:46:39",
                "fileName": "precheck2.doc",
                "state": "available",
                "updatedOn": "2020-06-29 14:46:41",
            },
            {
                "createdOn": "2020-06-30 12:18:35",
                "fileName": "precheck4.doc",
                "state": "available",
                "updatedOn": "2020-06-30 12:18:35",
            },
        ]
    }, "failed"


@pytest.mark.parametrize("kwargs", [data])
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
def test_attachment3(service3045_mock, kwargs):
    service3045_mock.return_value = {"result": {"details": "CHG0108229 (ATTACHMENT REMOVED)"}}
    result = attachment_upload(**kwargs)
    assert result == {"status": "CHG0108229 (ATTACHMENT REMOVED)", "ticketNumber": "CHG0108229"}, "failed"


@pytest.mark.parametrize("kwargs", [data3])
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
def test_attachment4(service3045_mock, kwargs):

    with app.test_request_context(
        method="POST",
        data={
            "attachment": FileStorage(
                stream=io.BytesIO(test_file),
                content_type="application/octet-stream",
                filename="requirements.txt",
            )
        },
        content_type="multipart/form-data",
    ):
        service3045_mock.return_value = {"result": {"details": "CHG0108229 (ATTACHMENT ADDED)"}}
        result = attachment_upload(**kwargs)
        assert (
            result.__dict__["body"]["title"] == "Supported types are text/plain,application/vnd.ms-excel,"
            "application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/zip"
        ), "failed"
        assert result.__dict__["body"]["status"] == 415


@pytest.mark.parametrize("kwargs", [data3])
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
def test_attachment5(service3045_mock, kwargs):

    with app.test_request_context(
        method="POST",
        data={
            "attachment": FileStorage(
                stream=io.BytesIO(test_file),
                filename="test.txt",
                content_type="application/msword",
            )
        },
        content_type="multipart/form-data",
    ):
        service3045_mock.side_effect = ValueError("error")
        result = attachment_upload(**kwargs)
        assert result.status_code == 404, "failed"
        assert result.__dict__["body"]["title"] == "Error in request body"


@pytest.mark.parametrize("kwargs", [data1])
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
@patch("base64.b64encode")
def test_attachment6(encode_mock, service3045_mock, kwargs):
    encode_mock.return_value = b"YmFzZTY0IGVuY29kZWQgc3RyaW5n"

    with app.test_request_context(
        method="POST",
        data={
            "attachment": FileStorage(
                stream=io.BytesIO(test_file),
                filename="test.txt",
                content_type="application/msword",
            )
        },
        content_type="multipart/form-data",
    ):
        service3045_mock.return_value = {}
        result = attachment_upload(**kwargs)
        assert result.__dict__["body"]["title"] == "Error while add/remove attachment on Spark"
        assert result.__dict__["body"]["status"] == 404


@pytest.mark.parametrize("kwargs", [data1])
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
def test_attachment7(service3045_mock, kwargs):
    service3045_mock.return_value = {}
    result = attachment_upload(**kwargs)
    assert result.__dict__["body"]["title"] == "Connector exception raised while creating the ticket"
    assert result.__dict__["body"]["status"] == 500


@pytest.mark.parametrize("kwargs", [data2])
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
def test_attachment8(service3045_mock, kwargs):
    service3045_mock.return_value = {}
    result = attachment_list(**kwargs)
    assert result.__dict__["body"]["title"] == "Error in accessing Spark ticketing system"
    assert result.__dict__["body"]["status"] == 404


@pytest.mark.parametrize("kwargs", [{}])
@patch("connectors.core.services.itsm.connector.SparkTicketService.service3045")
def test_attachment9(service3045_mock, kwargs):
    service3045_mock.return_value = {}
    result = attachment_list(**kwargs)
    assert result.__dict__["body"]["title"] == "Error in response from Spark or ticket not found"
    assert result.__dict__["body"]["status"] == 404


def test_attachment10():
    result = attachment_upload(**data4)
    assert result.__dict__["body"]["detail"] == "'attachment' is a required property"
    assert result.__dict__["body"]["title"] == "Error in request body"
    assert result.__dict__["body"]["status"] == 400


def test_attachment11():
    result = attachment_list(**data5)
    assert result.__dict__["body"]["detail"] == "'ticketNumber' is a required property"
    assert result.__dict__["body"]["title"] == "Error in request body"
    assert result.__dict__["body"]["status"] == 400
