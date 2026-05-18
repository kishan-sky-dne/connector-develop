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

# DNE Library
from connectors.core.exceptions import ConnectorsException
from connectors.core.services.dcs.cache_controller import CacheController

example_all_devices = [
    {
        "hostname": "ma0.test.bllab.it.bb.sky.com",
        "rev": "xxxxx",
    },
    {
        "hostname": "ta0.test.bllab.it.bb.sky.com",
        "rev": "xxxxx",
    },
    {
        "hostname": "ma1.test.bllab.it.bb.sky.com",
        "rev": "xxxxx",
    },
]

example_all_devices_2 = [
    {
        "hostname": "ma0.test.bllab.it.bb.sky.com",
        "rev": "xxxxx",
    }
]


@patch("connectors.core.services.dcs.cache_controller.config")
@patch("connectors.core.services.dcs.cache_controller.DeviceConfigurationService")
@patch("connectors.core.services.dcs.cache_controller.MinioManager")
def test_init(minio_mock, dcs_mock, conf_mock):
    """
    Test init initializes MinioManager and DCS and sets cache limit
    """
    conf_mock.get.return_value = "1"
    cache_controller = CacheController()
    minio_mock.assert_called_once()
    dcs_mock.assert_called_once_with(hostname=None, username="1", password="1")
    assert cache_controller.cache_limit_seconds == 1


@patch("connectors.core.services.dcs.cache_controller.CacheController._run_minio_thread")
@patch("connectors.core.services.dcs.cache_controller.datetime")
@patch("connectors.core.services.dcs.cache_controller.CacheController._update_minio")
@patch("connectors.core.services.dcs.cache_controller.CacheController.filter_by_hostname")
@patch("connectors.core.services.dcs.cache_controller.config")
@patch("connectors.core.services.dcs.cache_controller.DeviceConfigurationService")
@patch("connectors.core.services.dcs.cache_controller.MinioManager")
def test_get_filtered_devices_no_data(
    minio_mock, dcs_mock, conf_mock, filter_mock, _update_minio_mock, datetime_mock, run_thread_mock
):
    """
    Test get_filtered_devices when MinIO read returns None
    """
    minio_mock().read_data.return_value = None
    dcs_mock().all_devices.return_value = example_all_devices
    cache_controller = CacheController()
    cache_controller.get_filtered_devices(filtering_mechanism="filter_by_hostname", hostname="ma0")
    dcs_mock().all_devices.assert_called_once()
    run_thread_mock.assert_called_once_with(all_devices=example_all_devices)
    filter_mock.assert_called_once_with(example_all_devices, hostname="ma0")


@patch("connectors.core.services.dcs.cache_controller.CacheController._run_minio_thread")
@patch("connectors.core.services.dcs.cache_controller.datetime")
@patch("connectors.core.services.dcs.cache_controller.CacheController._update_minio")
@patch("connectors.core.services.dcs.cache_controller.CacheController.filter_by_hostname")
@patch("connectors.core.services.dcs.cache_controller.config")
@patch("connectors.core.services.dcs.cache_controller.DeviceConfigurationService")
@patch("connectors.core.services.dcs.cache_controller.MinioManager")
def test_get_filtered_devices_old_data(
    minio_mock, dcs_mock, conf_mock, filter_mock, _update_minio_mock, datetime_mock, run_thread_mock
):
    """
    Test get_filtered_devices when MinIO read returns old data
    """
    minio_mock().read_data.return_value = "dummy"
    minio_mock().minio_client.stat_object().last_modified.replace.return_value = 4
    datetime_mock.datetime.now.return_value = 6
    datetime_mock.timedelta.return_value = 1
    cache_controller = CacheController()
    cache_controller.get_filtered_devices(filtering_mechanism="filter_by_hostname", hostname="ma0")
    dcs_mock().all_devices.assert_not_called()
    run_thread_mock.assert_called_once_with()
    filter_mock.assert_called_once_with("dummy", hostname="ma0")


@patch("connectors.core.services.dcs.cache_controller.datetime")
@patch("connectors.core.services.dcs.cache_controller.threading")
@patch("connectors.core.services.dcs.cache_controller.CacheController._update_minio")
@patch("connectors.core.services.dcs.cache_controller.CacheController.filter_by_hostname")
@patch("connectors.core.services.dcs.cache_controller.config")
@patch("connectors.core.services.dcs.cache_controller.DeviceConfigurationService")
@patch("connectors.core.services.dcs.cache_controller.MinioManager")
def test_get_filtered_devices(
    minio_mock, dcs_mock, conf_mock, filter_mock, _update_minio_mock, threading_mock, datetime_mock
):
    """
    Test get_filtered_devices when MinIO read returns not too old data
    """
    minio_mock().read_data.return_value = "dummy"
    minio_mock().minio_client.stat_object().last_modified.replace.return_value = 4
    datetime_mock.datetime.now.return_value = 6
    datetime_mock.timedelta.return_value = 3
    cache_controller = CacheController()
    cache_controller.get_filtered_devices(filtering_mechanism="filter_by_hostname", hostname="ma0")
    dcs_mock().all_devices.assert_not_called()
    threading_mock.Thread.assert_not_called()
    threading_mock.Thread().start.assert_not_called()
    filter_mock.assert_called_once_with("dummy", hostname="ma0")


@patch("connectors.core.services.dcs.cache_controller.CacheController._remove_rev")
@patch("connectors.core.services.dcs.cache_controller.config")
@patch("connectors.core.services.dcs.cache_controller.DeviceConfigurationService")
@patch("connectors.core.services.dcs.cache_controller.MinioManager")
def test_update_minio_no_data(minio_mock, dcs_mock, conf_mock, remove_rev_mock):
    """
    Test when data is not given _update_minio fetches this from dcs and writes data
    """
    remove_rev_mock.return_value = "dummy"
    conf_mock.get.return_value = "2"
    cache_controller = CacheController()
    cache_controller._update_minio()
    dcs_mock().all_devices.assert_called_once()
    minio_mock().write_data.assert_called_once_with(bucket_name="2", object_key="2", data="dummy")


@patch("connectors.core.services.dcs.cache_controller.config")
@patch("connectors.core.services.dcs.cache_controller.DeviceConfigurationService")
@patch("connectors.core.services.dcs.cache_controller.MinioManager")
def test_update_minio(minio_mock, dcs_mock, conf_mock):
    """
    Test when data is given _update_minio does not call dcs and writes data
    """
    conf_mock.get.return_value = "2"
    cache_controller = CacheController()
    cache_controller._update_minio(data="dummy")
    dcs_mock().all_devices.assert_not_called()
    minio_mock().write_data.assert_called_once_with(bucket_name="2", object_key="2", data="dummy")


@patch("connectors.core.services.dcs.cache_controller.CacheController._is_minio_object_locked")
@patch("connectors.core.services.dcs.cache_controller.config")
@patch("connectors.core.services.dcs.cache_controller.DeviceConfigurationService")
@patch("connectors.core.services.dcs.cache_controller.MinioManager")
def test_update_minio_locked(minio_mock, dcs_mock, conf_mock, is_locked_mock):
    """
    Test while minio is being updated, new requests will not update it again
    """
    cache_controller = CacheController()
    cache_controller._is_minio_object_locked = "True"
    cache_controller._update_minio(data="dummy")
    dcs_mock().all_devices.assert_not_called()
    minio_mock().write_data.assert_not_called()


@patch("connectors.core.services.dcs.cache_controller.config")
@patch("connectors.core.services.dcs.cache_controller.DeviceConfigurationService")
@patch("connectors.core.services.dcs.cache_controller.MinioManager")
def test_update_minio_execption(minio_mock, dcs_mock, conf_mock, caplog):
    """
    Test when exception is raised, it is logged and not propagated
    """
    minio_mock().write_data.side_effect = Exception("dummy_exeption")
    cache_controller = CacheController()
    cache_controller.bucket_name = "dcs"
    cache_controller.object_key = "all_devices"
    with caplog.at_level(logging.ERROR):
        cache_controller._update_minio(data="dummy_data")
        assert (
            "Failed to update 'all_devices' object in MinIO 'dcs'. Future readings may be inaccurate. dummy_exeption"
            in caplog.text
        )


@patch("connectors.core.services.dcs.cache_controller.config")
@patch("connectors.core.services.dcs.cache_controller.DeviceConfigurationService")
@patch("connectors.core.services.dcs.cache_controller.MinioManager")
def test_filter_by_hostname(minio_mock, dcs_mock, conf_mock):
    """
    Test filter_by_hostname returns the list of hostnames as expected,
    """
    assert CacheController().filter_by_hostname(example_all_devices, "ma0") == [
        {"hostname": "ma0.test.bllab.it.bb.sky.com"}
    ]


@patch("connectors.core.services.dcs.cache_controller.config")
@patch("connectors.core.services.dcs.cache_controller.DeviceConfigurationService")
@patch("connectors.core.services.dcs.cache_controller.MinioManager")
def test_remove_rev(minio_mock, dcs_mock, conf_mock):
    """
    Test _remove_rev removes "rev" from devices to keep only "hostname" keys
    """
    assert CacheController()._remove_rev(example_all_devices_2) == [{"hostname": "ma0.test.bllab.it.bb.sky.com"}]


@patch("connectors.core.services.dcs.cache_controller.config")
@patch("connectors.core.services.dcs.cache_controller.DeviceConfigurationService")
@patch("connectors.core.services.dcs.cache_controller.MinioManager")
def test_set_locked_tag(minio_mock, dcs_mock, conf_mock):
    """
    Test _set_locked_tag will set locked tag to False by default
    """
    cache_controller = CacheController()
    cache_controller._set_locked_tag("False", {})
    cache_controller.minio.minio_client.set_object_tags.assert_called_once_with(
        bucket_name=ANY, object_name=ANY, tags={"locked": "False"}
    )


@patch("connectors.core.services.dcs.cache_controller.threading")
@patch("connectors.core.services.dcs.cache_controller.config")
@patch("connectors.core.services.dcs.cache_controller.DeviceConfigurationService")
@patch("connectors.core.services.dcs.cache_controller.MinioManager")
def test_run_minio_thread_with_data(minio_mock, dcs_mock, conf_mock, threading_mock):
    """
    Test _run_minio_thread passes all_devices argument if given
    """
    cache_controller = CacheController()
    cache_controller._run_minio_thread(all_devices="dummy")
    threading_mock.Thread.assert_called_once_with(name="minio_thread", target=ANY, args=("dummy",), daemon=True)
    threading_mock.Thread().start.assert_called_once()


@patch("connectors.core.services.dcs.cache_controller.threading")
@patch("connectors.core.services.dcs.cache_controller.config")
@patch("connectors.core.services.dcs.cache_controller.DeviceConfigurationService")
@patch("connectors.core.services.dcs.cache_controller.MinioManager")
def test_run_minio_thread_without_data(minio_mock, dcs_mock, conf_mock, threading_mock):
    """
    Test _run_minio_thread does not pass all_devices argument if not given
    """
    cache_controller = CacheController()
    cache_controller._run_minio_thread()
    threading_mock.Thread.assert_called_once_with(name="minio_thread", target=ANY, daemon=True)
    threading_mock.Thread().start.assert_called_once()


@patch("connectors.core.services.dcs.cache_controller.DeviceConfigurationService")
@patch("connectors.core.services.dcs.cache_controller.MinioManager")
def test_purge_cache(minio_mock, dcs_mock):
    """
    Test purge cache success scenarios
    """
    cache_controller = CacheController()
    rest = Mock()
    response = Mock()
    response.status_code = 200
    response._content = "Cache cleared successfully"
    rest.get = Mock(return_value=response)
    dcs_mock.return_value.rest = rest
    response = cache_controller.purge_cache("http://api-dev.dne.sky.com", "key=api/v1/ta0.bllabd3")
    assert response is True


@patch("connectors.core.services.dcs.cache_controller.DeviceConfigurationService")
@patch("connectors.core.services.dcs.cache_controller.MinioManager")
def test_purge_cache_fail(minio_mock, dcs_mock):
    """
    Test purge cache failure scenarios
    """
    cache_controller = CacheController()
    response = Mock()
    response.status_code = 400
    response._content = "Bad Request"
    rest = Mock()
    rest.get = Mock(return_value=response)
    dcs_mock.return_value.rest = rest
    with pytest.raises(ConnectorsException):
        cache_controller.purge_cache("http://api-dev.dne.sky.com", "key=api/v1/ta0.bllabd3")
