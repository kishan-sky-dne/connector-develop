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
import ast
import logging
import re

# DNE Library
from connectors.core.config.connectors_config import config

logger = logging.getLogger(__name__)

"""
List of hostname regex patterns and their corresponding TSR network domains.

Changes to this file may cause critical failures to the entirety of DNE Core.
Do not make changes unless explicity requested to by Technical Leads.

Do not add catch-all patterns to the top of the list until specifically requested.
The first pattern matched for a hostname is returned, so this may result in incorrect matches.

Format:
    (<regex_pattern>, "readable_pattern": <pattern>, "tsr_domain": <domain>}
"""

HOSTNAME_MAPPING = [
    ################################################################################
    # '.tci.' specific patterns must be first to avoid matching other patterns.
    {
        "regex_pattern": r"^ar(0|1)\.(gyhhe|gyslo)\.isp\.sky\.com",
        "readable_pattern": "ar#.<site>",
        "tsr_domain": "other",
        "role": "data-centre",
        "readable_role": "Data Centre",
    },
    {
        "regex_pattern": r"^er15\.(bllon|enlba|enslo|mimnc)\.isp\.sky\.com",
        "readable_pattern": "er##.<site>",
        "tsr_domain": "core",
        "role": "mobile-peering",
        "readable_role": "Mobile Peering",
    },
    {
        "regex_pattern": r"^er14\.(bllon|thlon)\.isp\.sky\.com",
        "readable_pattern": "er##.<site>",
        "tsr_domain": "core",
        "role": "easynet",
        "readable_role": "Easynet",
    },
    {
        "regex_pattern": r"^ar(0|1)-sky\.syetr\.isp\.sky\.com",
        "readable_pattern": "ar#-sky.<site>",
        "tsr_domain": "other",
        "role": "eistree",
        "readable_role": "studio campus for content production",
    },
    {
        "regex_pattern": r"^ar(0|1)\.(rmsa1|mimp1)\.it\.bb\.sky\.com",
        "readable_pattern": "ar#.<site>",
        "tsr_domain": "other",
        "role": "enterprise",
        "readable_role": "Enterprise",
    },
    {
        "regex_pattern": r"^ar(0|1)\.(test|stage)\.sglab\.it\.bb\.sky\.com",
        "readable_pattern": "ar#.<site>",
        "tsr_domain": "other",
        "role": "enterprise",
        "readable_role": "Enterprise",
    },
    {
        "regex_pattern": r"^ar(0|1)\.(mpmil|clmil)\.it\.isp\.sky\.com",
        "readable_pattern": "ar#.<site>",
        "tsr_domain": "other",
        "role": "rainbow",
        "readable_role": "Rainbow",
    },
    {
        "regex_pattern": r"^ar(2|3)\.(a1ahm|mume1)\.de\.isp\.sky\.com",
        "readable_pattern": "ar#.<site>",
        "tsr_domain": "other",
        "role": "rainbow",
        "readable_role": "Rainbow",
    },
    {"regex_pattern": r"^sp\d\.tci\.", "readable_pattern": "sp#.tci.", "tsr_domain": "other", "role": "telco-cloud"},
    {"regex_pattern": r"^as\d\.tci\.", "readable_pattern": "as#.tci.", "tsr_domain": "other", "role": "telco-cloud"},
    {
        "regex_pattern": r"^ls\d-voice\.tci\.",
        "readable_pattern": "ls#-voice.tci.",
        "tsr_domain": "other",
        "role": "telco-cloud",
    },
    {
        "regex_pattern": r"^nfm\d\d\.tci\.",
        "readable_pattern": "nfm##.tci.",
        "tsr_domain": "other",
        "role": "telco-cloud",
    },
    {
        "regex_pattern": r"^nvsc\d\d\.tci\.",
        "readable_pattern": "nvsc##.tci.",
        "tsr_domain": "other",
        "role": "telco-cloud",
    },
    {"regex_pattern": r"^os\d\.tci\.", "readable_pattern": "os#.tci.", "tsr_domain": "other", "role": "telco-cloud"},
    {"regex_pattern": r"^sp\d\.tci\.", "readable_pattern": "sp#.tci.", "tsr_domain": "other", "role": "telco-cloud"},
    {"regex_pattern": r"^sr\d\.tci\.", "readable_pattern": "sr#.tci.", "tsr_domain": "other", "role": "telco-cloud"},
    ################################################################################
    # Legacy/Global
    {
        "regex_pattern": r"^ar\d-cdn\.",
        "readable_pattern": "ar#-cdn",
        "tsr_domain": "legacy",
        "role": "cdn",
        "readable_role": "CDN",
    },  # Only used in Italy?
    ################################################################################
    # Unmapped/subscriber
    {
        "regex_pattern": r"^tr\d\.",
        "readable_pattern": "tr#",
        "tsr_domain": "subscriber",
        "role": "subscriber",
    },  # Not automated.
    {
        "regex_pattern": r"^tr\d\d\.",
        "readable_pattern": "tr##",
        "tsr_domain": "subscriber",
        "role": "subscriber",
    },  # Not automated.
    {"regex_pattern": r"^bs\d\.", "readable_pattern": "bs#", "tsr_domain": "subscriber", "role": "subscriber"},
    {
        "regex_pattern": r"^br\d-dist\.",
        "readable_pattern": "br#-dist",
        "tsr_domain": "core",
        "role": "subscriber",
    },
    {
        "regex_pattern": r"^br\d\.",  # In the lab, we only have br#. rather than cent/dist specific devices
        "readable_pattern": "br#",
        "tsr_domain": "core",
        "role": "subscriber",
    },
    {
        "regex_pattern": r"^br\d-cent\.",
        "readable_pattern": "br#-cent",
        "tsr_domain": "core",
        "role": "subscriber",
    },
    {"regex_pattern": r"^sr\d\d\.", "readable_pattern": "sr##", "tsr_domain": "core", "role": "bng"},  # BNG
    ################################################################################
    # Core
    {
        "regex_pattern": r"^pr\d\.",
        "readable_pattern": "pr#",
        "tsr_domain": "core",
        "role": "super-core",
        "readable_role": "Supercore",
    },
    {
        "regex_pattern": r"^er\d{3}\.(frha1|thlon)\.group\.",
        "readable_pattern": "er###.<site>.group",
        "tsr_domain": "core",
        "role": "group-peer-and-transit",
        "readable_role": "Group Peering & Transit",
    },
    {
        "regex_pattern": r"^er\d{3}\.(bllon)\.group\.",
        "readable_pattern": "er###.<site>.group",
        "tsr_domain": "core",
        "role": "group-asbr",
        "readable_role": "Group ASBR",
    },
    {
        "regex_pattern": r"^er\d{3}.*.group.",
        "readable_pattern": "er###.<site>.group",
        "tsr_domain": "core",
        "role": "group-peer-and-transit",
        "readable_role": "Group Peering & Transit",
    },
    {
        "regex_pattern": r"^er\d\.",
        "readable_pattern": "er#",
        "tsr_domain": "core",
        "role": "peer-and-transit",
        "readable_role": "Peering & Transit",
    },
    {
        "regex_pattern": r"^er\d\d\.",
        "readable_pattern": "er##",
        "tsr_domain": "core",
        "role": "peer-and-transit",
        "readable_role": "Peering & Transit",
    },
    {
        "regex_pattern": r"^er\d{1,3}-voicembl\.",
        "readable_pattern": "er#-voicembl",
        "tsr_domain": "core",
        "role": "mobile-peering",
        "readable_role": "Mobile Peering",
    },
    {"regex_pattern": r"^rr\d\.", "readable_pattern": "rr#", "tsr_domain": "core", "role": "core"},  # Clarify role
    {
        "regex_pattern": r"^rr\d\d\d\.",
        "readable_pattern": "rr###",
        "readable_role": "Route Reflector",
        "tsr_domain": "core",
        "role": "rr",
    },
    {
        "regex_pattern": r"^rr\d{1,3}-cont\.",
        "readable_pattern": "rr#-cont",
        "readable_role": "Contribution Route Reflector",
        "tsr_domain": "core",
        "role": "cont-rr",
    },
    {
        "regex_pattern": r"^ta\d\.",
        "readable_pattern": "ta#",
        "tsr_domain": "core",
        "role": "transport-agg",
        "readable_role": "Transport Aggregation",
    },
    {
        "regex_pattern": r"^ta\d\d\.",
        "readable_pattern": "ta##",
        "tsr_domain": "core",
        "role": "transport-agg",
        "readable_role": "TEMPORARY Transport Aggregation for BNG-FO",
    },
    {
        "regex_pattern": r"^pr\d\d\d\.*.group.",
        "readable_pattern": "pr#",
        "tsr_domain": "core",
        "role": "group-super-core",  # Bugfix: DNE-35701
        "readable_role": "Group Supercore",
    },
    {
        "regex_pattern": r"^pr\d\d\d\.",
        "readable_pattern": "pr#",
        "tsr_domain": "core",
        "role": "super-core",  # Bugfix: DNE-35701
        "readable_role": "Supercore",
    },
    ################################################################################
    # Metro
    {
        "regex_pattern": r"^ma\d+\.",
        "readable_pattern": "ma#",
        "tsr_domain": "metro",
        "role": "metro-agg",
        "readable_role": "Metro Aggregation",
    },
    {
        "regex_pattern": r"^ma\d+\.",
        "readable_pattern": "ma##",
        "tsr_domain": "metro",
        "role": "metro-agg",
        "readable_role": "Metro Aggregation",
    },
    {"regex_pattern": r"^me\d\.", "readable_pattern": "me#", "tsr_domain": "metro", "role": "metro"},
    {"regex_pattern": r"^me\d\d\.", "readable_pattern": "me##", "tsr_domain": "metro", "role": "metro"},
    {"regex_pattern": r"^as\d\.", "readable_pattern": "as#", "tsr_domain": "metro", "role": "metro"},
    {"regex_pattern": r"^as\d\d\d\.", "readable_pattern": "as###", "tsr_domain": "metro", "role": "metro"},
    {"regex_pattern": r"^as\d\d\.", "readable_pattern": "as##", "tsr_domain": "metro", "role": "metro"},
    {"regex_pattern": r"^ar\d\d\.", "readable_pattern": "ar##", "tsr_domain": "metro", "role": "metro"},
    ################################################################################
    # Access (note these will not be supported by DNE)
    {"regex_pattern": r"^cr\d\.", "readable_pattern": "cr0#", "tsr_domain": "access", "role": "access"},
    {"regex_pattern": r"^vm\d\.", "readable_pattern": "vm#", "tsr_domain": "access", "role": "access"},
    {"regex_pattern": r"^vm\d\d\.", "readable_pattern": "vm##", "tsr_domain": "access", "role": "access"},
    {"regex_pattern": r"^bm\d\.", "readable_pattern": "bm#", "tsr_domain": "access", "role": "access"},
    {"regex_pattern": r"^bm\d\d\.", "readable_pattern": "bm##", "tsr_domain": "access", "role": "access"},
    {"regex_pattern": r"^fm\d\.", "readable_pattern": "fm#", "tsr_domain": "access", "role": "access"},
    {"regex_pattern": r"^cmts\d\.", "readable_pattern": "cmts#", "tsr_domain": "access", "role": "access"},
    ################################################################################
    # Other
    {
        "regex_pattern": r"^ar\d{1,3}-cdn.*.group.",
        "readable_pattern": "ar###-cdn.#.group",
        "tsr_domain": "other",
        "role": "group-cdn",
        "readable_role": "group CDN",
    },
    {
        "regex_pattern": r"^ar\d\d-cdn\.",
        "readable_pattern": "ar##-cdn",
        "tsr_domain": "other",
        "role": "cdn",
        "readable_role": "CDN",
    },
    {
        "regex_pattern": r"^ar2\d\.",
        "readable_pattern": "ar2#",
        "tsr_domain": "other",
        "role": "cdn",
        "readable_role": "CDN",
    },
    {
        "regex_pattern": r"^glb\d-cdn\.",
        "readable_pattern": "glb#-cdn",
        "tsr_domain": "other",
        "role": "cdn",
        "readable_role": "CDN",
    },
    {"regex_pattern": r"^os\d\d\.", "readable_pattern": "os##", "tsr_domain": "other", "role": "dcn"},
    {"regex_pattern": r"^or\d\.", "readable_pattern": "or#", "tsr_domain": "other", "role": "dcn"},
    {"regex_pattern": r"^wbm\d\.", "readable_pattern": "wbm#", "tsr_domain": "other", "role": "witness"},
    {"regex_pattern": r"^os\d\.", "readable_pattern": "os#", "tsr_domain": "other", "role": "dcn"},
    {
        "regex_pattern": r"^da\d\.",
        "readable_pattern": "da#",
        "tsr_domain": "other",
        "role": "cdn",
        "readable_role": "CDN",
    },
    {
        "regex_pattern": r"^da\d\d\.",
        "readable_pattern": "da##",
        "tsr_domain": "other",
        "role": "cdn",
        "readable_role": "CDN",
    },
    {
        "regex_pattern": r"^rs\d-cdn\.",
        "readable_pattern": "rs#-cdn",
        "readable_role": "CDN",
        "tsr_domain": "other",
        "role": "cdn",
    },  # Clarify role
    {"regex_pattern": r"^aaa\d\.", "readable_pattern": "sr#", "tsr_domain": "other", "role": "aaa"},
    {"regex_pattern": r"^sr\d\.", "readable_pattern": "sr#", "tsr_domain": "other", "role": "application_router"},
    {"regex_pattern": r"^cm\d\.", "readable_pattern": "cm#", "tsr_domain": "other", "role": "console_server"},
    {"regex_pattern": r"^cm\d\d\.", "readable_pattern": "cm##", "tsr_domain": "other", "role": "console_server"},
    {"regex_pattern": r"^cm\d\d\d\.", "readable_pattern": "cm###", "tsr_domain": "other", "role": "console_server"},
    {
        "regex_pattern": r"^cr\d-sky\.",
        "readable_pattern": "cr#-sky",
        "tsr_domain": "other",
        "role": "enterprise",
        "readable_role": "Enterprise",
    },  # Customer-sky
    {"regex_pattern": r"^ds\d-ether\.", "readable_pattern": "ds#-ether", "tsr_domain": "other"},
    {"regex_pattern": r"^cs\d-secuni\.", "readable_pattern": "cs#-secuni", "tsr_domain": "other"},  # security:facility
    {"regex_pattern": r"^as\d-bms\.", "readable_pattern": "as#-bms", "tsr_domain": "other"},  # facility
    {
        "regex_pattern": r"^ar\d\d-rm\.",
        "readable_pattern": "ar##-rm",
        "tsr_domain": "other",
        "role": "rainman",
        "readable_role": "Rainman",
    },  # rainman
    {"regex_pattern": r"^as\d\d-rm\.", "readable_pattern": "as##-rm", "tsr_domain": "other"},  # rainman
    {"regex_pattern": r"^if\d\d-rm\.", "readable_pattern": "if##-rm", "tsr_domain": "other"},  # rainman
    {"regex_pattern": r"^ls\d\d-rm\.", "readable_pattern": "ls##-rm", "tsr_domain": "other"},  # rainman
    {"regex_pattern": r"^ar\d-is\.", "readable_pattern": "ar#-is", "tsr_domain": "other"},  # information systems
    {"regex_pattern": r"^as\d-is\.", "readable_pattern": "as#-is", "tsr_domain": "other"},  # information systems
    {"regex_pattern": r"^as\d\d-is\.", "readable_pattern": "as##-is", "tsr_domain": "other"},  # information systems
    {"regex_pattern": r"^as1\d\d-is\.", "readable_pattern": "as1##-is", "tsr_domain": "other"},  # information systems
    {"regex_pattern": r"^is1\d\d-is\.", "readable_pattern": "is1##-is", "tsr_domain": "other"},  # information systems
    {"regex_pattern": r"^ls\d-is\.", "readable_pattern": "ls#-is", "tsr_domain": "other"},  # information systems
    {"regex_pattern": r"^ls1\d\d-is\.", "readable_pattern": "ls1##-is", "tsr_domain": "other"},  # information systems
    {
        "regex_pattern": r"^ar\d\d-isp\.",
        "readable_pattern": "ar##-isp",
        "tsr_domain": "other",
        "role": "ironman",
        "readable_role": "Ironman",
    },  # isp services
    {"regex_pattern": r"^as\d\d-isp\.", "readable_pattern": "as##-isp", "tsr_domain": "other"},  # isp services
    {"regex_pattern": r"^cs\d-isp\.", "readable_pattern": "cs#-isp", "tsr_domain": "other"},  # isp services
    {"regex_pattern": r"^glb\d\d-isp\.", "readable_pattern": "glb##-isp", "tsr_domain": "other"},  # isp services
    {"regex_pattern": r"^is\d\d-isp\.", "readable_pattern": "is##-isp", "tsr_domain": "other"},  # isp services
    {"regex_pattern": r"^ls\d\d-isp\.", "readable_pattern": "ls##-isp", "tsr_domain": "other"},  # isp services
    {
        "regex_pattern": r"^ar\d{1,2}-nme\.",
        "readable_pattern": "ar#-nme",
        "tsr_domain": "other",
        "role": "nme",
        "readable_role": "Network Management Centre",
    },  # network management
    {
        "regex_pattern": r"^if\d-nme\.",
        "readable_pattern": "if#-nme",
        "tsr_domain": "other",
        "role": "firewall",
    },  # network management
    {"regex_pattern": r"^if\d\d\.", "readable_pattern": "if##", "tsr_domain": "other", "role": "firewall"},
    {
        "regex_pattern": r"^ge\d-\d-\d{3}\.if\d\.",
        "readable_pattern": "ge#-#-###.if#",
        "tsr_domain": "other",
        "role": "firewall",
    },
    {
        "regex_pattern": r"^vip.if\d\d-nme\.",
        "readable_pattern": "vip.if##-nme",
        "tsr_domain": "other",
        "role": "firewall",
    },
    {
        "regex_pattern": r"^vl\d{1,3}.if\d{1,2}\.",
        "readable_pattern": "vl###.if#(#)",
        "tsr_domain": "other",
        "role": "firewall",
    },
    {"regex_pattern": r"^ups\d\.", "readable_pattern": "ups#", "tsr_domain": "other", "role": "power_supply"},
    {"regex_pattern": r"^ls\d\.", "readable_pattern": "ls#", "tsr_domain": "other", "role": "load_balancer"},
    {
        "regex_pattern": r"^sky-.*-(vprime|pano|iewscr|icffw)",
        "readable_pattern": "sky-<>-(vprime|pano|iewscr|icffw)",
        "tsr_domain": "other",
        "role": "load_balancer",
    },
    {
        "regex_pattern": r"^ost(b|i)-mwr-\d{3}\.",
        "readable_pattern": "ost(b|i)-mwr-###",
        "tsr_domain": "other",
        "role": "transmission",
    },
    {
        "regex_pattern": r"^sl(eml|nsp|otn|pkt|pr)\d\.",
        "readable_pattern": "sl(eml|nsp|otn|pkt|pr)#",
        "tsr_domain": "other",
        "role": "transmission",
    },
    {
        "regex_pattern": r"^bl(eml|nsp|otne|pkt|pr)\d\.",
        "readable_pattern": "sl(eml|nsp|otne|pkt|pr)#",
        "tsr_domain": "other",
        "role": "transmission",
    },
    {
        "regex_pattern": r"^bv\d\d\.if\d{1,2}\.",
        "readable_pattern": "bv##.if(#|##)",
        "tsr_domain": "other",
        "role": "firewall",
    },
    {
        "regex_pattern": r"^ida\d{1,2}\.moon\.[a-z]{5}\.cdn\.",
        "readable_pattern": "ida#.moon.<site>.cdn",
        "tsr_domain": "other",
        "role": "cdn",
    },
    {"regex_pattern": r"^ir\d\.", "readable_pattern": "ir#", "tsr_domain": "other", "role": "internal:office"},
    {"regex_pattern": r"^is\d\.", "readable_pattern": "is#", "tsr_domain": "other", "role": "internal:office"},
    {"regex_pattern": r"^mr\d-ct\.", "readable_pattern": "mr#-ct", "tsr_domain": "other", "role": "ct"},
    {"regex_pattern": r"^mr\d-tvob\.", "readable_pattern": "mr#-tvob", "tsr_domain": "other", "role": "broadcast"},
    {"regex_pattern": r"^mr\d{1,2}-dvn\.", "readable_pattern": "mr#-dvn", "tsr_domain": "other", "role": "broadcast"},
    {"regex_pattern": r"^mr\d-wbmc\.", "readable_pattern": "mr#-wbmc ", "tsr_domain": "other", "role": "witness"},
    ################################################################################
    # Mobile
    {
        "regex_pattern": r"^ar\d-mbl\.",
        "readable_pattern": "ar#-mbl",
        "tsr_domain": "mobile",
        "role": "mobile",
        "readable_role": "Mobile",
    },
    {"regex_pattern": r"^as\d-mbl\.", "readable_pattern": "as#-mbl", "tsr_domain": "mobile"},
    {"regex_pattern": r"^as\d\d-mbl\.", "readable_pattern": "as##-mbl", "tsr_domain": "mobile"},
    {"regex_pattern": r"^if\d-mbl\.", "readable_pattern": "if#-mbl", "tsr_domain": "mobile"},
    {"regex_pattern": r"^ls\d-mbl\.", "readable_pattern": "ls#-mbl", "tsr_domain": "mobile"},
    {"regex_pattern": r"^8e\d\d\.", "readable_pattern": "8e##", "tsr_domain": "mobile"},
    {"regex_pattern": r"^aaadatalsw\d\d\.", "readable_pattern": "aaadatalsw00##", "tsr_domain": "mobile"},
    {"regex_pattern": r"^imsfw\d\d", "readable_pattern": "imsfw##", "tsr_domain": "mobile"},
    {"regex_pattern": r"^imslsw\d\d", "readable_pattern": "imslsw##", "tsr_domain": "mobile"},
    {
        "regex_pattern": r"^swbservice-vas\d\dsub\d\.",
        "readable_pattern": "swbservice-vas##sub#",
        "tsr_domain": "mobile",
    },
    {"regex_pattern": r"^swlsw\d(a|b)*\.", "readable_pattern": "swlsw#", "tsr_domain": "mobile"},
    {"regex_pattern": r"^sdblsw\d\d\.", "readable_pattern": "sdblsw##", "tsr_domain": "mobile"},
    {"regex_pattern": r"^spslsw\d\d\.", "readable_pattern": "spslsw##", "tsr_domain": "mobile"},
    {"regex_pattern": r"^u2000lsw\d\d\.", "readable_pattern": "u2000lsw##", "tsr_domain": "mobile"},
    {"regex_pattern": r"^uimlsw\d\d\.", "readable_pattern": "uimlsw##", "tsr_domain": "mobile"},
    {"regex_pattern": r"swboam-vas\d\dsub\d\.", "readable_pattern": "swboam-vas##sub#", "tsr_domain": "mobile"},
    {"regex_pattern": r"^swboam-ocs\d\dsub\d\.", "readable_pattern": "swboam-ocs##sub#", "tsr_domain": "mobile"},
    {
        "regex_pattern": r"^swbreplication-ocs\d\dsub\d\.",
        "readable_pattern": "swbreplication-ocs##sub#",
        "tsr_domain": "mobile",
    },
    {
        "regex_pattern": r"^swbservice-ocs\d\dsub\d\.",
        "readable_pattern": "swbservice-ocs##sub#",
        "tsr_domain": "mobile",
    },
    {"regex_pattern": r"icap\d\d\.", "readable_pattern": "icap##", "tsr_domain": "mobile"},
    {"regex_pattern": r"^pgw\d\d\.", "readable_pattern": "pgw##", "tsr_domain": "mobile"},
    {"regex_pattern": r"^sps\d\d\.", "readable_pattern": "sps##", "tsr_domain": "mobile"},
    {"regex_pattern": r"^swfw1(a|b)\.", "readable_pattern": "swfw1", "tsr_domain": "mobile"},
    {"regex_pattern": r"^vms1(a|b)-mobile\.", "readable_pattern": "vms1-mobile", "tsr_domain": "mobile"},
    {"regex_pattern": r"^drvms1-mobile\.", "readable_pattern": "drvms1-mobile", "tsr_domain": "mobile"},
    {"regex_pattern": r"^vmsnode\d-mobile\.", "readable_pattern": "vmsnode#-mobile", "tsr_domain": "mobile"},
    {"regex_pattern": r"^cgn\d\d\.", "readable_pattern": "cgn##", "tsr_domain": "mobile"},
    {
        "regex_pattern": r"^ar\d-mbl-",
        "readable_pattern": "ar#-mbl-",
        "tsr_domain": "mobile",
        "role": "mobile",
        "readable_role": "Mobile",
    },
    {"regex_pattern": r"^sdbfablsw\d*\.", "readable_pattern": "sdbfablsw##", "tsr_domain": "mobile"},
    {"regex_pattern": r"^cmgdata\d\d\.", "readable_pattern": "cmgdata##", "tsr_domain": "mobile"},
    {
        "regex_pattern": r"^fortinet-fortimanager-fe\d\.",
        "readable_pattern": "fortinet-fortimanager-fe#",
        "tsr_domain": "mobile",
    },
    ################################################################################
    # Voice
    {"regex_pattern": r"^as\d*-ims\.", "readable_pattern": "as#-ims", "tsr_domain": "voice", "role": "voice"},
    {"regex_pattern": r"^as\d\d-ims\.", "readable_pattern": "as##-ims", "tsr_domain": "voice", "role": "voice"},
    {"regex_pattern": r"\.voice\.", "readable_pattern": ".voice.", "tsr_domain": "voice", "role": "voice"},
    {"regex_pattern": r"^cmgvoice\d\d\.", "readable_pattern": "cmgvoice##", "tsr_domain": "voice", "role": "voice"},
    {"regex_pattern": r"^arl\d\d\.dra\.", "readable_pattern": "arl##.dra", "tsr_domain": "voice", "role": "voice"},
    {"regex_pattern": r"^cr\d-skyvoip\.", "readable_pattern": "cr#-skyvoip", "tsr_domain": "voice", "role": "voice"},
    {"regex_pattern": r"\.voice\.", "readable_pattern": ".voice.", "tsr_domain": "voice", "role": "voice"},
    {"regex_pattern": r"^as\d*-skyvoip\.", "readable_pattern": "as#-skyvoip", "tsr_domain": "voice", "role": "voice"},
    {"regex_pattern": r"^bbusbc\d(a|b)\.", "readable_pattern": "bbusbc#(a|b)", "tsr_domain": "voice", "role": "voice"},
    {"regex_pattern": r"^ctpci(a|b)\.", "readable_pattern": "ctpci(a|b)", "tsr_domain": "voice", "role": "voice"},
    {"regex_pattern": r"^drvms\d-fixed\.", "readable_pattern": "drvms#-fixed", "tsr_domain": "voice", "role": "voice"},
    {"regex_pattern": r"^insbc\d(a|b)\.", "readable_pattern": "insbc#(a|b)", "tsr_domain": "voice", "role": "voice"},
    {"regex_pattern": r"^isipsbc(a|b)\.", "readable_pattern": "isipsbc(a|b)", "tsr_domain": "voice", "role": "voice"},
    {"regex_pattern": r"^ospsbc\d(a|b)\.", "readable_pattern": "ospsbc#(a|b)", "tsr_domain": "voice", "role": "voice"},
    {"regex_pattern": r"^psb\d(a|b)\.", "readable_pattern": "psb#(a|b)", "tsr_domain": "voice", "role": "voice"},
    {"regex_pattern": r"^enhmimrf-dmrf\.", "readable_pattern": "enhmimrf-dmrf", "tsr_domain": "voice", "role": "voice"},
    {"regex_pattern": r"^ovoc\d\.", "readable_pattern": "ovoc#", "tsr_domain": "voice", "role": "voice"},
    {"regex_pattern": r"^sasbc\d(a|b)\.", "readable_pattern": "sasbc#(a|b)", "tsr_domain": "voice", "role": "voice"},
    {"regex_pattern": r"^A2-", "readable_pattern": "ls#", "tsr_domain": "voice", "role": "voice"},
    {"regex_pattern": r"^vms-mgmt\.", "readable_pattern": "vms-mgmt", "tsr_domain": "voice", "role": "voice"},
    {
        "regex_pattern": r"^vms\d(a|b)-fixed\.",
        "readable_pattern": "vms#(a|b)-fixed",
        "tsr_domain": "voice",
        "role": "voice",
    },
    {
        "regex_pattern": r"^vmsnode\d-fixed\.",
        "readable_pattern": "vmsnode#-fixed",
        "tsr_domain": "voice",
        "role": "voice",
    },
    {"regex_pattern": r"^voxsbc\d(a|b)\.", "readable_pattern": "voxsbc#(a|b)", "tsr_domain": "voice", "role": "voice"},
    {"regex_pattern": r"^vsldr\d\.", "readable_pattern": "vsldr#", "tsr_domain": "voice", "role": "voice"},
    {"regex_pattern": r"^vslmngtdr\.", "readable_pattern": "vslmgmtdr", "tsr_domain": "voice", "role": "voice"},
    {"regex_pattern": r"^rsm\d\.", "readable_pattern": "rsm#", "tsr_domain": "voice", "role": "voice"},
    {
        "regex_pattern": r"^mr\d*-skyvoip\.",
        "readable_pattern": "mr#-skyvoip",
        "tsr_domain": "voice",
        "role": "voice_ipsla",
    },
    {"regex_pattern": r"^mr\d{1,2}\.", "readable_pattern": "mr#", "tsr_domain": "voice", "role": "voice_ipsla"},
    {
        "regex_pattern": r"^as\d*-ncp\.",
        "readable_pattern": "as#-ncp",
        "tsr_domain": "voice",
        "role": "voice:nuisance_call",
    },
    ################################################################################
    {
        "regex_pattern": r"^ar\d-ct\.",
        "readable_pattern": "ar#-ct",
        "tsr_domain": "ct",
        "readable_role": "Customer Telephony",
        "role": "customer-telephony",
    },
    {"regex_pattern": r"^as\d-ct\.", "readable_pattern": "as#-ct", "tsr_domain": "ct"},
    {
        "regex_pattern": r"^ar\d-ctlab\.",
        "readable_pattern": "ar#-ctlab",
        "tsr_domain": "ct",
        "readable_role": "Customer Telephony",
        "role": "customer-telephony",
    },
    {
        "regex_pattern": r"^ar\d-nce\.",
        "readable_pattern": "ar#-nce",
        "tsr_domain": "nce",
        "role": "nce",
        "readable_role": "Network Cloud Engine",
    },
    {
        "regex_pattern": r"^er\d*-skyvoip\.",
        "readable_pattern": "er#-skyvoip",
        "tsr_domain": "skyvoip",
        "role": "voice-peering",
        "readable_role": "Voice Peering",
    },
    {
        "regex_pattern": r"^ar\d*-skyvoip\.",
        "readable_pattern": "ar#-skyvoip",
        "tsr_domain": "skyvoip",
        "role": "voice-peering",
        "readable_role": "Voice Peering",
    },
    {
        "regex_pattern": r"^ar\d-vso\.",
        "readable_pattern": "ar#-vso",
        "tsr_domain": "video",
        "role": "vso",
        "readable_role": "VOD Storage Origin",
    },
    {"regex_pattern": r"^as\d-vso\.", "readable_pattern": "as#-vso", "tsr_domain": "video"},
    {"regex_pattern": r"^radware-.*\.", "readable_pattern": "radware-*", "tsr_domain": "dos"},
    {"regex_pattern": r"^if\d-dos\.", "readable_pattern": "if#-dos", "tsr_domain": "dos"},
    {
        "regex_pattern": r"^ar\d-dos\.",
        "readable_pattern": "ar#-dos",
        "tsr_domain": "dos",
        "role": "ddos",
        "readable_role": "DDOS",
    },
    {"regex_pattern": r"^cs\d-dauntless\.", "readable_pattern": "cs#-dauntless", "tsr_domain": "compliance"},
    {"regex_pattern": r"^ar\d\.", "readable_pattern": "ar#", "tsr_domain": "ar-unclassified"},
    {
        "regex_pattern": r"^ar\d-dvn\.",
        "readable_pattern": "ar#-dvn",
        "tsr_domain": "digital video",
        "readable_role": "Digital Video Network",
        "role": "dvn",
    },
    {"regex_pattern": r"^ar\d-hawkeye\.", "readable_pattern": "ar#-hawkeye", "tsr_domain": "court_blocking"},
    {
        "regex_pattern": r"^ar\d-pcx\.",
        "readable_pattern": "ar#-pcx",
        "tsr_domain": "public_cloud_exchange",
        "role": "pcx",
        "readable_role": "Public Cloud Exchange",
    },
    {
        "regex_pattern": r"^ar\d{1,3}-sdc.*.group.",
        "readable_pattern": "ar#-sdc",
        "tsr_domain": "sky_over_ip",
        "role": "group-comcast-sdc",
        "readable_role": "Group Comcast SDC",
    },
    {
        "regex_pattern": r"^ar\d-sdc\.",
        "readable_pattern": "ar#-sdc",
        "tsr_domain": "sky_over_ip",
        "role": "comcast-sdc",
        "readable_role": "Comcast SDC",
    },
    {
        "regex_pattern": r"^ar\d\d\d-sdc\.",
        "readable_pattern": "ar#-sdc",
        "tsr_domain": "other",
        "role": "comcast-sdc",
        "readable_role": "Comcast SDC",
    },
    {
        "regex_pattern": r"^ar\d{1,3}-xvp\.*.group.",
        "readable_pattern": "ar#-xvp",
        "tsr_domain": "other",
        "role": "group-xvp",
        "readable_role": "Group XVP",
    },
    {
        "regex_pattern": r"^ar\d\d\d-xvp\.",
        "readable_pattern": "ar#-xvp",
        "tsr_domain": "other",
        "role": "group-xvp",
        "readable_role": "Group XVP",
    },
    {
        "regex_pattern": r"^ar\d{1,3}-xvp\.",
        "readable_pattern": "ar#-xvp",
        "tsr_domain": "other",
        "role": "xvp",
        "readable_role": "Xfinity Video Platform",
    },
    {
        "regex_pattern": r"^ar\d-sky\.",
        "readable_pattern": "ar#-sky",
        "tsr_domain": "enterprise",
        "role": "data-centre",
        "readable_role": "Data Centre",
    },
    {
        "regex_pattern": r"^ar\d-wifi\.",
        "readable_pattern": "ar#-wifi",
        "tsr_domain": "sky wifi",
        "readable_role": "Cloud Wifi",
        "role": "cloud-wifi",
    },
    {
        "regex_pattern": r"^ar\d-ws\.",
        "readable_pattern": "ar#-ws",
        "tsr_domain": "wholesale",
        "role": "wholesale",
        "readable_role": "Wholesale",
    },
    {"regex_pattern": r"^ls\d-nme\.", "readable_pattern": "ls#-nme", "tsr_domain": "load_balancer"},
    {"regex_pattern": r"^ls\d-voice\.", "readable_pattern": "ls#-voice", "tsr_domain": "load_balancer_voice"},
    {"regex_pattern": r"^tr\d{2}-sme\.", "readable_pattern": "tr##-sme", "tsr_domain": "sky_business"},
    {"regex_pattern": r"^cs\d\.", "readable_pattern": "cs#.", "tsr_domain": "enterprise"},
    {"regex_pattern": r"^as\d-lab\.", "readable_pattern": "as#-lab", "tsr_domain": "lab-production"},
    {"regex_pattern": r"^if\d\d-mbl-", "readable_pattern": "if##-", "tsr_domain": "mobile firewall"},
    {"regex_pattern": r"^vg\d-g\d\d\.", "readable_pattern": "vg#-g##", "tsr_domain": "customer telephony"},
    {"regex_pattern": r"^cs\d-g\d\d\.", "readable_pattern": "cs#-g##", "tsr_domain": "customer telephony"},
    {"regex_pattern": r"^cr\d-g\d\d\.", "readable_pattern": "cr#-g##", "tsr_domain": "customer telephony"},
    {"regex_pattern": r"-ctlab\.", "readable_pattern": "*-ctlab.", "tsr_domain": "customer telephony lab"},
    {"regex_pattern": r"-sky\.", "readable_pattern": "-sky.", "tsr_domain": "customer:sky"},
    {"regex_pattern": r"^as\d-cdn\.", "readable_pattern": "as#-cdn", "tsr_domain": "cdn"},
    {"regex_pattern": r"^tr\d-btroi\.", "readable_pattern": "tr#-btroi", "tsr_domain": "BT RoI peering"},
    {"regex_pattern": r"^as\d-nme\.", "readable_pattern": "as#-nme", "tsr_domain": "watchman"},
    {"regex_pattern": r"^as\d-cmp\.", "readable_pattern": "as#-cmp", "tsr_domain": "compliance"},
    {"regex_pattern": r"\.rdlab\.", "readable_pattern": ".rdlab.", "tsr_domain": "lab rr"},
    {"regex_pattern": r"^as\d-nme\.", "readable_pattern": "as#-nme", "tsr_domain": "watchman"},
    {
        "regex_pattern": r"^ne\d-cent\.",
        "readable_pattern": "ne#-cent",
        "tsr_domain": "core",
        "role": "mse",
        "readable_role": "Multi Service Edge",
    },
    {
        "regex_pattern": r"^ne\d-dist\.",
        "readable_pattern": "ne#-dist",
        "tsr_domain": "core",
        "role": "mse",
        "readable_role": "Multi Service Edge",
    },
    {
        "regex_pattern": r"^ne\d\.",
        "readable_pattern": "ne#",
        "tsr_domain": "core",
        "role": "mse",
        "readable_role": "Multi Service Edge",
    },  # Lab MSE pattern
    {"regex_pattern": r"^ar\d-.*\.", "readable_pattern": "ar#-****.", "tsr_domain": "application router"},
    {
        "regex_pattern": r"^ar\d{1,3}-cont.*.group.",
        "readable_pattern": "ar#-****.group",
        "tsr_domain": "application router",
        "role": "group-cont",
        "readable_role": "Group Contribution PE",
    },
    {
        "regex_pattern": r"^ar\d{1,3}-cont.*\.",
        "readable_pattern": "ar#-****.",
        "tsr_domain": "application router",
        "role": "cont",
        "readable_role": "Contribution PE",
    },
    # MAP-T Devices
    {
        "regex_pattern": r"^nr\d-map.*\.",
        "readable_pattern": "nr#-map.",
        "tsr_domain": "core",
        "role": "map-t",
        "readable_role": "MAP-T Router",
    },
    {
        "regex_pattern": r"^nr\d-mapx.*\.",
        "readable_pattern": "nr#-map.",
        "tsr_domain": "core",
        "role": "map-t",
        "readable_role": "MAP-T Router",
    },
]
GROUP_MAPPING = [
    {"regex_pattern": r"\.it\.bb\.sky\.com$", "group": "IT"},
    {"regex_pattern": r"\.ie.isp.sky.com$", "group": "IE"},
    {"regex_pattern": r"\.de\.isp\.sky\.com$", "group": "DE"},
    {"regex_pattern": r"isp.sky.com$", "group": "UK"},
]


def generate_local_mapping():
    entries = config.get(section="tsr", key="mapping_entries")

    if not entries:
        return HOSTNAME_MAPPING

    try:
        entries = ast.literal_eval(entries)
    except SyntaxError:
        logger.exception(f"TSR env var addition {entries} is not correctly formatted")
        return HOSTNAME_MAPPING

    if not isinstance(entries, list):
        logger.exception(f"TSR env var addition {entries} must be a list")
        return HOSTNAME_MAPPING

    hostname_mapping = HOSTNAME_MAPPING
    for entry in entries:

        if not validate_tsr_envvar_entry(entry):
            continue

        if entry.get("insert_at", "bottom") == "top":
            hostname_mapping.insert(0, entry)
            logger.debug(f"Added {entry} to top of TSR domain mapping")

        else:
            hostname_mapping.append(entry)
            logger.info(f"Added {entry} to bottom of TSR domain mapping")

    return hostname_mapping


def validate_tsr_envvar_entry(entry):
    if not isinstance(entry, dict):
        logger.exception(f"Entry in TSR env var addition is not a dictionary: {entry}")
        return False

    if any(x not in entry.keys() for x in ["regex_pattern", "tsr_domain"]):
        logger.exception(f"Entry in TSR env var addition must have 'tsr_domain' and 'regex_pattern' keys: {entry}")
        return False

    if entry["tsr_domain"] not in ["metro", "core", "access", "voice", "mobile", "other"]:
        logger.exception(f"Entry in TSR env var addition has invalid 'tsr_domain' value: {entry['tsr_domain']}")
        return False

    try:
        re.compile(entry["regex_pattern"])
    except re.error:
        logger.exception(f"Entry in TSR env var addition failed to validate regex: {entry}")
        return False

    return True
