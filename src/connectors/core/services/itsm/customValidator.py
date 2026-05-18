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
import time
from datetime import datetime, timedelta

# Third Party Library
import requests
from requests.exceptions import RequestException

# DNE Library
from connectors.core.services.itsm.exceptions import DateValidateError

logger = logging.getLogger(__name__)


class DateConverter:
    def __init__(self):
        logger.info(f"Initializing Date Converter Module")
        self.gov_uk_holidays_url = "https://www.gov.uk/bank-holidays.json"

    def get_working_day(self, get_date):
        try:
            bank_holidays = requests.get(self.gov_uk_holidays_url).json()["england-and-wales"]["events"]
            logger.debug(f"Collected bank holidays successfully from {self.gov_uk_holidays_url}")
        except RequestException as err:
            logger.exception(err)
            raise DateValidateError(
                f"Connector was not able to fetch the holiday data from the gov.uk website due to "
                f"error:{err.args[0]}"
            )
        if get_date.weekday() in [5]:
            get_date += timedelta(2)
            return self.get_working_day(get_date)
        elif get_date.weekday() in [6] or [
            True for holiday in bank_holidays if holiday["date"] == get_date.isoformat()
        ]:
            get_date += timedelta(1)
            return self.get_working_day(get_date)
        else:
            return get_date

    def convert(
        self, change_window_duration=None, days_to_wait=None, offset=0, add=0, is_change_on_holiday=False, **kwargs
    ):  # sourcery skip
        """
        Convert the change_window and wait_time into start time and end time for
        creating a spark ticket.

        The returned start time and end time values should not fall on weekends or a UK bank holiday
        unless is_change_on_holiday is true.

        Args:
             days_to_wait: Number of days
             change_window_duration: Time change window
             offset: Time in hours to offset from 00:00 for creating change
             add: Days to add , used during recursive calls

         Returns:
             start_date: start time since epoch
             end_date: end time since epoch

         Raises:
             DateValidateError
        """
        new_start_date = kwargs.get("start_date")
        today = new_start_date or datetime.today().date()
        wait = timedelta(days=days_to_wait + add)
        actual_start_date = today + wait

        logger.info(
            f"Today: {today}, days_to_wait: {days_to_wait}, wait:{wait}, offset: {offset}, add: {add}, "
            f"actual_start_date: {actual_start_date}, Change Window Duration: {change_window_duration}"
        )
        if not is_change_on_holiday:
            actual_start_date = self.get_working_day(actual_start_date)
        logger.debug(f"Change Window Duration: {change_window_duration}")
        start_date = (
            time.mktime(datetime.combine(actual_start_date, datetime.min.time()).utctimetuple()) + 3600 * offset
        )
        end_date_future = datetime.fromtimestamp(start_date).date()
        counter = int(change_window_duration / 24)
        if counter > 0:
            while counter > 0:
                counter -= 1
                if not is_change_on_holiday:
                    end_date_future = self.get_working_day(end_date_future + timedelta(1))
                else:
                    end_date_future = end_date_future + timedelta(1)
            end_date_start = datetime.fromtimestamp(start_date).date()
            end_date = start_date + ((end_date_future - end_date_start).total_seconds())
        else:
            end_date = start_date
        window = change_window_duration % 24
        if window:
            end_date = end_date + 3600 * window
        logger.info(f"StartDate: {start_date}, EndDate: {end_date}")
        return int(start_date), int(end_date)
