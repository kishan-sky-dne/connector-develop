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
# Third Party Library
import connexion

# DNE Library
from connectors.core.services.filehandler.basehandler import FileHandler
from connectors.core.services.filehandler.exceptions import (
    ColumnParse,
    EncodedFileError,
    FileWriteError,
    TemplateNotFound,
)


def parse_sheet(**kwargs):
    """ "
    Method is utilize to parse the data from given input using PUT method
    Input is base64encoded string file content
    :param
    :returned:dictionary data
    """
    try:
        file_handler = FileHandler(kwargs)
        output = file_handler.read()
    except EncodedFileError as err:
        return connexion.problem(
            status=400,
            title=f"File reading error found",
            detail=f"{err}",
        )
    except TemplateNotFound as err:
        return connexion.problem(
            status=404,
            title=f"Template not found",
            detail=f"{err}",
        )
    except ColumnParse as err:
        return connexion.problem(
            status=400,
            title=f"'dataOrientation' parameter value is incorrect",
            detail=f"{err}",
        )
    else:
        return output


def write_sheet(**kwargs):
    """
    Method is utilized to write given input data to the formatted template
    Input data is in dictionary format
    :param kwargs:
    :return:
    """
    try:
        file_handler = FileHandler(kwargs)
        output = file_handler.write()
    except FileWriteError as err:
        return connexion.problem(
            status=400,
            title=f"File writing error found",
            detail=f"{err}",
        )
    except TemplateNotFound as err:
        return connexion.problem(
            status=404,
            title=f"Template not Found",
            detail=f"{err}",
        )
    else:
        return output
