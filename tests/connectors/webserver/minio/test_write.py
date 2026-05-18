# Standard Library
import io
import os
from unittest.mock import Mock, patch

# Third Party Library
import flask
import pytest
from minio import S3Error
from werkzeug.datastructures import FileStorage

# DNE Library
from connectors.webserver.minio.write import upload_files

app = flask.Flask(__name__)
abs_dir = os.path.abspath(os.path.dirname(__file__))
test_file = "test_console_data".encode(encoding="utf-8")

data = {
    "body": {
        "bucketName": "software-update",
        "objectName": "console.log",
        "isCompressionNeeded": False,
    },
    "objectContent": FileStorage(open(f"{abs_dir}/../../../../requirements.txt", "r")),
}

upload_files_test_cases = (
    {"kwargs": data, "output": {"status": "SUCCESS"}, "minio_response": Mock(return_value="")},
    {
        "kwargs": data,
        "output": {
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-020-999-1001",
                    "message": "Unable to upload file console.log to MinIO bucket software-update"
                    " due to S3 operation failed; code: 1, message: Error, resource: ,"
                    " request_id: , host_id: ",
                }
            ],
        },
        "minio_response": Mock(side_effect=S3Error(1, "Error", "", "", "", "")),
    },
    {
        "kwargs": data,
        "output": {
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-020-999-1002",
                    "message": "ValueError occurred while uploading file console.log "
                    "to MinIO bucket software-update due to Error",
                }
            ],
        },
        "minio_response": Mock(side_effect=ValueError("Error")),
    },
)


@pytest.mark.parametrize("params", upload_files_test_cases)
@patch("connectors.webserver.minio.write.MinioManager")
def test_upload_files(minio_mock, params):
    """
    Testcases for uploading files to minio
    1. success
    2. S3Error
    3. GenericException
    """
    with app.test_request_context(
        method="POST",
        data={
            "objectContent": FileStorage(
                stream=io.BytesIO(test_file),
                content_type="application/octet-stream",
                filename="console.log",
            )
        },
        content_type="multipart/form-data",
    ):
        minio_mock.return_value.write_data = params["minio_response"]
        response = upload_files(**params["kwargs"])
        assert response == params["output"]
