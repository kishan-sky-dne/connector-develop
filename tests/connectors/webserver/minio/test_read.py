# Standard Library
from unittest.mock import Mock, patch

# Third Party Library
import pytest
from minio import S3Error

# DNE Library
from connectors.webserver.minio.read import download_files, get_file_names

data = {
    "bucketName": "software-update",
    "orderId": "BPM-192982",
}


file_resp = {
    "filenames": [
        "BPM-192982/console-logs_0_RSP1_CPU0_ta0_bllabd3_732v6_to_732v5_TS_2024_09_20-11_57_18.log",
        "BPM-192982/console-logs_0_RSP0_CPU0_ta0_bllabd3_732v6_to_732v5_TS_2024_09_20-11_57_18.log",
    ]
}

get_files_test_cases = (
    {"kwargs": data, "output": file_resp, "minio_response": Mock(return_value=file_resp)},
    {
        "kwargs": data,
        "output": {
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-020-999-1001",
                    "message": "Unable to fetch file names from order BPM-192982 in MinIO bucket software-update"
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
                    "message": "ValueError occurred while fetching file names from order"
                    " BPM-192982 in MinIO bucket software-update due to Error",
                }
            ],
        },
        "minio_response": Mock(side_effect=ValueError("Error")),
    },
)


@pytest.mark.parametrize("params", get_files_test_cases)
@patch("connectors.webserver.minio.read.MinioManager")
def test_get_file_names(minio_mock, params):
    """
    Testcases for fetching file names from minio
    1. success
    2. S3Error
    3. GenericException
    """
    minio_mock.return_value.get_file_names = params["minio_response"]
    response = get_file_names(**params["kwargs"])
    assert response == params["output"]


console_resp = {
    "0/RP0/CPU0": [
        "install replace /harddisk:/upgrade-image/upgrade_732_v5/ncs5500-goldenk9-x-7.3.2-v5.iso noprompt",
        "",
        "",
        "",
        "Thu Sep 19 14:59:05.585 BST",
        "",
    ],
    "0/RP1/CPU0": [
        "install replace /harddisk:/upgrade-image/upgrade_732_v5/ncs5500-goldenk9-x-7.3.2-v5.iso noprompt",
        "",
        "",
        "",
        "Thu Sep 19 14:59:05.585 BST",
        "",
    ],
    "status": "SUCCESS",
}

data_1 = {
    "bucketName": "software-update",
    "filename": ["0/RP0/CPU0", "0/RP1/CPU0"],
}

download_files_test_cases = (
    {"kwargs": data_1, "output": console_resp, "minio_response": Mock(return_value=console_resp)},
    {
        "kwargs": data_1,
        "output": {
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-020-999-1001",
                    "message": "Unable to download files ['0/RP0/CPU0', '0/RP1/CPU0'] from MinIO bucket"
                    " software-update due to S3 operation failed; code: 1, message: Error, resource: ,"
                    " request_id: , host_id: ",
                }
            ],
        },
        "minio_response": Mock(side_effect=S3Error(1, "Error", "", "", "", "")),
    },
    {
        "kwargs": data_1,
        "output": {
            "errorCategory": "FAILED",
            "errors": [
                {
                    "code": "ERR-020-999-1002",
                    "message": "ValueError occurred while downloading files ['0/RP0/CPU0', '0/RP1/CPU0']"
                    " from MinIO bucket software-update due to Error",
                }
            ],
        },
        "minio_response": Mock(side_effect=ValueError("Error")),
    },
)


@pytest.mark.parametrize("params", download_files_test_cases)
@patch("connectors.webserver.minio.read.MinioManager")
def test_download_files(minio_mock, params):
    """
    Testcases for downloading files to minio
    1. success
    2. S3Error
    3. GenericException
    """
    minio_mock.return_value.download_files = params["minio_response"]
    response = download_files(**params["kwargs"])
    assert response == params["output"]
