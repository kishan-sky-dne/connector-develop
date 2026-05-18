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
import base64
import logging
import tempfile

# Third Party Library
import xlrd
import xlwt
from xlutils.copy import copy

# DNE Library
from connectors.core.services.filehandler.exceptions import ColumnParse, EncodedFileError, FileWriteError
from connectors.core.services.filehandler.prepare_index import get_indexes
from connectors.core.utils.exceptions import GenericConnectorsException

borders = xlwt.Borders()  # Create Borders
borders.left = xlwt.Borders.THIN
borders.right = xlwt.Borders.THIN
borders.top = xlwt.Borders.THIN
borders.bottom = xlwt.Borders.THIN
borders.left_colour = 0x40
borders.right_colour = 0x40
borders.top_colour = 0x40
borders.bottom_colour = 0x40
style = xlwt.XFStyle()  # Create Style
style.borders = borders  # Add Borders to Style
logger = logging.getLogger(__name__)


class XlsFileHandler:
    def __init__(self, data):
        self.file_name = data.get("templateName")
        self.file_content = data.get("fileContent")
        self.data_orientation = data.get("dataOrientation", "row")
        self.rules_schema = data.get("rules_schema")
        self.data_input = data
        self.workbook = data.get("workbook")

    def read_xls(self):  # noqa: C901
        """
        Reading xls file
        :return:
        """
        if self.data_orientation == "row":
            sheets = {"templateName": self.file_name, "dataOrientation": self.data_orientation, "sheets": []}
            try:
                workbook = xlrd.open_workbook(file_contents=base64.decodebytes(bytes(self.file_content, "utf-8")))
                logger.info(f"File have been opened successfully")
            except:  # noqa:802
                logger.error(f"File contents are not matching with the rules or wrong file uploaded.")
                raise EncodedFileError("File contents are not matching with the rules or wrong file uploaded.")

            try:
                sheet_names = workbook.sheet_names()
                if not sheet_names:
                    logger.error(f"File contents are not matching with the rules or wrong file uploaded.")
                    raise EncodedFileError("File contents are not matching with the rules or wrong file uploaded.")
                for sheet in self.rules_schema["sheets"]:
                    sheet_index = sheet["sheetIndex"]
                    try:
                        sheet_data = {"sections": [], "sheet_name": sheet_names[sheet_index]}
                    except:  # noqa : N802
                        logger.error(f"File contents are not matching with the rules or wrong file uploaded.")
                        raise EncodedFileError("File contents are not matching with the rules or wrong file uploaded.")
                    for section in sheet["sections"]:
                        start_index, end_index = get_indexes(section["startIndex"], section["endIndex"])
                        logger.info(f"Started reading sheet: {sheet_data['sheet_name']}")
                        output, err = self.read_table(
                            workbook.sheet_by_name(sheet_names[sheet_index]),
                            rows=(start_index[0] - 1, end_index[0]),
                            columns=(start_index[1], end_index[1] + 1),
                            merged=section.get("sectionFormat", None),
                            header=section.get("headerFlag"),
                        )
                        logger.info(f"Completed reading sheet: {sheet_data['sheet_name']}")
                        if err:
                            workbook.release_resources()
                            logger.error(f"Encoded File Error, sheet: {sheet_data['sheet_name']}")
                            raise EncodedFileError(f"Encoded File Error")

                        row = {"rows": output}
                        sheet_data["sections"].append(row)
                    sheets["sheets"].append(sheet_data)

                workbook.release_resources()
                return sheets
            except Exception as err:
                logger.exception(f"Encoded File Error : {err}")
                raise EncodedFileError(f"{err}")
        elif self.data_orientation == "col":
            logger.info("Column wise parsing not in the scope")
            raise ColumnParse("Column wise parsing is not in the scope")
        else:
            logger.info("dataOrientation' value either 'row' or 'col'")
            raise ColumnParse("'dataOrientation' value either 'row' or 'col'")

    @staticmethod  # noqa: C901
    def read_table(work_book_frame, rows, columns, merged, header=True):  # noqa: C901
        """
        Read the table data row wise by taking input as particular row and column, Based on rules
        :param work_book_frame: excel sheets content
        :param rows: contains row start index and end index
        :param columns: contains columns start index and end index.
        :param header: This flag states whether the 1st row considered to have column header information or Not.
                        If flag set to False, Data will be parsed from the 1st row and column name shall be
                        such as "col_0, "col_1" etc..
        :param merged: In the rule book - Section format , if set "Merged", then all the information
                        read in that Section considered as single column data and represented as single cell data.
        :return: Should be each row data
            {
                  "AC / DC": "N/A",
                  "Console": "YES",
                  "Console IP": "NO",
                  "Console baud rate": 115200.0,
                  "Device Names": "sr10.cyasd _RP0",
                  "Machine Room": "N/A",
                  "Rack": "Suite 1 Rack 2",
                  "Switchport": "YES",
                  "Switchport IP": "YES"
            }
        """
        logger.info("Reading row wise")
        lower_row, higher_row = rows
        if merged == "Merged":
            header_val = "Col" + str(lower_row)
            if header:
                cell_data = ""
                try:
                    header_val = work_book_frame.cell_value(lower_row, 0).strip()
                    cell_data = work_book_frame.cell_value(lower_row + 1, 0)
                    return {header_val: cell_data}, None
                except:  # noqa: E722
                    return {header_val: cell_data}, None
            else:
                return {"key": work_book_frame.cell_value(lower_row, 0)}, None
        else:
            content = []
            lower_column, higher_column = columns
            try:
                for index, row in enumerate(range(lower_row, higher_row)):
                    row_empty = True
                    row_content = []
                    for column in range(lower_column, higher_column):
                        value = work_book_frame.cell_value(row, column)
                        if isinstance(value, float) and value.is_integer():
                            value = int(value)
                        if value != "":
                            row_empty = False
                        row_content.append(value)
                    if header and index == 0:
                        content.append(row_content)
                    elif not row_empty:
                        content.append(row_content)
            except Exception as err:
                logger.exception(f"File contents are not matching with the rules or wrong file uploaded.{err}")
                raise EncodedFileError("File contents are not matching with the rules or wrong file uploaded.")
            if header:
                headers = list(map(lambda x: x.strip() if isinstance(x, str) else x, content[0]))
                for index, header_name in enumerate(headers):
                    if header_name == "":
                        headers[index] = f"col_{index}"
                return [{header: data[index] for index, header in enumerate(headers)} for data in content[1:]], None
            return content, None

    def write_xls(self):
        """
        writing xls
        :return:
        """
        try:
            headers_column_map = None
            wb_read = self.workbook
            wb_write = copy(wb_read)  # copy work book for write
            self.workbook.release_resources()
            sheet_names = wb_read.sheet_names()
            for sheet in self.rules_schema.get("sheets"):
                sheet_index = sheet["sheetIndex"]
                try:
                    work_sheet_read = wb_read.sheet_by_name(sheet_names[sheet_index])
                except Exception as err:
                    logger.error(f"Data payload is not matching with the rules and template file. Err: {err}")
                    raise FileWriteError(
                        "Data payload is not matching with the rules and template file." "Please verify input data"
                    )

                for section_index, section in enumerate(sheet["sections"]):
                    start_index, end_index = get_indexes(section["startIndex"], section["endIndex"])

                    headers_column_map = {
                        work_sheet_read.cell_value(start_index[0] - 1, column).strip(): column
                        for column in range(start_index[1], end_index[1] + 1)
                    }
                    try:
                        sheet_frame_write = wb_write.get_sheet(sheet_index)
                    except Exception as err:
                        logger.error(f"Data payload is not matching with the rules and template file. Err: {err}")
                        raise FileWriteError(
                            "Data payload is not matching with the rules and template file." "Please verify input data"
                        )

                    # Section based Info
                    self.modify(
                        sheet_frame_write,
                        rules_sheet_idx=sheet_index,
                        data=self.data_input,
                        rows=(start_index[0] - 1, end_index[0]),
                        rules_section_index=section_index,
                        merged=section["merged"],
                        headers_loc=headers_column_map,
                    )

            temp_file = tempfile.NamedTemporaryFile(mode="rb")
            wb_write.save(temp_file.name)
            encoded_data = base64.b64encode(temp_file.read()).decode("utf-8")
            temp_file.close()
            logger.info("Completed writing file")
            return {"fileName": self.rules_schema.get("fileName"), "fileContent": str(encoded_data)}
        except Exception as err:
            logger.exception(f"File writing error found : {err}")
            raise FileWriteError(f"{err}")

    @staticmethod  # noqa: C901
    def modify(wb_write, rules_sheet_idx, data, rows, rules_section_index, merged, headers_loc=None):
        """
        Adding data to template
        :param headers_loc: has headers locations
        :param wb_write:  has copy of the xls file template
        :param rules_section_index: contains rules sheet index
        :param rules_sheet_idx: contains rules sections index
        :param data: Actual dictionary data which is going to write in excel.
        :param rows: Start and end index of the row
        :param merged: boolean true or false

        """
        if merged:
            # TBD ..
            logger.info(f"Merged feature is not implemented.")
            raise GenericConnectorsException("Merged feature is not implemented.")
        else:
            lower_row, higher_row = rows
            try:
                for index, content in enumerate(
                    data["sheets"][rules_sheet_idx]["sections"][rules_section_index]["rows"]
                ):
                    write_row = lower_row + 1 + index
                    for key, write_col in headers_loc.items():
                        if write_row >= higher_row:
                            break
                        wb_write.write(write_row, write_col, content.get(key, ""), style)
            except Exception as err:
                logger.error(f"Data payload is not matching with the rules and template file. Err: {err}")
                raise FileWriteError(
                    "Data payload is not matching with the rules and template file." "Please verify input data"
                )


class CsvFileHandler:
    def __init__(self):
        pass

    def read_csv(self):
        """Read csv file. TBD"""
        raise GenericConnectorsException("Read csv file is not immediate requirement, TBD")

    def write_csv(self):
        """Write csv file.TBD"""
        raise GenericConnectorsException("Write csv file is not immediate requirement, TBD")
