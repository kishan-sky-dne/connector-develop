# Standard Library
import logging
import re
import sys

# Third Party Library
import connexion

# Sky Library
from isp_config import ConfigManagerException

# DNE Library
from connectors.core.config import connectors_config
from connectors.core.services.inca.connector import IncaService
from connectors.core.utils.helpers import exception_handler, validate_json_request_payload
from connectors.core.utils.oauth import token_generator
from connectors.webserver.dcs.tasks.read import getDeviceDetails

logger = logging.getLogger(__name__)

try:
    config = connectors_config.ConnectorsConfigManager()
    config.load_config()
except ConfigManagerException:
    sys.exit(1)

"""
INCA/C-Auth Parameters
"""
# INCA
base_url = config.get(section="inca", key="base_url")
nexa_username = config.get(section="inca", key="nexa_username")
nexa_password = config.get(section="inca", key="nexa_password")
username = config.get(section="inca", key="username")
password = config.get(section="inca", key="password")
environment = config.get(section="internals", key="environment").lower()


def _validate_inca_update_data(**data) -> tuple:
    """
    Method to validate the request body for NEXA INCA update
    request:
        data: Request body
    response:
        True/False with errors if any
    """
    body = data["body"]
    logger.info("Validating request body data for INCA update")
    errors = []
    for item in body.get("circuitDetails", []):
        if item.get("circuitState") == "GEA-CEASE":
            _validate_gea_cease(item, errors)
        else:
            _validate_item(item, errors)
    return (False, errors, data) if errors else (True, [], data)


def _validate_gea_cease(item: dict, errors: list) -> None:
    """
    Validates given GEA cease circuit details for INCA update
    """
    if item.get("configStatus") != "success":
        if item.get("configStatus") != "failure":
            errors.append(
                {
                    "code": "ERR-011-999-0008",
                    "message": (
                        "configStatus must be either 'failure' or 'success' for "
                        f"GEA-CEASE circuit {item.get('circuitId')} "
                    ),
                }
            )
        return
    if not item.get("sparkReference"):
        errors.append(
            {
                "code": "ERR-011-999-0003",
                "message": (
                    f"sparkReference must be provided for GEA-CEASE circuit {item.get('circuitId')} "
                    "when configStatus is success."
                ),
            }
        )
    if not item.get("configCeaseDate"):
        errors.append(
            {
                "code": "ERR-011-999-0004",
                "message": (
                    f"configCeaseDate must be provided for GEA-CEASE circuit {item.get('circuitId')} "
                    "when configStatus is success."
                ),
            }
        )
    if not item.get("orCeaseDate"):
        errors.append(
            {
                "code": "ERR-011-999-0005",
                "message": (
                    f"orCeaseDate must be provided for GEA-CEASE circuit {item.get('circuitId')} "
                    "when configStatus is success."
                ),
            }
        )
    if not item.get("orCeaseRef"):
        errors.append(
            {
                "code": "ERR-011-999-0006",
                "message": (
                    f"orCeaseRef must be provided for GEA-CEASE circuit {item.get('circuitId')} "
                    "when configStatus is success."
                ),
            }
        )
    if not item.get("circuitCeaseOrderRef"):
        errors.append(
            {
                "code": "ERR-011-999-0007",
                "message": (
                    f"circuitCeaseOrderRef must be provided for GEA-CEASE circuit {item.get('circuitId')} "
                    "when configStatus is success."
                ),
            }
        )


def _validate_item(item: dict, errors: list) -> None:
    """
    Validates given circuit details for INCA update
    """
    if (
        item.get("configStatus") in ["success", "inprogress"]
        and not item.get("sparkReference")
        and item.get("circuitState") == "Ready-For-Service"
    ):
        errors.append(
            {
                "code": "ERR-011-999-0001",
                "message": (
                    f"sparkReference must be provided for circuit {item.get('circuitId')} as configStatus "
                    f"is {item.get('configStatus')}"
                ),
            }
        )
    if (
        item.get("configStatus") == "inprogress"
        and not item.get("sparkReference")
        and item.get("circuitState") == "Ready-For-Config"
    ):
        errors.append(
            {
                "code": "ERR-011-999-0001",
                "message": (
                    f"sparkReference must be provided for circuit {item.get('circuitId')} as configStatus "
                    f"is {item.get('configStatus')} and circuitState is {item.get('circuitState')}"
                ),
            }
        )
    if item.get("configStatus") == "success" and not item.get("configDate"):
        errors.append(
            {
                "code": "ERR-011-999-0002",
                "message": (
                    f"configDate must be provided for circuit {item.get('circuitId')} as configStatus "
                    f"is {item.get('configStatus')}"
                ),
            }
        )
    if item.get("circuitState", "") == "Ready-For-Config" and item.get("configStatus") not in [
        "success",
        "inprogress",
        "failure",
    ]:
        errors.append(
            {
                "code": "ERR-011-999-0002",
                "message": (
                    f"configStatus must be one of ['success', 'inprogress', 'failure'] "
                    f"for circuit {item.get('circuitId')} as circuitState is {item.get('circuitState')}"
                ),
            }
        )
    if (
        item.get("circuitState", "") == "Ready-For-Config"
        and item.get("configStatus") == "success"
        and not item.get("testRef")
    ):
        errors.append(
            {
                "code": "ERR-011-999-0002",
                "message": (
                    f"testRef must be provided for circuit {item.get('circuitId')} as circuitState is "
                    f"{item.get('circuitState')} and configStatus is {item.get('configStatus')}"
                ),
            }
        )

    if (item.get("testRef") or item.get("comments")) and item.get("circuitState", "") != "Ready-For-Config":
        errors.append(
            {
                "code": "ERR-011-999-0002",
                "message": (
                    f"testRef or comments must not be provided for circuit {item.get('circuitId')} as circuitState "
                    f"is not Ready-For-Config"
                ),
            }
        )
    if (
        (item.get("configStatus", {}) == "inprogress")
        and (item.get("circuitState", {}) == "Ready-For-Config")
        and not item.get("orderRef", {})
    ):
        errors.append(
            {
                "code": "ERR-011-999-0002",
                "message": f"'orderRef' must be provided for circuit {item.get('circuitId')} "
                f"when 'circuitState' is '{item.get('circuitState')}'"
                f" and 'configStatus' is '{item.get('configStatus')}'",
            }
        )
    if item.get("orderRef", {}) and (
        item.get("configStatus", {}) != "inprogress" or item.get("circuitState", "") != "Ready-For-Config"
    ):
        errors.append(
            {
                "code": "ERR-011-999-0002",
                "message": "'orderRef' is required only when 'circuitState' is 'inprogress' "
                "and 'configStatus' is 'Ready-For-Config'",
            }
        )


@exception_handler
def _validate_inca_new_switch_data(**data: dict) -> tuple[bool, list, dict]:
    """
    This function validates inca newSwitch data
    """
    body = data["body"]
    errors = []
    logger.info("Validating request body data for INCA update")
    host_regex = ".it.bb.sky.com|.isp.sky.com|.(dev|test|stage)-uk"
    device_name = re.sub(host_regex, "", body.get("hostname"))
    output = getDeviceDetails(hostname=body.get("hostname"))

    if isinstance(output, dict):
        # COMMENTING BELOW LINES Temporary for BUG FIX DNE-37482
        # description = output.get("snmp_sysdescr", "").lower()
        # applicable_models = ["ncs-540", "ncs-540x", "n540x-acc-sys", "n540-acc-sys"]
        # model_status = any(description.find(model) > -1 for model in applicable_models)
        # device_dcs_status = output.get("status", "").lower()
        # if (
        #     not model_status
        #     or device_dcs_status == "decommissioned"
        #     or (environment == "production" and device_dcs_status != environment)
        # ):
        #     status = False
        #     error = (
        #         f"Device {body.get('hostname')} has un-supported status in dcs inventory: '{device_dcs_status}'"
        #         if model_status
        #         else (
        #             f"Applicable only for models {applicable_models}, device {body.get('hostname')} model is "
        #             f"{output.get('model')}"
        #         )
        #     )
        #     errors.append(
        #         {
        #             "code": "ERR-011-999-0001",
        #             "message": error,
        #         }
        #     )
        data["body"]["hostname"] = device_name
        status = True
        return (True, [], data) if status else (False, errors, data)
    else:
        errors.append(
            {
                "code": "ERR-011-999-0002",
                "message": f"Device {body.get('hostname')} is decommissioned or not found in dcs",
            }
        )
        return False, errors, {}


inca_type = {
    "gea": {"nexa_url": "apex/nexaREST/v0/message", "validation": _validate_inca_update_data},
    "wholesale": {
        "uni": {
            "new": "apex/incaREST/v0/putWsalePlugUpRFS",
            "update": "apex/incaREST/v0/putWsalePlugUpRFS",
            "cease": "apex/incaREST/v0/putWsaleCeaseComplete",
        },
        "partner": {"new": "apex/incaREST/v0/postWsalePartner", "cease": "apex/incaREST/v0/retireWsalePartner"},
        "interconnect": {
            "new": "apex/incaREST/v0/postWsaleNNI",
            "update": "apex/incaREST/v0/putWsaleNNI",
            "cease": "apex/incaREST/v0/retireWsaleNNI",
        },
    },
}


@exception_handler
def update_device_decommissioned(**kwargs) -> dict:
    """
    calling INCA module to update status for device decommissioned

    kwargs:
        body: request body containing device details

    Returns:
            jobID
    """
    logger.info("Entering into INCA module to update device decommissioned details in INCA Inventory")
    token_url = f"{base_url}apex/incaREST/oauth/token"
    access_token = token_generator(url=token_url, username=username, password=password)
    kwargs["headers"] = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    kwargs["url"] = "apex/incaREST/v0/setDeviceDNEDecommissioned"
    inca_obj = IncaService()
    output = inca_obj.update_inca_device_decommissioned(**kwargs)
    logger.info(f"Response for device decommissioned update in INCA Inventory is: {output}")
    return output


@exception_handler
def update_inca_details(**kwargs) -> dict:
    """
    calling INCA module to update status for various INCA type (e.g gea) details

    kwargs:
        type: type of the INCA

    Returns:
            jobID

    Raises:
        Exception

    """
    logger.info(f"Entering into INCA module to fetch details for {kwargs['type']} from INCA Inventory")
    logger.debug(f"kwargs to update INCA for type {kwargs['type']} is: {kwargs}")
    output = ""
    token_url = f"{base_url}apex/nexaREST/oauth/token"
    access_token = token_generator(url=token_url, username=nexa_username, password=nexa_password)
    kwargs["headers"] = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "message_type": "GC",
        "Authorization": f"Bearer {access_token}",
    }
    data = kwargs.get("body", {}).get("circuitDetails")
    for idx, item in enumerate(data):
        if not item.get("circuitState"):
            data[idx]["circuitState"] = "Ready-For-Service"
    inca_obj = IncaService()
    for key in inca_type:
        if kwargs["type"] == key:
            kwargs["url"] = inca_type[key]["nexa_url"]
            status, errors, kwargs = inca_type[key]["validation"](**kwargs)
            if not status:
                return {"errorCategory": "FAILED", "errors": errors}
            output = inca_obj.update_inca_type_details(**kwargs)
    logger.info("Exiting INCA module after sending the api response")
    return output


inca_type_rfs = {
    "newMetroSwitch": {"url": "apex/incaREST/v0/putNewSwitchRFS", "validation": _validate_inca_new_switch_data},
}


@exception_handler
def update_inca_rfs_details(**kwargs):
    """
    calling INCA module to update status for various INCA type (e.g newMetroSwitch) details

    kwargs:
        type: type of the INCA

    Returns:
         {'result': "OK"}

    Raises:
        Exception

    """
    logger.info(f"Entering into INCA module to fetch details for {kwargs['type']} from INCA Inventory")
    logger.debug(f"kwargs to update INCA for type {kwargs['type']} is: {kwargs}")
    output = ""
    token_url = base_url + "apex/incaREST/oauth/token"
    access_token = token_generator(url=token_url, username=username, password=password)
    kwargs["headers"] = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    inca_obj = IncaService()
    for key in inca_type_rfs:
        if kwargs["type"] == key:
            kwargs["url"] = inca_type_rfs[key]["url"]
            status, errors, kwargs = inca_type_rfs[key]["validation"](**kwargs)
            if not status:
                return {"errorCategory": "FAILED", "errors": errors}
            output = inca_obj.update_inca_type_details(**kwargs)
    logger.info("Exiting INCA module after sending the api response")
    return output


@exception_handler
def update_wholesale_details(**kwargs):
    """
    Calling INCA module to update service request(uni,interconnect,partner) status for
    various request type (e.g new,update,cease)
    Request:
          kwargs:
            requestType
            serviceType
            headers
            url
            body
    Response:
            Status/Exception
    """
    kwargs["usecase"] = "wholesale"
    kwargs["file_path"] = f"wholesale/{kwargs['serviceType']}/{kwargs['requestType']}"
    if (
        kwargs["serviceType"] == "interconnect"
        and kwargs["requestType"] == "new"
        and "remote-nni-lag" not in kwargs["body"]
        and len(kwargs["body"]["ports"]) > 1
    ):  # bugfix:wholesale-2358
        return connexion.problem(
            status=400,
            detail="Multiple interfaces are not allowed when remote-nni-lag is not given",
            title="Bad Request",
        )
    status, response = validate_json_request_payload(**kwargs)
    if not status:
        return response
    logger.info(
        f"Entering into INCA module to update {kwargs['serviceType']} service request for request type :"
        f"{kwargs['requestType']}"
    )
    token_url = base_url + "apex/incaREST/oauth/token"
    access_token = token_generator(url=token_url, username=username, password=password)
    kwargs["headers"] = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    function_mapper = {
        "uni": get_wholesale_uni_request_body,
        "interconnect": get_wholesale_interconnect_request_body,
        "partner": get_wholesale_partner_request_body,
    }
    kwargs["formatted_body"] = function_mapper[kwargs["serviceType"]](**kwargs)
    if inca_type["wholesale"]:
        inca_obj = IncaService()
        kwargs["url"] = inca_type["wholesale"][kwargs["serviceType"]][kwargs["requestType"]]
        output = inca_obj.update_wholesale_details(**kwargs)
        logger.info(
            "Exiting INCA module after sending the api response for {kwargs['serviceType']}:" f"{kwargs['requestType']}"
        )
        return output


def get_wholesale_uni_request_body(**kwargs):
    """
    This Method returns request body for serviceType(uni) for requestType(new,update,cease)
    Design-Link: https://wiki.at.sky/display/IA/INCA#INCA-ConnectorAPIDetails.2
    Request: Request body for service type uni and request types (new,update and cease)
            new,update:
                asset-id
                spark-change-ticket
                completion-date
                ani-engineer-name
            cease:
                asset-id
                spark-change-ticket
                completion-date
    Response: Response for service type uni and request types (new,update and cease)
             new,update:{
                            "assetRef" : "SKY-CL01-003",
                            "plugUpFields":[{
                                "plugUpSparkRef":"CHG1234567",
                                "plugUpCompleteDate":"01-jan-2019"
                            }],
                            "testFields":[{
                                "testingCHG":"CHG1234567",
                                "ANIEngineer":"joe.bloggs",
                                "testingResult":"PASS",
                                "failureReason":null,
                                "testingComments":"text",
                                "providerTestResult":"PASS",
                                "providerTestResultComments":"text"
                            }],
                            "configFields":[{
                                "configComplete":"01-jan-2019"
                            }]
             }
             Cease: {
                    "assetRef" : "SKY-CL01-003",
                    "sparkRef": "CHG0000001",
                    "completeDate": "01-jan-2019"
             }


    """
    item = kwargs["body"]
    if kwargs["requestType"] in ["update", "new"]:
        return {
            "assetRef": item.get("asset-id"),
            "plugUpFields": [
                {
                    "plugUpSparkRef": item.get("spark-change-ticket"),
                    "plugUpCompleteDate": item.get("completion-date"),
                }
            ],
            "testFields": [
                {
                    "testingCHG": item.get("spark-change-ticket"),
                    "ANIEngineer": item.get("ani-engineer-name"),
                    "testingResult": "PASS",
                    "failureReason": None,
                    "testingComments": None,
                    "providerTestResult": "PASS",
                    "providerTestResultComments": None,
                }
            ],
            "configFields": [{"configComplete": item.get("completion-date")}],
        }
    else:
        return {
            "assetRef": item.get("asset-id"),
            "sparkRef": item.get("spark-change-ticket"),
            "completeDate": item.get("completion-date"),
        }


def get_wholesale_partner_request_body(**kwargs):
    """
    Method format request body for wholesale partner serviceType(partner) and requestType(new,cease)
    Design-Link:https://wiki.at.sky/pages/viewpage.action?spaceKey=IA&title=INCA#INCA-INCAAPIDetails(APIsprovidedbyINCA)
    Request: Request body for service type partner and request types (new, and cease)
            new:{
                "partner-code": "OFNL",
                "partner-name": "OFNL Wholesale",
                "partner-parent-company-name": "IFNL",
                "wholesale-service-type":"activeStandby",
                "uni-service-type":"unTagged",
            }
            cease: {
                "partner-code": "OFNL",
                "partner-cease-date": "2022-08-07"
            }
    Response:  Request body for service type partnerand request types (new and cease)
        new:{
            "companyCode" : " Sky Business ",
            "companyName" : " Sky Business ",
            "parentCompanyName" : null,
            "vcidPrefix" : 9899,
            "activeActive" : "N",
            "activeActivePlus": null,
            "hybrid" : "N",
            "qualityOfService" : 0,
            "UNIService" : " Untagged",
            "uniqueNetworkCodeRangeStart" : 700000,
            "uniqueNetworkCodeRangeEnd" : 709999,
            "uniqueNetworkCodePosition" : 2
            "comment": "Example partner details based on Sky Business"
        }
        cease:{
            "companyCode" : " Sky Business ",
            "ceaseDate" : "31-dec-2022"
        }
    """
    item = kwargs["body"]
    logger.info(
        f"Formatting wholesale partner details for {kwargs['requestType']} in INCA Inventory for"
        f" partner {item.get('partner-code')} "
    )
    service_type_mapping = {
        "activeActive": {"nonResilient": "N", "activeStandby": "N", "2active": "Y", "4active": "Y"},
        "activeActivePlus": {"nonResilient": "N", "activeStandby": "N", "2active": "N", "4active": "Y"},
    }
    if kwargs["requestType"] == "cease":
        return {
            "companyCode": item["partner-code"],
            "ceaseDate": item["partner-cease-date"],
        }
    formatted_body = {
        "companyCode": item["partner-code"],
        "companyName": item["partner-name"],
        "vcidPrefix": 0,
        "activeActive": service_type_mapping["activeActive"][item["wholesale-service-type"]],
        "activeActivePlus": service_type_mapping["activeActivePlus"][item["wholesale-service-type"]],
        "hybrid": "N",
        "qualityOfService": 0,
        "UNIService": item["uni-service-type"].capitalize(),
        "uniqueNetworkCodeRangeStart": 0,
        "uniqueNetworkCodeRangeEnd": 0,
        "uniqueNetworkCodePosition": 0,
        "comment": item.get("comment", "Added partner details"),
    }
    if item.get("partner-parent-company-name"):
        formatted_body["parentCompanyName"] = item["partner-parent-company-name"]
    return formatted_body


def get_wholesale_interconnect_request_body(**kwargs):
    """
    Method format request body for wholesale serviceType(interconnect) and requestType(cease,new,update)
    DesignLink:https://wiki.at.sky/display/IA/INCA#INCA-INCAAPIDetails.3
    Request: Request body for service type interconnect and request types (new,update and cease)
            new,update :{
                "partner-code": "OFNL",
                "asset-id": "SKY-LNTW-FLDA-1",
                "nni-name": "London Bricklane", #Applicable only for requestType new
                "remote-nni-pe":"aro-wifi.bllon",
                "remote-nni-lag": "lag10",
                "rfs-date":"01-jan-2022",
                "ports": [{
                    "interface": "po1/1/1",
                    "bearer-rate": "10",
                    "circuit-id": "TIC-063340"
                }]
            }
            cease:{
                    "asset-id": "SKY-LNTW-FLDA-1",
                    "cease-date": "2022-08-06"
                }
    Response: Response body for service type interconnect and request types (new,update and cease)
             new,update :{
                "companyCode" : "Sky Business",  #Applicable only for requestType new
                "nniCode" : "SKY-LNTW-FLDA-1",
                "nniName" : "London Brick Lane",  #Applicable only for requestType new
                "remoteNNIPE": "ar0-wifi.bllon",
                "remoteNNILag": "lag 10",
                "rfsDate" : "01-JAN-2020",
                "comment" : "Added nni details",
                "ports": [{
                        "circuitId": "CircuitReference1",
                        "port": "po1/1/1",
                        "bearerRate": 10
                    }]
            }
            cease:
                {
                "nniCode" : "SKY-LNTW-FLDA-1",
                "ceaseDate" : “31-dec-2022”
                }
    """
    item = kwargs["body"]
    logger.info(
        f"INCA request payload for service type {kwargs['serviceType']}:{kwargs['requestType']} for "
        f"{item.get('asset-id')}"
    )

    if kwargs["requestType"] == "cease":
        return {
            "nniCode": item["asset-id"],
            "ceaseDate": item["cease-date"],
        }
    request_body = {
        "nniCode": item["asset-id"],
        "remoteNNIPE": item["remote-nni-pe"],
        "remoteNNILag": item.get("remote-nni-lag"),
        "rfsDate": item["rfs-date"],
        "ports": [],
        "comment": item.get("comment", "Added NNI details"),
    }
    for port in item["ports"]:
        port_details = {
            "port": port["interface"],
            "bearerRate": port["bearer-rate"],
            "circuitId": port["circuit-id"],
        }
        request_body["ports"].append(port_details)
    if kwargs["requestType"] == "new":
        request_body.update(companyCode=item.get("partner-code"), nniName=item["nni-name"])
    return request_body
