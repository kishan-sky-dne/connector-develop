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
import logging

logger = logging.getLogger(__name__)

UPDATE_REGION_BY_MODEL: dict = {"ASR9K": "ALL"}


def query_count(query_table):
    """
    to find query count
    :param query_table:(type: query)
    :return:
    """
    logger.info("Entering query_count module to find query count")
    return query_table.count()
