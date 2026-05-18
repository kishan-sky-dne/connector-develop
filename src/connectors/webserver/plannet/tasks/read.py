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
from datetime import date, datetime

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.services.plannet.connector import PlannetService
from connectors.core.utils.exceptions import RestUtilityException
from connectors.core.utils.helpers import exception_handler, key_in_dict

# from connectors.core.utils.oauth import azure_ad_token_generator

logger = logging.getLogger(__name__)

"""
Plannet/AD Parameters
"""
base_url = config.get(section="plannet", key="base_url")
ad_username = config.get(section="plannet", key="username")
ad_password = config.get(section="plannet", key="password")
access_token = config.get(section="plannet", key="access_token")
# Instantiating plannet object
plannet_obj = PlannetService()


def get_circuit_types(**kwargs):
    """
    Landing function to fetch circuit types from PLANNET inventory
    kwargs:
        type: type of circuit e.g gea > sting (optional)
        id: circuit Id > integer (optional)
        limit: limit the number of response (optional)
        offset: skip the number of response from top (optional)
    returns:
        Plannet data in JSON format
    """
    logger.info("Entering into plannet connector module to get circuit type details from plannet Inventory")
    try:
        # access_token = azure_ad_token_generator(ad_username=ad_username, ad_password=ad_password)
        kwargs["headers"] = {
            "Content-Type": "application/json",
            "Authorization": f"Token {access_token}",
        }

        query_list = [
            f"name={kwargs.get('type')}",
            f"id={kwargs.get('id')}",
            f"provider={kwargs.get('provider')}",
            f"q={kwargs.get('filter')}",
            f"limit={kwargs['limit']}",
            f"offset={kwargs['offset']}",
        ]
        # Apply only those queries that are provided by user
        query_list = list(filter(lambda x: "None" not in x, query_list))
        query_url = f"?{'&'.join(query_list)}"
        kwargs["url"] = f"api/circuits/circuit-types{query_url}"
        data = plannet_obj.get_plannet_details(**kwargs)
        logger.debug(f"Fetched plannet data from plannet inventory: {data}")
        output = {"count": data.get("count", 0), "results": data.get("results", [])}
        if data.get("next"):
            output["next"] = data.get("next").replace(
                f"{base_url}api/circuits/circuit-types", "/inventory/plannet/circuitTypes"
            )

        if data.get("previous"):
            output["previous"] = data.get("previous").replace(
                f"{base_url}api/circuits/circuit-types", "/inventory/plannet/circuitTypes"
            )

        logger.debug(f"Details from plannet circuitDetails : {output}")
    except RestUtilityException as err:
        message = f"Request Exception while accessing the URL {err.args[0]}"
        logger.exception(message, exc_info=True)
        return {"errorCategory": "FAILED", "errors": [{"code": "ERR-010-999-0001", "message": message}]}
    except Exception as err:
        message = (
            f"Connector exception raised while sending url to PLANNET inventory: "
            f"{err.__class__.__name__} - {err.args[0]}"
        )
        logger.exception(message, exc_info=True)
        return {"errorCategory": "FAILED", "errors": [{"code": "ERR-010-999-0002", "message": message}]}
    else:
        logger.info("Exiting get circuit type PLANNET module after sending the api response")
        return output


def get_interface_links(**kwargs):
    logger.info("Entering into plannet connector module to fetch details for interface links from plannet Inventory")

    try:
        current_timestamp = datetime.now()
        # access_token = azure_ad_token_generator(ad_username=ad_username, ad_password=ad_password)
        kwargs["headers"] = {
            "Content-Type": "application/json",
            "Authorization": f"Token {access_token}",
        }
        link_type = "" if kwargs.get("linkType") == "None" else kwargs.get("linkType")
        query_list = [
            f"link_type={link_type}",
            f"from_ne={kwargs.get('fromHostName')}",
            f"to_ne={kwargs.get('toHostName')}",
            f"on_ne={kwargs.get('onHostName')}",
            f"circuit={kwargs.get('circuitID')}",
            f"search_live_date={kwargs.get('date')}",
            f"id={kwargs.get('id')}",
            f"name={kwargs.get('name')}",
            f"interface_1={kwargs.get('interface1')}",
            f"interface_2={kwargs.get('interface2')}",
            f"ne_1={kwargs.get('ne1')}",
            f"ne_2={kwargs.get('ne2')}",
            f"is_transmission={kwargs.get('isTransmission')}",
            f"description={kwargs.get('description')}",
            f"link_prev={kwargs.get('linkPrev')}",
            f"atg={kwargs.get('atg')}",
            f"dtg={kwargs.get('dtg')}",
            f"rate={kwargs.get('rate')}",
            f"on_interface={kwargs.get('onInterface')}",
            f"from_interface={kwargs.get('fromInterface')}",
            f"to_interface={kwargs.get('toInterface')}",
            f"subrate={kwargs.get('subrate')}",
            f"is_active={kwargs.get('isActive')}",
            f"pw_id={kwargs.get('pwId')}",
            f"search_atg_id={kwargs.get('searchAtgId')}",
            f"search_dtg_id={kwargs.get('searchDtgId')}",
            f"search_atg_date={kwargs.get('searchAtgDate')}",
            f"search_dtg_date={kwargs.get('searchDtgDate') or '2099-12-31'}",
            f"search_atg_date_0={kwargs.get('searchAtgDate0')}",
            f"search_atg_date_1={kwargs.get('searchAtgDate1') or current_timestamp.strftime('%Y-%m-%d')}",
            f"search_dtg_date_0={kwargs.get('searchDtgDate0')}",
            f"search_dtg_date_1={kwargs.get('searchDtgDate1')}",
            f"search_live_date_range_0={kwargs.get('searchLiveDateRange0')}",
            f"search_live_date_range_1={kwargs.get('searchLiveDateRange1')}",
            f"q={kwargs.get('filter')}",
            f"pk={kwargs.get('pk')}",
            f"child={kwargs.get('child')}",
            f"limit={kwargs['limit']}",
            f"offset={kwargs['offset']}",
        ]
        # Apply only those queries that are provided by user
        query_list = list(filter(lambda x: "None" not in x, query_list))
        query_url = f"?{'&'.join(query_list)}"
        kwargs["url"] = f"api/dcim/interface-links/{query_url}"
        data = plannet_obj.get_plannet_details(**kwargs)
        if data.get("next"):
            data["next"] = data.get("next").replace(
                f"{base_url}api/dcim/interface-links/", "/inventory/plannet/interfaceLinks"
            )

        if data.get("previous"):
            data["previous"] = data.get("previous").replace(
                f"{base_url}api/dcim/interface-links/", "/inventory/plannet/interfaceLinks"
            )

        logger.debug(f"Details from PLANNET for interface links : {data}")
    except RestUtilityException as err:
        message = f"Request Exception while accessing the URL {err.args[0]}"
        logger.exception(message, exc_info=True)
        return {"errorCategory": "FAILED", "errors": [{"code": "ERR-010-999-0001", "message": message}]}
    except Exception as err:
        message = (
            f"Connector exception raised while sending url for interface links to PLANNET: "
            f"{err.__class__.__name__} - {err.args[0]}"
        )
        logger.exception(message, exc_info=True)
        return {"errorCategory": "FAILED", "errors": [{"code": "ERR-010-999-0002", "message": message}]}
    else:
        logger.info("Exiting PLANNET module after sending the api response")
        return data


def get_nes_details(**kwargs) -> list | dict:
    """
    Listing and details of NE (Network elements) within the Sky's network
    """
    logger.info("Entering into plannet connector module to fetch details for network elements from plannet Inventory")

    try:
        # access_token = azure_ad_token_generator(ad_username=ad_username, ad_password=ad_password)
        kwargs["headers"] = {
            "Content-Type": "application/json",
            "Authorization": f"Token {access_token}",
        }
        query_list = [
            f"search_live_date={kwargs.get('searchLiveDate')}",
            f"search_atg_id={kwargs.get('searchAtgId')}",
            f"search_dtg_id={kwargs.get('searchDtgId')}",
            f"search_atg_date={kwargs.get('searchAtgDate')}",
            f"search_dtg_date={kwargs.get('searchDtgDate')}",
            f"search_atg_date_0={kwargs.get('searchAtgDate0')}",
            f"search_atg_date_1={kwargs.get('searchAtgDate1')}",
            f"search_dtg_date_0={kwargs.get('searchDtgDate0')}",
            f"search_dtg_date_1={kwargs.get('searchDtgDate1')}",
            f"search_live_date_range_0={kwargs.get('searchLiveDateRange0')}",
            f"search_live_date_range_1={kwargs.get('searchLiveDateRange1')}",
            f"q={kwargs.get('filter')}",
            f"name={kwargs.get('name')}",
            f"hostname={kwargs.get('hostName')}",
            f"description={kwargs.get('description')}",
            f"serial={kwargs.get('serial')}",
            f"asn={kwargs.get('asn')}",
            f"search_room={kwargs.get('searchRoom')}",
            f"id={kwargs.get('id')}",
            f"parent={kwargs.get('parent')}",
            f"manufacturer_id={kwargs.get('manufacturerId')}",
            f"parents={kwargs.get('parents')}",
            f"search_region={kwargs.get('searchRegion')}",
            f"search_site={kwargs.get('searchSite')}",
            f"search_ne_role={kwargs.get('searchNeRole')}",
            f"search_tenant={kwargs.get('searchTenant')}",
            f"search_manufacturer={kwargs.get('searchManufacturer')}",
            f"search_ne_type={kwargs.get('searchNeType')}",
            f"search_platform={kwargs.get('searchPlatform')}",
            f"search_rack={kwargs.get('searchRack')}",
            f"is_pseudo={kwargs.get('isPseudo')}",
            f"q_customised={kwargs.get('qCustomised')}",
            f"limit={kwargs['limit']}",
            f"offset={kwargs['offset']}",
            f"resilient_for={kwargs.get('resilient_for')}",
        ]
        # Apply only those queries that are provided by user
        query_list = list(filter(lambda x: "None" not in x, query_list))
        query_url = f"?{'&'.join(query_list)}"
        kwargs["url"] = f"api/dcim/nes/{query_url}"
        data = plannet_obj.get_plannet_details(**kwargs)
        if data.get("next"):
            data["next"] = data.get("next").replace(f"{base_url}api/dcim/nes/", "/inventory/plannet/nes")

        if data.get("previous"):
            data["previous"] = data.get("previous").replace(f"{base_url}api/dcim/nes/", "/inventory/plannet/nes")

        logger.debug(f"Details from PLANNET for network elements : {data}")
    except RestUtilityException as err:
        message = f"Request Exception while accessing the URL {err.args[0]}"
        logger.exception(message, exc_info=True)
        return {"errorCategory": "FAILED", "errors": [{"code": "ERR-010-999-0001", "message": message}]}
    except Exception as err:
        message = (
            f"Connector exception raised while sending url for network elements data to PLANNET: "
            f"{err.__class__.__name__} - {err.args[0]}"
        )
        logger.exception(message, exc_info=True)
        return {"errorCategory": "FAILED", "errors": [{"code": "ERR-010-999-0002", "message": message}]}
    else:
        logger.info("Exiting PLANNET module after sending the api response")
        return data


def set_downstream_devices(**kwargs):
    """setting values to downstream and other than ma devices

    Param:
        dict:
        result(dict) : result
        circuit_mapping(dict) : key and circuit value
        role_mapping(dict) : key and role value
        downstream_devices(dict) : devices with id and role
        end(dict) : ne_1, ne_2
        mas(dict) : True/False based on mas or other than mas to be fetched

    Return:
        dict: downstream devices
    """
    logger.info(f"Inside set_downstream_devices kwargs {kwargs}")
    result = kwargs.get("result")
    circuit_mapping = kwargs.get("circuit_mapping")
    role_mapping = kwargs.get("role_mapping")
    downstream_devices = kwargs.get("downstream_devices")
    end = kwargs.get("end")
    mas = kwargs.get("mas", True)
    if (
        mas
        and result.get("circuit")
        and int(result.get("circuit", {}).get("type", "").split("/")[-1]) in circuit_mapping
        and int(result.get(end, {}).get("ne_role", "").split("/")[-1]) in role_mapping
    ) or (not mas and int(result.get(end, {}).get("ne_role", "").split("/")[-1]) in role_mapping):
        downstream_devices.setdefault(
            result.get(end, {}).get("name", ""),
            {
                "id": int(result.get(end, {}).get("id", "")),
                "role": role_mapping.get(int(result.get(end, {}).get("ne_role", "").split("/")[-1]), ""),
            },
        )
    logger.info(f"Exit set_downstream_devices downstream_devices {downstream_devices}")
    return downstream_devices


def find_downstream_devices(hostnames, circuit_mapping={}, role_mapping={}, traversed_hosts=[]):
    """
    Method to recursively find the downstream devices that are affected if MA's provided in argument
    are in down state.
    Args:
        hostnames - list of hostnames (head-end MA's)
        circuit_mapping - list of id's for applicable circuit types
        role_mapping - list of id's for applicable device roles
        traversed_hosts - list
    Returns:
        list of downstream devices that will be affected
    """
    logger.info(f"find downstream devices for {hostnames}")
    downstream_devices = {}
    other_than_mas = {}
    for host, value in hostnames.items():
        if host not in traversed_hosts:
            traversed_hosts.append(host)
            nes_data = get_nes_details(name=host, limit=50, offset=0)
            logger.info(f"nes_data {nes_data}")
            if nes_data and nes_data.get("count") != 0:
                host_id = nes_data["results"][0]["id"]
                intf_link_response = get_interface_links(
                    linkType="Ethernet Bearer", date=date.today(), limit=100, ne1=host_id, offset=0
                )
                logger.debug(f"interface links response  data {intf_link_response}")
                logger.info(f"circuit_mapping {circuit_mapping}")
                logger.info(f"role_mapping {role_mapping}")
                if intf_link_response:
                    for result in intf_link_response.get("results", []):
                        kwargs = {"result": result, "circuit_mapping": circuit_mapping, "role_mapping": role_mapping}
                        if (
                            len(hostnames.keys()) == 1
                            and result.get("ne_1", {}).get("name", "") == list(hostnames.keys())[0]
                        ):
                            downstream_devices = set_downstream_devices(
                                **{"end": "ne_1", "downstream_devices": downstream_devices, **kwargs}
                            )
                        downstream_devices = set_downstream_devices(
                            **{"end": "ne_2", "downstream_devices": downstream_devices, **kwargs}
                        )
                        other_than_mas = set_downstream_devices(
                            **{"end": "ne_2", "downstream_devices": other_than_mas, "mas": False, **kwargs}
                        )
                    if downstream_devices:
                        child_devices = find_downstream_devices(
                            downstream_devices, circuit_mapping, role_mapping, traversed_hosts
                        )
                        logger.info(f"child_devices {child_devices}")
                        if child_devices:
                            downstream_devices.update(child_devices)
                    downstream_devices.update(other_than_mas)
                else:
                    err_msg = f"Failed to fetch interface links data from plannet for host {host}"
                    logger.error(intf_link_response)
                    return err_msg
            else:
                # err_msg = f"Failed to fetch network element data from plannet for host {host}"
                err_msg = f"Provided Host {host} is not registered with Planet"
                logger.error(nes_data)
                return err_msg
    logger.info(f"Fetched downstream device {downstream_devices} for hostnames {hostnames}")
    return downstream_devices


def fetch_circuit_types(type_list=None):
    """
    Method to get required circuit types
    Returns:
        status
        circuit_type
    """
    try:
        circuit_types = get_circuit_types(limit=100, offset=0)
        logger.info(f"circuit_types {circuit_types}")
        circuit_type = {
            device_type["id"]: device_type["name"]
            for device_type in circuit_types["results"]
            if type_list is None or device_type["name"] in type_list
        }  # Sourcery suggestion
        logger.info(f"circuit types are {circuit_type}")
        return circuit_type
    except Exception as err:
        err_msg = f"get circuit types Failed with error {str(err)}"
        logger.exception(err)
        return err_msg


def get_downstream_device(hostnames, circuit_type_list, role_list):
    """
    Get downstream device list from plannet api for given hostnames. Downstream MA's will be depend on
    circuit type and device roles passed
    Args:
        hostnames - list of hostnames (head-end MA's)
        service_type - denotes specific service type eg: wholesale, voice
        circuit_type_list - circuit type eg: ["Backhaul", "Intra-exchange link"]
        role_list - roles eg: ["m_agg", "m_edge"]
    Returns:
        list of downstream ma
    """
    try:
        logger.info(
            f"Get downstream device detail for hostnames: {hostnames} "
            f"circuit_type_list {circuit_type_list} role_list {role_list}"
        )
        circuit_mapping = fetch_circuit_types(type_list=circuit_type_list)
        # if not isinstance(circuit_mapping,str):
        #     logger.info(f"get_downstream_device circuit_mapping {circuit_mapping}")
        #     circuit_mapping = list(map(int, circuit_mapping.keys()))
        if isinstance(circuit_mapping, str):
            return "Failed to fetch circuit types data from connector plannet api"
        role_mapping = {}
        for role in role_list:
            device_role = get_device_roles(name=role, limit=100, offset=0)
            logger.info(f"device_role {device_role}")
            if "results" in device_role and device_role.get("count") == 1:
                role_mapping[device_role["results"][0]["id"]] = role
            else:
                return f"Failed to fetch {role} role data from connector plannet api"
        # logger.info(
        #     f"fetched downstream device detail for hostnames: {hostnames} and" f" service type : {service_type}"
        # )
        return find_downstream_devices(hostnames, circuit_mapping, role_mapping, traversed_hosts=[])
    except (AttributeError, KeyError, TypeError) as err:
        err_msg = f"Exception while fetching circuit and role mapping failed : {err}"
        logger.exception(err_msg)
        return err_msg
    except Exception as err:
        err_msg = f"Get circuit and role mapping failed due to generic exception : {err}"
        logger.exception(err_msg)
        return err_msg


def fetch_circuits(hostnames):
    """_summary_

    Args:
        hostnames (dict): hostnames with id and role

    Returns:
        dict: circuit details
    """
    logger.info(f"Inside fetch_circuits hostnames {hostnames}")
    try:
        oghp_cid = []
        wholesale_cid = []
        oghp_cis = []
        wholesale_cis = []
        wholesale_cis_not_ebcl = []
        wholesale_cis_ebcl = []
        circuit_type_mapper = {
            "wholesale": ["Wholesale Access"],
            "oghp": ["GEA cablelink"],
        }
        circuit_types = get_circuit_types(limit=100, offset=0)
        logger.info(f"fetch_circuits circuit_types {circuit_types}")
        for result in circuit_types.get("results", []):
            if result["name"] in circuit_type_mapper["wholesale"]:
                wholesale_cid.extend([str(result["id"])])
            elif result["name"] in circuit_type_mapper["oghp"]:
                oghp_cid.extend([str(result["id"])])

        for ci, values in hostnames.items():
            circuit_link = get_interface_links(linkType="Ethernet Bearer", onHostName=ci, limit=100, offset=0)
            logger.info(f"circuit_link {circuit_link}")
            for link in circuit_link.get("results", []):
                if link["circuit"]:
                    oghp_cis.extend([link["circuit"]["cid"] for item in oghp_cid if item in link["circuit"]["type"]])
                    wholesale_cis_not_ebcl.extend(
                        [
                            link["circuit"]["cid"]
                            for item in wholesale_cid
                            if item in link["circuit"]["type"] and not link["circuit"]["cid"].startswith("EBCL")
                        ]
                    )
                    wholesale_cis_ebcl.extend(
                        [
                            link["circuit"]["cid"].split("-")[0] + "/" + link["circuit"].get("parent_ref", "")
                            for item in wholesale_cid
                            if (item in link["circuit"]["type"])
                            and link["circuit"]["cid"].startswith("EBCL")
                            and link["circuit"].get("parent_ref")
                        ]
                    )
                    wholesale_cis.extend(wholesale_cis_not_ebcl + wholesale_cis_ebcl)
        wholesale_values = {"wholesale": list(set(wholesale_cis))} if wholesale_cis else {}
        gea_values = {"geas": list(set(oghp_cis))} if oghp_cis else {}
        return wholesale_values | gea_values
    except (AttributeError, KeyError, TypeError) as err:
        err_msg = f"Exception while fetching circuit failed : {err}"
        logger.exception(err_msg)
        return err_msg
    except Exception as err:
        err_msg = f"Get circuit failed due to generic exception : {err}"
        logger.exception(err_msg)
        return err_msg


def fetch_nes(hostnames):
    """fetching nes based on role

    Args:
        hostnames (dict): hostnames with id and role

    Returns:
        dict: ne details
    """
    response_nes = {}
    ne_map = {
        "switches": ["m_switch"],
        "mas": ["m_agg", "m_edge"],
        "llus": ["llu"],
        "exchangeMgmtNes": ["exch.mgmt"],
        "wapNNI": ["wap-nni"],
    }
    for host, values in hostnames.items():
        for key, map in ne_map.items():
            if values.get("role") in map:
                response_nes.setdefault(key, []).append(host)
    return response_nes


def get_cis_details(**kwargs):
    """get cis details recursively from planned

    Args:
        host (string): hostname
        _include (list): [nes,circuits]

    Returns:
        dict: nes and circuits
    """
    logger.info("Entering into plannet connector module to fetch details for network elements from plannet Inventory")
    nes = None
    circuits = None
    hostnames = {}
    errors = []
    circuit_type_list = ["Backhaul", "Intra-exchange link"]
    # role_list = ["m_agg", "m_edge","m_switch","ISAM-B","ISAM-V","llu","AR-999","AR-999","exch.mgmt"]
    role_list = ["m_agg", "m_edge", "m_switch", "llu", "exch.mgmt", "wap-nni"]
    # for service_type in ["wholesale", "voice"]:
    response = get_downstream_device({kwargs.get("host"): ""}, circuit_type_list, role_list)
    logger.info(f"get_downstream_device response {response}")
    if isinstance(response, dict):
        hostnames.update(response)
        logger.debug(f"List of recursively connected downstream devices - {list(response)}")
    else:
        errors.append(response)
    if errors:
        return {"errorCategory": "FAILED", "errors": [{"code": "ERR-010-999-0001", "message": msg} for msg in errors]}
    include_values = kwargs.get("_include", [])
    if not include_values or "circuits" in include_values:
        circuits = fetch_circuits(hostnames)
        logger.info(f"final circuits {circuits}")
    if not include_values or "nes" in include_values:
        nes = fetch_nes(hostnames)
    return {"nes": nes or None, "circuits": circuits or None}


def get_device_roles(**kwargs):
    logger.info("Entering into plannet connector module to fetch details for device roles from plannet Inventory")

    try:
        # access_token = azure_ad_token_generator(ad_username=ad_username, ad_password=ad_password)
        kwargs["headers"] = {
            "Content-Type": "application/json",
            "Authorization": f"Token {access_token}",
        }
        query_list = [
            f"id={kwargs.get('id')}",
            f"name={kwargs.get('name')}",
            f"description={kwargs.get('description')}",
            f"color={kwargs.get('color')}",
            f"q={kwargs.get('filter')}",
            f"limit={kwargs['limit']}",
            f"offset={kwargs['offset']}",
        ]
        # Apply only those queries that are provided by user
        query_list = list(filter(lambda x: "None" not in x, query_list))
        query_url = f"?{'&'.join(query_list)}"
        kwargs["url"] = f"api/dcim/ne-roles/{query_url}"
        data = plannet_obj.get_plannet_details(**kwargs)
        if data.get("next"):
            data["next"] = data.get("next").replace(f"{base_url}api/dcim/ne-roles/", "/inventory/plannet/deviceRoles")

        if data.get("previous"):
            data["previous"] = data.get("previous").replace(
                f"{base_url}api/dcim/ne-roles/", "/inventory/plannet/deviceRoles"
            )

        logger.debug(f"Details from PLANNET for device roles : {data}")
    except RestUtilityException as err:
        message = f"Request Exception while accessing the URL {err.args[0]}"
        logger.exception(message, exc_info=True)
        return {"errorCategory": "FAILED", "errors": [{"code": "ERR-010-999-0001", "message": message}]}
    except Exception as err:
        message = (
            f"Connector exception raised while sending url for device roles data to PLANNET: "
            f"{err.__class__.__name__} - {err.args[0]}"
        )
        logger.exception(message, exc_info=True)
        return {"errorCategory": "FAILED", "errors": [{"code": "ERR-010-999-0002", "message": message}]}
    else:
        logger.info("Exiting PLANNET module after sending the api response")
        return data


def get_sites(**kwargs):
    """
    Landing function to fetch sites from PLANNET inventory
    kwargs:
        type: type of site e.g exch (optional)
        filter: CLB, GATE, 6NJ (optional)
        limit: limit the number of response (optional)
        offset: skip the number of response from top (optional)
    returns:
        Plannet data in JSON format
    """
    logger.info("Entering into plannet connector module to get sites info details from plannet Inventory")
    try:
        # access_token = azure_ad_token_generator(ad_username=ad_username, ad_password=ad_password)
        kwargs["headers"] = {
            "Content-Type": "application/json",
            "Authorization": f"Token {access_token}",
        }

        query_list = [
            f"types={kwargs.get('types')}",
            f"id={kwargs.get('id')}",
            f"q={kwargs.get('filter')}",
            f"limit={kwargs.get('limit')}",
            f"offset={kwargs.get('offset')}",
            f"name={kwargs.get('name')}",
            f"code_ip={kwargs.get('codeIp')}",
            f"code_op={kwargs.get('codeOp')}",
            f"provider={kwargs.get('provider')}",
            f"physical_address={kwargs.get('physicalAddress')}",
            f"postcode={kwargs.get('postcode')}",
            f"description={kwargs.get('description')}",
            f"subtypes={kwargs.get('subtypes')}",
            f"latitude={kwargs.get('latitude')}",
            f"longitude={kwargs.get('longitude')}",
            f"id__in={kwargs.get('ids')}",
            f"fullname={kwargs.get('fullname')}",
            f"region_id={kwargs.get('regionId')}",
            f"region={kwargs.get('region')}",
            f"tenant={kwargs.get('tenant')}",
            f"tenant_id={kwargs.get('tenantId')}",
        ]
        # Apply only those queries that are provided by user
        query_list = list(filter(lambda x: "None" not in x, query_list))
        query_url = f"?{'&'.join(query_list)}"
        kwargs["url"] = f"api/dcim/sites{query_url}"
        data = plannet_obj.get_plannet_details(**kwargs)
        logger.debug(f"Fetched plannet data from plannet inventory: {data}")
        output = {"count": data.get("count", 0), "results": data.get("results", [])}
        if data.get("next"):
            output["next"] = data.get("next").replace(f"{base_url}api/dcim/sites", "/inventory/plannet/sites")

        if data.get("previous"):
            output["previous"] = data.get("previous").replace(f"{base_url}api/dcim/sites", "/inventory/plannet/sites")

        logger.debug(f"Details from plannet sites : {output}")
    except RestUtilityException as err:
        message = f"Request Exception while accessing the URL {err.args[0]}"
        logger.exception(message, exc_info=True)
        return {"errorCategory": "FAILED", "errors": [{"code": "ERR-010-999-0001", "message": message}]}
    except Exception as err:
        message = (
            f"Connector exception raised while sending url to PLANNET inventory: "
            f"{err.__class__.__name__} - {err.args[0]}"
        )
        logger.exception(message, exc_info=True)
        return {"errorCategory": "FAILED", "errors": [{"code": "ERR-010-999-0002", "message": message}]}
    else:
        logger.info("Exiting get circuit type PLANNET module after sending the api response")
        return output


def get_circuit_info(**kwargs):
    """
    Landing function to fetch circuits from PLANNET inventory
    returns:
        Plannet data in JSON format
    """
    logger.info("Entering into Plannet connector module to fetch details for circuits from Plannet Inventory")
    try:
        # access_token = azure_ad_token_generator(ad_username=ad_username, ad_password=ad_password)
        kwargs["headers"] = {
            "Content-Type": "application/json",
            "Authorization": f"Token {access_token}",
        }

        query_list = [
            f"parent_ref={kwargs.get('parentRef')}",
            f"q={kwargs.get('filter')}",
            f"limit={kwargs['limit']}",
            f"offset={kwargs['offset']}",
            f"id={kwargs.get('id')}",
            f"cid={kwargs.get('cid')}",
            f"id__in={kwargs.get('ids')}",
            f"provider_id={kwargs.get('providerId')}",
            f"provider={kwargs.get('provider')}",
            f"type_id={kwargs.get('typeId')}",
            f"type={kwargs.get('type')}",
            f"tenant_id={kwargs.get('tenantId')}",
            f"tenant={kwargs.get('tenant')}",
            f"site_name={kwargs.get('siteName')}",
            f"ne_name={kwargs.get('neName')}",
            f"sub_type={kwargs.get('subType')}",
            f"link_type={kwargs.get('linkType')}",
        ]
        # Apply only those queries that are provided by user
        query_list = list(filter(lambda x: "None" not in x, query_list))
        query_url = f"?{'&'.join(query_list)}"
        kwargs["url"] = f"api/circuits/circuits/{query_url}"
        data = plannet_obj.get_plannet_details(**kwargs)
        logger.debug(f"Fetched plannet data from plannet inventory: {data}")
        output = {"count": data.get("count", 0), "results": data.get("results", [])}
        if data.get("next"):
            output["next"] = data.get("next").replace(f"{base_url}api/circuits/circuits", "/inventory/plannet/circuits")

        if data.get("previous"):
            output["previous"] = data.get("previous").replace(
                f"{base_url}api/circuits/circuits", "/inventory/plannet/circuits"
            )

        logger.debug(f"Details from plannet circuits : {output}")
    except RestUtilityException as err:
        message = f"Request Exception while accessing the URL {err.args[0]}"
        logger.exception(message, exc_info=True)
        return {"errorCategory": "FAILED", "errors": [{"code": "ERR-010-999-0001", "message": message}]}
    except Exception as err:
        message = (
            f"Connector exception raised while sending url to PLANNET inventory: "
            f"{err.__class__.__name__} - {err.args[0]}"
        )
        logger.exception(message, exc_info=True)
        return {"errorCategory": "FAILED", "errors": [{"code": "ERR-010-999-0002", "message": message}]}
    else:
        logger.info("Exiting get circuit type PLANNET module after sending the api response")
        return output


def get_dwdm_info(**kwargs):
    """
    Landing function to fetch DWDM information from PLANNET inventory
    returns:
        Plannet data in JSON format
    """
    logger.info("Entering into Plannet connector module to fetch details for circuits from Plannet Inventory")
    try:
        kwargs["headers"] = {
            "Content-Type": "application/json",
            "Authorization": f"Token {access_token}",
        }

        query_list = [
            f"id={kwargs.get('id')}",
            f"ne_type={kwargs.get('ne_type')}",
            f"interface={kwargs.get('interface')}",
            f"channel_nb={kwargs.get('channel_nb')}",
            f"frequency={kwargs.get('frequency')}",
            f"wavelength={kwargs.get('wavelength')}",
        ]
        # Apply only those queries that are provided by user
        query_list = list(filter(lambda x: "None" not in x, query_list))
        query_url = f"?{'&'.join(query_list)}"
        kwargs["url"] = f"api/dcim/mux-mapping/{query_url}"
        data = plannet_obj.get_plannet_details(**kwargs)
        logger.debug(f"Fetched plannet data from plannet inventory: {data}")

        output = [
            {
                "id": result["id"],
                "ne_type": result["ne_type"]["name"],
                "interface": result["interface"],
                "channel_number": result["channel_nb"],
                "frequency": result["frequency"],
                "wavelength": result["wavelength"],
            }
            for result in data.get("results")
        ]

        #  While loop to use "data["next"]"" value to get next 50 items from Plannet API and append to output
        next_list = []
        while (
            data.get("next")
            and "limit=50" in data.get("next")
            and data.get("next") not in next_list
            and (not kwargs.get("limit") or kwargs.get("limit") % 50 != 0)
        ):
            next_list.append(data.get("next"))
            kwargs["url"] = data.get("next").replace(base_url, "")
            data = plannet_obj.get_plannet_details(**kwargs)
            output.extend(
                [
                    {
                        "id": result["id"],
                        "ne_type": result["ne_type"]["name"],
                        "interface": result["interface"],
                        "channel_number": result["channel_nb"],
                        "frequency": result["frequency"],
                        "wavelength": result["wavelength"],
                    }
                    for result in data.get("results")
                ]
            )

        logger.debug(f"Details from plannet mux-mapping : {output}")

    except RestUtilityException as err:
        message = f"Request Exception while accessing the URL {err.args[0]}"
        logger.exception(message, exc_info=True)
        return {"errorCategory": "FAILED", "errors": [{"code": "ERR-010-999-0001", "message": message}]}
    except Exception as err:
        message = (
            f"Connector exception raised while sending url to PLANNET inventory: "
            f"{err.__class__.__name__} - {err.args[0]}"
        )
        logger.exception(message, exc_info=True)
        return {"errorCategory": "FAILED", "errors": [{"code": "ERR-010-999-0002", "message": message}]}
    else:
        logger.info("Exiting get DWDM type PLANNET module after sending the api response")
        return output


@exception_handler
def get_transition_group_data(**kwargs):
    """
    Gets transition group info

    Returns:
        dict: Transition group info
    """
    tg_id: str = kwargs["id"]
    tg_id = tg_id.lower().replace("tg", "")

    logger.info(f"Entering into PlanNet module to get transition group details for {tg_id}.")
    request: dict = {
        "url": f"api/dcim/tgs/{tg_id}/",
        "headers": {"Content-Type": "application/json", "Authorization": f"Token {access_token}"},
    }
    plannet = PlannetService()
    return plannet.get_plannet_details(**request)


def get_fhrps(**kwargs) -> dict[str, str | list]:
    """
    Landing function to fetch fhrps from PLANNET inventory
    kwargs:
        protocol (str): Type of redundancy protocol
        fhrpIds (int): List of comma separated fhrp ids
        service (str): Service type
        bridgeDomain (str): Bridge domain type
        virtualIpv4 (str): Virtual ipv4 address
        virtualIpv6 (str): Virtual ipv6 address
        devicename (str): Hostname of the device
        query (str): General query
        limit (int): limit the number of response
        offset (int): skip the number of response from top
        _include (str): To include the peer device fhrp info
    returns:
        dict[str, str | list]: Plannet data in JSON format
    """
    logger.info("Entering into plannet connector module to get fhrps details from plannet Inventory")
    if "_include" in kwargs and ("devicename" not in kwargs or "protocol" not in kwargs):
        message: str = "'devicename' and 'protocol' both are required parameter when '_include' parameter is added."
        logger.exception(message, exc_info=True)
        return {"errorCategory": "FAILED", "errors": [{"code": "ERR-010-999-0003", "message": message}]}
    try:
        kwargs["headers"] = {
            "Content-Type": "application/json",
            "Authorization": f"Token {access_token}",
        }
        fhrpids: str | None = ",".join(map(str, kwargs.get("fhrpIds", []))) or None
        query_list: tuple[str] = (
            f"protocol={kwargs.get('protocol')}",
            f"fhrp_ids={fhrpids}",
            f"service={kwargs.get('service')}",
            f"bridge_domain={kwargs.get('bridgeDomain')}",
            f"virtual_ipv4={kwargs.get('virtualIpv4')}",
            f"virtual_ipv6={kwargs.get('virtualIpv6')}",
            f"device_name={kwargs.get('devicename')}",
            f"q={kwargs.get('query')}",
            f"limit={kwargs.get('limit')}",
            f"offset={kwargs.get('offset')}",
        )
        # Apply only those queries that are provided by user
        query_list = list(filter(lambda x: "None" not in x, query_list))
        query_url: str = f"?{'&'.join(query_list)}"
        kwargs["url"] = f"api/dcim/fhrps/{query_url}"
        if "_include" in kwargs:
            output: dict[str, str | list] = get_peer_devices(**kwargs)
        else:
            output: dict[str, str | list] = fetch_fhrps_details_from_plannet(**kwargs)
    except RestUtilityException as err:
        message = f"Request Exception while accessing the URL {err.args[0]}"
        logger.exception(message, exc_info=True)
        return {"errorCategory": "FAILED", "errors": [{"code": "ERR-010-999-0001", "message": message}]}
    except Exception as err:
        message = (
            f"Connector exception raised while sending url to PLANNET inventory: "
            f"{err.__class__.__name__} - {err.args[0]}"
        )
        logger.exception(message, exc_info=True)
        return {"errorCategory": "FAILED", "errors": [{"code": "ERR-010-999-0002", "message": message}]}
    else:
        logger.info("Exiting get fhrps PLANNET module after sending the api response")
        return output


def fetch_fhrps_details_from_plannet(**kwargs) -> dict[str, str | list]:
    """
    Fetch the fhrps details from plannet with the provided filters
    kwargs:
        protocol (str): Type of redundancy protocol
        fhrpIds (int): List of comma separated fhrp ids
        service (str): Service type
        bridgeDomain (str): Bridge domain type
        virtualIpv4 (str): Virtual ipv4 address
        virtualIpv6 (str): Virtual ipv6 address
        devicename (str): Hostname of the device
        query (str): General query
        limit (int): limit the number of response
        offset (int): skip the number of response from top
        _include (str): To include the peer device fhrp info
    returns:
        dict[str, str | list]: Plannet data in JSON format
    """
    data: dict[str, str | list] = plannet_obj.get_plannet_details(**kwargs)
    logger.debug(f"Fetched plannet data from plannet inventory: {data}")
    output: dict[str, str | list] = {"count": data.get("count", 0), "results": data.get("results", [])}
    if data.get("next"):
        output["next"] = data.get("next").replace(f"{base_url}api/dcim/fhrps", "/inventory/plannet/fhrps")

    if data.get("previous"):
        output["previous"] = data.get("previous").replace(f"{base_url}api/dcim/fhrps", "/inventory/plannet/fhrps")

    logger.debug(f"Details from plannet fhrps : {output}")
    return output


def get_peer_devices(**kwargs) -> dict[str, str | list]:
    """get the VRRP/HSRP peer devices

    kwargs:
        protocol (str): Type of redundancy protocol
        devicename (str): Hostname of the device
        limit (int): limit the number of response
        offset (int): skip the number of response from top
        _include (str): To include the peer device fhrp info

    Returns:
        dict[str, str | list]: peer device details
    """
    fhrps, fhrp_ids = get_fhrp_ids(**kwargs)
    peer_fhrps: list[dict] = get_peer_fhrp_info(fhrp_ids, **kwargs)
    peer_lookup: dict[tuple[str], list[dict[str, str]]] = {}

    # create a lookup dict based on the fhrp_id and virtual_ipv4/virtual_ipv6 pair
    for peer in peer_fhrps["results"]:
        if ip := peer.get("virtual_ipv4") or peer.get("virtual_ipv6"):
            peer_lookup.setdefault((peer.get("fhrp_id"), ip), []).append(peer)

    # Searching for peer details based on the peer lookup data
    for fhrp in fhrps["results"]:
        if ip := fhrp.get("virtual_ipv4") or fhrp.get("virtual_ipv6"):
            fhrp["fhrps"].extend(
                peer["fhrps"][0]
                for peer in peer_lookup[(fhrp.get("fhrp_id"), ip)]
                if fhrp["fhrps"][0]["device_name"] != peer["fhrps"][0]["device_name"]
            )
    return fhrps


def get_fhrp_ids(**kwargs) -> tuple[list[dict], list[int]]:
    """Get all FHRP Ids for the current device

    kwargs:
        protocol (str): Type of redundancy protocol
        devicename (str): Hostname of the device
        _include (str): To include the peer device fhrp info

    Returns:
        tuple[list[dict], list[int]]: fhrp details and fhrp ids
    """
    data: list[dict] = plannet_api_call(**kwargs)
    return parse_fhrps(data), list(set(key_in_dict("fhrp_id", data, [])))


def parse_fhrps(fhrp_data: list[dict]) -> dict[str, list[dict]]:
    """Parse the FHRP resposne

    Args:
        fhrp_data (list[dict]): FHRP data getting from Plannet API

    Returns:
        dict[str, list[dict]]: Parsed FHRPs
    """
    return {
        "results": [
            {
                "protocol": peer.get("protocol"),
                "fhrp_id": peer.get("fhrp_id"),
                "virtual_ipv4": peer.get("virtual_ipv4"),
                "virtual_ipv6": peer.get("virtual_ipv6"),
                "fhrps": [
                    {
                        "device_name": fhrp.get("device_name"),
                        "ipv4_address": fhrp.get("ipv4_address"),
                        "ipv6_address": fhrp.get("ipv6_address"),
                    }
                    for fhrp in peer.get("fhrps")
                ],
            }
            for peer in fhrp_data
        ]
    }


def get_peer_fhrp_info(fhrp_ids: list[str], **kwargs) -> dict[list]:
    """Get FHRPs for the peer devices

    Args:
        fhrp_ids (list[str]): fhrp ids found from the device
    kwargs:
        protocol (str): Type of redundancy protocol
        devicename (str): Hostname of the device
        _include (str): To include the peer device fhrp info

    Returns:
        dict[list]: parsed FHRPs
    """
    fhrp_ids: list[str] = [str(id) for id in fhrp_ids]
    kwargs["url"] = f"api/dcim/fhrps/?protocol={kwargs.get('protocol')}&fhrp_ids={','.join(fhrp_ids)}"
    data: list[dict] = plannet_api_call(**kwargs)
    return parse_fhrps(data)


def plannet_api_call(**kwargs) -> dict:
    """PlanNet API calls

    kwargs:
        protocol (str): Type of redundancy protocol
        devicename (str): Hostname of the device
        _include (str): To include the peer device fhrp info

    Returns:
        dict: PlanNet API response
    """
    results: list = []
    max_retry: int = 3
    current_count: int = 0
    while max_retry > current_count:
        try:
            plannet_data: dict = plannet_obj.get_plannet_details(**kwargs)
            results.extend(plannet_data.get("results"))
            if not plannet_data.get("next"):
                break
            kwargs["url"] = plannet_data.get("next").replace(f"{base_url}", "")
        except RestUtilityException as err:
            message = (
                f"Connector exception raised while sending url to PLANNET inventory: "
                f"{err.__class__.__name__} - {err.args[0]}"
            )
            logger.exception(message, exc_info=True)
            current_count += 1
    return results
