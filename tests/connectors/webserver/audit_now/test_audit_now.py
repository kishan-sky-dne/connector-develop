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
from unittest.mock import patch

# DNE Library
from connectors.webserver.audit_now.audit_now import audit_now_status, start_audit_now, stop_audit_now


@patch("connectors.webserver.audit_now.audit_now.stop_event")
@patch("connectors.webserver.audit_now.audit_now.config")
@patch("connectors.webserver.audit_now.audit_now.AuditNowThread")
def test_start_audit_now_first_call(auditnow_thread_mock, conf_mock, stop_mock):
    """
    Test first call
    """
    auditnow_thread_mock().is_alive.return_value = False
    assert start_audit_now() == {"info": "Started AuditNow."}
    stop_mock.clear.assert_called_once()
    auditnow_thread_mock().start.assert_called_once()


@patch("connectors.webserver.audit_now.audit_now.stop_event")
@patch("connectors.webserver.audit_now.audit_now.config")
@patch("connectors.webserver.audit_now.audit_now.AuditNowThread")
def test_start_audit_now_subsequent_calls(auditnow_thread_mock, conf_mock, stop_mock):
    """
    Test subsequent calls
    """
    auditnow_thread_mock().is_alive.return_value = True
    assert start_audit_now() == {"info": "AuditNow is already running."}
    stop_mock.clear.assert_called_once()
    auditnow_thread_mock().start.assert_not_called()


@patch("connectors.webserver.audit_now.audit_now.stop_event")
@patch("connectors.webserver.audit_now.audit_now.config")
@patch("connectors.webserver.audit_now.audit_now.AuditNowThread")
def test_stop_audit_now(auditnow_thread_mock, conf_mock, stop_mock):
    """
    Test when AuditNow is not running
    """
    assert stop_audit_now() == {"info": "AuditNow is not running."}
    stop_mock.set.assert_not_called()


@patch("connectors.webserver.audit_now.audit_now.stop_event")
@patch("connectors.webserver.audit_now.audit_now.config")
@patch("connectors.webserver.audit_now.audit_now.AuditNowThread")
def test_audit_now_status(auditnow_thread_mock, conf_mock, stop_mock):
    """
    Test when AuditNow is not running
    """
    assert audit_now_status() == {"info": "AuditNow is not running."}
