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
from datetime import datetime
from unittest.mock import patch

# Third Party Library
import pytest

# DNE Library
from connectors.core.services.itsm.conflictResolver import Resolver
from connectors.core.services.itsm.exceptions import DateGeneratorError


def get_working_day_side_effect(*args, **kwargs):
    class Dummy:
        def json(self, **kwargs):
            return {"england-and-wales": {"events": []}}

    return Dummy()


@patch("connectors.core.services.itsm.conflictResolver.Resolver.check_weekend")
def test_find_time_slot_with_nilchangefreeze(mock_chk_weekend):
    """
    test to verify find_time_slot routine returns slot which is in between and change freeze list is None
    """
    mock_chk_weekend.return_value = True
    cr_list = [
        {"u_impact_start_date": "26/5/2020 01:00:00", "u_impact_end_date": "26/5/2020 05:00:00"},
        {"u_impact_start_date": "28/5/2020 01:00:00", "u_impact_end_date": "28/5/2020 05:00:00"},
        {"u_impact_start_date": "25/5/2020 01:00:00", "u_impact_end_date": "25/5/2020 05:00:00"},
    ]
    cf_list = None
    obj = Resolver()
    status, midnight_start_date, midnight_end_date = obj.find_time_slot(
        change_request=cr_list, start_date=1590451200, change_window=4, change_freeze=cf_list, slot_end_date=1591056000
    )
    assert status
    # exp start slot == >Wednesday, 27 May 2020
    exp_s_date = datetime(2020, 5, 27)
    assert datetime.fromtimestamp(midnight_start_date).date() == exp_s_date.date()


@patch("connectors.core.services.itsm.conflictResolver.Resolver.check_weekend")
def test_find_time_slot_with_changefreeze(mock_chk_weekend):
    """
    test to verify find_time_slot routine returns slot when change freeze is also present
    """
    mock_chk_weekend.return_value = True
    cr_list = [
        {"u_impact_start_date": "26/5/2020 01:00:00", "u_impact_end_date": "26/5/2020 05:00:00"},
        {"u_impact_start_date": "28/5/2020 01:00:00", "u_impact_end_date": "28/5/2020 05:00:00"},
        {"u_impact_start_date": "25/5/2020 01:00:00", "u_impact_end_date": "25/5/2020 05:00:00"},
    ]
    cf_list = [{"event_start_time": "27/5/2020 01:00:00", "event_end_time": "27/5/2020 12:59:59"}]
    obj = Resolver()
    status, midnight_start_date, midnight_end_date = obj.find_time_slot(
        change_request=cr_list, start_date=1590451200, change_window=4, change_freeze=cf_list, slot_end_date=1591056000
    )
    assert status
    # exp start slot == > Friday, 29 May 2020 01:00:00
    exp_s_date = datetime(2020, 5, 29)
    assert datetime.fromtimestamp(midnight_start_date).date() == exp_s_date.date()


@patch.object(Resolver, "check_weekend")
@patch.object(Resolver, "check_live_changes")
def test_find_time_slot_sub_routines_check(cl_mock, cw_mock):
    """
    test to verify find_time_slot routine calls subroutine
    """
    cr_list = [
        {"u_impact_start_date": "26/5/2020 01:00:00", "u_impact_end_date": "26/5/2020 05:00:00"},
        {"u_impact_start_date": "28/5/2020 01:00:00", "u_impact_end_date": "28/5/2020 05:00:00"},
        {"u_impact_start_date": "25/5/2020 01:00:00", "u_impact_end_date": "25/5/2020 05:00:00"},
    ]
    cf_list = [{"event_start_time": "27/5/2020 01:00:00", "event_end_time": "27/5/2020 12:59:59"}]
    obj = Resolver()
    obj.find_time_slot(
        change_request=cr_list, start_date=1590451200, change_window=4, change_freeze=cf_list, slot_end_date=1591056000
    )
    cl_mock.assert_called()
    cw_mock.assert_called()


@patch.object(Resolver, "check_weekend")
@patch.object(Resolver, "check_live_changes")
def test_find_time_slot_gea_case(cl_mock, cw_mock):
    """
    test to verify find_time_slot routine calls subroutine
    """
    cr_list = [
        {"u_impact_start_date": "26/5/2020 01:00:00", "u_impact_end_date": "26/5/2020 05:00:00"},
        {"u_impact_start_date": "28/5/2020 01:00:00", "u_impact_end_date": "28/5/2020 05:00:00"},
        {"u_impact_start_date": "25/5/2020 01:00:00", "u_impact_end_date": "25/5/2020 05:00:00"},
    ]
    cf_list = [{"event_start_time": "27/5/2020 01:00:00", "event_end_time": "27/5/2020 12:59:59"}]
    obj = Resolver()
    obj.find_time_slot(
        change_request=cr_list,
        start_date=1590451200,
        change_window=4,
        change_freeze=cf_list,
        slot_end_date=1591056000,
        service_type="geaProvisioning",
    )
    cl_mock.assert_called()
    cw_mock.assert_called()


@patch.object(Resolver, "check_live_changes")
def test_neg_find_time_slot_check_livechange_fail(clv_mock):
    """
    negative test to verify find_time_slot routine returns slot when check live change routine is false
    """
    clv_mock.return_value = False
    cr_list = [
        {"u_impact_start_date": "26/5/2020 01:00:00", "u_impact_end_date": "26/5/2020 05:00:00"},
        {"u_impact_start_date": "28/5/2020 01:00:00", "u_impact_end_date": "28/5/2020 05:00:00"},
        {"u_impact_start_date": "25/5/2020 01:00:00", "u_impact_end_date": "25/5/2020 05:00:00"},
    ]
    cf_list = [{"event_start_time": "27/5/2020 01:00:00", "event_end_time": "27/5/2020 12:59:59"}]
    obj = Resolver()
    status, midnight_start_date, midnight_end_date = obj.find_time_slot(
        change_request=cr_list, start_date=1590451200, change_window=4, change_freeze=cf_list, slot_end_date=1591056000
    )
    assert not status


@patch("connectors.core.services.itsm.customValidator.requests.get")
def test_check_weekend(rest_get_mock):
    """
    test case for the verify weekend dates
    """
    rest_get_mock.side_effect = get_working_day_side_effect
    # Sunday, 7 June 2020
    date_in_epoch = 1591488000
    obj = Resolver()
    assert not obj.check_weekend(start_date=date_in_epoch, change_window_duration=4, days_to_wait=0)
    # Thursday, 4 June 2020
    date_in_epoch = 1591228800
    assert obj.check_weekend(start_date=date_in_epoch, change_window_duration=4, days_to_wait=0)


def test_dtm_to_epoch():
    """
    verify dtm to epoch check
    """
    dtm = 1591228800
    obj = Resolver()
    result = obj.dtm_to_epoch(dtm=dtm)
    assert isinstance(result, int)
    dtm = datetime(2020, 5, 27, 5, 0)
    with pytest.raises(DateGeneratorError):
        obj.dtm_to_epoch(dtm=dtm)


def test_add_delta_to_epoch():
    """
    verify add delta to epoch routine
    """
    # Thursday, 4 June 2020 01:00:00
    dtm = 1591228800
    obj = Resolver()
    res = obj.add_delta_to_epoch(dtm=dtm, days=1, minutes=0, hours=0)
    # Friday, 5 June 2020
    exp_date = datetime(2020, 6, 5)
    assert datetime.fromtimestamp(res).date() == exp_date.date()
    dtm = datetime(2020, 5, 27, 5, 0)
    with pytest.raises(DateGeneratorError):
        obj.add_delta_to_epoch(dtm=dtm, days=1, minutes=20, hours=3)


@patch("connectors.core.services.itsm.customValidator.requests.get")
def test_find_time_slot_with_changefreeze1(rest_get_mock):
    """
    test to verify find_time_slot routine returns slot when change freeze is also present
    """
    rest_get_mock.side_effect = get_working_day_side_effect
    cr_list = [
        {"u_impact_start_date": "26/1/2021 11:00:00", "u_impact_end_date": "29/1/2021 05:00:00"},
        {"u_impact_start_date": "29/1/2021 06:00:00", "u_impact_end_date": "29/1/2021 22:00:00"},
        {"u_impact_start_date": "04/2/2021 01:00:00", "u_impact_end_date": "05/2/2021 15:00:00"},
    ]
    cf_list = [{"event_start_time": "04/2/2021 00:00:00", "event_end_time": "05/2/2021 23:59:59"}]
    obj = Resolver()
    status, midnight_start_date, midnight_end_date = obj.standard_find_time_slot(
        change_request=cr_list, start_date=1611565200, change_window=27, change_freeze=cf_list, slot_end_date=1612774800
    )
    assert status
    # exp start slot == > Friday, 29 May 2020 01:00:00
    exp_s_date = datetime(2021, 2, 1)
    assert datetime.fromtimestamp(midnight_start_date).date() == exp_s_date.date()


@patch("connectors.core.services.itsm.customValidator.requests.get")
def test_find_time_slot_with_changefreeze2(rest_get_mock):
    """
    test to verify find_time_slot routine returns slot when change freeze is also present
    """
    rest_get_mock.side_effect = get_working_day_side_effect
    cr_list = [
        {"u_impact_start_date": "26/1/2021 11:00:00", "u_impact_end_date": "27/1/2021 05:00:00"},
        {"u_impact_start_date": "29/1/2021 06:00:00", "u_impact_end_date": "29/1/2021 22:00:00"},
        {"u_impact_start_date": "04/2/2021 01:00:00", "u_impact_end_date": "05/2/2021 15:00:00"},
    ]
    cf_list = [{"event_start_time": "04/2/2021 00:00:00", "event_end_time": "05/2/2021 23:59:59"}]
    obj = Resolver()
    status, midnight_start_date, midnight_end_date = obj.standard_find_time_slot(
        change_request=cr_list, start_date=1611565200, change_window=27, change_freeze=cf_list, slot_end_date=1612774800
    )
    assert status
    # exp start slot == > Friday, 29 May 2020 01:00:00
    exp_s_date = datetime(2021, 1, 27)
    assert datetime.fromtimestamp(midnight_start_date).date() == exp_s_date.date()


@patch("connectors.core.services.itsm.customValidator.requests.get")
def test_find_time_slot_with_changefreeze3(rest_get_mock):
    """
    test to verify find_time_slot routine returns slot when change freeze is also present
    """
    rest_get_mock.side_effect = get_working_day_side_effect
    cr_list = [
        {"u_impact_start_date": "26/1/2021 11:00:00", "u_impact_end_date": "27/1/2021 05:00:00"},
        {"u_impact_start_date": "29/1/2021 06:00:00", "u_impact_end_date": "29/1/2021 22:00:00"},
        {"u_impact_start_date": "04/2/2021 01:00:00", "u_impact_end_date": "05/2/2021 15:00:00"},
    ]
    cf_list = [{"event_start_time": "04/2/2021 00:00:00", "event_end_time": "05/2/2021 23:59:59"}]
    obj = Resolver()
    status, midnight_start_date, midnight_end_date = obj.standard_find_time_slot(
        change_request=cr_list, start_date=1611565200, change_window=51, change_freeze=cf_list, slot_end_date=1612774800
    )
    assert status
    # exp start slot == > Friday, 29 May 2020 01:00:00
    exp_s_date = datetime(2021, 2, 1)
    assert datetime.fromtimestamp(midnight_start_date).date() == exp_s_date.date()


@patch("connectors.core.services.itsm.customValidator.requests.get")
def test_find_time_slot_with_changefreeze4(rest_get_mock):
    """
    test to verify find_time_slot routine returns slot when change freeze is also present
    """
    rest_get_mock.side_effect = get_working_day_side_effect
    cr_list = [
        {"u_impact_start_date": "26/1/2021 11:00:00", "u_impact_end_date": "27/1/2021 05:00:00"},
        {"u_impact_start_date": "29/1/2021 06:00:00", "u_impact_end_date": "29/1/2021 22:00:00"},
        {"u_impact_start_date": "04/2/2021 01:00:00", "u_impact_end_date": "05/2/2021 15:00:00"},
    ]
    cf_list = [{"event_start_time": "01/2/2021 00:00:00", "event_end_time": "02/2/2021 23:59:59"}]
    obj = Resolver()
    status, midnight_start_date, midnight_end_date = obj.standard_find_time_slot(
        change_request=cr_list, start_date=1611565200, change_window=51, change_freeze=cf_list, slot_end_date=1612774800
    )
    assert not status
    # exp start slot == > Friday, 29 May 2020 01:00:00
    exp_s_date = datetime(2021, 2, 8)
    assert datetime.fromtimestamp(midnight_start_date).date() == exp_s_date.date()


@patch("connectors.core.services.itsm.customValidator.requests.get")
def test_find_time_slot_with_nilchangefreeze_standard(rest_get_mock):
    """
    test to verify find_time_slot routine returns slot which is in between and change freeze list is None
    """
    rest_get_mock.side_effect = get_working_day_side_effect
    cr_list = [
        {"u_impact_start_date": "26/5/2020 01:00:00", "u_impact_end_date": "26/5/2020 05:00:00"},
        {"u_impact_start_date": "28/5/2020 01:00:00", "u_impact_end_date": "28/5/2020 05:00:00"},
        {"u_impact_start_date": "25/5/2020 01:00:00", "u_impact_end_date": "25/5/2020 05:00:00"},
    ]
    cf_list = None
    obj = Resolver()
    status, midnight_start_date, midnight_end_date = obj.standard_find_time_slot(
        change_request=cr_list, start_date=1590451200, change_window=4, change_freeze=cf_list, slot_end_date=1591056000
    )
    assert status
    # exp start slot == >Wednesday, 27 May 2020
    exp_s_date = datetime(2020, 5, 27)
    assert datetime.fromtimestamp(midnight_start_date).date() == exp_s_date.date()


@patch("connectors.core.services.itsm.customValidator.requests.get")
def test_find_time_slot_with_changefreeze_standard(rest_get_mock):
    """
    test to verify find_time_slot routine returns slot when change freeze is also present
    """
    rest_get_mock.side_effect = get_working_day_side_effect
    cr_list = [
        {"u_impact_start_date": "26/5/2020 01:00:00", "u_impact_end_date": "26/5/2020 05:00:00"},
        {"u_impact_start_date": "28/5/2020 01:00:00", "u_impact_end_date": "28/5/2020 05:00:00"},
        {"u_impact_start_date": "25/5/2020 01:00:00", "u_impact_end_date": "25/5/2020 05:00:00"},
    ]
    cf_list = [{"event_start_time": "27/5/2020 01:00:00", "event_end_time": "27/5/2020 12:59:59"}]
    obj = Resolver()
    status, midnight_start_date, midnight_end_date = obj.standard_find_time_slot(
        change_request=cr_list, start_date=1590451200, change_window=4, change_freeze=cf_list, slot_end_date=1591056000
    )
    assert status
    # exp start slot == > Friday, 29 May 2020 01:00:00
    exp_s_date = datetime(2020, 5, 29)
    assert datetime.fromtimestamp(midnight_start_date).date() == exp_s_date.date()
