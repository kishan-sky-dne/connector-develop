# Standard Library
import logging

# Third Party Library
import connexion
from minio.error import S3Error

# DNE Library
from connectors.core.utils.minio_manager import MinioManager

logger = logging.getLogger(__name__)


def upload_files(**kwargs: dict) -> dict[str, str]:
    """
    Uploads files to the specified bucket in MinIO storage.
    kwargs:
        bucketName(string): Name of the bucket to upload files
        objectName(string): Name of the file
        objectContent(string): The file content to be uploaded, encoded in base64.
        isCompressionNeeded(bool): Compress the object content before uploading if set to true.
                                   otherwise, upload without compression. The default value is true.
    Returns:
        dict: success or failure response
    """
    payload: dict = kwargs["body"]
    logger.info(f"Uploading the file {payload['objectName']} to bucket name {payload['bucketName']} in MinIO")
    try:
        minio_manager: MinioManager = MinioManager()
        data: dict = connexion.request.files.to_dict()
        object_content: str = data["objectContent"].read()
        minio_manager.write_data(
            bucket_name=payload["bucketName"],
            object_key=payload["objectName"],
            data=object_content,
            is_compression_needed=payload.get("isCompressionNeeded", True),
        )
        logger.info(
            f"Successfully uploaded the file {payload['objectName']} to bucket name {payload['bucketName']} in MinIO"
        )
        return {"status": "SUCCESS"}
    except S3Error as err:
        logger.exception(
            f"S3Error occurred while uploading file {payload['objectName']} to bucket {payload['bucketName']}"
            f" in MinIO due to {err}"
        )
        return {
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-020-999-1001",
                    "message": f"Unable to upload file {payload['objectName']} to MinIO bucket {payload['bucketName']}"
                    f" due to {err}",
                }
            ],
        }
    except Exception as err:
        logger.exception(
            f"{err.__class__.__name__} occurred while uploading file {payload['objectName']}"
            f" to bucket {payload['bucketName']} in MinIO due to {err}"
        )
        return {
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-020-999-1002",
                    "message": f"{err.__class__.__name__} occurred while uploading file {payload['objectName']}"
                    f" to MinIO bucket {payload['bucketName']} due to {err}",
                }
            ],
        }
