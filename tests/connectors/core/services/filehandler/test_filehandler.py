# Standard Library
from unittest.mock import Mock, patch

# Third Party Library
import pytest

# DNE Library
from connectors.core.services.filehandler.basehandler import FileHandler
from connectors.core.services.filehandler.exceptions import (
    ColumnParse,
    EncodedFileError,
    FileWriteError,
    TemplateNotFound,
)
from connectors.core.services.filehandler.operations import XlsFileHandler
from connectors.core.services.filehandler.prepare_index import get_indexes
from connectors.core.utils.exceptions import GenericConnectorsException
from connectors.core.utils.helpers import generic_secret

file_content = generic_secret(50)


success_base64_string = generic_secret(8)
base64_string_size_exceed = generic_secret(8)
read_data_1 = {
    "body": {
        "templateName": "DCN_PatchingRequest",
        "fileContent": file_content,
        "fileType": "csv",
    }
}
read_data_2 = {
    "body": {
        "templateName": "",
        "fileContent": file_content,
        "fileType": "xls",
    }
}
read_data_3 = {"body": {"templateName": "", "fileContent": "", "fileType": "csv"}}
read_data_4 = {
    "body": {
        "templateName": "dcnDataParserRulesDbFlagTrue",
        "data_orinetation": "",
        "fileContent": "",
        "fileType": "xls",
    }
}
read_data_5 = {
    "body": {
        "templateName": "dcnDataParserRules",
        "dataOrientation": "row",
        "fileContent": file_content,
        "fileType": "xls",
    }
}
read_data_6 = {
    "body": {"templateName": "dcnDataParserRules", "dataOrientation": "col", "fileContent": "", "fileType": "xls"}
}
read_data_7 = {
    "body": {"templateName": "dcnDataParserRules", "dataOrientation": "col", "fileContent": "", "fileType": "csv"}
}
read_data_8 = {
    "body": {
        "templateName": "dcnDataParserRules",
        "dataOrientation": "row",
        "fileContent": success_base64_string,
        "fileType": "xls",
    }
}
read_data_9 = {
    "body": {
        "templateName": "dcnDataParserRulesFileType",
        "dataOrientation": "row",
        "fileContent": "",
        "fileType": "xls",
    }
}
read_data_10 = {
    "body": {"templateName": "dcnDataParserRules_csv", "dataOrientation": "row", "fileContent": "", "fileType": "csv"}
}
parsed_output = {
    "dataOrientation": "row",
    "sheets": [
        {
            "sections": [
                {
                    "rows": [
                        {
                            "AC / DC": "N/A",
                            "Console": "YES",
                            "Console IP": "NO",
                            "Console baud rate": 115200.0,
                            "Device Names": "sr10.cyasd _RP0",
                            "Machine Room": "N/A",
                            "Switchport": "YES",
                            "Switchport IP": "YES",
                            "col_2": "Suite 1 Rack 2",
                        },
                        {
                            "AC / DC": "N/A",
                            "Console": "YES",
                            "Console IP": "NO",
                            "Console baud rate": 115200.0,
                            "Device Names": "sr10.cyasd _RP1",
                            "Machine Room": "N/A",
                            "Switchport": "YES",
                            "Switchport IP": "YES",
                            "col_2": "Suite 1 Rack 2",
                        },
                        {
                            "AC / DC": "N/A",
                            "Console": "NO",
                            "Console IP": "NO",
                            "Console baud rate": "N/A",
                            "Device Names": "sr10.cyasd _VIP",
                            "Machine Room": "N/A",
                            "Switchport": "NO",
                            "Switchport IP": "YES",
                            "col_2": "Suite 1 Rack 2",
                        },
                        {
                            "AC / DC": "",
                            "Console": "NO",
                            "Console IP": "NO",
                            "Console baud rate": "",
                            "Device Names": "",
                            "Machine Room": "",
                            "Switchport": "NO",
                            "Switchport IP": "NO",
                            "col_2": "",
                        },
                        {
                            "AC / DC": "",
                            "Console": "NO",
                            "Console IP": "NO",
                            "Console baud rate": "",
                            "Device Names": "",
                            "Machine Room": "",
                            "Switchport": "NO",
                            "Switchport IP": "NO",
                            "col_2": "",
                        },
                        {
                            "AC / DC": "",
                            "Console": "NO",
                            "Console IP": "NO",
                            "Console baud rate": "",
                            "Device Names": "",
                            "Machine Room": "",
                            "Switchport": "NO",
                            "Switchport IP": "NO",
                            "col_2": "",
                        },
                        {
                            "AC / DC": "",
                            "Console": "NO",
                            "Console IP": "NO",
                            "Console baud rate": "",
                            "Device Names": "",
                            "Machine Room": "",
                            "Switchport": "NO",
                            "Switchport IP": "NO",
                            "col_2": "",
                        },
                        {
                            "AC / DC": "",
                            "Console": "NO",
                            "Console IP": "NO",
                            "Console baud rate": "",
                            "Device Names": "",
                            "Machine Room": "",
                            "Switchport": "NO",
                            "Switchport IP": "NO",
                            "col_2": "",
                        },
                        {
                            "AC / DC": "",
                            "Console": "NO",
                            "Console IP": "NO",
                            "Console baud rate": "",
                            "Device Names": "",
                            "Machine Room": "",
                            "Switchport": "NO",
                            "Switchport IP": "NO",
                            "col_2": "",
                        },
                        {
                            "AC / DC": "",
                            "Console": "NO",
                            "Console IP": "NO",
                            "Console baud rate": "",
                            "Device Names": "",
                            "Machine Room": "",
                            "Switchport": "NO",
                            "Switchport IP": "NO",
                            "col_2": "",
                        },
                        {
                            "AC / DC": "",
                            "Console": "NO",
                            "Console IP": "NO",
                            "Console baud rate": "",
                            "Device Names": "",
                            "Machine Room": "",
                            "Switchport": "NO",
                            "Switchport IP": "NO",
                            "col_2": "",
                        },
                        {
                            "AC / DC": "",
                            "Console": "NO",
                            "Console IP": "NO",
                            "Console baud rate": "",
                            "Device Names": "",
                            "Machine Room": "",
                            "Switchport": "NO",
                            "Switchport IP": "NO",
                            "col_2": "",
                        },
                    ]
                }
            ],
            "sheet_name": "Request",
        },
        {
            "sections": [
                {
                    "rows": [
                        {
                            "Allocated Console Port": 2.0,
                            "Allocated Console Port IP": "N/A",
                            "Console Location": "N/A",
                            "Console Name": "cm0.cyasd",
                            "Device / Console details": "sr10.cyasd _RP0",
                        },
                        {
                            "Allocated Console Port": 3.0,
                            "Allocated Console Port IP": "N/A",
                            "Console Location": "N/A",
                            "Console Name": "cm0.cyasd",
                            "Device / Console details": "sr10.cyasd _RP1",
                        },
                    ]
                }
            ],
            "sheet_name": "Allocation Console",
        },
        {
            "sections": [
                {
                    "rows": [
                        {
                            "Allocated Switch Port": "Fa0/6",
                            "Allocated Switch Port IP": "10.200.146.10",
                            "Device / Switchport details": "sr10.cyasd _RP0",
                            "Switch Location": "N/A",
                            "Switch Name": "os0.cyasd",
                        },
                        {
                            "Allocated Switch Port": "Fa0/7",
                            "Allocated Switch Port IP": "10.200.146.11",
                            "Device / Switchport details": "sr10.cyasd _RP1",
                            "Switch Location": "N/A",
                            "Switch Name": "os0.cyasd",
                        },
                        {
                            "Allocated Switch Port": "N/A",
                            "Allocated Switch Port IP": "10.200.146.12",
                            "Device / Switchport details": "sr10.cyasd _VIP",
                            "Switch Location": "N/A",
                            "Switch Name": "N/A",
                        },
                    ]
                }
            ],
            "sheet_name": "Allocation Switchport",
        },
    ],
    "templateName": "dcnDataParserRules",
}


@patch(
    "connectors.core.services.filehandler.basehandler.file_store_path",
    "tests/connectors/core/services/filehandler/files/",
)
def test_read():
    with pytest.raises(TemplateNotFound):
        FileHandler(read_data_1).read()

    with pytest.raises(TemplateNotFound):
        FileHandler(read_data_2).read()

    with pytest.raises(TemplateNotFound):
        FileHandler(read_data_3).read()

    with pytest.raises(EncodedFileError):
        FileHandler(read_data_4).read()

    with pytest.raises(EncodedFileError):
        FileHandler(read_data_5).read()

    with pytest.raises(ColumnParse):
        FileHandler(read_data_6).read()

    with pytest.raises(TemplateNotFound):
        FileHandler(read_data_7).read()

    with pytest.raises(TemplateNotFound):
        FileHandler(read_data_9).read()

    with pytest.raises(GenericConnectorsException):
        FileHandler(read_data_10).read()


file_size_exceed_input_xls = {
    "body": {
        "templateName": "dcnDataParserRules",
        "dataOrientation": "row",
        "fileType": "xls",
        "fileContent": base64_string_size_exceed,
    }
}
file_size_exceed_input_xls_data = {
    "body": {
        "templateName": "dcnDataParserRulesDbFlagTrue",
        "dataOrientation": "row",
        "fileType": "xls",
        "fileContent": base64_string_size_exceed,
    }
}
file_size_exceed_input_csv = {
    "body": {
        "templateName": "dcnDataParserRules_csv",
        "dataOrientation": "row",
        "fileType": "csv",
        "fileContent": base64_string_size_exceed,
    }
}


@patch("connectors.core.services.filehandler.basehandler.sys.getsizeof")
@patch(
    "connectors.core.services.filehandler.basehandler.file_store_path",
    "tests/connectors/core/services/filehandler/files/",
)
def test_base_handler_file_size(getsizeof_mock):
    getsizeof_mock.return_value = 10**10
    check_obj_xls = FileHandler(file_size_exceed_input_xls)
    output_xls = check_obj_xls.read()
    assert output_xls != "", "Fail"

    check_obj_csv = FileHandler(file_size_exceed_input_csv)
    output_csv = check_obj_csv.read()
    assert output_csv != "", "Fail"

    check_obj_xls_exce = FileHandler(file_size_exceed_input_xls_data)
    check_obj_xls = check_obj_xls_exce.read()
    assert check_obj_xls != "", "Fail"


def test_prepare_index():
    assert get_indexes("A2", "U6") == ((2, 0), (6, 20)), "Success"
    assert get_indexes("AA1", "RR1") == ((1, 26), (1, 485)), "Success"
    assert get_indexes("C6", "U6") != ((2, 0), (6, 20)), "Failed to get indexes"
    assert get_indexes("H7", "P6") != ((2, 0), (6, 20)), "Failed to get indexes"


call_write_data_1 = {"body": {"templateName": "dcnDataParserRules22", "fileType": "xls", "sheets": []}}
call_write_data_2 = {"body": {"templateName": "patchingDataWriteRulesw", "fileType": "xls", "sheets": []}}
call_write_data_3 = {"body": {"templateName": "patchingDataWriteRulesFileType", "fileType": "xls", "sheets": []}}
write_data_1 = {
    "body": {
        "templateName": "patchingDataWriteRules",
        "fileType": "xls",
        "sheets": [
            {
                "sheetIndex": 0,
                "sections": [
                    {
                        "rows": [
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                                "Port": "RP0 Console",
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                                "Port": "RP1 Console",
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                                "Port": "RP0 Mgmt",
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                                "Port": "RP1 Mgmt",
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "NCS-5508",
                                "Port": "HundredGigE0/3/0/31",
                                "Media": "MM",
                                "Connector": "MPO-12",
                                "Transceiver": "CIS-QSFP-100G-SR4-S",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "NCS-5508",
                                "Port": "HundredGigE0/3/0/31",
                                "Media": "MM",
                                "Connector": "MPO-12",
                                "Transceiver": "CIS-QSFP-100G-SR4-S",
                                "Transmission Port": "LOCAL",
                            },
                        ]
                    },
                    {
                        "rows": [
                            {
                                "Device Vendor": "Lantronix ",
                                "Location": "",
                                "Chassis Model": "N/A",
                                "Port": 2,
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                                "Hostname": "cm0.cyasd.it.isp.sky.com 123",
                            },
                            {
                                "Hostname": "cm1.cyasd.it.isp.sky.com",
                                "Device Vendor": "Lantronix ",
                                "Location": "",
                                "Chassis Model": "N/A",
                                "Port": 4,
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "os7.thlon.it.isp.sky.com",
                                "Device Vendor": "N/A",
                                "Location": "",
                                "Chassis Model": "N/A",
                                "Port": "fa0/2",
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "os7.thlon.it.isp.sky.com",
                                "Device Vendor": "N/A",
                                "Location": "",
                                "Chassis Model": "N/A",
                                "Port": "ge1/2/3",
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "sr10.pomnc.isp.sky.com",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "NCS-5508",
                                "Port": "Fa1/2/1",
                                "Media": "MM",
                                "Connector": "MPO-12",
                                "Transceiver": "CIS-QSFP-100G-SR4-S",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "sr10.pomnc.isp.sky.com",
                                "Device Vendor": "Nokia",
                                "Location": "mimnc",
                                "Chassis Model": "7750-SR12",
                                "Port": "1/2/1",
                                "Media": "MM",
                                "Connector": "MPO-12",
                                "Transceiver": "ALU-SFP-10G-LR",
                                "Transmission Port": "LOCAL",
                            },
                        ]
                    },
                    {
                        "rows": [
                            {"Comments": "ABC"},
                            {"Comments": "BCD"},
                            {"Comments": "XYZ"},
                            {"Comments": "ABC"},
                            {"Comments": "ABC"},
                        ]
                    },
                ],
            }
        ],
    }
}
output = {
    "fileContent": file_content,
    "fileName": "Patching Request Details ver 1.0.xls",
}


@patch("connectors.core.services.filehandler.basehandler.XlsFileHandler")
@patch(
    "connectors.core.services.filehandler.basehandler.file_store_path",
    "tests/connectors/core/services/filehandler/files/",
)
def test_file_write_1(xls_filehandler_mock):
    with pytest.raises(TemplateNotFound):
        FileHandler(call_write_data_1).write()

    with pytest.raises(TemplateNotFound):
        FileHandler(call_write_data_2).write()

    with pytest.raises(TemplateNotFound):
        FileHandler(call_write_data_3).write()

    assert FileHandler(write_data_1).write() == xls_filehandler_mock.return_value.write_xls.return_value


def test_write_2():
    with pytest.raises(TemplateNotFound):
        FileHandler(call_write_data_2).write()


write_data_3 = {"body": {"templateName": "patchingDataWriteRules", "fileType": "csv", "sheets": []}}


def test_write_3():
    with pytest.raises(TemplateNotFound):
        FileHandler(write_data_3).write()


write_data_4 = {
    "body": {
        "templateName": "patchingDataWriteRules",
        "fileType": "xls",
        "sheets": [
            {
                "sheetIndex": 0,
                "sections": [
                    {
                        "rows": [
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                                "Port": "RP0 Console",
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                                "Port": "RP1 Console",
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                                "Port": "RP0 Mgmt",
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                                "Port": "RP1 Mgmt",
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "NCS-5508",
                                "Port": "HundredGigE0/3/0/31",
                                "Media": "MM",
                                "Connector": "MPO-12",
                                "Transceiver": "CIS-QSFP-100G-SR4-S",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "NCS-5508",
                                "Port": "HundredGigE0/3/0/31",
                                "Media": "MM",
                                "Connector": "MPO-12",
                                "Transceiver": "CIS-QSFP-100G-SR4-S",
                                "Transmission Port": "LOCAL",
                            },
                        ]
                    },
                    {
                        "rows": [
                            {
                                "Device Vendor": "Lantronix ",
                                "Location": "",
                                "Chassis Model": "N/A",
                                "Port": 2,
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                                "Hostname": "cm0.cyasd.it.isp.sky.com 123",
                            },
                            {
                                "Hostname": "cm1.cyasd.it.isp.sky.com",
                                "Device Vendor": "Lantronix ",
                                "Location": "",
                                "Chassis Model": "N/A",
                                "Port": 4,
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "os7.thlon.it.isp.sky.com",
                                "Device Vendor": "N/A",
                                "Location": "",
                                "Chassis Model": "N/A",
                                "Port": "fa0/2",
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "os7.thlon.it.isp.sky.com",
                                "Device Vendor": "N/A",
                                "Location": "",
                                "Chassis Model": "N/A",
                                "Port": "ge1/2/3",
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "sr10.pomnc.isp.sky.com",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "NCS-5508",
                                "Port": "Fa1/2/1",
                                "Media": "MM",
                                "Connector": "MPO-12",
                                "Transceiver": "CIS-QSFP-100G-SR4-S",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "sr10.pomnc.isp.sky.com",
                                "Device Vendor": "Nokia",
                                "Location": "mimnc",
                                "Chassis Model": "7750-SR12",
                                "Port": "1/2/1",
                                "Media": "MM",
                                "Connector": "MPO-12",
                                "Transceiver": "ALU-SFP-10G-LR",
                                "Transmission Port": "LOCAL",
                            },
                        ]
                    },
                    {
                        "rows": [
                            {"Comments": "ABC"},
                            {"Comments": "BCD"},
                            {"Comments": "XYZ"},
                            {"Comments": "ABC"},
                            {"Comments": "ABC"},
                        ]
                    },
                ],
            }
        ],
    }
}


@patch("connectors.core.services.filehandler.basehandler.XlsFileHandler")
@patch(
    "connectors.core.services.filehandler.basehandler.file_store_path",
    "tests/connectors/core/services/filehandler/files/",
)
def test_write_4(xls_filehandler_mock):
    assert FileHandler(write_data_4).write() == xls_filehandler_mock.return_value.write_xls.return_value


body = {}


def test_xls_file_handler_instance():
    xls_obj = XlsFileHandler(body)
    assert isinstance(xls_obj, XlsFileHandler)
    assert xls_obj.file_content is None
    assert xls_obj.file_name is None
    assert xls_obj.data_orientation == "row"
    assert xls_obj.rules_schema is None
    assert xls_obj.data_input != ""
    assert xls_obj.workbook != ""


def test_read_operation_case1():
    with pytest.raises(ColumnParse):
        xls_obj = XlsFileHandler(body)
        xls_obj.data_orientation = "col"
        xls_obj.read_xls()


def test_read_operation_case2():
    with pytest.raises(ColumnParse):
        xls_obj = XlsFileHandler(body)
        xls_obj.data_orientation = ""
        xls_obj.read_xls()


write_rule_schema = {
    "fileType": "xls",
    "fileName": "Patching Request Details ver 1.0.xls",
    "sheets": [
        {
            "sheetIndex": 0,
            "sections": [
                {"merged": "No", "startIndex": "C3", "endIndex": "K10"},
                {"merged": "No", "startIndex": "L3", "endIndex": "T10"},
                {"merged": "No", "startIndex": "U3", "endIndex": "U10"},
            ],
        }
    ],
}


def test_write_operation_case3():
    with pytest.raises(FileWriteError):
        xls_obj = XlsFileHandler(body)
        xls_obj.workbook = ""
        xls_obj.rules_schema = write_rule_schema
        xls_obj.write_xls()


test_write_data_4 = {"body": {"templateName": "patchingDataWriteRules", "fileType": "xls", "sheets": []}}


def test_write_operation_case4():
    with pytest.raises(FileWriteError):
        xls_obj = XlsFileHandler(test_write_data_4)
        xls_obj.workbook = ""
        xls_obj.rules_schema = write_rule_schema
        xls_obj.write_xls()


test_write_data_5 = {
    "body": {"templateName": "patchingDataWriteRules", "fileType": "xls", "sheets": [{"sheetIndex": 0, "sections": []}]}
}


def test_write_operation_case5():
    with pytest.raises(FileWriteError):
        xls_obj = XlsFileHandler(test_write_data_5)
        xls_obj.workbook = ""
        xls_obj.rules_schema = write_rule_schema
        xls_obj.write_xls()


test_write_data_6 = {
    "body": {"templateName": "patchingDataWriteRules", "fileType": "xls", "sheets": [{"sections": []}]}
}


def test_write_operation_case6():
    with pytest.raises(FileWriteError):
        xls_obj = XlsFileHandler(test_write_data_6)
        xls_obj.workbook = ""
        xls_obj.rules_schema = write_rule_schema
        xls_obj.write_xls()


test_write_data_7 = {
    "body": {"templateName": "patchingDataWriteRules", "fileType": "xls", "sheets": [{"sheetIndex": 4, "sections": []}]}
}


def test_write_operation_case7():
    with pytest.raises(FileWriteError):
        xls_obj = XlsFileHandler(test_write_data_7)
        xls_obj.workbook = ""
        xls_obj.rules_schema = write_rule_schema
        xls_obj.write_xls()


test_write_data_8 = {
    "body": {
        "templateName": "patchingDataWriteRules",
        "fileType": "xls",
        "sheets": [
            {
                "sheetIndex": 4,
                "sections": [
                    {
                        "row": [
                            {
                                "B-End": {
                                    "Hostname": "br0.pafw1",
                                    "Device Model": "Huawei CX600-X8A",
                                    "Location": "PAFW1",
                                    "Chassis/Card/Slot": "LPUI-480 (CR5D00E4NB70)",
                                    "Port": "100GE1/0/0",
                                    "Media": "",
                                    "Connector": "",
                                    "Transceiver": "QSFP-100G-SR4-S",
                                    "Transmission Port": "LOCAL",
                                },
                                "comments": "Some string 34",
                            }
                        ]
                    }
                ],
            }
        ],
    }
}


def test_write_operation_case8():
    with pytest.raises(FileWriteError):
        xls_obj = XlsFileHandler(test_write_data_8)
        xls_obj.workbook = ""
        xls_obj.rules_schema = write_rule_schema
        xls_obj.write_xls()


test_write_data_9 = {
    "body": {
        "templateName": "patchingDataWriteRules",
        "fileType": "xls",
        "sheets": [{"sheetIndex": 4, "sections": [{"row": [{}]}]}],
    }
}


def test_write_operation_case9():
    with pytest.raises(FileWriteError):
        xls_obj = XlsFileHandler(test_write_data_9)
        xls_obj.workbook = ""
        xls_obj.rules_schema = write_rule_schema
        xls_obj.write_xls()


read_rules_schema = {
    "fileType": "xls",
    "sheets": [
        {"sheetIndex": 0, "sections": [{"startIndex": "A22", "endIndex": "I34", "headerFlag": True}]},
        {"sheetIndex": 1, "sections": [{"startIndex": "A2", "endIndex": "E8", "headerFlag": True}]},
        {"sheetIndex": 2, "sections": [{"startIndex": "A2", "endIndex": "E8", "headerFlag": True}]},
    ],
    "dbStorageFlag": False,
}


def test_read_operation_case4():
    with pytest.raises(EncodedFileError):
        xls_obj = XlsFileHandler(read_data_8)
        xls_obj.rules_schema = read_rules_schema
        xls_obj.read_xls()


@patch("connectors.core.services.filehandler.operations.xlrd")
def test_read_operation_case5(xlrd):
    workbook_mock = Mock()
    xlrd.open_workbook.return_value = workbook_mock
    workbook_mock.sheet_names.return_value = ["sheet1", "sheet2", "sheet3"]
    xls_obj = XlsFileHandler(read_data_8)
    xls_obj.file_content = generic_secret(8)
    xls_obj.file_name = "dcnDataParserRules"
    xls_obj.data_orientation = "row"
    xls_obj.rules_schema = read_rules_schema
    return_success = xls_obj.read_xls()
    assert return_success != ""


read_rules_schema_data = {
    "fileType": "xls",
    "sheets": [
        {"sheetIndex": 0, "sections": [{"startIndex": "A22", "endIndex": "I34", "headerFlag": True}]},
        {
            "sheetIndex": 1,
            "sections": [
                {"startIndex": "A2", "endIndex": "E8", "headerFlag": True},
                {"startIndex": "A9", "endIndex": "E16", "headerFlag": True, "SectionFormat": "Merged"},
            ],
        },
        {"sheetIndex": 2, "sections": [{"startIndex": "A2", "endIndex": "E8", "headerFlag": True}]},
    ],
    "dbStorageFlag": False,
}


def test_read_operation_case6():
    with pytest.raises(EncodedFileError):
        xls_obj = XlsFileHandler(read_data_8)
        xls_obj.file_content = success_base64_string
        xls_obj.file_name = "dcnDataParserRules"
        xls_obj.data_orientation = "row"
        xls_obj.rules_schema = read_rules_schema_data
        return_success = xls_obj.read_xls()
        assert return_success != ""


error_base64_string = "xyz"


def test_read_operation_case7():
    with pytest.raises(EncodedFileError):
        xls_obj = XlsFileHandler(read_data_8)
        xls_obj.file_content = error_base64_string
        xls_obj.file_name = "dcnDataParserRules"
        xls_obj.data_orientation = "row"
        xls_obj.rules_schema = read_rules_schema_data
        return_success = xls_obj.read_xls()
        assert return_success != ""


read_rules_schema_data_head_false = {
    "fileType": "xls",
    "sheets": [
        {"sheetIndex": 0, "sections": [{"startIndex": "A22", "endIndex": "I34", "headerFlag": False}]},
        {
            "sheetIndex": 1,
            "sections": [
                {"startIndex": "A2", "endIndex": "E8", "headerFlag": True},
                {"startIndex": "A9", "endIndex": "E16", "headerFlag": True, "SectionFormat": "Merged"},
            ],
        },
        {"sheetIndex": 2, "sections": [{"startIndex": "A2", "endIndex": "E8", "headerFlag": True}]},
    ],
    "dbStorageFlag": False,
}


def test_read_operation_case8():
    with pytest.raises(EncodedFileError):
        xls_obj = XlsFileHandler(read_data_8)
        xls_obj.file_content = success_base64_string
        xls_obj.file_name = "dcnDataParserRules"
        xls_obj.data_orientation = "row"
        xls_obj.rules_schema = read_rules_schema_data_head_false
        return_success = xls_obj.read_xls()
        assert return_success != ""


write_data_colum_missing = {
    "body": {
        "templateName": "patchingDataWriteRules",
        "fileType": "xls",
        "sheets": [
            {
                "sheetIndex": 0,
                "sections": [
                    {
                        "rows": [
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                        ]
                    },
                    {
                        "rows": [
                            {
                                "Device Vendor": "Lantronix 12",
                                "Location": "",
                                "Chassis Model": "N/A",
                                "Port": 2,
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                                "Hostname": "cm0.cyasd.it.isp.sky.com 123",
                            },
                            {
                                "Hostname": "cm1.cyasd.it.isp.sky.com",
                                "Device Vendor": "Lantronix ",
                                "Location": "",
                                "Chassis Model": "N/A",
                                "Port": 4,
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "os7.thlon.it.isp.sky.com",
                                "Device Vendor": "N/A",
                                "Location": "",
                                "Chassis Model": "N/A",
                                "Port": "fa0/2",
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "os7.thlon.it.isp.sky.com",
                                "Device Vendor": "N/A",
                                "Location": "",
                                "Chassis Model": "N/A",
                                "Port": "ge1/2/3",
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "sr10.pomnc.isp.sky.com",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "NCS-5508",
                                "Port": "Fa1/2/1",
                                "Media": "MM",
                                "Connector": "MPO-12",
                                "Transceiver": "CIS-QSFP-100G-SR4-S",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "sr10.pomnc.isp.sky.com",
                                "Device Vendor": "Nokia",
                                "Location": "mimnc",
                                "Chassis Model": "7750-SR12",
                                "Port": "1/2/1",
                                "Media": "MM",
                                "Connector": "MPO-12",
                                "Transceiver": "ALU-SFP-10G-LR",
                                "Transmission Port": "LOCAL",
                            },
                        ]
                    },
                    {
                        "rows": [
                            {"Comments": "ABC"},
                            {"Comments": "BCD"},
                            {"Comments": "XYZ"},
                            {"Comments": "ABC"},
                            {"Comments": "ABC"},
                        ]
                    },
                ],
            }
        ],
    }
}
write_data_output = {
    "fileContent": file_content,
    "fileName": "Patching Request Details ver 1.0.xls",
}
read_rules_schema_colum = {
    "fileType": "xls",
    "fileName": "Patching Request Details ver 1.0.xls",
    "sheets": [
        {
            "sheetIndex": 0,
            "sections": [
                {"merged": False, "startIndex": "C3", "endIndex": "K20"},
                {"merged": False, "startIndex": "L3", "endIndex": "T20"},
                {"merged": False, "startIndex": "U3", "endIndex": "U20"},
            ],
        }
    ],
}


@patch(
    "connectors.core.services.filehandler.basehandler.file_store_path",
    "tests/connectors/core/services/filehandler/files/",
)
def test_write_operation_case10():
    assert FileHandler(write_data_colum_missing).write() != write_data_output, "Fail"


write_data_another_section = {
    "body": {
        "templateName": "patchingDataWriteRules",
        "fileType": "xls",
        "sheets": [
            {
                "sheetIndex": 0,
                "sections": [
                    {
                        "rows": [
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                        ]
                    },
                    {
                        "rows": [
                            {
                                "Device Vendor": "Lantronix 12",
                                "Location": "",
                                "Chassis Model": "N/A",
                                "Port": 2,
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                                "Hostname": "cm0.cyasd.it.isp.sky.com 123",
                            },
                            {
                                "Hostname": "cm1.cyasd.it.isp.sky.com",
                                "Device Vendor": "Lantronix ",
                                "Location": "",
                                "Chassis Model": "N/A",
                                "Port": 4,
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "os7.thlon.it.isp.sky.com",
                                "Device Vendor": "N/A",
                                "Location": "",
                                "Chassis Model": "N/A",
                                "Port": "fa0/2",
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "os7.thlon.it.isp.sky.com",
                                "Device Vendor": "N/A",
                                "Location": "",
                                "Chassis Model": "N/A",
                                "Port": "ge1/2/3",
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "sr10.pomnc.isp.sky.com",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "NCS-5508",
                                "Port": "Fa1/2/1",
                                "Media": "MM",
                                "Connector": "MPO-12",
                                "Transceiver": "CIS-QSFP-100G-SR4-S",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "sr10.pomnc.isp.sky.com",
                                "Device Vendor": "Nokia",
                                "Location": "mimnc",
                                "Chassis Model": "7750-SR12",
                                "Port": "1/2/1",
                                "Media": "MM",
                                "Connector": "MPO-12",
                                "Transceiver": "ALU-SFP-10G-LR",
                                "Transmission Port": "LOCAL",
                            },
                        ]
                    },
                    {
                        "rows": [
                            {"Comments": "ABC"},
                            {"Comments": "BCD"},
                            {"Comments": "XYZ"},
                            {"Comments": "ABC"},
                            {"Comments": "ABC"},
                        ]
                    },
                    {
                        "rows": [
                            {"Comments": "ABC"},
                            {"Comments": "BCD"},
                            {"Comments": "XYZ"},
                            {"Comments": "ABC"},
                            {"Comments": "ABC"},
                        ]
                    },
                ],
            }
        ],
    }
}
write_data_another_section_output = {
    "fileContent": file_content,
    "fileName": "Patching Request Details ver 1.0.xls",
}


@patch(
    "connectors.core.services.filehandler.basehandler.file_store_path",
    "tests/connectors/core/services/filehandler/files/",
)
def test_write_operation_case11():
    assert FileHandler(write_data_another_section).write() != write_data_another_section_output, "Fail"


write_data_row_limit_exceed_data = {
    "body": {
        "templateName": "patchingDataWriteRules",
        "fileType": "xls",
        "sheets": [
            {
                "sheetIndex": 0,
                "sections": [
                    {
                        "rows": [
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                            {
                                "Hostname": "ta0.tost1.it.isp.sky.com 11",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "N/A",
                            },
                        ]
                    },
                    {
                        "rows": [
                            {
                                "Device Vendor": "Lantronix 12",
                                "Location": "",
                                "Chassis Model": "N/A",
                                "Port": 2,
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                                "Hostname": "cm0.cyasd.it.isp.sky.com 123",
                            },
                            {
                                "Hostname": "cm1.cyasd.it.isp.sky.com",
                                "Device Vendor": "Lantronix ",
                                "Location": "",
                                "Chassis Model": "N/A",
                                "Port": 4,
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "os7.thlon.it.isp.sky.com",
                                "Device Vendor": "N/A",
                                "Location": "",
                                "Chassis Model": "N/A",
                                "Port": "fa0/2",
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "os7.thlon.it.isp.sky.com",
                                "Device Vendor": "N/A",
                                "Location": "",
                                "Chassis Model": "N/A",
                                "Port": "ge1/2/3",
                                "Media": "Copper",
                                "Connector": "RJ45",
                                "Transceiver": "N/A",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "sr10.pomnc.isp.sky.com",
                                "Device Vendor": "Cisco",
                                "Location": "mimnc",
                                "Chassis Model": "NCS-5508",
                                "Port": "Fa1/2/1",
                                "Media": "MM",
                                "Connector": "MPO-12",
                                "Transceiver": "CIS-QSFP-100G-SR4-S",
                                "Transmission Port": "LOCAL",
                            },
                            {
                                "Hostname": "sr10.pomnc.isp.sky.com",
                                "Device Vendor": "Nokia",
                                "Location": "mimnc",
                                "Chassis Model": "7750-SR12",
                                "Port": "1/2/1",
                                "Media": "MM",
                                "Connector": "MPO-12",
                                "Transceiver": "ALU-SFP-10G-LR",
                                "Transmission Port": "LOCAL",
                            },
                        ]
                    },
                    {
                        "rows": [
                            {"Comments": "ABC"},
                            {"Comments": "BCD"},
                            {"Comments": "XYZ"},
                            {"Comments": "ABC"},
                            {"Comments": "ABC"},
                        ]
                    },
                    {
                        "rows": [
                            {"Comments": "ABC"},
                            {"Comments": "BCD"},
                            {"Comments": "XYZ"},
                            {"Comments": "ABC"},
                            {"Comments": "ABC"},
                        ]
                    },
                ],
            }
        ],
    }
}
write_data_row_limit_exceed_data_output = {
    "fileContent": file_content,
    "fileName": "Patching Request Details ver 1.0.xls",
}


@patch(
    "connectors.core.services.filehandler.basehandler.file_store_path",
    "tests/connectors/core/services/filehandler/files/",
)
def test_write_operation_case12():
    assert FileHandler(write_data_row_limit_exceed_data).write() != write_data_row_limit_exceed_data_output, "Fail"
