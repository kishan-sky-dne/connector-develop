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
from datetime import datetime, timedelta

# Third Party Library
import pytz

# DNE Library
from connectors.core.services.itsm.customValidator import DateConverter
from connectors.core.services.itsm.exceptions import DateGeneratorError, DateValidateError

logger = logging.getLogger(__name__)
converter = DateConverter()

timezone = pytz.timezone("Europe/London")


class Resolver:
    def __init__(self, **kwargs):
        self.epoch = (
            datetime(1970, 1, 1, 1, 0, 0) if timezone.localize(datetime.now()).dst() else datetime(1970, 1, 1)
        )  # Adding 1 hour to handle default epoch in BST
        self.startDate = None
        self.endDate = None

    def resolve(self, conflict_response, field_name, **kwargs):
        """
        custom function which resolves the conflicts due to startDate/endDate unavailability
        Args:
            changewindow, conflictErrorResponse
        Returns:
            response: startDate,endDate
        Raises:
            Exception
        """
        conflict_details = []
        try:
            for conflict_element in conflict_response.get("change_request"):
                conflict_end_time = conflict_element.get(f"{field_name}")
                conflict_details.append(datetime.strptime(conflict_end_time, "%d/%m/%Y %H:%M:%S"))
            logger.info(f"Conflict Details: {conflict_details}")
            latest_conflict_time = max(conflict_details)
            # Attempt to create a ticket again with a different startDate and endDate
            new_end_date_in_epoch = self.dtm_to_epoch(dtm=latest_conflict_time)
            return new_end_date_in_epoch
        except (ValueError, KeyError, TypeError) as err:
            raise DateValidateError(
                f"Error occurred while generating start & end date in conflict stage: {err.args[0]}"
            )

    def standard_find_time_slot(
        self,
        change_request=None,
        start_date=None,
        change_window=None,
        change_freeze=None,
        slot_end_date=None,
        is_change_on_holiday=False,
    ):  # noqa: ignore=C901
        # sourcery skip: low-code-quality
        """
        :param change_request:
        :param start_date:
        :param change_window:
        :param change_freeze:
        :param slot_end_date:
        :return:
        """
        logger.info("Inside method to find a correct time slot because of the given CRs and Change Freezes")
        date_today = datetime.today().date()
        date_start = (
            datetime.fromtimestamp(start_date).date()
            if timezone.localize(datetime.fromtimestamp(start_date)).dst()
            else datetime.utcfromtimestamp(start_date).date()
        )
        slot_start_day = (date_start - self.epoch.date()).total_seconds()  # Fix for Bug DNE-18345
        wait_time = (date_start - date_today).days
        offset = (start_date - slot_start_day) / (60 * 60)
        cr_time_slot = []
        cf_time_slot = []
        start_date_in_epoch, end_date_in_epoch = converter.convert(
            change_window_duration=change_window,
            days_to_wait=wait_time,
            offset=offset,
            is_change_on_holiday=is_change_on_holiday,
        )
        if change_request:
            cr_time_slot = self.get_cr_time_slot("task_ci", change_request)
        if change_freeze:
            cf_time_slot = self.get_cr_time_slot("change_freeze", change_freeze)
        total_time_slots = cr_time_slot + cf_time_slot
        total_time_slots.sort()
        for times in total_time_slots:
            if (
                (start_date_in_epoch <= times[0] < end_date_in_epoch)
                or (start_date_in_epoch < times[1] <= end_date_in_epoch)
                or (start_date_in_epoch > times[0] and times[1] > end_date_in_epoch)
            ):
                date_start = (
                    datetime.fromtimestamp(times[1]).date()
                    if timezone.localize(datetime.fromtimestamp(times[1])).dst()
                    else datetime.utcfromtimestamp(times[1]).date()
                )
                new_wait_time = (date_start - date_today).days
                if wait_time == new_wait_time:
                    new_wait_time += 1
                wait_time = new_wait_time
                start_date_in_epoch, end_date_in_epoch = converter.convert(
                    change_window_duration=change_window,
                    days_to_wait=new_wait_time,
                    offset=offset,
                    is_change_on_holiday=is_change_on_holiday,
                )
                if start_date_in_epoch < times[1]:
                    start_date_in_epoch, end_date_in_epoch = converter.convert(
                        change_window_duration=change_window,
                        days_to_wait=new_wait_time + 1,
                        offset=offset,
                        is_change_on_holiday=is_change_on_holiday,
                    )
            if slot_end_date < end_date_in_epoch:
                return False, start_date_in_epoch, end_date_in_epoch
        return True, start_date_in_epoch, end_date_in_epoch

    def get_cr_time_slot(self, table: str, record: list) -> list:
        """
        Returns a list of lists with cr start and end dates in epoch
        """
        dates_list = []
        if record:
            logger.info(f"Logging live changes for {record}")
            for item in record:
                if table == "task_ci":
                    change_event_start_time = self.dtm_to_epoch(dtm=item.get("u_impact_start_date"), origin=item)
                    change_event_end_time = self.dtm_to_epoch(dtm=item.get("u_impact_end_date"), origin=item)
                elif table == "change_freeze":
                    change_event_start_time = self.dtm_to_epoch(dtm=item.get("event_start_time"))
                    change_event_end_time = self.dtm_to_epoch(dtm=item.get("event_end_time"))
                dates_list.append([change_event_start_time, change_event_end_time])
        return dates_list

    def find_time_slot(
        self,
        change_request=None,
        start_date=None,
        change_window=None,
        change_freeze=None,
        slot_end_date=None,
        service_type=None,
    ):  # noqa: ignore=C901
        """
        :param change_request:
        :param start_date:
        :param change_window:
        :param change_freeze:
        :param slot_end_date:
        :param service_type:
        :return:
        """
        logger.info(f"Entering into module to find a time slot for the given CRs and Change Freezes")
        slot_start_day = self.dtm_to_epoch(dtm=start_date)
        slot_end_day = self.dtm_to_epoch(dtm=slot_end_date)
        if service_type == "geaProvisioning":
            slot_start_day = start_date
            slot_end_day = slot_end_date

        dates_list = []  # to store the days from start date to slot end date
        """
        Preparing the list for given start and slot end date.
        Slot = 1 week
        Start: 2020-06-01 xx:yy:zz
        Start: 2020-06-02 xx:yy:zz
        .....
        Start: 2020-06-07 xx:yy:zz
        """
        day_iterator = slot_start_day
        while day_iterator <= slot_end_day:
            dates_list.append(day_iterator)
            if service_type == "geaProvisioning":
                day_iterator += 86400  # 24 * 3600 = 1 day
            else:
                next_date = self.add_delta_to_epoch(dtm=day_iterator, days=1)
                day_iterator = self.dtm_to_epoch(dtm=next_date)
        logger.debug(f"List prepared: {dates_list}")
        """
        Looping through identified prepared start & end date with change freezes/request
        """
        for day_in_epoch in dates_list:
            midnight_start_date = day_in_epoch
            midnight_end_date = int(
                datetime.fromtimestamp(day_in_epoch).replace(hour=change_window, minute=0, second=0).timestamp()
            )
            if service_type == "geaProvisioning":
                midnight_end_date = int(day_in_epoch + change_window * 3600)

            logger.debug(f"midnight_start_date : {midnight_start_date}, midnight_end_date: {midnight_end_date}")
            if self.check_live_changes(
                start_date_in_epoch=midnight_start_date,
                end_date_in_epoch=midnight_end_date,
                record=change_freeze,
                table="change_freeze",
            ):
                if self.check_weekend(
                    start_date=midnight_start_date, change_window_duration=change_window, days_to_wait=0, offset=0
                ):
                    if self.check_live_changes(
                        start_date_in_epoch=midnight_start_date,
                        end_date_in_epoch=midnight_end_date,
                        record=change_request,
                        table="task_ci",
                    ):
                        logger.info(
                            f"Time slot found with start date: {midnight_start_date} & "
                            f"end date: {midnight_end_date}"
                        )
                        return True, midnight_start_date, midnight_end_date
        return False, start_date, slot_end_date

    def check_live_changes(
        self, start_date_in_epoch: int, end_date_in_epoch: int, record: list, table: str = None
    ) -> bool:
        """
        :param start_date_in_epoch:
        :param end_date_in_epoch:
        :param record:
        :param table:
        :return:
        """
        if record:
            logger.debug(f"Logging live changes for {table}: {record}")
            change_event_start_time = None
            change_event_end_time = None
            for item in record:
                if table == "task_ci":
                    change_event_start_time = self.dtm_to_epoch(dtm=item.get("u_impact_start_date"), origin=item)
                    change_event_end_time = self.dtm_to_epoch(dtm=item.get("u_impact_end_date"), origin=item)
                elif table == "change_freeze":
                    change_event_start_time = self.dtm_to_epoch(dtm=item.get("event_start_time"))
                    change_event_end_time = self.dtm_to_epoch(dtm=item.get("event_end_time"))
                if start_date_in_epoch in range(
                    change_event_start_time, change_event_end_time
                ) or end_date_in_epoch in range(
                    change_event_start_time, change_event_end_time
                ):  # noqa: E501
                    return False
        return True

    def check_weekend(self, start_date, change_window_duration=None, days_to_wait=None, offset=0):
        logger.debug(f"Epoch : {self.epoch}")
        if start_date is not None:
            converter = DateConverter()
            start_date_in_epoch, end_date_in_epoch = converter.convert(
                change_window_duration=change_window_duration,
                days_to_wait=days_to_wait,
                offset=offset,
                start_date=datetime.fromtimestamp(start_date),
            )
            if start_date_in_epoch == start_date:
                return True
            else:
                return False

    def dtm_to_epoch(self, dtm=None, hours=0, minutes=0, seconds=0, origin=None) -> int:
        logger.debug(f"dtm value to be converted: '{dtm}'." + (f" Fetched from: {origin}" if origin else ""))
        try:
            if isinstance(dtm, str):
                delta_epoch = datetime.strptime(dtm, "%d/%m/%Y %H:%M:%S")
            else:
                delta_epoch = datetime.fromtimestamp(dtm).replace(hour=hours, minute=minutes, second=0)
            return int((delta_epoch - self.epoch).total_seconds())
        except (ValueError, TypeError, AttributeError) as err:
            raise DateGeneratorError(
                f"Problem in Conflict resolver during conversion of dtm to epoch: {err.args[0]}."
                + (
                    f" Issue originated due to change '{origin.get('task', {}).get('display_value')}' "
                    f"with start date '{origin.get('u_impact_start_date')}' and "
                    f"end date '{origin.get('u_impact_end_date')}'"
                    if origin
                    else ""
                )
            ) from err

    def add_delta_to_epoch(self, dtm=None, days=0, minutes=0, hours=0):
        try:
            delta_dtm = datetime.fromtimestamp(dtm) + timedelta(days=days, minutes=minutes, hours=hours)
            return int((delta_dtm - self.epoch).total_seconds())
        except (ValueError, TypeError, AttributeError) as err:
            raise DateGeneratorError(f"Problem in Conflict resolver while adding delta to epoch: {err.args[0]}")
