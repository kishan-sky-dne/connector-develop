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
import re
import string
from typing import Any


def get_indexes(start_index: int, end_index: int) -> tuple[tuple[int, Any], tuple[int, Any]]:
    """
    Prepare start-indexes and end-indexes of using this method
    :param start_index:
    :param end_index:
    :return:
    """

    def get_column(index):
        """
        Based on column name(A1,A2....Z2,Z5) preparing column indexes
        :param index:
        :return:
        """
        char_map = {}
        for inx, char in enumerate(string.ascii_uppercase):
            char_map[char] = inx
        column = list(re.split("[0-9]", index)[0])
        if len(column) == 1:
            translated_col = char_map[column[0]]
        else:
            sum = 0
            for prior in column[:-1]:
                sum += (char_map[prior] + 1) * 26
            else:
                sum += char_map[column[-1]]
            translated_col = sum
        return translated_col

    def get_row(index):
        """
        Preparing rows indexs
        :param index:
        :return:
        """
        return int(re.split("[a-zA-z]", index)[-1])

    return (get_row(start_index), get_column(start_index)), (get_row(end_index), get_column(end_index))
