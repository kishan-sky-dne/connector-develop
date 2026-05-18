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
import datetime
import logging
import threading
from typing import Any

# Third Party Library
from minio.commonconfig import Tags

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.exceptions import ConnectorsException
from connectors.core.services.dcs.connector import DeviceConfigurationService
from connectors.core.utils.minio_manager import MinioManager

logger = logging.getLogger(__name__)


class CacheController:
    def __init__(self):
        """
        Initializes DCS CacheController.
        filter_function_mapper can be updated to support new filters.
        """
        logger.info("Initializing DCS CacheController")
        self.minio = MinioManager()
        self.dcs = DeviceConfigurationService(
            hostname=None,
            username=config.get(section="cauth", key="username"),
            password=config.get(section="cauth", key="password"),
        )
        self.bucket_name = config.get(section="dcs", key="minio_bucket_name")
        self.object_key = config.get(section="dcs", key="minio_object_key")
        self.cache_limit_seconds = int(config.get(section="dcs", key="cache_limit_seconds"))
        self.filter_function_mapper = {
            "filter_by_hostname": self.filter_by_hostname,
        }

    def get_filtered_devices(self, filtering_mechanism: str, **params) -> Any:
        """
        Filters devices using the selected filtering function and given parameters.
        Updates the object in the MinIO bucket if not exists or its last modified date is over 'cache_limit_seconds'

        Args:
            filtering_mechanism: The key that maps to desired filtering function
            params: Any parameters to be used in filtering function

        Returns:
            Filtered devices. Its type depends on the selected filtering function.
        """
        logger.debug(
            f"Getting filtered_devices with '{filtering_mechanism}' filtering_mechanism and '{params}' paramters"
        )
        all_devices = self.minio.read_data(self.bucket_name, self.object_key)
        if not all_devices:
            logger.debug(
                f"Failed to read object '{self.object_key}' in bucket '{self.bucket_name}'. "
                "Calling DCS to get all devices"
            )
            all_devices = self._remove_rev(self.dcs.all_devices())
            self._run_minio_thread(all_devices=all_devices)

        elif datetime.datetime.now() - self.minio.minio_client.stat_object(
            self.bucket_name, self.object_key
        ).last_modified.replace(tzinfo=None) > datetime.timedelta(seconds=self.cache_limit_seconds):
            logger.debug(
                f"Object '{self.object_key}' in bucket '{self.bucket_name}' will be updated "
                f"as it was modified over '{self.cache_limit_seconds}' seconds ago"
            )
            self._run_minio_thread()

        filter_function = self.filter_function_mapper.get(filtering_mechanism)
        logger.debug(f"Calling the selected filtering function '{filter_function}'")
        return filter_function(all_devices, **params)

    def _update_minio(self, data: list[dict] = None):
        """
        Updates the MinIO object with given data only if it is not being updated already.
        Data will be fetched using dcs.all_devices call if not given.
        """
        if self._is_minio_object_locked != "True":
            logger.debug(
                f"'{self.object_key}' object in MinIO '{self.bucket_name}' bucket is currently not being updated."
                " Starting update process."
            )
            tags = Tags.new_object_tags()
            self._set_locked_tag("True", tags)
            try:
                if not data:
                    logger.debug("Calling DCS all devices to get updated results")
                    data = self._remove_rev(self.dcs.all_devices())
                logger.debug(f"Updating the MinIO bucket '{self.bucket_name}' object {self.object_key}")
                self.minio.write_data(bucket_name=self.bucket_name, object_key=self.object_key, data=data)
            except Exception as err:
                logger.error(
                    f"Failed to update '{self.object_key}' object in MinIO '{self.bucket_name}'. "
                    f"Future readings may be inaccurate. {err.args[0]}"
                )
            finally:
                self._set_locked_tag("False", tags)
        else:
            logger.debug(f"'{self.object_key}' object in MinIO '{self.bucket_name}' bucket is already being updated.")

    def _set_locked_tag(self, lock: str, tags: dict):
        """
        Sets "locked" object tags
        """
        tags["locked"] = lock
        logger.debug(
            "Setting the tag 'locked' "
            f"for '{self.object_key}' object in MinIO '{self.bucket_name}' to '{tags['locked']}'."
        )
        self.minio.minio_client.set_object_tags(bucket_name=self.bucket_name, object_name=self.object_key, tags=tags)

    def filter_by_hostname(self, all_devices: list[dict], hostname: str) -> list[dict[str, str]]:
        """
        Filters given 'all_devices' and returns those with given 'hostname' in their hostname field
        """
        logger.debug(f"Filtering devices to fetch those with '{hostname}' in their hostnames ")
        return [device for device in all_devices if hostname in device.get("hostname")]

    def _remove_rev(self, devices):
        """
        Removes "rev" from devices to keep only "hostname" keys
        """
        for device in devices:
            del device["rev"]
        return devices

    def _run_minio_thread(self, all_devices: list[dict] = None):
        """
        Creates and runs minio_thread.
        """
        if all_devices:
            minio_thread = threading.Thread(
                name="minio_thread", target=self._update_minio, args=(all_devices,), daemon=True
            )
        else:
            minio_thread = threading.Thread(name="minio_thread", target=self._update_minio, daemon=True)
        minio_thread.start()

    @property
    def _is_minio_object_locked(self) -> str:
        """
        Returns MinIO object's 'locked' tag value. False if not set.
        """
        tags = self.minio.minio_client.get_object_tags(bucket_name="dcs", object_name="all_devices")
        is_minio_object_locked = tags.get("locked", "False") if tags else "False"
        logger.debug(f"Property 'is_minio_object_locked' is set to {is_minio_object_locked}")
        return is_minio_object_locked

    def purge_cache(self, base_url: str, key: str) -> bool:
        """
        Purges cache from API gateway for the given hostname after DCS update
        Args:
           base_url(str): base url of api gateway
           key(str): key to be cleared from cache
        Returns:
            status(bool): True/False
        Raises:
            ConnectorsException if cache is not cleared
        """
        logger.info(f"Clearing cache for key {key}")
        response = self.dcs.rest.get(url=f"{base_url}?key={key}")
        logger.debug(f"Cache clear response from API gateway {response._content}")
        if response.status_code != 200:
            raise ConnectorsException(f"Failed to clear API gateway cache due to {response._content}")
        logger.info(f"Cache cleared successfully for key {key}")
        return True
