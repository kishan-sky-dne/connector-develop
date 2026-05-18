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
import sys

# Sky Library
from isp_config import ConfigManagerException

# DNE Library
from connectors.core.config import connectors_config

logger = logging.getLogger(__name__)

try:
    config = connectors_config.ConnectorsConfigManager()
    config.load_config()
except ConfigManagerException:
    sys.exit(1)

ethernetsegment_parent_ticket = config.get(section="itsm", key="ethernetsegment_parent_ticket")
managementevpn_parent_ticket = config.get(section="itsm", key="managementevpn_parent_ticket")
subscriberevpn_parent_ticket = config.get(section="itsm", key="subscriberevpn_parent_ticket")
evpn_parent_ticket = config.get(section="itsm", key="evpn_parent_ticket")
gea_provisioning_parent_ticket = config.get(section="itsm", key="gea_provisioning_parent_ticket")

ethernetsegment_assign_group = config.get(section="itsm", key="ethernetsegment_assignment_group")
managementevpn_assign_group = config.get(section="itsm", key="managementevpn_assignment_group")
subscriberevpn_assign_group = config.get(section="itsm", key="subscriberevpn_assignment_group")
evpn_assign_group = config.get(section="itsm", key="evpn_assignment_group")
metro_assign_group = config.get(section="itsm", key="metro_assignment_group")
external_assign_group = config.get(section="itsm", key="external_assignment_group")
gea_provisioning_assign_group = config.get(section="itsm", key="gea_provisioning_assignment_group")
wap_provisioning_assign_group = config.get(section="itsm", key="wap_provisioning_assignment_group")
wholesale_uni_assign_group = config.get(section="itsm", key="wholesale_uni_assignment_group")
wholesale_nni_assign_group = config.get(section="itsm", key="wholesale_nni_assignment_group")
lag_expansion_assign_group = config.get(section="itsm", key="lag_expansion_assignment_group")
quattro_prefix_sets_assign_group = config.get(section="itsm", key="quattro_prefix_sets_assignment_group")
software_update_assign_group = config.get(section="itsm", key="software_update_assignment_group")
mapt_provisioning_assign_group = config.get(section="itsm", key="mapt_provisioning_assignment_group")
lag_upgrade_assignment_group = config.get(section="itsm", key="lag_upgrade_assignment_group")
openreach_retest_assign_group = config.get(section="itsm", key="openreach_retest_assign_group")
bng_failover_assign_group = config.get(section="itsm", key="bng_failover_assignment_group")
port_shut_unshut_assign_group = config.get(section="itsm", key="port_shut_unshut_assign_group")
wholesale_eth2_assign_group = config.get(section="itsm", key="wholesale_eth2_assign_group")
route_server_mapping_assign_group = config.get(section="itsm", key="route_server_mapping_assignment_group")

ethernet_segment_configuration_group = config.get(section="itsm", key="ethernet_segment_configuration_group")
management_evpn_configuration_group = config.get(section="itsm", key="management_evpn_configuration_group")
subscriber_evpn_configuration_group = config.get(section="itsm", key="subscriber_evpn_configuration_group")
evpn_configuration_group = config.get(section="itsm", key="evpn_configuration_group")
metro_configuration_group = config.get(section="itsm", key="metro_configuration_group")
external_configuration_group = config.get(section="itsm", key="external_configuration_group")
gea_provisioning_configuration_group = config.get(section="itsm", key="gea_provisioning_configuration_group")
wap_provisioning_configuration_group = config.get(section="itsm", key="wap_provisioning_configuration_group")
wholesale_uni_configuration_group = config.get(section="itsm", key="wholesale_uni_configuration_group")
wholesale_nni_configuration_group = config.get(section="itsm", key="wholesale_nni_configuration_group")
lag_expansion_configuration_group = config.get(section="itsm", key="lag_expansion_configuration_group")
quattro_prefix_sets_configuration_group = config.get(section="itsm", key="quattro_prefix_sets_configuration_group")
software_update_configuration_group = config.get(section="itsm", key="software_update_configuration_group")
mapt_provisioning_configuration_group = config.get(section="itsm", key="mapt_provisioning_configuration_group")
lag_upgrade_configuration_group = config.get(section="itsm", key="lag_upgrade_configuration_group")
openreach_retest_configuration_group = config.get(section="itsm", key="openreach_retest_configuration_group")
bng_failover_configuration_group = config.get(section="itsm", key="bng_failover_configuration_group")
port_shut_unshut_configuration_group = config.get(section="itsm", key="port_shut_unshut_configuration_group")
wholesale_eth2_configuration_group = config.get(section="itsm", key="wholesale_eth2_configuration_group")
route_server_mapping_configuration_group = config.get(section="itsm", key="route_server_mapping_configuration_group")

mapt_update_similar_change_pattern = config.get(section="itsm", key="mapt_update_similar_change_pattern").split(",")
gea_provisioning_similar_change_pattern = config.get(
    section="itsm", key="gea_provisioning_similar_change_pattern"
).split(",")


class ITSMFactory:
    @staticmethod
    def create(
        description=None, short_description=None, parent_change=None, assignment_group=None, config_group=None, **kwargs
    ):  # noqa: ignore=C901
        return {
            "description": description,
            "short_description": short_description,
            "parent_change": parent_change,
            "assignment_group": assignment_group,
            "config_group": config_group,
            "extra_args": kwargs,
        }

    @staticmethod
    def update():
        return NotImplementedError("The ITSM ticket update method is currently not required")

    @staticmethod
    def resolve():
        return NotImplementedError("The ITSM ticket resolve method is currently not required")

    @staticmethod
    def fetch():
        return NotImplementedError("The ITSM ticket fetch method is currently not required")


service = ITSMFactory()

mapper = {
    "ethernetSegment": {
        "create": service.create(
            description="Creation of Ethernet Segment on devices ",
            short_description="Ethernet Segment configuration via DNE order ",  # Bug fix for 3664
            parent_change=ethernetsegment_parent_ticket,
            assignment_group=ethernetsegment_assign_group,
            config_group=ethernet_segment_configuration_group,
        )
    },
    "managementEvpn": {
        "create": service.create(
            description="Creation of Management EVPN on devices ",
            short_description="Management EVPN configuration via DNE order ",  # Bug fix for 3664
            parent_change=managementevpn_parent_ticket,
            assignment_group=managementevpn_assign_group,
            config_group=management_evpn_configuration_group,
        )
    },
    "subscriberEvpn": {
        "create": service.create(
            description="Creating of Subscriber EVPN on devices ",
            short_description="Subscriber EVPN configuration via DNE order ",  # Bug fix for 3664
            parent_change=subscriberevpn_parent_ticket,
            assignment_group=subscriberevpn_assign_group,
            config_group=subscriber_evpn_configuration_group,
        )
    },
    "evpn": {
        "create": service.create(
            description="Creating of Ethernet Segment and Management EVPN on devices ",  # Bug fix for 3305
            short_description="ES and MEVPN configuration via DNE order ",  # Bug fix for 3664
            parent_change=evpn_parent_ticket,
            assignment_group=evpn_assign_group,
            config_group=evpn_configuration_group,
        )
    },
    "metroServiceMigration": {
        "create": service.create(
            description="All affected CIs and services  are added to parent change. This ticket will have all "
            "change execution logs and status for the activity stated in short description. For more "
            "details go to https://dne.cf.sky.com",  # noqa: E126
            short_description="",
            parent_change="",
            assignment_group=metro_assign_group,
            config_group=metro_configuration_group,
        )
    },
    "ubbMigration": {
        "create": service.create(
            description="All affected CIs and services  are added to parent change. This ticket will have all "
            "change execution logs and status for the activity stated in short description. For more "
            "details go to https://dne.cf.sky.com",  # noqa: E126
            short_description="",
            parent_change="",
            assignment_group=metro_assign_group,
            config_group=metro_configuration_group,
        )
    },
    "metroMigration": {
        "create": service.create(
            description="All affected CIs and services  are added to parent change. This ticket will have all "
            "change execution logs and status for the activity stated in short description. For more "
            "details go to https://dne.cf.sky.com",  # noqa: E126
            short_description="",
            parent_change="",
            assignment_group=metro_assign_group,
            config_group=metro_configuration_group,
        )
    },
    "serviceIncident": {
        "create": service.create(
            description="All affected CIs and services  are added to ticket.This ticket will have all "
            "change execution logs and status for the activity stated in short description. For more "
            "details go to https://dne.cf.sky.com",
            short_description="",
            parent_change="",
            assignment_group=metro_assign_group,
            config_group=metro_configuration_group,
        )
    },
    "external": {
        "create": service.create(
            description="",
            short_description="",
            parent_change="",
            assignment_group=external_assign_group,
            config_group=external_configuration_group,
        )
    },
    "geaProvisioning": {
        "create": service.create(
            description="Creating of GEA Provisioning on devices ",
            short_description="",
            parent_change=gea_provisioning_parent_ticket,
            assignment_group=gea_provisioning_assign_group,
            config_group=gea_provisioning_configuration_group,
            max_change_window=10,
        )
    },
    "wapProvisioning": {
        "create": service.create(
            description="Creating of WAP Provisioning on devices ",
            short_description="",
            assignment_group=wap_provisioning_assign_group,
            config_group=wap_provisioning_configuration_group,
        )
    },
    "wholesaleUni": {
        "create": service.create(
            description="",
            short_description="",
            assignment_group=wholesale_uni_assign_group,
            config_group=wholesale_uni_configuration_group,
        )
    },
    "wholesaleNni": {
        "create": service.create(
            description="",
            short_description="",
            assignment_group=wholesale_nni_assign_group,
            config_group=wholesale_nni_configuration_group,
        )
    },
    "lagExpansion": {
        "create": service.create(
            description="Expanding Lag on device through Adding Ports",
            short_description="",
            assignment_group=lag_expansion_assign_group,
            config_group=lag_expansion_configuration_group,
        )
    },
    "quattroPrefixSets": {
        "create": service.create(
            description="Updation of prefix-sets on devices ",
            short_description="",
            assignment_group=quattro_prefix_sets_assign_group,
            config_group=quattro_prefix_sets_configuration_group,
        )
    },
    "newSwitchInstall": {
        "create": service.create(
            description="All affected CIs and services  are added to change ticket. This ticket will have all "
            "change execution logs and status for the activity stated in short description. For more "
            "details go to https://dne.cf.sky.com",  # noqa: E126
            short_description="",
            parent_change="",
            assignment_group=metro_assign_group,
            config_group=metro_configuration_group,
        )
    },
    "retrofit": {
        "create": service.create(
            description="All affected CIs and services  are added to change ticket. This ticket will have all "
            "change execution logs and status for the activity stated in short description. For more "
            "details go to https://dne.cf.sky.com",  # noqa: E126
            short_description="",
            parent_change="",
            assignment_group=metro_assign_group,
            config_group=metro_configuration_group,
        )
    },
    "softwareUpdate": {
        "create": service.create(
            description="",
            short_description="",
            assignment_group=software_update_assign_group,
            config_group=software_update_configuration_group,
        )
    },
    "mapTprovisioning": {
        "create": service.create(
            description="Creating map-t prefixes on BNG and MAP-BR",
            short_description="",
            parent_change="",
            assignment_group=mapt_provisioning_assign_group,
            config_group=mapt_provisioning_configuration_group,
        )
    },
    "lagUpgrade": {
        "create": service.create(
            description="",
            short_description="",
            parent_change="",
            assignment_group=lag_upgrade_assignment_group,
            config_group=lag_upgrade_configuration_group,
        )
    },
    "maptUpdate": {
        "create": service.create(
            description="Performing Drain/Undrain on BNG for MAP-T prefixes",
            short_description="",
            parent_change="",
            assignment_group=mapt_provisioning_assign_group,
            config_group=mapt_provisioning_configuration_group,
            similar_change_pattern=mapt_update_similar_change_pattern,
        )
    },
    "openreachretest": {
        "create": service.create(
            description="",
            short_description="",
            assignment_group=openreach_retest_assign_group,
            config_group=openreach_retest_configuration_group,
        )
    },
    "bngFailover": {
        "create": service.create(
            description="UK BNGs are deployed in resilient pairs which make it possible to take one member "
            "out-of-service for maintenance/testing/incident resolution purposes and bring it back "
            "in-service without any impact to the running subscriber services. Switchover and "
            "switchback procedures will be performed automatically by DNE on the BNG pair in "
            "this change",
            short_description="",
            assignment_group=bng_failover_assign_group,
            config_group=bng_failover_configuration_group,
        )
    },
    "maptDelete": {
        "create": service.create(
            description="Decommissioning map-t prefixes on BNG and MAP-BR",
            short_description="",
            parent_change="",
            assignment_group=mapt_provisioning_assign_group,
            config_group=mapt_provisioning_configuration_group,
        )
    },
    "geaOpenReachTest": {
        "create": service.create(
            description="GEA Open Reach Test",
            short_description="",
            parent_change="",
            assignment_group=gea_provisioning_assign_group,
            config_group=gea_provisioning_configuration_group,
        )
    },
    "geaProvisioningV2": {
        "create": service.create(
            description="Provisioning GEA circuits.",
            short_description="",
            parent_change="",
            assignment_group=gea_provisioning_assign_group,
            config_group=gea_provisioning_configuration_group,
            similar_change_pattern=gea_provisioning_similar_change_pattern,
        )
    },
    "portshutunshut": {
        "create": service.create(
            description="",
            short_description="",
            assignment_group=port_shut_unshut_assign_group,
            config_group=port_shut_unshut_configuration_group,
        )
    },
    "wholesaleEth2": {
        "create": service.create(
            description="",
            short_description="",
            assignment_group=wholesale_eth2_assign_group,
            config_group=wholesale_eth2_configuration_group,
        )
    },
    "geaPlugup": {
        "create": service.create(
            description="GEA Circuit PlugUp",
            short_description="",
            parent_change="",
            assignment_group=gea_provisioning_assign_group,
            config_group=gea_provisioning_configuration_group,
        )
    },
    "metroServiceDecommissioning": {
        "create": service.create(
            description="Decommissioning GEA service.",
            short_description="",
            parent_change="",
            assignment_group=gea_provisioning_assign_group,
            config_group=gea_provisioning_configuration_group,
        )
    },
    "routeServerMappingUpdate": {  # new service for route server mapping updates
        "create": service.create(
            description="UK CDN mapping update by DNE",
            short_description="",
            parent_change="",
            assignment_group=route_server_mapping_assign_group,
            config_group=route_server_mapping_configuration_group,
        )
    },
}
