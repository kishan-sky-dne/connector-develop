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
import json
import logging
import sys

# Third Party Library
import connexion
import xlrd

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.exceptions import ServiceDBException
from connectors.core.services.filehandler.exceptions import RaiseDbError, TemplateNotFound
from connectors.core.services.filehandler.operations import CsvFileHandler, XlsFileHandler
from connectors.core.utils.serviceDB import ServiceDB

logger = logging.getLogger(__name__)

APP_PATH = config.get(section="internals", key="app_path")
file_store_path = f"{APP_PATH}/templates/filehandler/"
file_size_limit_in_kb = config.get(section="fileHandler", key="file_size_limit_in_KB")


class FileHandler:
    """
    File handler, Parsing and Writing excel file as per the rules which
    is predefined under template directory.
    """

    def __init__(self, request_body):
        self.data = request_body["body"]

    def read(self):  # noqa: C901
        """
        Parse the data from given file content (file content is base64 encoded).
        Decoding the file content and create a separate temporary xls file name as
        using the file name which is passing
        through the input payload. Read the Data from file.
        :param data:
            Sample input :
            {
                "templateName" : "DCN_PatchingRequest",
                "fileContent" : "abvcX",
                "dataOrientation" : "row"
            }
        :return:
            sample return output :
            {
                "orientation": "row",
                "templateName": "dcnDataParserRules"
                "sheets": [{
                        "sheet_name": "Request",
                        "sections": [{
                                "rows": [{
                                            "AC / DC": "N/A",
                                            "Console": "YES",
                                            "Console IP": "NO",
                                            "Console baud rate": 115200.0,
                                            "Device Names": "sr10.cyasd _RP0",
                                            "Machine Room": "N/A",
                                            "Rack": "Suite 1 Rack 2",
                                            "Switchport": "YES",
                                            "Switchport IP": "YES"
                                        }],
                                }]
                    }]
            }
        """
        logger.info(f"Entering into reading rules {self.data['templateName']}")
        file_type = self.data["fileType"].strip()
        target_file_type_path = file_store_path + file_type + "/"
        try:
            with open("{0}{1}{2}".format(target_file_type_path, self.data["templateName"], ".json")) as file:
                rules_schema = json.loads(file.read())
            logger.info(
                f"Template file found :"
                f"{'{0}{1}{2}'.format(target_file_type_path, self.data['templateName'], '.json')}"
            )
        except Exception as err:
            logger.exception(
                f"Given file type is not supported or templateName is not available. Rules file Path : "
                f"{'{0}{1}{2}'.format(target_file_type_path, self.data['templateName'], '.json')}, err:{err}"
            )
            raise TemplateNotFound(f"Given file type is not supported or templateName is not available.")

        # bug fix 1724 ( File size in below log message has been corrected. )
        logger.info(
            f"Read file size: {'{:.2f}'.format(round(sys.getsizeof(self.data['fileContent']) / 1024, 2))} KB and "
            f"file size limit is : {int(file_size_limit_in_kb)} KB"
        )

        if int(sys.getsizeof(self.data["fileContent"])) <= int(file_size_limit_in_kb) * 1024:
            exceed_payload_size = False
        else:
            exceed_payload_size = True

        if rules_schema.get("fileType") != file_type:
            msg = "Given file type is not matching with rules file type."
            logger.exception(msg)
            raise TemplateNotFound(msg)
        else:
            if rules_schema.get("fileType") == "xls":
                logger.info(f"Reading xls file")
                self.data["rules_schema"] = rules_schema

                if exceed_payload_size and rules_schema.get("dbStorageFlag"):
                    # Store data in mongo db. TBD..
                    msg = (
                        f"File size is - "
                        f"{'{:.2f}'.format(round(sys.getsizeof(self.data['fileContent']) / 1024, 2))} KB. If you "
                        f"have provided more than {int(file_size_limit_in_kb)} KB file, Data will get stored in "
                        f"service db. But DB Storage feature is not implemented."
                    )
                    logger.info(msg)
                    return connexion.problem(
                        status=400,
                        title=f"File size exceeded",
                        detail=msg,
                    )
                elif (not exceed_payload_size) and rules_schema.get("dbStorageFlag"):
                    return XlsFileHandler(self.data).read_xls()
                elif exceed_payload_size and (not rules_schema.get("dbStorageFlag")):
                    msg = (
                        f"File size is - "
                        f"{'{:.2f}'.format(round(sys.getsizeof(self.data['fileContent']) / 1024, 2))} KB. If you "
                        f"have provided more than {int(file_size_limit_in_kb)} KB file, Data will get stored in service"
                        f" db.But 'dbStorageFlag' is disabled."
                    )
                    logger.info(msg)
                    return connexion.problem(
                        status=400,
                        title=f"File size exceeded",
                        detail=msg,
                    )
                elif not (exceed_payload_size and rules_schema.get("dbStorageFlag")):
                    return XlsFileHandler(self.data).read_xls()

            elif rules_schema.get("fileType") == "csv":
                logger.info(f"Reading csv file, ")
                if exceed_payload_size and rules_schema.get("dbStorageFlag"):
                    # Store data in mongo db. TBD..
                    return connexion.problem(
                        status=400,
                        title=f"File size exceeded",
                        detail="",
                    )
                elif (not exceed_payload_size) and rules_schema.get("dbStorageFlag"):
                    return CsvFileHandler().read_csv()
                elif exceed_payload_size and (not rules_schema.get("dbStorageFlag")):
                    return connexion.problem(
                        status=400,
                        title=f"File size exceeded",
                        detail="",
                    )
                elif not (exceed_payload_size and rules_schema.get("dbStorageFlag")):
                    return CsvFileHandler().read_csv()

    def write(self):
        """
        This method will write the xls file as per provided data.
        Data will be written on already stored formatted xls file based on the rule described
        in template file.
        :return:
            sample output :
            {
                'fileContent':base64encoded string,
                'filename':'patchingDataWriteRules.json'
            }

        """
        logger.info(f"Entering into writing xls file")
        file_type = self.data["fileType"].strip()
        target_file_type_path = file_store_path + file_type + "/"
        try:
            with open("{0}{1}{2}".format(target_file_type_path, self.data["templateName"].strip(), ".json")) as file:
                rules_schema = json.loads(file.read())
        except IOError as err:
            logger.exception(
                f"Given file type is not supported or templateName is not available. "
                f"Template not Found {'{0}{1}{2}'.format(target_file_type_path, self.data['templateName'], '.json')}, "
                f"err:{err}"
            )
            raise TemplateNotFound(f"Given file type is not supported or templateName is not available.")

        logger.info(f"file type is {file_type}")
        if rules_schema.get("fileType") != file_type:
            logger.exception(
                f"Given file type is not supported or templateName is not available. "
                f"Template not Found {'{0}{1}{2}'.format(target_file_type_path, self.data['templateName'], '.json')}"
            )
            raise TemplateNotFound(f"Given file type is not supported or templateName is not available.")
        else:
            if rules_schema.get("fileType") == "xls":
                workbook = xlrd.open_workbook(
                    "{0}{1}".format(target_file_type_path, rules_schema.get("fileName")), formatting_info=True
                )
                self.data["rules_schema"] = rules_schema
                self.data["workbook"] = workbook
                logger.info(f"Writing xls file")
                return XlsFileHandler(self.data).write_xls()
            elif rules_schema.get("fileType") == "csv":
                logger.info(f"Writing CSV file")
                return CsvFileHandler().write_csv()

    def mongo_db_service(self, data):
        """TBD..
        MongoDB has to be utilised to store the data only when to be parse file size is
        more than 100KB"""
        try:
            logger.info(f"Connecting to service DB")
            file_handler_db_collection = config.get(section="fileHandler", key="collection")
            file_handler_db_instance = ServiceDB(file_handler_db_collection)
            logger.info(f"ServiceDB connected {file_handler_db_instance}")
            status = file_handler_db_instance.insert(data)
            logger.info(f"data inserted into DB successfully {status}")
        except ServiceDBException as err:
            raise RaiseDbError(err.args[0])
