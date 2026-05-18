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

# Third Party Library
from sqlalchemy.exc import SQLAlchemyError

# DNE Library
from connectors.core.utils.sqldb.model import CiscoTokens
from connectors.core.utils.sqldb.sqlDB import MySQLDB

logger = logging.getLogger(__name__)


class CiscoSmartOperations:
    def __init__(self, token=None, expiry_date=None, export_control=None, created_by=None):
        self.token = token
        self.expiry_date = expiry_date
        self.export_control = export_control
        self.created_by = created_by

    def add_token_operations(self):
        """
        Method to add token
        Returns: token
        """
        try:
            logger.info(f"Adding token to the Database operation")
            sql_instance = MySQLDB()
            with sql_instance.transactional_session() as session:
                cisco_token = CiscoTokens(
                    Token=self.token,
                    ExpiryDate=self.expiry_date,
                    ExportControl=self.export_control,
                    CreatedBy=self.created_by,
                )
                session.add(cisco_token)
                token = cisco_token.Token
            return token
        except SQLAlchemyError as error:
            return error.__dict__["orig"]

    def get_smart_token_operations(self):
        """
        Method to get the token
        Returns: token and token_expiry_date
        """
        try:
            logger.info(f"Fetching the latest token from the database")
            sql_instance = MySQLDB()
            with sql_instance.transactional_session() as session:
                token_details = (
                    session.query(CiscoTokens.Token, CiscoTokens.ExpiryDate)
                    .order_by(CiscoTokens.TokenId.desc())
                    .limit(1)
                    .all()
                )
                if len(token_details) == 0:
                    return None
                else:
                    token = token_details[0].Token
                    token_expiry_date = token_details[0].ExpiryDate
                    return token, token_expiry_date
        except SQLAlchemyError as error:
            return error.__dict__["orig"]
