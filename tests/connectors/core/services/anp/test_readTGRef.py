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
import sys
from unittest.mock import patch

# Sky Library
from isp_config import ConfigManagerException

# DNE Library
from connectors.core.config import connectors_config
from connectors.core.services.anp.connector import ReadTGService
from connectors.webserver.anp.tasks import read

try:
    config = connectors_config.ConnectorsConfigManager()
    config.load_config()
except ConfigManagerException:
    sys.exit(1)

username = config.get(section="anp", key="ad_username")
password = config.get(section="anp", key="ad_password")
userspace_kwarg = {
    "domain": "core",
    "projectName": "Sacramento",
    "tgReference": "TG7399",
    "userSpace": ["NDSS", "Tx Design"],
}
metadata_kwarg = {"domain": "core", "projectName": "Sacramento", "tgReference": "TG7399"}
metadata_kwarg_invalid = {"domain": "core", "projectName": "Sacramento", "tgReference": "XXXX"}
userspace_kwarg_invalid = {
    "domain": "core",
    "projectName": "Sacramento",
    "tgReference": "XXXX",
    "userSpace": ["NDSS", "Tx Design"],
}
metadata_response = {
    "metadata": {
        "created": "2020-07-13T14:17:37.457799+01:00",
        "dates": {"delivery": "None", "required": "2020-07-21"},
        "description": "",
        "domain": "core",
        "effective_from": "2020-07-13T14:17:37.457799+01:00",
        "impact": "low",
        "managers": ["fiona.ochan@sky.uk"],
        "name": "sr10.pomnc-pr2.hobir migration to ta0.pomnc",
        "project": "Sacramento",
        "reference": "TG7399",
        "status": "new",
        "system": False,
        "uid": "7c036094-c75b-4c7d-a5eb-5f5b9ef49701",
    },
    "status": "success",
}
userspacedata_response = {
    "status": "success",
    "metadata": {
        "uid": "7c036094-c75b-4c7d-a5eb-5f5b9ef49701",
        "name": "sr10.pomnc-pr2.hobir migration to ta0.pomnc",
        "description": "",
        "reference": "TG7399",
        "impact": "low",
        "status": "new",
        "system": False,
        "created": "2020-07-13T14:17:37.457799+01:00",
        "effective_from": "2020-07-13T14:17:37.457799+01:00",
        "dates": {"delivery": "None", "required": "2020-07-21"},
        "managers": ["fiona.ochan@sky.uk"],
        "rows": [
            {
                "NDSS": {
                    "location_aEnd": "pomnc",
                    "hostName_aEnd": "sr10.pomnc.isp.sky.com",
                    "chassisModel_aEnd": "7750-SR12",
                    "deviceVendor_aEnd": "Nokia",
                    "port_aEnd": "2/2/1",
                    "transceiver_aEnd": "ALU-CFP-100G-LR4",
                    "media_aEnd": "SM",
                    "connector_aEnd": "LC",
                    "location_bEnd": "pomnc",
                    "hostName_bEnd": "ta0.pomnc.isp.sky.com",
                    "chassisModel_bEnd": "NCS-5508",
                    "deviceVendor_bEnd": "Cisco",
                    "port_bEnd": "HundredGigE0/3/0/35",
                    "transceiver_bEnd": "CIS-QSFP-100G-LR4-S",
                    "media_bEnd": "SM",
                    "connector_bEnd": "LC",
                },
                "Tx Design": {
                    "Transmission Circuit Reference": "None",
                    "Circuit No": "None",
                    "LLD and New 100G Required": "None",
                    "transmissionPort_aEnd": "None",
                    "transmissionPort_bEnd": "None",
                },
            },
            {
                "NDSS": {
                    "location_aEnd": "hobir",
                    "hostName_aEnd": "pr2.hobir.isp.sky.com",
                    "chassisModel_aEnd": "NCS-6008",
                    "deviceVendor_aEnd": "Cisco",
                    "port_aEnd": "HundredGigE0/6/0/0",
                    "transceiver_aEnd": "CIS-CPAK-100G-SR10",
                    "media_aEnd": "MM",
                    "connector_aEnd": "MPO-12",
                    "location_bEnd": "pomnc",
                    "hostName_bEnd": "ta0.pomnc.isp.sky.com",
                    "chassisModel_bEnd": "NCS-5508",
                    "deviceVendor_bEnd": "Cisco",
                    "port_bEnd": "HundredGigE0/0/0/0",
                    "transceiver_bEnd": "CIS-QSFP-100G-LR4-S",
                    "media_bEnd": "SM",
                    "connector_bEnd": "LC",
                },
                "Tx Design": {
                    "Transmission Circuit Reference": "None",
                    "Circuit No": "None",
                    "LLD and New 100G Required": "None",
                    "transmissionPort_aEnd": "None",
                    "transmissionPort_bEnd": "None",
                },
            },
        ],
    },
}

userspace_response = {
    "data": {
        "metadata": {
            "domain": "core",
            "project": "Sacramento",
            "rows": [
                {
                    "NDSS": {
                        "chassisModel_aEnd": "7750-SR12",
                        "chassisModel_bEnd": "NCS-5508",
                        "connector_aEnd": "LC",
                        "connector_bEnd": "LC",
                        "deviceVendor_aEnd": "Nokia",
                        "deviceVendor_bEnd": "Cisco",
                        "hostName_aEnd": "sr10.pomnc.isp.sky.com",
                        "hostName_bEnd": "ta0.pomnc.isp.sky.com",
                        "location_aEnd": "pomnc",
                        "location_bEnd": "pomnc",
                        "media_aEnd": "SM",
                        "media_bEnd": "SM",
                        "port_aEnd": "2/2/1",
                        "port_bEnd": "HundredGigE0/3/0/35",
                        "transceiver_aEnd": "ALU-CFP-100G-LR4",
                        "transceiver_bEnd": "CIS-QSFP-100G-LR4-S",
                    }
                },
                {
                    "NDSS": {
                        "chassisModel_aEnd": "NCS-6008",
                        "chassisModel_bEnd": "NCS-5508",
                        "connector_aEnd": "MPO-12",
                        "connector_bEnd": "LC",
                        "deviceVendor_aEnd": "Cisco",
                        "deviceVendor_bEnd": "Cisco",
                        "hostName_aEnd": "pr2.hobir.isp.sky.com",
                        "hostName_bEnd": "ta0.pomnc.isp.sky.com",
                        "location_aEnd": "hobir",
                        "location_bEnd": "pomnc",
                        "media_aEnd": "MM",
                        "media_bEnd": "SM",
                        "port_aEnd": "HundredGigE0/6/0/0",
                        "port_bEnd": "HundredGigE0/0/0/0",
                        "transceiver_aEnd": "CIS-CPAK-100G-SR10",
                        "transceiver_bEnd": "CIS-QSFP-100G-LR4-S",
                    }
                },
            ],
            "tgReference": "TG7399",
        },
        "status": "success",
    },
    "success": True,
}
userspace_response_1 = {
    "data": {
        "metadata": {
            "domain": "core",
            "project": "Sacramento",
            "rows": [
                {
                    "NDSS": {
                        "chassisModel_aEnd": "NCS-6008",
                        "chassisModel_bEnd": "NCS-5508",
                        "connector_aEnd": "MPO-12",
                        "connector_bEnd": "LC",
                        "deviceVendor_aEnd": "Cisco",
                        "deviceVendor_bEnd": "Cisco",
                        "hostName_aEnd": "pr2.hobir.isp.sky.com",
                        "hostName_bEnd": "ta0.pomnc.isp.sky.com",
                        "location_aEnd": "hobir",
                        "location_bEnd": "pomnc",
                        "media_aEnd": "MM",
                        "media_bEnd": "SM",
                        "port_aEnd": "HundredGigE0/6/0/0",
                        "port_bEnd": "HundredGigE0/0/0/0",
                        "transceiver_aEnd": "CIS-CPAK-100G-SR10",
                        "transceiver_bEnd": "CIS-QSFP-100G-LR4-S",
                    }
                },
                {
                    "NDSS": {
                        "chassisModel_aEnd": "7750-SR12",
                        "chassisModel_bEnd": "NCS-5508",
                        "connector_aEnd": "LC",
                        "connector_bEnd": "LC",
                        "deviceVendor_aEnd": "Nokia",
                        "deviceVendor_bEnd": "Cisco",
                        "hostName_aEnd": "sr10.pomnc.isp.sky.com",
                        "hostName_bEnd": "ta0.pomnc.isp.sky.com",
                        "location_aEnd": "pomnc",
                        "location_bEnd": "pomnc",
                        "media_aEnd": "SM",
                        "media_bEnd": "SM",
                        "port_aEnd": "2/2/1",
                        "port_bEnd": "HundredGigE0/3/0/35",
                        "transceiver_aEnd": "ALU-CFP-100G-LR4",
                        "transceiver_bEnd": "CIS-QSFP-100G-LR4-S",
                    }
                },
            ],
            "tgReference": "TG7399",
        },
        "status": "success",
    },
    "success": True,
}
metadata_exception = {
    "errors": [
        {
            "code": "ERR-005-006-1001",
            "message": "Failed to get tg reference  data for tgreference: XXXX and domain: core ",
        }
    ],
    "metadata": {"domain": "core", "project": "Sacramento", "tgReference": "XXXX"},
    "status": "failure",
}
userspacedata_exception = {
    "errors": [
        {
            "code": "ERR-005-006-1001",
            "message": "Failed to get tg reference  data for tgreference: XXXX and domain: core ",
        }
    ],
    "metadata": {"domain": "core", "project": "Sacramento", "tgReference": "XXXX"},
    "status": "failure",
}
parent_projects_data = {
    "success": True,
    "data": {
        "_links": {
            "self": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core/deliverables?reference=TG7399"},
            "parent": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core"},
        },
        "deliverables": [
            {
                "_links": {
                    "self": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core/deliverables/834"},
                    "parent": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core/projects/35"},
                    "userspaces": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core/projects/35/userspaces"},
                },
                "uid": "7c036094-c75b-4c7d-a5eb-5f5b9ef49701",
                "name": "sr10.pomnc-pr2.hobir migration to ta0.pomnc",
                "description": "",
                "reference": "TG7399",
                "impact": "low",
                "status": "new",
                "system": False,
                "created": "2020-07-13T14:17:37.457799+01:00",
                "effective_from": "2020-07-13T14:17:37.457799+01:00",
                "dates": {"delivery": "None", "required": "2020-07-21"},
                "managers": ["fiona.ochan@sky.uk"],
            }
        ],
    },
    "uid": "7c036094-c75b-4c7d-a5eb-5f5b9ef49701",
}
cell_data = {
    "_links": {
        "self": {"href": "https://insightandplanning-qa.sns.sky.com/ut/userspaces/124/cells"},
        "parent": {"href": "https://insightandplanning-qa.sns.sky.com/ut/userspaces/124"},
    },
    "rows": [
        {
            "deliverable": "578abeda-6ec1-44ab-abb1-48ef1af80b0e",
            "activity": "a88be56a-b5ef-4206-8152-8b0f4fb2066e",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "pomnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "sr10.pomnc.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "7750-SR12"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Nokia"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "1/2/1"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "ALU-QSFP-100G-SR4"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "MM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "pomnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta0.pomnc.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "HundredGigE0/3/0/31"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "MM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "1e2b382c-53ac-4db4-a742-8f6ef1c284b4",
            "activity": "66acdf89-e11c-41d3-9c39-1bbe29550a7b",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "pomnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "sr10.pomnc.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "7750-SR12"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Nokia"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "6/2/1"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "ALU-QSFP-100G-SR4"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "MM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "pomnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.pomnc.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "HundredGigE0/3/0/31"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "MM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "68d16bb8-3227-4c05-a9bb-e93ff1eaba1c",
            "activity": "7f33f934-a3e8-4752-b722-349e5a9323d5",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "pomnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.pomnc.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "HundredGigE0/7/0/0"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "MM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "pomnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.pomnc.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "HundredGigE0/7/0/0"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "MM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "6b40c875-cfe1-4cd6-addd-72d78532d820",
            "activity": "f8d8843b-d3be-4cbc-ad7b-6f4c3b0d4b8e",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "mimnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.mimnc.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "HundredGigE0/7/0/0"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "MM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "mimnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.mimnc.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "HundredGigE0/7/0/0"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "MM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "7c036094-c75b-4c7d-a5eb-5f5b9ef49701",
            "activity": "a3caa154-bb4e-49b8-aaf2-75970fccf5ea",
            "cells": {
                "location_aEnd": "hobir",
                "hostName_aEnd": "pr2.hobir.isp.sky.com",
                "chassisModel_aEnd": "NCS-6008",
                "deviceVendor_aEnd": "Cisco",
                "port_aEnd": "HundredGigE0/6/0/0",
                "transceiver_aEnd": "CIS-CPAK-100G-SR10",
                "media_aEnd": "MM",
                "connector_aEnd": "MPO-12",
                "location_bEnd": "pomnc",
                "hostName_bEnd": "ta0.pomnc.isp.sky.com",
                "chassisModel_bEnd": "NCS-5508",
                "deviceVendor_bEnd": "Cisco",
                "port_bEnd": "HundredGigE0/0/0/0",
                "transceiver_bEnd": "CIS-QSFP-100G-LR4-S",
                "media_bEnd": "SM",
                "connector_bEnd": "LC",
            },
        },
        {
            "deliverable": "b2b551b3-8d19-4daa-858e-bd4eee91201b",
            "activity": "b70e9ffd-ad57-48e4-82f9-341fd1203310",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "enlba"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "pr5.enlba.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5516"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "HundredGigE0/7/0/8"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-100G-LR4-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "SM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "LC"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "pomnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.pomnc.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "HundredGigE0/0/0/0"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-100G-LR4-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "SM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "LC"},
            },
        },
        {
            "deliverable": "68d16bb8-3227-4c05-a9bb-e93ff1eaba1c",
            "activity": "67441808-691f-43bf-ba63-8f603aa9676c",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "pomnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.pomnc.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "HundredGigE0/7/0/1"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "MM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "pomnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.pomnc.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "HundredGigE0/7/0/1"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "MM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "68d16bb8-3227-4c05-a9bb-e93ff1eaba1c",
            "activity": "2a840dbe-ebfb-42be-a438-652995e09b01",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "pomnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.pomnc.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "HundredGigE0/7/0/2"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "MM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "pomnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.pomnc.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "HundredGigE0/7/0/2"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "MM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "68d16bb8-3227-4c05-a9bb-e93ff1eaba1c",
            "activity": "55e1be73-dbaa-4e89-8621-21357c523ec7",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "pomnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.pomnc.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "HundredGigE0/7/0/3"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "MM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "pomnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.pomnc.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "HundredGigE0/7/0/3"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "MM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "68d16bb8-3227-4c05-a9bb-e93ff1eaba1c",
            "activity": "66354467-69eb-47b7-a877-49ad2448dcdc",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "pomnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.pomnc.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "HundredGigE0/7/0/4"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "MM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "pomnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.pomnc.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "HundredGigE0/7/0/4"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "MM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "68d16bb8-3227-4c05-a9bb-e93ff1eaba1c",
            "activity": "bc6db11b-5d5c-41bf-97ba-8825eaf86049",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "pomnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.pomnc.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "HundredGigE0/7/0/5"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "MM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "pomnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.pomnc.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "HundredGigE0/7/0/5"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "MM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "68d16bb8-3227-4c05-a9bb-e93ff1eaba1c",
            "activity": "353ba079-c11c-4cc8-a828-396d2febf1e3",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "pomnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.pomnc.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "HundredGigE0/7/0/6"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "MM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "pomnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.pomnc.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "HundredGigE0/7/0/6"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "MM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "68d16bb8-3227-4c05-a9bb-e93ff1eaba1c",
            "activity": "3d7c24fb-24f9-4c1d-83ca-663fdbd61f7c",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "pomnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.pomnc.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "HundredGigE0/7/0/7"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "MM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "pomnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.pomnc.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "HundredGigE0/7/0/7"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "MM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "7c036094-c75b-4c7d-a5eb-5f5b9ef49701",
            "activity": "c16afe91-f9dc-443b-91a4-8a0de046ccda",
            "cells": {
                "location_aEnd": "pomnc",
                "hostName_aEnd": "sr10.pomnc.isp.sky.com",
                "chassisModel_aEnd": "7750-SR12",
                "deviceVendor_aEnd": "Nokia",
                "port_aEnd": "2/2/1",
                "transceiver_aEnd": "ALU-CFP-100G-LR4",
                "media_aEnd": "SM",
                "connector_aEnd": "LC",
                "location_bEnd": "pomnc",
                "hostName_bEnd": "ta0.pomnc.isp.sky.com",
                "chassisModel_bEnd": "NCS-5508",
                "deviceVendor_bEnd": "Cisco",
                "port_bEnd": "HundredGigE0/3/0/35",
                "transceiver_bEnd": "CIS-QSFP-100G-LR4-S",
                "media_bEnd": "SM",
                "connector_bEnd": "LC",
            },
        },
        {
            "deliverable": "b2b551b3-8d19-4daa-858e-bd4eee91201b",
            "activity": "c54a4098-3f3e-4041-a924-603368412a8c",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "pomnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "sr10.pomnc.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "7750-SR12"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Nokia"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "7/2/1"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "ALU-CFP-100G-LR4"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "SM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "LC"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "pomnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.pomnc.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "HundredGigE0/3/0/35"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-100G-LR4-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "SM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "LC"},
            },
        },
        {
            "deliverable": "6b40c875-cfe1-4cd6-addd-72d78532d820",
            "activity": "a636ae36-0553-4fda-a306-8278fb7fdd04",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "mimnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.mimnc.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "HundredGigE0/7/0/1"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "MM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "mimnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.mimnc.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "HundredGigE0/7/0/1"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "MM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "6b40c875-cfe1-4cd6-addd-72d78532d820",
            "activity": "8d406f58-76ed-4b9f-a377-e428032010d1",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "mimnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.mimnc.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "HundredGigE0/7/0/2"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "MM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "mimnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.mimnc.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "HundredGigE0/7/0/2"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "MM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "6b40c875-cfe1-4cd6-addd-72d78532d820",
            "activity": "ff61b6e7-4d18-4c0f-b9f3-ca8e4f17bba0",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "mimnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.mimnc.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "HundredGigE0/7/0/3"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "MM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "mimnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.mimnc.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "HundredGigE0/7/0/3"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "MM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "6b40c875-cfe1-4cd6-addd-72d78532d820",
            "activity": "21bd682c-0350-46f1-8c88-03f70967deb0",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "mimnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.mimnc.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "HundredGigE0/7/0/4"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "MM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "mimnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.mimnc.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "HundredGigE0/7/0/4"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "MM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "6b40c875-cfe1-4cd6-addd-72d78532d820",
            "activity": "4b3a49ad-b6a1-47ef-8089-d8fd761b1823",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "mimnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.mimnc.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "HundredGigE0/7/0/5"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "MM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "mimnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.mimnc.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "HundredGigE0/7/0/5"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "MM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "6b40c875-cfe1-4cd6-addd-72d78532d820",
            "activity": "436c0084-3734-4392-a590-2a39930517be",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "mimnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.mimnc.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "HundredGigE0/7/0/6"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "MM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "mimnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.mimnc.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "HundredGigE0/7/0/6"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "MM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "6b40c875-cfe1-4cd6-addd-72d78532d820",
            "activity": "d3ec66e1-ba5c-496f-9dd7-3d96410a31fd",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "mimnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.mimnc.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "HundredGigE0/7/0/7"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "MM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "mimnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.mimnc.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "HundredGigE0/7/0/7"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-100G-SR4-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "MM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "c4fbe878-44e9-4871-87dc-ca3a54f24a6f",
            "activity": "c97f111e-b2f1-449e-b80d-21899be2c42a",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "pomnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.dev-uk.bllab.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "TenGigE0/7/0/10/3"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-4X10G-LR-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "SM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "pomnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.dev-uk.bllab.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "TenGigE0/0/0/15/3"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-4X10G-LR-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "SM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "9b01e419-5389-47f7-8c5c-7ac299c086fc",
            "activity": "9b03cce2-becb-4604-a443-201938e6477f",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "pomnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.dev-uk.bllab.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "TenGigE0/7/0/11/0"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-4X10G-LR-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "SM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "pomnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.dev-uk.bllab.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "TenGigE0/0/0/16/0"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-4X10G-LR-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "SM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "3587a2af-e79e-416f-974f-8f3ed8c84d70",
            "activity": "028465de-9a32-47af-8bf0-bd723c19b14e",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "pomnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.dev-uk.bllab.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "TenGigE0/7/0/11/1"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-4X10G-LR-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "SM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "pomnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.dev-uk.bllab.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "TenGigE0/0/0/16/1"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-4X10G-LR-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "SM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "59d9f55c-fd6c-42c7-91ea-3782b766cfe1",
            "activity": "3ca43fd4-be0d-41c4-bf0e-2974cd0abda0",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "thlon"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.dev-uk.bllab.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "TenGigE0/0/0/15/0"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-4X10G-LR-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "SM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "pomnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.dev-uk.bllab.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": ""},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-4X10G-LR-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "SM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "b0f566bb-daf4-4a5d-addd-d1487268b366",
            "activity": "30636e4f-80b8-4fa8-b2de-4915838c8dca",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "pomnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.dev-uk.bllab.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "TenGigE0/0/0/15/0"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": ""},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "SM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "pomnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.dev-uk.bllab.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "TenGigE0/0/0/16/1"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-4X10G-LR-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "SM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "8c08a4d8-6a3a-4688-b99d-8207d72a96c2",
            "activity": "5b27b183-fe17-4ca8-8c81-7ec3610d9ccf",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "pomnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta1.dev-uk.bllab.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "TenGigE0/0/0/15/2"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-4X10G-LR-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "SM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "LC"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "pomnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "sr16.dev-uk.bllab.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "7750-SR12"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Nokia"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "9/1/1"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "ALU-SFP-10G-SR"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "SM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "LC"},
            },
        },
        {
            "deliverable": "fa8f7875-8ca3-43c6-b92f-f825adea0463",
            "activity": "37004853-8ec3-4f90-a297-a4f4cd255cc8",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "pomnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta1.dev-uk.bllab.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "TenGigE0/0/0/16/2"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-4X10G-LR-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "SM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "LC"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "pomnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "sr16.dev-uk.bllab.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "7750-SR12"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Nokia"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "10/1/3"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "ALU-SFP-10G-SR"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "SM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "LC"},
            },
        },
        {
            "deliverable": "c5d17227-2660-43d0-9ee4-c4ba3156c4f3",
            "activity": "5ca25cb0-19c2-4537-895f-33f33bc74afb",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "bllon"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.dev-uk.bllab.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "TenGigE0/7/0/10/3"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-4X10G-LR-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "SM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "pomnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.dev-uk.bllab.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "TenGigE0/0/0/15/3"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-4X10G-LR-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "SM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "f36616ed-7989-4fa4-bbc6-50d9a5aea41e",
            "activity": "74cf8781-130c-40e6-ab4d-ebb26817d109",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "bllon"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.dev-uk.bllab.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "TenGigE0/7/0/11/3"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-4X10G-LR-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "SM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "pomnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.dev-uk.bllab.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "TenGigE0/0/0/16/3"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-4X10G-LR-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "SM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
        {
            "deliverable": "c4fbe878-44e9-4871-87dc-ca3a54f24a6f",
            "activity": "9597e7e0-74d5-45ca-9d60-e38a4f0d6b1b",
            "cells": {
                "location_aEnd": {"type": "string", "name": "location_aEnd", "value": "pomnc"},
                "hostName_aEnd": {"type": "string", "name": "hostName_aEnd", "value": "ta0.dev-uk.bllab.isp.sky.com"},
                "chassisModel_aEnd": {"type": "string", "name": "chassisModel_aEnd", "value": "NCS-5508"},
                "deviceVendor_aEnd": {"type": "string", "name": "deviceVendor_aEnd", "value": "Cisco"},
                "port_aEnd": {"type": "string", "name": "port_aEnd", "value": "TenGigE0/7/0/11/3"},
                "transceiver_aEnd": {"type": "string", "name": "transceiver_aEnd", "value": "CIS-QSFP-4X10G-LR-S"},
                "media_aEnd": {"type": "string", "name": "media_aEnd", "value": "SM"},
                "connector_aEnd": {"type": "string", "name": "connector_aEnd", "value": "MPO-12"},
                "location_bEnd": {"type": "string", "name": "location_bEnd", "value": "pomnc"},
                "hostName_bEnd": {"type": "string", "name": "hostName_bEnd", "value": "ta1.dev-uk.bllab.isp.sky.com"},
                "chassisModel_bEnd": {"type": "string", "name": "chassisModel_bEnd", "value": "NCS-5508"},
                "deviceVendor_bEnd": {"type": "string", "name": "deviceVendor_bEnd", "value": "Cisco"},
                "port_bEnd": {"type": "string", "name": "port_bEnd", "value": "TenGigE0/0/0/16/3"},
                "transceiver_bEnd": {"type": "string", "name": "transceiver_bEnd", "value": "CIS-QSFP-4X10G-LR-S"},
                "media_bEnd": {"type": "string", "name": "media_bEnd", "value": "SM"},
                "connector_bEnd": {"type": "string", "name": "connector_bEnd", "value": "MPO-12"},
            },
        },
    ],
}
uid = "dummy_uid"
dummy_token = "dummy_token"
headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer {0}".format(dummy_token),
}


def test_read_tg_service_instance():
    read_tgservice_obj = ReadTGService(userspace_kwarg, username, password)
    assert isinstance(read_tgservice_obj, ReadTGService)
    assert read_tgservice_obj.domain == userspace_kwarg["domain"]
    assert read_tgservice_obj.projectName == userspace_kwarg["projectName"]
    assert read_tgservice_obj.tgReference == userspace_kwarg["tgReference"]
    assert read_tgservice_obj.payloadUserSpaces == userspace_kwarg.get("userSpace")
    assert read_tgservice_obj.username == username
    assert read_tgservice_obj.password == password
    assert read_tgservice_obj.url == config.get(section="anp", key="uat_url")


@patch("connectors.core.services.anp.connector.ReadTGService.read_user_space_data")
@patch("connectors.core.services.anp.connector.ReadTGService.read_meta_data")
@patch("connectors.core.services.anp.connector.ReadTGService.get_token")
def test_read_tg(token_mock, read_meta_data_mock, read_user_space_data_mock):
    token_mock.return_value = "dummy_token"
    read_tgservice_obj = ReadTGService(metadata_kwarg, username, password)
    read_tgservice_obj.url = "dummy_url"
    read_meta_data_mock.return_value = {
        "success": True,
        "data": {
            "_links": {
                "self": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core/deliverables?reference=TG7399"},
                "parent": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core"},
            },
            "deliverables": [
                {
                    "_links": {
                        "self": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core/deliverables/834"},
                        "parent": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core/projects/35"},
                        "userspaces": {
                            "href": "https://insightandplanning-qa.sns.sky.com/ut/core/projects/35/userspaces"
                        },
                    },
                    "uid": "7c036094-c75b-4c7d-a5eb-5f5b9ef49701",
                    "name": "sr10.pomnc-pr2.hobir migration to ta0.pomnc",
                    "description": "",
                    "reference": "TG7399",
                    "impact": "low",
                    "status": "new",
                    "system": False,
                    "created": "2020-07-13T14:17:37.457799+01:00",
                    "effective_from": "2020-07-13T14:17:37.457799+01:00",
                    "dates": {"delivery": "None", "required": "2020-07-21"},
                    "managers": ["fiona.ochan@sky.uk"],
                }
            ],
        },
        "uid": "7c036094-c75b-4c7d-a5eb-5f5b9ef49701",
    }
    assert read_tgservice_obj.read_tg() == metadata_response

    read_tgservice_obj = ReadTGService(userspace_kwarg, username, password)
    read_tgservice_obj.url = "dummy_url"
    read_user_space_data_mock.return_value = {
        "success": True,
        "data": {
            "status": "success",
            "metadata": {
                "uid": "7c036094-c75b-4c7d-a5eb-5f5b9ef49701",
                "name": "sr10.pomnc-pr2.hobir migration to ta0.pomnc",
                "description": "",
                "reference": "TG7399",
                "impact": "low",
                "status": "new",
                "system": False,
                "created": "2020-07-13T14:17:37.457799+01:00",
                "effective_from": "2020-07-13T14:17:37.457799+01:00",
                "dates": {"delivery": "None", "required": "2020-07-21"},
                "managers": ["fiona.ochan@sky.uk"],
                "rows": [
                    {
                        "NDSS": {
                            "location_aEnd": "pomnc",
                            "hostName_aEnd": "sr10.pomnc.isp.sky.com",
                            "chassisModel_aEnd": "7750-SR12",
                            "deviceVendor_aEnd": "Nokia",
                            "port_aEnd": "2/2/1",
                            "transceiver_aEnd": "ALU-CFP-100G-LR4",
                            "media_aEnd": "SM",
                            "connector_aEnd": "LC",
                            "location_bEnd": "pomnc",
                            "hostName_bEnd": "ta0.pomnc.isp.sky.com",
                            "chassisModel_bEnd": "NCS-5508",
                            "deviceVendor_bEnd": "Cisco",
                            "port_bEnd": "HundredGigE0/3/0/35",
                            "transceiver_bEnd": "CIS-QSFP-100G-LR4-S",
                            "media_bEnd": "SM",
                            "connector_bEnd": "LC",
                        },
                        "Tx Design": {
                            "Transmission Circuit Reference": "None",
                            "Circuit No": "None",
                            "LLD and New 100G Required": "None",
                            "transmissionPort_aEnd": "None",
                            "transmissionPort_bEnd": "None",
                        },
                    },
                    {
                        "NDSS": {
                            "location_aEnd": "hobir",
                            "hostName_aEnd": "pr2.hobir.isp.sky.com",
                            "chassisModel_aEnd": "NCS-6008",
                            "deviceVendor_aEnd": "Cisco",
                            "port_aEnd": "HundredGigE0/6/0/0",
                            "transceiver_aEnd": "CIS-CPAK-100G-SR10",
                            "media_aEnd": "MM",
                            "connector_aEnd": "MPO-12",
                            "location_bEnd": "pomnc",
                            "hostName_bEnd": "ta0.pomnc.isp.sky.com",
                            "chassisModel_bEnd": "NCS-5508",
                            "deviceVendor_bEnd": "Cisco",
                            "port_bEnd": "HundredGigE0/0/0/0",
                            "transceiver_bEnd": "CIS-QSFP-100G-LR4-S",
                            "media_bEnd": "SM",
                            "connector_bEnd": "LC",
                        },
                        "Tx Design": {
                            "Transmission Circuit Reference": "None",
                            "Circuit No": "None",
                            "LLD and New 100G Required": "None",
                            "transmissionPort_aEnd": "None",
                            "transmissionPort_bEnd": "None",
                        },
                    },
                ],
            },
        },
    }
    assert read_tgservice_obj.read_tg() == userspacedata_response

    # Negative cases
    read_tgservice_obj = ReadTGService(metadata_kwarg_invalid, username, password)
    read_tgservice_obj.url = "dummy_url"
    read_meta_data_mock.return_value = {
        "success": False,
        "message": "Failed to get tg reference  data for tgreference: XXXX and domain: core ",
    }
    assert read_tgservice_obj.read_tg() == metadata_exception

    read_tgservice_obj = ReadTGService(userspace_kwarg_invalid, username, password)
    read_tgservice_obj.url = "dummy_url"
    read_user_space_data_mock.return_value = {
        "success": False,
        "message": "Failed to get tg reference  data for tgreference: XXXX and domain: core ",
    }
    assert read_tgservice_obj.read_tg() == userspacedata_exception


@patch("connectors.core.services.anp.connector.ReadTGService.get_cell_data")
@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_read_userspace_data(get_mock, get_cell_data_mock):
    read_tgservice_obj = ReadTGService(userspace_kwarg, username, password)
    read_tgservice_obj.url = "dummy_url"
    get_mock.return_value = {
        "_links": {
            "self": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core/projects/35/userspaces"},
            "parent": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core/projects/35"},
        },
        "userspaces": [
            {
                "_links": {
                    "self": {"href": "https://insightandplanning-qa.sns.sky.com/ut/userspaces/124"},
                    "parent": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core/projects/35"},
                    "cells": {"href": "https://insightandplanning-qa.sns.sky.com/ut/userspaces/124/cells"},
                },
                "uid": "32f92c77-901e-4f81-bfd1-68a80bd59d4e",
                "name": "NDSS",
                "description": None,
                "sequence": 10,
                "owner": "Alexandre.Jaron@sky.uk",
                "effective_from": "2020-07-13T12:42:57.399075+01:00",
                "locked": {},
                "schema": [
                    {"coltype": "string", "colname": "location_aEnd"},
                    {"coltype": "string", "colname": "hostName_aEnd"},
                    {"coltype": "string", "colname": "chassisModel_aEnd"},
                    {"coltype": "string", "colname": "deviceVendor_aEnd"},
                    {"coltype": "string", "colname": "port_aEnd"},
                    {"coltype": "string", "colname": "transceiver_aEnd"},
                    {"coltype": "string", "colname": "media_aEnd"},
                    {"coltype": "string", "colname": "connector_aEnd"},
                    {"coltype": "string", "colname": "location_bEnd"},
                    {"coltype": "string", "colname": "hostName_bEnd"},
                    {"coltype": "string", "colname": "chassisModel_bEnd"},
                    {"coltype": "string", "colname": "deviceVendor_bEnd"},
                    {"coltype": "string", "colname": "port_bEnd"},
                    {"coltype": "string", "colname": "transceiver_bEnd"},
                    {"coltype": "string", "colname": "media_bEnd"},
                    {"coltype": "string", "colname": "connector_bEnd"},
                ],
            },
            {
                "_links": {
                    "self": {"href": "https://insightandplanning-qa.sns.sky.com/ut/userspaces/125"},
                    "parent": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core/projects/35"},
                    "cells": {"href": "https://insightandplanning-qa.sns.sky.com/ut/userspaces/125/cells"},
                },
                "uid": "2875fc33-4c76-48a5-acf8-ad2a5f97b7e5",
                "name": "Tx Design",
                "description": None,
                "sequence": 20,
                "owner": "Alexandre.Jaron@sky.uk",
                "effective_from": "2020-07-13T12:42:57.842507+01:00",
                "locked": {},
                "schema": [
                    {"coltype": "string", "colname": "Transmission Circuit Reference"},
                    {"coltype": "string", "colname": "Circuit No"},
                    {"coltype": "string", "colname": "LLD and New 100G Required"},
                    {"coltype": "string", "colname": "transmissionPort_aEnd"},
                    {"coltype": "string", "colname": "transmissionPort_bEnd"},
                ],
            },
            {
                "_links": {
                    "self": {"href": "https://insightandplanning-qa.sns.sky.com/ut/userspaces/126"},
                    "parent": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core/projects/35"},
                    "cells": {"href": "https://insightandplanning-qa.sns.sky.com/ut/userspaces/126/cells"},
                },
                "uid": "823ed95b-b06c-460e-be41-555980aa6183",
                "name": "PMO and T&D",
                "description": None,
                "sequence": 30,
                "owner": "Alexandre.Jaron@sky.uk",
                "effective_from": "2020-07-13T15:07:49.990036+01:00",
                "locked": {},
                "schema": [
                    {"coltype": "string", "colname": "Logistics"},
                    {"coltype": "string", "colname": "Scheduled"},
                    {"coltype": "string", "colname": "Spark Ticket"},
                    {"coltype": "string", "colname": "Tier 3 Engineer"},
                    {"coltype": "string", "colname": "Field Engineer"},
                    {"coltype": "string", "colname": "CHG Ticket Status"},
                    {"coltype": "string", "colname": "Circuit Owner"},
                ],
            },
            {
                "_links": {
                    "self": {"href": "https://insightandplanning-qa.sns.sky.com/ut/userspaces/127"},
                    "parent": {"href": "https://insightandplanning-qa.sns.sky.com/ut/core/projects/35"},
                    "cells": {"href": "https://insightandplanning-qa.sns.sky.com/ut/userspaces/127/cells"},
                },
                "uid": "0caa301d-e32f-452d-82ab-9adeabe3bc05",
                "name": "Ops Implementation",
                "description": None,
                "sequence": 40,
                "owner": "Alexandre.Jaron@sky.uk",
                "effective_from": "2020-07-13T18:30:11.359184+01:00",
                "locked": {},
                "schema": [
                    {"coltype": "string", "colname": "rack_aEnd"},
                    {"coltype": "string", "colname": "length_aEnd"},
                    {"coltype": "string", "colname": "rack_bEnd"},
                    {"coltype": "string", "colname": "length_bEnd"},
                ],
            },
        ],
    }
    get_cell_data_mock.return_value = [
        {
            "NDSS": {
                "deliverable": "7c036094-c75b-4c7d-a5eb-5f5b9ef49701",
                "activity": "a3caa154-bb4e-49b8-aaf2-75970fccf5ea",
                "cells": {
                    "location_aEnd": "hobir",
                    "hostName_aEnd": "pr2.hobir.isp.sky.com",
                    "chassisModel_aEnd": "NCS-6008",
                    "deviceVendor_aEnd": "Cisco",
                    "port_aEnd": "HundredGigE0/6/0/0",
                    "transceiver_aEnd": "CIS-CPAK-100G-SR10",
                    "media_aEnd": "MM",
                    "connector_aEnd": "MPO-12",
                    "location_bEnd": "pomnc",
                    "hostName_bEnd": "ta0.pomnc.isp.sky.com",
                    "chassisModel_bEnd": "NCS-5508",
                    "deviceVendor_bEnd": "Cisco",
                    "port_bEnd": "HundredGigE0/0/0/0",
                    "transceiver_bEnd": "CIS-QSFP-100G-LR4-S",
                    "media_bEnd": "SM",
                    "connector_bEnd": "LC",
                },
            }
        },
        {
            "NDSS": {
                "deliverable": "7c036094-c75b-4c7d-a5eb-5f5b9ef49701",
                "activity": "c16afe91-f9dc-443b-91a4-8a0de046ccda",
                "cells": {
                    "location_aEnd": "pomnc",
                    "hostName_aEnd": "sr10.pomnc.isp.sky.com",
                    "chassisModel_aEnd": "7750-SR12",
                    "deviceVendor_aEnd": "Nokia",
                    "port_aEnd": "2/2/1",
                    "transceiver_aEnd": "ALU-CFP-100G-LR4",
                    "media_aEnd": "SM",
                    "connector_aEnd": "LC",
                    "location_bEnd": "pomnc",
                    "hostName_bEnd": "ta0.pomnc.isp.sky.com",
                    "chassisModel_bEnd": "NCS-5508",
                    "deviceVendor_bEnd": "Cisco",
                    "port_bEnd": "HundredGigE0/3/0/35",
                    "transceiver_bEnd": "CIS-QSFP-100G-LR4-S",
                    "media_bEnd": "SM",
                    "connector_bEnd": "LC",
                },
            }
        },
    ]
    assert (
        read_tgservice_obj.read_user_space_data(
            headers, read_tgservice_obj.projectName, ["NDSS", "Tx Design"], parent_projects_data
        )
        == userspace_response
        or userspace_response_1
    )


@patch("connectors.core.utils.rest_api_utility.RestUtility.get")
def test_get_cell_data(get_mock):
    read_tgservice_obj = ReadTGService(userspace_kwarg, username, password)
    read_tgservice_obj.url = "dummy_url"
    get_mock.return_value = cell_data
    assert read_tgservice_obj.get_cell_data("dummy_user_space_row_data_url", "NDSS", uid, headers) == []
    assert read_tgservice_obj.get_cell_data("dummy_user_space_row_data_url", "Tx Design", uid, headers) == []

    read_tgservice_obj = ReadTGService(userspace_kwarg, username, password)
    read_tgservice_obj.url = "dummy_url"
    get_mock.return_value = {"_links": {"self": {"href": ""}, "parent": {"href": ""}}, "rows": []}
    assert read_tgservice_obj.get_cell_data("dummy_user_space_row_data_url", "NDSS", uid, headers) == []


# Negative cases
@patch("connectors.core.services.anp.connector.ReadTGService.read_tg")
def test_read_metadata(read_mock):
    read_mock.return_value = metadata_response
    metadata_kwargs = {
        "domain": "core",
        "projectName": "Sacramento",
        "tgReference": "TG7399",
        "user": "ipnd_dne_ops_dev",
        "token_info": {
            "sub": "ipnd_dne_ops_dev",
            "scopes": "orch:read orch:write dial:write dial:read connector:read " "connector:write",
        },
    }

    assert read.read_tg_reference(**metadata_kwargs) == metadata_response


@patch("connectors.core.services.anp.connector.ReadTGService.read_tg")
def test_read_userspacedata(read_mock):
    read_mock.return_value = userspacedata_response
    userspace_kwargs = {
        "domain": "core",
        "projectName": "Sacramento",
        "tgReference": "TG7399",
        "userSpace": ["NDSS", "Tx Design"],
        "user": "ipnd_dne_ops_dev",
        "token_info": {
            "sub": "ipnd_dne_ops_dev",
            "scopes": "orch:read orch:write dial:write dial:read connector:read " "connector:write",
        },
    }
    assert read.read_tg_reference(**userspace_kwargs) == userspacedata_response
