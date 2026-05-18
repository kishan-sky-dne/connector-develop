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
from types import SimpleNamespace
from unittest.mock import ANY, Mock, patch

# Third Party Library
import pytest
from minio.error import S3Error

# DNE Library
from connectors.core.utils.minio_manager import MinioManager


@patch("connectors.core.utils.minio_manager.urllib3")
@patch("connectors.core.utils.minio_manager.Minio")
def test_init(minio_mock, urllib3_mock):
    """
    Test init initializes Minio and uses CA cert
    """
    minio_mock.return_value = "dummy"
    minio_manger = MinioManager()
    urllib3_mock.PoolManager.assert_called_once_with(cert_reqs="CERT_REQUIRED", ca_certs=ANY)
    assert minio_manger.minio_client == "dummy"


@patch("connectors.core.utils.minio_manager.json")
@patch("connectors.core.utils.minio_manager.zstd")
@patch("connectors.core.utils.minio_manager.io")
@patch("connectors.core.utils.minio_manager.urllib3")
@patch("connectors.core.utils.minio_manager.Minio")
def test_write_data(minio_mock, urllib3_mock, io_mock, zstd_mock, json_mock):
    """
    Test write_data processes data as expected
    """
    json_mock.dumps.return_value = "json dumps results"
    zstd_mock.compress.return_value = "zstd compressed data"
    io_mock.BytesIO.return_value = "BytesIO data"

    minio_manger = MinioManager()
    minio_manger.write_data("dummy_bucket", "dummy_object", "dummy_data")

    zstd_mock.compress.assert_called_once_with(b"json dumps results")
    io_mock.BytesIO.assert_called_once_with("zstd compressed data")
    minio_manger.minio_client.put_object.assert_called_once_with(
        bucket_name="dummy_bucket", object_name="dummy_object", data="BytesIO data", length=20
    )


@patch("connectors.core.utils.minio_manager.json")
@patch("connectors.core.utils.minio_manager.zstd")
@patch("connectors.core.utils.minio_manager.io")
@patch("connectors.core.utils.minio_manager.urllib3")
@patch("connectors.core.utils.minio_manager.Minio")
def test_write_data_execption(minio_mock, urllib3_mock, io_mock, zstd_mock, json_mock):
    """
    Test write_data raises S3Error when put_object throws the exception
    """
    minio_mock().put_object.side_effect = S3Error(Mock, Mock, Mock, Mock, Mock, Mock)
    minio_manger = MinioManager()
    with pytest.raises(S3Error):
        minio_manger.write_data("dummy_bucket", "dummy_object", "dummy_data")


@patch("connectors.core.utils.minio_manager.json")
@patch("connectors.core.utils.minio_manager.zstd")
@patch("connectors.core.utils.minio_manager.io")
@patch("connectors.core.utils.minio_manager.urllib3")
@patch("connectors.core.utils.minio_manager.Minio")
def test_read_data(minio_mock, urllib3_mock, io_mock, zstd_mock, json_mock):
    """
    Test read_data processes data as expected
    """
    minio_mock().get_object().read.return_value = "read data"
    zstd_mock.decompress.return_value = "zstd decompressed data"
    json_mock.loads.return_value = "json loads results"

    minio_manger = MinioManager()
    assert minio_manger.read_data("dummy_bucket", "dummy_object") == "json loads results"

    zstd_mock.decompress.assert_called_once_with("read data")
    json_mock.loads.assert_called_once_with("zstd decompressed data")


@patch("connectors.core.utils.minio_manager.json")
@patch("connectors.core.utils.minio_manager.zstd")
@patch("connectors.core.utils.minio_manager.io")
@patch("connectors.core.utils.minio_manager.urllib3")
@patch("connectors.core.utils.minio_manager.Minio")
def test_read_data_execption(minio_mock, urllib3_mock, io_mock, zstd_mock, json_mock):
    """
    Test read_data returns None when get_object throws S3Error exception
    """
    minio_mock().get_object.side_effect = S3Error(Mock, Mock, Mock, Mock, Mock, Mock)
    minio_manger = MinioManager()
    assert minio_manger.read_data("dummy_bucket", "dummy_object") is None


get_file_resp = {
    "filenames": [
        "BPM-192982/console-logs_0_RSP1_CPU0_ta0_bllabd3_732v6_to_732v5_TS_2024_09_20-11_57_18.log",
        "BPM-192982/console-logs_0_RSP0_CPU0_ta0_bllabd3_732v6_to_732v5_TS_2024_09_20-11_57_18.log",
    ]
}


list_data = [
    SimpleNamespace(
        _last_modified="2024-09-05 09:07:59.825000+00:00",
        _object_name="BPM-192982/console-logs_0_RSP1_CPU0_ta0_bllabd3_732v6_to_732v5_TS_2024_09_20-11_57_18.log",
        _bucket_name="software-update",
    ),
    SimpleNamespace(
        _last_modified="2024-09-05 09:07:59.825000+00:00",
        _object_name="BPM-192982/console-logs_0_RSP0_CPU0_ta0_bllabd3_732v6_to_732v5_TS_2024_09_20-11_57_18.log",
        _bucket_name="software-update",
    ),
]


@patch("connectors.core.utils.minio_manager.urllib3")
@patch("connectors.core.utils.minio_manager.Minio")
def test_get_file_names(minio_mock, urllib3_mock):
    """
    Test get_file_names to get list of file names from MinIO
    """
    minio_mock().list_objects = Mock(return_value=list_data)
    minio_manager = MinioManager()
    assert minio_manager.get_file_names("software-update", "BPM-192982") == get_file_resp


log_files_resp = {
    "0/RP0/CPU0": ["install replace /harddisk:/upgrade-image/upgrade_732_v5/ncs5500-x-7.3.2-v5.iso", "noprompt"],
    "0/RP1/CPU0": ["install replace /harddisk:/upgrade-image/upgrade_732_v5/ncs5500-x-7.3.2-v5.iso", "noprompt"],
    "status": "SUCCESS",
}


@patch("connectors.core.utils.minio_manager.urllib3")
@patch("connectors.core.utils.minio_manager.Minio")
def test_download_files(minio_mock, urllib3_mock):
    """
    Test download_files processes data for log files in MinIO
    """
    mock_response = Mock()
    mock_response.stream.return_value = [
        b"install replace /harddisk:/upgrade-image/upgrade_732_v5/ncs5500-x-7.3.2-v5.iso\nnoprompt"
    ]
    minio_mock().get_object = Mock(return_value=mock_response)
    minio_manager = MinioManager()
    assert minio_manager.download_files("software-update", ["0/RP0/CPU0", "0/RP1/CPU0"]) == log_files_resp


@patch("connectors.core.utils.minio_manager.urllib3")
@patch("connectors.core.utils.minio_manager.Minio")
def test_get_file_names_exception(minio_mock, urllib3_mock):
    """
    Test get_file_names returns None when list_object throws S3Error exception
    """
    minio_mock().list_objects.side_effect = S3Error(Mock, Mock, Mock, Mock, Mock, Mock)
    minio_manger = MinioManager()
    assert minio_manger.get_file_names("dummy_bucket", "dummy_object") is None


@patch("connectors.core.utils.minio_manager.urllib3")
@patch("connectors.core.utils.minio_manager.Minio")
def test_download_files_exception(minio_mock, urllib3_mock):
    """
    Test download_files returns None when get_object throws S3Error exception
    """
    minio_mock().get_object.side_effect = S3Error(Mock, Mock, Mock, Mock, Mock, Mock)
    minio_manger = MinioManager()
    assert minio_manger.download_files("dummy_bucket", ["dummy_object"]) is None
