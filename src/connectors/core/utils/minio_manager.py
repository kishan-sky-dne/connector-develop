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
import json
import logging
from typing import Any

# Third Party Library
import urllib3
import zstd
from minio import Minio
from minio.error import S3Error

# DNE Library
from connectors.core.config.connectors_config import config

logger = logging.getLogger(__name__)

endpoint = config.get(section="minio", key="endpoint")
access_key = config.get(section="minio", key="access_key")
secret_key = config.get(section="minio", key="secret_key")
ca_cert_path = config.get(section="internals", key="ca_certs")


class MinioManager:
    def __init__(self):
        """
        Initializes a MinIO client with the configuration specified in environment variables.
        """
        logger.info("Initializing MinIO Manager")
        http_client = urllib3.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=ca_cert_path)
        self.minio_client = Minio(
            endpoint=endpoint, access_key=access_key, secret_key=secret_key, http_client=http_client
        )

    def write_data(self, bucket_name: str, object_key: str, data: Any, **kwargs: dict) -> None:
        """
        Writes data to MinIO.
        Given data (Python object) is serialized and compressed before being stored.

        Args:
            bucket_name: The name of the bucket in MinIO
            object_key: The key of the object in the bucket
            data: Data to be stored
        Returns:
            None
        Raises:
            S3Error
        """
        logger.info(f"Creating object '{object_key}' in bucket '{bucket_name}'.")
        object_content: bytes = data if isinstance(data, bytes) else json.dumps(data).encode()
        compressed_data: bytes = (
            zstd.compress(object_content) if kwargs.get("is_compression_needed", True) else object_content
        )
        data_io = io.BytesIO(compressed_data)
        try:
            self.minio_client.put_object(
                bucket_name=bucket_name, object_name=object_key, data=data_io, length=len(compressed_data)
            )
            logger.debug(f"Object '{object_key}' created successfully in bucket '{bucket_name}'.")
        except S3Error as e:
            logger.exception(f"Exception while creating object: '{object_key}' in bucket: '{bucket_name}'. {e}")
            raise

    def read_data(self, bucket_name: str, object_key: str) -> Any:
        """
        Reads data from MinIO.
        Fetched data is then decompressed and deserialized.

        Args:
            bucket_name: The name of the bucket in MinIO
            object_key: The key of the object in the bucket
        Returns:
            Processed data. None, if exception occurs
        """
        logger.info(f"Reading object '{object_key}' in bucket '{bucket_name}'.")
        try:
            response = self.minio_client.get_object(bucket_name=bucket_name, object_name=object_key)
            logger.debug(f"Object '{object_key}' in bucket '{bucket_name}' successfully read.")
            return json.loads(zstd.decompress(response.read()))
        except S3Error as e:
            logger.exception(f"Exception while reading data from object: {object_key} bucket: {bucket_name}. {e}")
            return None

    def get_file_names(self, bucket_name: str, order_id: str) -> dict[str, list]:
        """
        Get file names from MinIO.
        Args:
            bucket_name: The name of the bucket in MinIO
            order_id: The order id in the bucket
        Returns:
            list of file names fetched from minio
        """
        try:
            logger.info(f"Fetching file names in '{order_id}' from bucket '{bucket_name}'.")
            objects = self.minio_client.list_objects(bucket_name, order_id, recursive=True)
            file_name_list: list = []
            object_list = sorted(objects, key=lambda a: a._last_modified, reverse=False)
            for obj in object_list:
                obj_value = obj.__dict__
                file_name_list.append(obj_value["_object_name"])
            logger.info(f"File names in '{order_id}' from minio bucket '{bucket_name}' successfully Fetched.")
            return {"filenames": file_name_list}

        except S3Error as e:
            logger.exception(f"Exception while reading file names from object: {order_id} bucket: {bucket_name}. {e}")
            return None

    def download_files(self, bucket_name: str, file_names: list) -> dict[str, str | list]:
        """
        Download logs data from MinIO.
        Args:
            bucket_name: The name of the bucket in MinIO
            file_name: file name to be downloaded from minio
        Returns:
            Processed data. None, if exception occurs
        """
        try:
            logger.info(f"Downloading files '{file_names}' from bucket '{bucket_name}'.")
            final_response: dict = {}
            for file_name in file_names:
                response = self.minio_client.get_object(bucket_name=bucket_name, object_name=file_name)
                # Read the file in chunks of 32KB
                logs_list: list = []
                for line in response.stream(32 * 2048):
                    logs_list.extend(line.decode("utf-8").splitlines())
                final_response |= {file_name: logs_list}
            logger.info(f"Log file names '{file_names}' from minio bucket '{bucket_name}' successfully downloaded.")
            final_response |= {"status": "SUCCESS"}
            return final_response

        except S3Error as e:
            logger.exception(f"Exception while reading data from object: {file_names} bucket: {bucket_name}. {e}")
            return None
