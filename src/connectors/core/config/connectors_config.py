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
# """
# Connectors Configuration Manager
# """

# Standard Library
import logging
import sys

# Sky Library
from isp_config import ConfigManager, ConfigManagerException

from ..utils.singleton import Singleton

logger = logging.getLogger(__name__)


class ConnectorsConfigManager(ConfigManager, metaclass=Singleton):
    ENV_PREFIX = "CONNECTORS"

    config_params = [
        {"section": "internals", "key": "spec_file", "env": "INTERNALS_SPEC_FILE", "fallback": None},
        {"section": "internals", "key": "jwt_pub_key", "env": "JWT_PUB_KEY", "fallback": None},
        {"section": "internals", "key": "ca_certs", "env": "CA_CERTS", "fallback": None},
        {"section": "internals", "key": "secret_key", "env": "SECRET_KEY", "fallback": None},
        {"section": "internals", "key": "app_path", "env": "APP_PATH", "fallback": "/app"},
        {"section": "internals", "key": "environment", "env": "ENVIRONMENT", "fallback": "DEVELOPMENT"},
        {"section": "internals", "key": "api_gw_url", "env": "API_GW_URL", "fallback": None},
        {
            "section": "internals",
            "key": "regional_domain",
            "env": "INTERNALS_REGIONAL_DOMAIN",
            "fallback": "isp.sky.com it.bb.sky.com",
        },
        {"section": "custom", "key": "tma_url", "env": "CUSTOM_TMA_URL", "fallback": None},
        {"section": "custom", "key": "grandma_url", "env": "CUSTOM_GRANDMA_URL", "fallback": None},
        {"section": "custom", "key": "tma_cis_from_sparkId", "env": "CUSTOM_TMA_SPARK_URL", "fallback": None},
        {"section": "options", "key": "log_level", "env": "OPTIONS_LOG_LEVEL", "fallback": "INFO"},
        {"section": "cauth", "key": "username", "env": "CAUTH_USERNAME", "fallback": None},
        {"section": "cauth", "key": "password", "env": "CAUTH_PASSWORD", "fallback": None},
        {"section": "dcs", "key": "url", "env": "DCS_URL", "fallback": "https://dev-config.nme.sns.sky.com/api/v3/"},
        {"section": "dcs", "key": "cache_limit_seconds", "env": "DCS_CACHE_LIMIT_SECONDS", "fallback": None},
        {"section": "dcs", "key": "minio_bucket_name", "env": "DCS_MINIO_BUCKET_NAME", "fallback": None},
        {"section": "dcs", "key": "minio_object_key", "env": "DCS_MINIO_OBJECT_KEY", "fallback": None},
        {
            "section": "anp",
            "key": "prod_url",
            "env": "ANP_PROD_URL",
            "fallback": "https://insightandplanning.sns.sky.com",
        },
        {
            "section": "anp",
            "key": "uat_url",
            "env": "ANP_UAT_URL",
            "fallback": "https://insightandplanning-qa.sns.sky.com",
        },
        {"section": "anp", "key": "environment", "env": "ANP_ENVIRONMENT", "fallback": "uat"},
        {"section": "anp", "key": "ad_username", "env": "AD_USERNAME", "fallback": None},
        {"section": "anp", "key": "ad_password", "env": "AD_PASSWORD", "fallback": None},
        {"section": "itsm", "key": "url", "env": "ITSM_URL", "fallback": None},
        {"section": "itsm", "key": "max_ci_list_length", "env": "ITSM_MAX_CI", "fallback": None},
        {"section": "itsm", "key": "pop_site_list", "env": "ITSM_POP_SITE_LIST", "fallback": None},
        {"section": "itsm", "key": "subscription_key", "env": "ITSM_SUBSCRIPTION_KEY", "fallback": None},
        {
            "section": "itsm",
            "key": "ethernetsegment_parent_ticket",
            "env": "ITSM_ETHERNETSEGMENT_PARENT_TICKET",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "managementevpn_parent_ticket",
            "env": "ITSM_MANAGEMENTEVPN_PARENT_TICKET",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "subscriberevpn_parent_ticket",
            "env": "ITSM_SUBSCRIBEREVPN_PARENT_TICKET",
            "fallback": None,
        },
        {"section": "itsm", "key": "evpn_parent_ticket", "env": "ITSM_EVPN_PARENT_TICKET", "fallback": None},
        {
            "section": "itsm",
            "key": "gea_provisioning_parent_ticket",
            "env": "ITSM_GEA_PROVISIONING_PARENT_TICKET",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "ethernetsegment_assignment_group",
            "env": "ITSM_ETHERNETSEGMENT_ASSIGNMENT_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "managementevpn_assignment_group",
            "env": "ITSM_MANAGEMENTEVPN_ASSIGNMENT_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "subscriberevpn_assignment_group",
            "env": "ITSM_SUBSCRIBEREVPN_ASSIGNMENT_GROUP",
            "fallback": None,
        },
        {"section": "itsm", "key": "evpn_assignment_group", "env": "ITSM_EVPN_ASSIGNMENT_GROUP", "fallback": None},
        {
            "section": "itsm",
            "key": "metro_assignment_group",
            "env": "ITSM_METRO_ASSIGNMENT_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "external_assignment_group",
            "env": "ITSM_EXTERNAL_ASSIGNMENT_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "gea_provisioning_assignment_group",
            "env": "ITSM_GEA_PROVISIONING_ASSIGNMENT_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "wap_provisioning_assignment_group",
            "env": "ITSM_WAP_PROVISIONING_ASSIGNMENT_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "wholesale_uni_assignment_group",
            "env": "ITSM_WHOLESALE_UNI_ASSIGNMENT_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "wholesale_nni_assignment_group",
            "env": "ITSM_WHOLESALE_NNI_ASSIGNMENT_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "lag_expansion_assignment_group",
            "env": "ITSM_LAG_EXPANSION_ASSIGNMENT_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "quattro_prefix_sets_assignment_group",
            "env": "ITSM_QUATTRO_PREFIX_SETS_ASSIGNMENT_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "software_update_assignment_group",
            "env": "ITSM_SOFTWARE_UPDATE_ASSIGNMENT_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "mapt_provisioning_assignment_group",
            "env": "ITSM_MAPT_ASSIGNMENT_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "lag_upgrade_assignment_group",
            "env": "ITSM_LAG_UPGRADE_ASSIGNMENT_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "ethernet_segment_configuration_group",
            "env": "ITSM_ETHERNETSEGMENT_CONFIG_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "management_evpn_configuration_group",
            "env": "ITSM_MANAGEMENTEVPN_CONFIG_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "subscriber_evpn_configuration_group",
            "env": "ITSM_SUBSCRIBEREVPN_CONFIG_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "metro_configuration_group",
            "env": "ITSM_METRO_CONFIG_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "external_configuration_group",
            "env": "ITSM_EXTERNAL_CONFIG_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "gea_provisioning_configuration_group",
            "env": "ITSM_GEA_PROVISIONING_CONFIG_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "wap_provisioning_configuration_group",
            "env": "ITSM_WAP_PROVISIONING_CONFIG_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "wholesale_uni_configuration_group",
            "env": "ITSM_WHOLESALE_UNI_CONFIGURATION_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "lag_expansion_configuration_group",
            "env": "ITSM_LAG_EXPANSION_CONFIG_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "wholesale_nni_configuration_group",
            "env": "ITSM_WHOLESALE_NNI_CONFIGURATION_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "bng_failover_assignment_group",
            "env": "BNG_FAILOVER_ASSIGNMENT_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "bng_failover_configuration_group",
            "env": "BNG_FAILOVER_CONFIGURATION_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "quattro_prefix_sets_configuration_group",
            "env": "ITSM_QUATTRO_PREFIX_SETS_CONFIGURATION_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "software_update_configuration_group",
            "env": "ITSM_SOFTWARE_UPDATE_CONFIGURATION_GROUP",
            "fallback": None,
        },
        {"section": "itsm", "key": "evpn_configuration_group", "env": "ITSM_EVPN_CONFIG_GROUP", "fallback": None},
        {
            "section": "itsm",
            "key": "mapt_provisioning_configuration_group",
            "env": "ITSM_MAPT_CONFIG_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "lag_upgrade_configuration_group",
            "env": "ITSM_LAG_UPGRADE_CONFIG_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "mapt_update_similar_change_pattern",
            "env": "ITSM_MAPT_UPDATE_SIMILAR_CHANGE_PATTERN",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "gea_provisioning_similar_change_pattern",
            "env": "ITSM_GEA_PROVISIONING_SIMILAR_CHANGE_PATTERN",
            "fallback": None,
        },
        {"section": "itsm", "key": "supported_types", "env": "ITSM_SUPPORTED_FILE_TYPE", "fallback": None},
        {"section": "itsm", "key": "assigned_to", "env": "ITSM_ASSIGNED_TO", "fallback": None},
        {"section": "itsm", "key": "updated_by", "env": "ITSM_UPDATED_BY", "fallback": None},
        {"section": "itsm", "key": "3800_incident_projection", "env": "ITSM_INC_PROJECTION", "fallback": None},
        {"section": "itsm", "key": "3800_change_request_projection", "env": "ITSM_CHG_PROJECTION", "fallback": None},
        {"section": "itsm", "key": "sleep_interval", "env": "ITSM_SLEEP_INTERVAL", "fallback": None},
        {"section": "itsm", "key": "check_duration", "env": "ITSM_CHECK_DURATION", "fallback": None},
        {
            "section": "itsm",
            "key": "ticket_creation_attachment_limit",
            "env": "ITSM_TICKET_CREATION_ATTACHMENT_LIMIT",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "ticket_creation_attachment_size_limit",
            "env": "ITSM_TICKET_CREATION_ATTACHMENT_SIZE_LIMIT",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "openreach_retest_configuration_group",
            "env": "ITSM_OPENREACH_RETEST_CONFIGURATION_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "openreach_retest_assign_group",
            "env": "ITSM_OPENREACH_RETEST_ASSIGNMENT_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "port_shut_unshut_configuration_group",
            "env": "ITSM_PORT_SHUT_UNSHUT_CONFIGURATION_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "port_shut_unshut_assign_group",
            "env": "ITSM_PORT_SHUT_UNSHUT_ASSIGNMENT_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "wholesale_eth2_configuration_group",
            "env": "ITSM_WHOLESALE_ETH2_CONFIGURATION_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "route_server_mapping_assignment_group",
            "env": "ITSM_ROUTE_SERVER_MAPPING_ASSIGNMENT_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "route_server_mapping_configuration_group",
            "env": "ITSM_ROUTE_SERVER_MAPPING_CONFIGURATION_GROUP",
            "fallback": None,
        },
        {
            "section": "itsm",
            "key": "wholesale_eth2_assign_group",
            "env": "ITSM_WHOLESALE_ETH2_ASSIGNMENT_GROUP",
            "fallback": None,
        },
        {"section": "itsm", "key": "template_category", "env": "ITSM_TEMPLATE_CATEGORY", "fallback": None},
        {"section": "itsm", "key": "service_type", "env": "ITSM_3800_SERVICE_TYPE", "fallback": None},
        {"section": "itsm", "key": "cag_base_url", "env": "ITSM_CAG_BASE_URL", "fallback": None},
        {"section": "itsm", "key": "cag_api_key", "env": "ITSM_CAG_API_KEY", "fallback": None},
        {"section": "itsm", "key": "impact_type_precedence", "env": "ITSM_IMPACT_TYPE_PRECEDENCE", "fallback": None},
        {"section": "itsm", "key": "third_party_impact", "env": "ITSM_THIRD_PARTY_IMPACT", "fallback": None},
        {"section": "mailer", "key": "allowed_domains", "env": "MAILER_ALLOWED_DOMAINS", "fallback": None},
        {"section": "mailer", "key": "feature_flag", "env": "MAILER_FEATURE_FLAG", "fallback": "OFF"},
        {"section": "mailer", "key": "max_recipients", "env": "MAILER_MAX_RECIPIENTS", "fallback": 30},
        {"section": "mailer", "key": "smtp_server", "env": "MAILER_SMTP_SERVER", "fallback": None},
        {"section": "mailer", "key": "smtp_port", "env": "MAILER_SMTP_PORT", "fallback": 25},
        {"section": "mailer", "key": "from_address", "env": "MAILER_FROM_ADDRESS", "fallback": None},
        {"section": "mailer", "key": "template_category", "env": "MAILER_TEMPLATE_CATEGORY", "fallback": None},
        {"section": "mailer", "key": "template_locale", "env": "MAILER_TEMPLATE_LOCALE", "fallback": None},
        {"section": "mailer", "key": "max_attachment_size", "env": "MAILER_MAX_ATTACHMENT_SIZE", "fallback": None},
        {"section": "mailer", "key": "max_attachment_count", "env": "MAILER_MAX_ATTACHMENT_COUNT", "fallback": None},
        # cauth token
        {"section": "oauth", "key": "url", "env": "OAUTH_URL", "fallback": None},
        {"section": "oauth", "key": "username", "env": "OAUTH_USERNAME", "fallback": None},
        {"section": "oauth", "key": "password", "env": "OAUTH_PASSWORD", "fallback": None},
        {"section": "oauth", "key": "scope", "env": "OAUTH_SCOPE", "fallback": None},
        {"section": "oauth", "key": "verify", "env": "OAUTH_VERIFY", "fallback": True},
        {"section": "oauth", "key": "skip_token", "env": "OAUTH_SKIP_TOKEN", "fallback": "false"},
        # ServiceDB
        {"section": "serviceDB", "key": "username", "env": "SERVICEDB_USERNAME", "fallback": None},
        {"section": "serviceDB", "key": "password", "env": "SERVICEDB_PASSWORD", "fallback": "DEBUG"},
        {"section": "serviceDB", "key": "port", "env": "SERVICEDB_PORT", "fallback": None},
        {"section": "serviceDB", "key": "instances", "env": "SERVICEDB_INSTANCES", "fallback": None},
        {"section": "serviceDB", "key": "replicaSet", "env": "SERVICEDB_REPLICASET", "fallback": None},
        {"section": "serviceDB", "key": "readPreference", "env": "SERVICEDB_READPREFERENCE", "fallback": None},
        {"section": "serviceDB", "key": "localThresholdMs", "env": "SERVICEDB_LOCALTHRESHOLDMS", "fallback": None},
        {"section": "serviceDB", "key": "maxTimeMS", "env": "SERVICEDB_MAXTIMEMS", "fallback": 30000},
        # Session Parameters
        {"section": "session", "key": "error_codes", "env": "SESSION_ERROR_CODES", "fallback": None},
        {"section": "session", "key": "backoff_factor", "env": "SESSION_BACKOFF_FACTOR", "fallback": 0.5},
        {"section": "session", "key": "max_retries", "env": "SESSION_MAX_RETRIES", "fallback": 5},
        {"section": "session", "key": "verify", "env": "SESSION_VERIFY", "fallback": True},
        {"section": "session", "key": "backoff_max_time", "env": "SESSION_BACKOFF_MAX_TIME", "fallback": 60},
        {"section": "session", "key": "backoff_retry_after", "env": "SESSION_BACKOFF_RETRY_AFTER", "fallback": 20},
        # External
        {"section": "external", "key": "url", "env": "EXTERNAL_URL", "fallback": "https://bpa-dne.sky.com/"},
        # File handler
        {"section": "fileHandler", "key": "collection", "env": "FH_COLLECTION", "fallback": None},
        {"section": "fileHandler", "key": "file_size_limit_in_KB", "env": "FH_FILE_SIZEINKB", "fallback": 100},
        # IPAM
        {"section": "ipam", "key": "netbox_url", "env": "NETBOX_URL", "fallback": None},
        {"section": "ipam", "key": "netbox_token", "env": "NETBOX_TOKEN", "fallback": None},
        {"section": "ipam", "key": "netbox_status", "env": "NETBOX_STATUS", "fallback": 1},
        # MysqlDB
        {"section": "mysqlDB", "key": "username", "env": "MYSQLDB_USERNAME", "fallback": None},
        {"section": "mysqlDB", "key": "password", "env": "MYSQLDB_PASSWORD", "fallback": None},
        {"section": "mysqlDB", "key": "port", "env": "MYSQLDB_PORT", "fallback": None},
        {"section": "mysqlDB", "key": "host", "env": "MYSQLDB_HOST", "fallback": None},
        {"section": "mysqlDB", "key": "driver", "env": "MYSQLDB_DRIVER", "fallback": None},
        {"section": "mysqlDB", "key": "database_name", "env": "MYSQLDB_DATABASE_NAME", "fallback": None},
        {
            "section": "mysqlDB",
            "key": "sw_upgrade_database_name",
            "env": "SOFTWARE_LIFECYCLE_MANAGEMENT",
            "fallback": None,
        },
        # cisco Smart Account
        {"section": "ciscoSmartAccount", "key": "client_id", "env": "CISCO_SMART_ACCOUNT_CLIENT_ID", "fallback": None},
        {
            "section": "ciscoSmartAccount",
            "key": "client_secret",
            "env": "CISCO_SMART_ACCOUNT_CLIENT_SECRET",
            "fallback": None,
        },
        {"section": "ciscoSmartAccount", "key": "username", "env": "CISCO_SMART_ACCOUNT_USERNAME", "fallback": None},
        {"section": "ciscoSmartAccount", "key": "password", "env": "CISCO_SMART_ACCOUNT_PASSWORD", "fallback": None},
        # INCA auth token
        {"section": "inca", "key": "base_url", "env": "INCA_BASE_URL", "fallback": None},
        {"section": "inca", "key": "username", "env": "INCA_USERNAME", "fallback": None},
        {"section": "inca", "key": "password", "env": "INCA_PASSWORD", "fallback": None},
        {"section": "inca", "key": "nexa_username", "env": "INCA_NEXA_USERNAME", "fallback": None},
        {"section": "inca", "key": "nexa_password", "env": "INCA_NEXA_PASSWORD", "fallback": None},
        # PLANNET auth token
        {"section": "plannet", "key": "base_url", "env": "PLANNET_BASE_URL", "fallback": None},
        {
            "section": "plannet",
            "key": "network_domain_endpoint",
            "env": "PLANNET_NETWORK_DOMAIN_ENDPOINT",
            "fallback": "",
        },
        {"section": "plannet", "key": "username", "env": "PLANNET_USERNAME", "fallback": None},
        {"section": "plannet", "key": "password", "env": "PLANNET_PASSWORD", "fallback": None},
        {"section": "plannet", "key": "access_token", "env": "PLANNET_ACCESS_TOKEN", "fallback": None},
        # Azure AD Auth token
        {"section": "azureAdAuth", "key": "client_id", "env": "AZURE_AD_AUTH_CLIENT_ID", "fallback": None},
        {
            "section": "azureAdAuth",
            "key": "client_credential",
            "env": "AZURE_AD_AUTH_CLIENT_CREDENTIAL",
            "fallback": None,
        },
        {"section": "azureAdAuth", "key": "authority", "env": "AZURE_AD_AUTH_AUTHORITY", "fallback": None},
        {"section": "azureAdAuth", "key": "scopes", "env": "AZURE_AD_AUTH_SCOPES", "fallback": None},
        # Network Domains
        {"section": "networkDomain", "key": "core", "env": "NETWORK_DOMAIN_CORE_MEMBERS", "fallback": ""},
        {"section": "networkDomain", "key": "metro", "env": "NETWORK_DOMAIN_METRO_MEMBERS", "fallback": ""},
        {"section": "networkDomain", "key": "access", "env": "NETWORK_DOMAIN_ACCESS_MEMBERS", "fallback": ""},
        # GIT auth token
        {"section": "git", "key": "token", "env": "GIT_TOKEN", "fallback": None},
        {"section": "git", "key": "base_url", "env": "GIT_BASE_URL", "fallback": None},
        # Service Record
        {
            "section": "service_record",
            "key": "records_per_page",
            "env": "SERVICE_RECORD_RECORDS_PER_PAGE",
            "fallback": None,
        },
        {"section": "service_record", "key": "max_time_ms", "env": "SERVICE_RECORD_MAX_TIME_MS", "fallback": None},
        # TSR
        {"section": "tsr", "key": "mapping_entries", "env": "TSR_ADDITIONAL_MAPPING_ENTRIES", "fallback": ""},
        # Kafka
        {
            "section": "kafka",
            "key": "bootstrap_servers",
            "env": "KAFKA_BOOTSTRAP_SERVERS",
            "fallback": None,
        },
        {
            "section": "kafka",
            "key": "reset",
            "env": "KAFKA_RESET",
            "fallback": None,
        },
        {
            "section": "kafka",
            "key": "commit",
            "env": "KAFKA_COMMIT",
            "fallback": None,
        },
        {
            "section": "kafka",
            "key": "sasl_username",
            "env": "KAFKA_SASL_USERNAME",
            "fallback": None,
        },
        {
            "section": "kafka",
            "key": "sasl_password",
            "env": "KAFKA_SASL_PASSWORD",
            "fallback": None,
        },
        {
            "section": "kafka",
            "key": "sasl_username_write",
            "env": "KAFKA_SASL_USERNAME_WRITE",
            "fallback": None,
        },
        {
            "section": "kafka",
            "key": "sasl_password_write",
            "env": "KAFKA_SASL_PASSWORD_WRITE",
            "fallback": None,
        },
        {
            "section": "kafka",
            "key": "order_status_delivery_timeout",
            "env": "KAFKA_ORDER_STATUS_DELIVERY_TIMEOUT",
            "fallback": None,
        },
        {
            "section": "kafka",
            "key": "order_status_flush_timeout",
            "env": "KAFKA_ORDER_STATUS_FLUSH_TIMEOUT",
            "fallback": None,
        },
        {
            "section": "kafka",
            "key": "order_status_connectivity_timeout",
            "env": "KAFKA_ORDER_STATUS_CONNECTIVITY_TIMEOUT",
            "fallback": None,
        },
        # Elasticsearch
        {
            "section": "elasticsearch",
            "key": "nodes",
            "env": "ELASTICSEARCH_NODES",
            "fallback": None,
        },
        {
            "section": "elasticsearch",
            "key": "username",
            "env": "ELASTICSEARCH_USERNAME",
            "fallback": None,
        },
        {
            "section": "elasticsearch",
            "key": "password",
            "env": "ELASTICSEARCH_PASSWORD",
            "fallback": None,
        },
        # PostgresDB
        {"section": "postgresDB", "key": "username", "env": "POSTGRESDB_USERNAME", "fallback": None},
        {"section": "postgresDB", "key": "password", "env": "POSTGRESDB_PASSWORD", "fallback": None},
        {"section": "postgresDB", "key": "port", "env": "POSTGRESDB_PORT", "fallback": None},
        {"section": "postgresDB", "key": "host", "env": "POSTGRESDB_HOST", "fallback": None},
        {"section": "postgresDB", "key": "database_name", "env": "POSTGRESDB_DATABASE_NAME", "fallback": None},
        # AuditNow
        {"section": "auditnow", "key": "retry_attempts", "env": "AUDITNOW_RETRY_ATTEMPTS", "fallback": None},
        {"section": "auditnow", "key": "retry_backoff", "env": "AUDITNOW_RETRY_BACKOFF", "fallback": None},
        {"section": "auditnow", "key": "topic", "env": "AUDITNOW_TOPIC", "fallback": None},
        {"section": "auditnow", "key": "consumer_group_id", "env": "AUDITNOW_CONSUMER_GROUP_ID", "fallback": None},
        # radius
        {"section": "radius", "key": "base_url", "env": "RADIUS_BASE_URL", "fallback": None},
        {"section": "radius", "key": "username", "env": "RADIUS_USERNAME", "fallback": None},
        {"section": "radius", "key": "password", "env": "RADIUS_PASSWORD", "fallback": None},
        {"section": "radius", "key": "scope", "env": "RADIUS_SCOPE", "fallback": None},
        # orderStatus
        {"section": "orderStatus", "key": "topic_mapper", "env": "ORDER_STATUS_TOPIC_MAPPER", "fallback": None},
        {"section": "orderStatus", "key": "url", "env": "ORDER_STATUS_URL", "fallback": None},
        # minio
        {"section": "minio", "key": "endpoint", "env": "MINIO_ENDPOINT", "fallback": None},
        {"section": "minio", "key": "access_key", "env": "MINIO_ACCESS_KEY", "fallback": None},
        {"section": "minio", "key": "secret_key", "env": "MINIO_SECRET_KEY", "fallback": None},
        # horizon
        {"section": "horizon", "key": "endpoint", "env": "HORIZON_ENDPOINT", "fallback": None},
        {"section": "horizon", "key": "email", "env": "HORIZON_DNE_EMAIL", "fallback": None},
        # rsa
        {"section": "rsa", "key": "private_key", "env": "RSA_PRIVATE_KEY", "fallback": None},
        {"section": "rsa", "key": "public_key", "env": "RSA_PUBLIC_KEY", "fallback": None},
        # nap
        {"section": "nap", "key": "base_url", "env": "NAP_BASE_URL", "fallback": None},
        {"section": "nap", "key": "username", "env": "NAP_USER_NAME", "fallback": None},
        {"section": "nap", "key": "password", "env": "NAP_PASSWORD", "fallback": None},
    ]

    def __init__(self):
        try:
            conffile = self.get_env_var("CONFIG")
        except KeyError:
            conffile = "/app/config/connectors.conf"

        super().__init__(conffile)


try:
    config = ConnectorsConfigManager()
    config.load_config()
except ConfigManagerException:
    sys.exit(1)
