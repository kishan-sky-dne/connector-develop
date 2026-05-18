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
# Sample inputs for mailer-send (email notifications)

mailer_payload = {
    "toList": ["user@sky.uk", "user@sky.it", "user@comcast.com"],
    "bccList": ["user@sky.uk", "user@sky.it", "user@comcast.com"],
    "ccList": ["user@sky.uk", "user@sky.it", "user@comcast.com"],
    "language": "en",
    "mailTemplate": "taskAssignment",
    "parameters": {
        "orderNumber": "123",
        "orderType": "OLT Commissioning",
        "taskName": "taskAssignment",
        "siteId": "1",
        "url": "https://testurl.com",
    },
    "attachmentList": [
        {"fileName": "taskAssignment.pdf", "fileContent": "YWJjMTIzIT8kKiYoKScPUB+="},
        {"fileName": "releaseNotes.jpeg", "fileContent": "YWJjMTIzIT8kKiYoKScPUB=="},
    ],
}

payload_empty_to_list = {
    "toList": [],
    "bccList": ["user@sky.uk", "user@sky.it", "user@comcast.com"],
    "ccList": ["user@sky.uk", "user@sky.it", "user@comcast.com"],
    "language": "en",
    "mailTemplate": "taskAssignment",
    "parameters": {"orderNumber": "123", "orderType": "OLT Commissioning", "siteId": "1", "url": "https://testurl.com"},
    "attachmentList": [
        {"fileName": "taskAssignment.pdf", "fileContent": "YWJjMTIzIT8kKiYoKScPUB+="},
        {"fileName": "releaseNotes.jpeg", "fileContent": "YWJjMTIzIT8kKiYoKScPUB=="},
    ],
}

payload_invalid_to_list = {
    "toList": ["user@test.com", "user@test.it", "user@test.uk"],
    "bccList": ["user@sky.uk", "user@sky.it", "user@comcast.com"],
    "ccList": ["user@sky.uk", "user@sky.it", "user@comcast.com"],
    "language": "en",
    "mailTemplate": "taskAssignment",
    "parameters": {"orderNumber": "123", "orderType": "OLT Commissioning", "siteId": "1", "url": "https://testurl.com"},
    "attachmentList": [
        {"fileName": "taskAssignment.pdf", "fileContent": "YWJjMTIzIT8kKiYoKScPUB+="},
        {"fileName": "releaseNotes.jpeg", "fileContent": "YWJjMTIzIT8kKiYoKScPUB=="},
    ],
}

payload_incorrect_template_name = {
    "toList": ["user@sky.uk", "user@sky.it", "user@comcast.com"],
    "bccList": ["user@sky.uk", "user@sky.it", "user@comcast.com"],
    "ccList": ["user@sky.uk", "user@sky.it", "user@comcast.com"],
    "language": "en",
    "mailTemplate": "xyz",
    "parameters": {"orderNumber": "123", "orderType": "OLT Commissioning", "siteId": "1", "url": "https://testurl.com"},
    "attachmentList": [
        {"fileName": "taskAssignment.pdf", "fileContent": "YWJjMTIzIT8kKiYoKScPUB+="},
        {"fileName": "releaseNotes.jpeg", "fileContent": "YWJjMTIzIT8kKiYoKScPUB=="},
    ],
}
