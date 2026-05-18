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
import json
import logging

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.utils.exceptions import ConnectorException, ResourceServiceNotAvailable, RestUtilityException
from connectors.core.utils.rest_api_utility import RestUtility

logger = logging.getLogger(__name__)


netbox_url = config.get(section="ipam", key="netbox_url")
netbox_token = "Token " + config.get(section="ipam", key="netbox_token")
status = config.get(section="ipam", key="netbox_status")
statuses = {"Active": 1, "Reserved": 2, "Deprecated": 3, "DHCP": 5}
headers = {"Authorization": netbox_token}
post_headers = {"Authorization": netbox_token, "content-type": "application/json"}


class ReserveIpAddress:
    def __init__(self, request_body):
        self.address = request_body["address"]
        self.network = request_body["network"]
        self.domain = request_body["domain"]
        self.prefix = request_body.get("prefix")
        self.vrf = request_body.get("vrf") or "Global"
        self.route_distinguisher = request_body.get("routeDistinguisher")
        self.status = statuses.get(request_body.get("status")) or status
        self.description = request_body.get("description")
        self.tags = request_body.get("tags")
        self.custom_fields = request_body.get("custom_fields")
        self.rest = RestUtility()

    def reserve_ip(self):
        tenant_id = self.validate_tenant()
        vrf_id = None if self.vrf in [None, "Global", "GRT"] else self.validate_vrf()
        response_object, reserve_payload = {}, {"address": self.address, "tenant": tenant_id}
        reserve_status = {}

        if vrf_id:
            reserve_payload["vrf"] = vrf_id
        if self.status:
            reserve_payload["status"] = self.status
        if self.description:
            reserve_payload["description"] = self.description
        if self.tags:
            reserve_payload["tags"] = self.tags

        reserve_url = netbox_url + "ipam/ip-addresses/"
        try:
            reserve_status = self.rest.post(
                reserve_url,
                headers=post_headers,
                data=json.dumps(reserve_payload),
            )
        except RestUtilityException as err:
            logger.error(f"IP Reservation for Interface failed.IP address is not free: {err.args[0]}")

        if reserve_status and reserve_status.get("id"):
            response_object = {"status": "success", "id": reserve_status.get("id")}
        else:
            response_object = {
                "status": "failure",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-006-999-0005",
                        "message": "IP Reservation for Interface failed. Provided IP is already reserved",
                    }
                ],
                "metadata": {"vrf": self.vrf},
            }

        return response_object

    def validate_vrf(self):
        if not self.route_distinguisher:
            logger.error(f"routeDistinguisher is not provided for the vrf: {self.vrf}")
            raise ConnectorException(f"routeDistinguisher is not provided for the vrf:{self.vrf}")

        vrf_id = ""
        try:
            url = netbox_url + "ipam/vrfs/?name=" + self.vrf + "&rd=" + self.route_distinguisher
            vrf_response = self.rest.get(url, headers=headers)
            count = vrf_response["count"]
            if not count:
                vrf_id = None
                logger.info(f"Provided vrf is not found in Netbox {self.vrf}")
            else:
                vrf_id = vrf_response["results"][0]["id"]
        except RestUtilityException as err:
            logger.error(f"Failed to validate vrf {err}")
        except (ValueError, TypeError, AttributeError, KeyError) as err:
            raise ResourceServiceNotAvailable(f"Validation failed for the vrf:{self.vrf} {err}")
        return vrf_id

    def validate_tenant(self):
        try:
            url = netbox_url + "tenancy/tenants/?name=" + self.network + "-" + self.domain
            tenant_response = self.rest.get(url, headers=headers)
        except RestUtilityException as err:
            logger.error(f"Failed to validate tenant {err}")
            raise ConnectorException(f"could not validate the provided network and domain: {err.args[0]}")
        try:
            count = tenant_response["count"]
            if not count:
                logger.error(
                    "Tenant is not found in Netbox for provided network '{0}' and domain '{1}'".format(
                        self.network, self.domain
                    )
                )
            else:
                return tenant_response["results"][0]["id"]
        except (ValueError, TypeError, AttributeError, KeyError) as err:
            raise ResourceServiceNotAvailable(f"could not validate the provided network and domain: {err.args[0]}")


class PrefixAvailableIps:
    def __init__(self, request_body):
        self.prefix = request_body["prefix"]
        self.limit = request_body.get("quantity")
        self.domain = request_body["domain"]
        self.network = request_body.get("network")
        self.err_msg = "Unknown"
        self.rest = RestUtility()

    def get_prefix_available_ips(self):
        """
        Args:
            self
        Returns: status, metadata as avlIpAddressList and vrf
        """
        logger.info(f"Fetching the available ips for the prefix {self.prefix}")
        try:
            ipam_prefix_response = self.get_ipam_prefixes()
            if ipam_prefix_response["count"]:
                id, vrf = (
                    ipam_prefix_response["results"][0]["id"],
                    ipam_prefix_response["results"][0]["vrf"] or "Global",
                )
                response_available_ips = self.get_ipam_prefix_available_ips(id)
                list_of_ip_address = [
                    result["address"] for result in response_available_ips if result["address"] != self.prefix
                ]
                if list_of_ip_address:
                    json_response = {
                        "status": "success",
                        "metadata": {"vrf": vrf, "avlIpAddressList": list_of_ip_address},
                    }
                else:
                    json_response = {
                        "status": "failure",
                        "errorCategory": "FAILED",
                        "errors": [
                            {
                                "code": "ERR-006-999-1003",
                                "message": "Prefix has been exhausted and There is No Available IPs. "
                                "Please validate the Prefix",
                            }
                        ],
                    }
            else:
                json_response = {
                    "status": "failure",
                    "errorCategory": "FAILED",
                    "errors": [
                        {"code": "ERR-006-999-0001", "message": "Prefix does not exists. Please provide proper Prefix"}
                    ],
                }
                raise ResourceServiceNotAvailable(json_response)
            return json_response
        except (KeyError, ValueError, AttributeError, ConnectorException) as err:
            self.err_msg = (
                f"Getting the available ips for the given prefix operation failed due to Exception: "
                f"{err.__class__.__name__} {err.args[0]}"
            )
            logger.error(f"Getting the available ips for the given {self.prefix} failed due to {self.err_msg}")
            return self.err_msg

    def get_ipam_prefixes(self):
        """
        Args:
            self
            response : returns response from the netbox prefix api
        """
        logger.info(f"Invoking the netbox prefix api for ipam")
        try:
            url = netbox_url + "ipam/prefixes/?prefix=" + self.prefix
            return self.rest.get(url, headers=headers)
        except (ValueError, TypeError, AttributeError) as err:
            logger.exception(f"{err.args[0]} while invoking the netbox prefix api for ipam", exc_info=True)
            raise ConnectorException(
                f"Invoking the netbox prefix api from ipam failed due to " f"Exception: {err.args[0]}"
            )

    def get_ipam_prefix_available_ips(self, id):
        """
        Args:
            id: id to be used as parameter to invoke prefix available ips netbox api
        Returns:
            response : returns response from the netbox prefix available ips api

        """
        logger.info(f"Invoking the netbox available ips api for ipam")
        try:
            url = netbox_url + "ipam/prefixes/" + str(id) + "/available-ips/?limit=" + str(self.limit)
            return self.rest.get(url, headers=headers)
        except (ValueError, TypeError, AttributeError) as err:
            logger.exception(f"{err.args[0]} while invoking the netbox available ips api for ipam", exc_info=True)
            raise ConnectorException(
                f"Invoking the get prefix available ips api  from ipam failed due to " f"Exception: {err.args[0]}"
            )


class DeleteIpAddress:
    def __init__(self, request_body):
        self.id_to_delete = request_body["ID"]
        self.rest = RestUtility()

    def delete_ip(self):
        """
        Delete a IP from Netbox

        Args:
        user_model

        Returns:
            Status, msg

        Raises:
            Problem in deleting IP from Netbox
        """
        try:
            delete_url = netbox_url + "ipam/ip-addresses/" + str(self.id_to_delete) + "/"
            response = self.rest.delete(delete_url, headers=headers)
            if response == 204:
                return {
                    "status": "success",
                }
            else:
                return {
                    "status": "failure",
                    "errorCategory": "FAILED",
                    "errors": [{"code": "ERR-006-999-0007", "message": "Delete IP: ID not found"}],
                }
        except (ValueError, TypeError, AttributeError, KeyError, RestUtilityException) as err:
            raise ConnectorException(f"{err.args[0]}")


class CreatePrefix:
    def __init__(self, request_body):
        self.rest = RestUtility()
        self.site = request_body.get("site")
        self.vrf = request_body.get("vrf")
        self.tenant = request_body.get("tenant")
        self.role = request_body.get("role")
        self.is_pool = request_body.get("is_pool") is True
        self.prefix = request_body["prefix"]
        self.description = request_body.get("description")
        self.tags = request_body.get("tags")
        self.custom_fields = request_body.get("custom_fields")

    def create_prefix(self):  # noqa: C901
        """Create a prefix from Netbox"""
        prefix_status = {}
        prefix_payload = {"prefix": self.prefix, "is_pool": self.is_pool}
        if self.description:
            prefix_payload["description"] = self.description
        if self.tags:
            prefix_payload["tags"] = self.tags
        if self.custom_fields:
            prefix_payload["custom_fields"] = self.custom_fields
        if self.role:
            try:
                role_url = netbox_url + "ipam/roles/?name=" + self.role
                role_response = self.rest.get(role_url, headers=headers)
                prefix_payload["role"] = role_response["results"][0]["id"]
            except (ValueError, TypeError, AttributeError, KeyError, IndexError) as err:
                raise ResourceServiceNotAvailable(f"could not validate the provided role: {err.args[0]}")

        if self.tenant:
            try:
                tenant_url = netbox_url + "tenancy/tenants/?name=" + self.tenant
                tenant_response = self.rest.get(tenant_url, headers=headers)
                prefix_payload["tenant"] = tenant_response["results"][0]["id"]
            except (ValueError, TypeError, AttributeError, KeyError, IndexError) as err:
                raise ResourceServiceNotAvailable(f"could not validate the provided tenant: {err.args[0]}")

        if self.vrf:
            try:
                vrf_url = netbox_url + "ipam/vrfs/?name=" + self.vrf
                vrf_response = self.rest.get(vrf_url, headers=headers)
                prefix_payload["vrf"] = vrf_response["results"][0]["id"]
            except (ValueError, TypeError, AttributeError, KeyError, IndexError) as err:
                raise ResourceServiceNotAvailable(f"could not validate the provided vrf: {err.args[0]}")

        if self.site:
            try:
                site_url = netbox_url + "dcim/sites/?name=" + self.site
                site_response = self.rest.get(site_url, headers=headers)
                prefix_payload["site"] = site_response["results"][0]["id"]
            except (ValueError, TypeError, AttributeError, KeyError, IndexError) as err:
                raise ResourceServiceNotAvailable(f"could not validate the provided site: {err.args[0]}")

        try:
            prefix_url = netbox_url + "ipam/prefixes/"
            prefix_status = self.rest.post(
                prefix_url,
                headers=post_headers,
                data=json.dumps(prefix_payload),
            )
        except RestUtilityException as err:
            logger.error(f"Create prefix Interface failed: {err.args[0]}")

        if prefix_status and prefix_status.get("id"):
            response_object = {"status": "success", "id": prefix_status.get("id")}
        else:
            response_object = {
                "status": "failure",
                "errorCategory": "FAILED",
                "errors": [
                    {
                        "code": "ERR-006-999-0008",
                        "message": "Prefix creation Interface failed. Provided prefix already exists",
                    }
                ],
            }

        return response_object


class DeletePrefix:
    def __init__(self, request_body):
        self.id_to_delete = request_body["ID"]
        self.rest = RestUtility()

    def delete_prefix(self):
        """
        Delete a prefix from Netbox
        Args: ID
        Returns: Status, msg
        Raises: Problem in deleting prefix from Netbox
        """
        try:
            delete_url = netbox_url + "ipam/prefixes/" + str(self.id_to_delete) + "/"
            delete_response = self.rest.delete(delete_url, headers=headers)
            if delete_response == 204:
                return {
                    "status": "success",
                }
            else:
                return {
                    "status": "failure",
                    "errorCategory": "FAILED",
                    "errors": [{"code": "ERR-006-999-0009", "message": "Delete Prefix: ID not found"}],
                }
        except (ValueError, TypeError, AttributeError, KeyError, RestUtilityException) as err:
            raise ConnectorException(f"{err.args[0]}")
