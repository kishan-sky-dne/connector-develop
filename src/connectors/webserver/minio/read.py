# Standard Library
import logging

# Third Party Library
from minio.error import S3Error

# DNE Library
from connectors.core.utils.minio_manager import MinioManager

logger = logging.getLogger(__name__)


def get_file_names(**kwargs: dict) -> dict[str, list | str]:
    """
    Method to get file names from minio
    Kwargs:
        bucketName (str): minio bucket to get file
        orderId(str): orderId from where object name which need to get file names from minio
    Returns:
        response(dict): response of file names from minio
    """
    bucket_name: str = kwargs["bucketName"]
    order_id: str = kwargs["orderId"]
    logger.info(f"Fetching the file names from order {order_id} in bucket name {bucket_name} from MinIO")
    try:
        minio_manager: MinioManager = MinioManager()
        response = minio_manager.get_file_names(bucket_name=bucket_name, order_id=order_id)
        logger.info(
            f"Successfully fetched the file names from order {order_id} in bucket name {bucket_name} from MinIO"
        )
        return response
    except S3Error as err:
        logger.exception(
            f"S3Error occurred while fetching the file names from order {order_id} in bucket {bucket_name}"
            f" in MinIO due to {err}"
        )
        return {
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-020-999-1001",
                    "message": f"Unable to fetch file names from order {order_id} in MinIO bucket {bucket_name}"
                    f" due to {err}",
                }
            ],
        }
    except Exception as err:
        logger.exception(
            f"{err.__class__.__name__} occurred while fetching file names from order {order_id} in "
            f"bucket {bucket_name} in MinIO due to {err}"
        )
        return {
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-020-999-1002",
                    "message": f"{err.__class__.__name__} occurred while fetching file names from order {order_id}"
                    f" in MinIO bucket {bucket_name} due to {err}",
                }
            ],
        }


def download_files(**kwargs: dict) -> dict[str, list | str]:
    """
    Method to download file from minio
    Kwargs:
        bucketName (str): minio bucket to download file
        orderId(str): orderId from where object name which need to download from minio
    Returns:
        response(dict): response of file downloaded from minio
    """
    file_name: list = kwargs["filename"]
    bucket_name: str = kwargs["bucketName"]
    logger.info(f"Downloading the log files {file_name} from bucket name {bucket_name} in MinIO")
    try:
        minio_manager: MinioManager = MinioManager()
        response = minio_manager.download_files(file_names=file_name, bucket_name=bucket_name)
        logger.info(f"Successfully downloaded the log files {file_name} from bucket name {bucket_name} in MinIO")
        return response
    except S3Error as err:
        logger.exception(
            f"S3Error occurred while downloading the log files {file_name} from bucket {bucket_name}"
            f" in MinIO due to {err}"
        )
        return {
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-020-999-1001",
                    "message": f"Unable to download files {file_name} from MinIO bucket {bucket_name}" f" due to {err}",
                }
            ],
        }
    except Exception as err:
        logger.exception(
            f"{err.__class__.__name__} occurred while downloading files {file_name} from "
            f"bucket {bucket_name} in MinIO due to {err}"
        )
        return {
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-020-999-1002",
                    "message": f"{err.__class__.__name__} occurred while downloading files {file_name}"
                    f" from MinIO bucket {bucket_name} due to {err}",
                }
            ],
        }
