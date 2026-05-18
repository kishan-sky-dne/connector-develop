# Standard Library
import logging
import threading
import time
from datetime import datetime, timedelta
from json.decoder import JSONDecodeError
from random import shuffle
from urllib.parse import quote

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.services.itsm.exceptions import (
    InvalidRequest,
    InvalidStateRequest,
    ResourceServiceNotAvailable,
    SizeLimitExceeded,
)
from connectors.core.utils.exceptions import GenericConnectorsException, RestUtilityException
from connectors.core.utils.rest_api_utility import RestUtility

logger = logging.getLogger(__name__)

itsm_url = config.get(section="itsm", key="url")
itsm_keys = config.get(section="itsm", key="subscription_key").split(",")
change_request_projection = config.get(section="itsm", key="3800_change_request_projection")
incident_projection = config.get(section="itsm", key="3800_incident_projection")
sleep_interval = config.get(section="itsm", key="sleep_interval")

spark_state_mapping = {
    "Awaiting Approval": "-3",
    "Awaiting Authorisation": "-7",
    "Under Assessment": "-4",
    "Authorised": "-2",
    "Under Implementation": "-1",
}

add_checks_for_ticket = {
    "STD6588": [  # lag upgrade
        "Authorised",
        "Under Implementation",
        "Awaiting Approval",
        "Awaiting Authorisation",
        "Under Assessment",
    ],
    "STD4833": [  # slice/unslice
        "Authorised",
        "Under Implementation",
        "Awaiting Approval",
        "Awaiting Authorisation",
        "Under Assessment",
    ],
    "common": ["Authorised", "Under Implementation"],
}


class SparkTicketService:
    """
    Calling Spark Service Now to create, update, close and fetch ticket.

    :rtype: None
    """

    def __init__(self) -> None:
        """
        Initializes SparkTicketService class
        """
        logger.debug("Initializing Spark Service Now")
        self.rest = RestUtility(respect_retry_after=False)
        self.base_url = itsm_url
        self.append_url = "/request"
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        shuffle(itsm_keys)
        self.api_keys = iter(itsm_keys)
        self.headers["ocp-apim-subscription-key"] = next(self.api_keys)
        self.max_ci_list_length = int(config.get(section="itsm", key="max_ci_list_length"))

    def spark_request(self, method, url, **kwargs):
        """
        Helper method to wrap calls to Spark (via the REST utility) and
        automatically rotate keys.

        If all keys are rate-limited, the call will be re-attempted after sleeping
        for the period mentioned in the response Retry-After header.

        Args:
            method (str): HTTP verb in lowercase
            url (str): Full request URL

        Returns:
            Decoded JSON response from Spark

        Raises:
            RestUtilityException

        """
        while True:
            try:
                return getattr(self.rest, method)(url, headers=self.headers, **kwargs)
            except RestUtilityException as err:
                if err.response.status_code == 429:
                    try:
                        self.headers["Ocp-Apim-Subscription-Key"] = next(self.api_keys)
                    except StopIteration:
                        retry_after = int(err.response.headers.get("Retry-After", 15))
                        time.sleep(retry_after)
                        self.api_keys = iter(itsm_keys)
                        return getattr(self.rest, method)(url, headers=self.headers, **kwargs)
                    else:
                        continue
                else:
                    raise

    def service3405(self, **kwargs):
        """
        Calling Spark Service Now 3405 service to create a minor/routine change.

        Currently only minor change creation is supported.

        Args:
            cmdbci: List of active CIs
            createdBy: User creating the minor change
            start_date: start time in seconds since the Epoch
            end_date: end time in seconds since the Epoch
            assignment_group: Spark Groups for assignment
            chgType: minor or routine change
            parent_change: Parent Change
            short_description: Short description of the minor change
            description: Long description of the minor change

        Returns:
            {"result":{"details":"CTASK0015716 (MINOR CHANGE RAISED)"}​}

        Raises:
            ResourceServiceNotAvailable

        """
        logger.info("Entering into Service3405 capability")
        if kwargs.get("chgType") == "routine":
            raise ResourceServiceNotAvailable("Currently only creating minor change is supported via DNE")

        logger.debug(f"The kwargs for creating a minor ticket is {kwargs}")

        cmdb_ci = kwargs["cmdbci"]
        config_group = kwargs["config_group"]
        servicenum = "service3405"
        try:
            request = (
                f"cmdb_ci={config_group}&created_by="
                + kwargs["createdBy"]
                + "&start_date="
                + kwargs["start_date"]
                + "&end_date="
                + kwargs["end_date"]
                + "&assignment_group="
                + kwargs["assignment_group"]
                + "&parent_change="
                + kwargs["parent_change"]
                + "&short_description="
                + kwargs["short_description"]
                + "&description="
                + kwargs["description"]
            )

            logger.debug(f"The request sent to Spark Service Now for {servicenum} is: {request}")
        except KeyError as err:
            raise InvalidRequest(f"Mandatory keys missing while creating the minor change: {err.args[0]}") from err

        url = self.base_url + servicenum + self.append_url

        try:
            logger.info(f"Calling Spark Service Now API #{servicenum} : {url}")
            data = self.spark_request("post", url, data=request)
            result = data["result"]
            if any(key in result for key in ("error_details", "conflict_details")):
                logger.error(f"Response from Spark for {servicenum} :{result}")
            else:
                logger.debug(f"Response from Spark for {servicenum} :{result}")
            # now adding CIs to the ticket if there are more than one CIs
            logger.debug(f"CMDB CIs:{len(cmdb_ci)}")
            if all(key not in result for key in ("error_details", "conflict_details")) and len(cmdb_ci) > 0:
                ticket = result.get("details").split()[0]
                result_ci = self.service3040(
                    ticket=ticket,
                    ci_list=cmdb_ci,
                    impact_start=kwargs["start_date"],
                    impact_end=kwargs["end_date"],
                    operation="add",
                    operation_by=kwargs["createdBy"],
                )
                if not result_ci:
                    # todo add logic to close the minor ticket
                    raise ResourceServiceNotAvailable(
                        f"Ticket {ticket} raised but unable to add one or more CIs {cmdb_ci[1:]}"
                        f"to the ticket, the ticket will need to be manually closed"
                    )
            logger.info("Exiting into Service3405 capability")
            return data
        except (ValueError, TypeError, AttributeError) as err:
            raise GenericConnectorsException(f"Problem in accessing the ITSM Service 3405: {err.args[0]}") from err

    def service3400(self, ticket_number=None, return_fields=None):
        """
        Calling Spark Service Now 3400 service to retrieve a change.

        Args:
            ticket_number: ticketNumber

        Returns:
            [Change/Minor ticket JSONArray]

        Raises:
            Exception

        """
        logger.info("Entering into Service3400 capability")
        servicenum = "service3400"
        request = {"ticket_number": ticket_number}
        if return_fields:
            request["return_fields"] = return_fields
        url = self.base_url + servicenum + self.append_url
        try:
            logger.info(f"Calling Spark Service Now API #{servicenum} : {url}")
            data = self.spark_request("get", url, params=request)
            result = data
            if any(key in result for key in ("error_details", "conflict_details")):
                logger.error(f"Response from Spark for {servicenum} :{result}")
            else:
                logger.debug(f"Response from Spark for {servicenum} :{result}")
            logger.info("Exiting into Service3400 capability")
            return result
        except (ValueError, TypeError, AttributeError) as err:
            raise GenericConnectorsException(f"Problem in accessing the ITSM Service 3400: {err.args[0]}") from err

    def service3401(self, **kwargs):
        """
        Calling Spark Service Now 3401  service to Raise Change Ticket for "normal/standard" type

        Args:
            createdBy: User creating the Change Ticket
            template: Template to create Standard Ticket
            start_date: start time in seconds since the Epoch
            end_date: end time in seconds since the Epoch
            short_description: Short description of the change ticket
            implementation_plan: Mapping of previous change ticket number attribute to "Implementation Plan
            justification: Justification for change ticket

        Returns:
            response: JSON Schema with the ticket details

        Raises:
            InvalidRequest
            ResourceServiceNotAvailable

        """
        logger.info("Entering into Service3401 capability")
        servicenum = "service3401"
        try:
            data = (
                "template="  # noqa: E126
                + kwargs["templateName"]
                + "&created_by="
                + kwargs["createdBy"]
                + "&start_date="
                + kwargs["start_date"]
                + "&end_date="
                + kwargs["end_date"]
            )
            if kwargs["short_description"]:
                data += "&short_description=" + kwargs["short_description"]
            if kwargs["implementation_plan"]:
                data += "&implementation_plan=" + kwargs["implementation_plan"]
            if kwargs["justification"]:
                data += "&justification=" + kwargs["justification"]
            if kwargs.get("configuration_item"):
                data += "&cmdb_ci=" + kwargs["configuration_item"]
        except KeyError as err:
            raise InvalidRequest(f"Mandatory key or keys missing from the payload: {err.args[0]}") from err

        url = self.base_url + servicenum + self.append_url

        try:
            logger.info(f"Calling Spark Service Now API #{servicenum} : {url}")
            data = self.spark_request("post", url, data=data)
            result = data["result"]
            if any(key in result for key in ("error_details", "conflict_details")):
                logger.error(f"Response from Spark for {servicenum} :{result}")
            else:
                logger.debug(f"Response from Spark for {servicenum} :{result}")
            logger.info("Exiting from Service3401 capability")
            return data

        except (ValueError, TypeError, AttributeError) as err:
            raise GenericConnectorsException(f"Problem in accessing the ITSM Service 3401: {err.args[0]}") from err

        except KeyError as err:
            raise ResourceServiceNotAvailable(
                f"Error while getting response from Spark, missing `result` key in " f"payload: {err.args[0]}"
            ) from err

    def service3406(self, **kwargs):
        """
        Calling Spark Service Now 3406 service to update/close a change.

        Args:
            ticket_number: ticketNumber
            updated_by: user
            assigned_to: groups
            state: state to change
            work_notes: any remarks

        Returns:
            response: JSON Schema with the ticket details

        Raises:
            InvalidRequest
            ResourceServiceNotAvailable

        """
        logger.info("Entering into Service3406 capability")
        servicenum = "service3406"
        try:

            data = (
                "ticket_number="  # noqa: E126
                + kwargs["ticket_number"]
                + "&updated_by="
                + kwargs["updated_by"]
                + "&assigned_to="
                + kwargs["assigned_to"]
                + "&state="
                + kwargs["state"]
                + "&work_notes="
                + kwargs["work_notes"]
            )
        except KeyError as err:
            raise InvalidRequest(f"Mandatory key or keys missing from the payload: {err.args[0]}") from err

        url = self.base_url + servicenum + self.append_url

        try:
            logger.info(f"Calling Spark Service Now API #{servicenum} : {url}")
            data = self.spark_request("post", url, data=data)
            result = data
            if any(key in result for key in ("error_details", "conflict_details")):
                logger.error(f"Response from Spark for {servicenum} :{result}")
            else:
                logger.debug(f"Response from Spark for {servicenum} :{result}")
            logger.info("Exiting into Service3406 capability")
            return result
        except (ValueError, TypeError, AttributeError) as err:
            raise GenericConnectorsException(f"Problem in accessing the ITSM Service 3406: {err.args[0]}") from err

    def service3040(self, ticket, ci_list, operation, impact_start, impact_end, operation_by):
        """
        Calling Spark Service Now 3040 service to add, update or remove a CI from the change.

        Args:
            ticket: Change ticket for which the CI needs to be added/removed/updated
            ci_list: list of CIs to be added/removed/updated
            operation: add or update or remove
            impact_start: Impact start time for the CI
            impact_end: Impact end time for the CI
            operation_by: user-id

        Returns:
            True/False

        Raises:
            ResourceServiceNotAvailable
        """
        logger.info("Entering into Service3040 capability")
        servicenum = "service3040"
        url = self.base_url + servicenum + self.append_url

        main_status = []

        def add_infra_ci(ticket, ci, operation, impact_start, impact_end, operation_by):
            nonlocal main_status
            try:
                request = (
                    "ticket_number="  # noqa: E126
                    + ticket
                    + "&ci_name="
                    + ci["ciName"]
                    + "&impact_type="
                    + ci["impactType"]
                    + "&impact_start="
                    + impact_start
                    + "&impact_end="
                    + impact_end
                    + "&operation="
                    + operation
                    + "&operation_by="
                    + operation_by
                )
                logger.info(
                    f"Calling Spark Service Now API #{servicenum} {url} for CHG {ticket} "
                    f"to {operation} {ci['ciName']}"
                )
                data = self.spark_request("post", url, data=request)
                result = data
                if any(key in result for key in ("error_details", "conflict_details")):  # Fix for DNE-7606
                    logger.error(f"Response from Spark for {servicenum} : {ci['ciName']} : {result}")
                else:
                    logger.debug(f"Response from Spark for {servicenum} : {ci['ciName']} : {result}")
                logger.info("Exiting into Service3040 capability")

                main_status.append(True)
            except (ValueError, TypeError, AttributeError):
                main_status.append(False)

        thread_list = []
        for ci in ci_list:
            # To ensure spark does not get overloaded
            time.sleep(1.25)
            add_ci_thread = threading.Thread(
                target=add_infra_ci,
                args=(
                    ticket,
                    ci,
                    operation,
                    impact_start,
                    impact_end,
                    operation_by,
                ),
            )
            add_ci_thread.daemon = False
            add_ci_thread.start()
            thread_list.append(add_ci_thread)

            # wait till all thread are complete
        while True:
            threads_complete = []
            for thread in thread_list:
                if thread.is_alive() and threads_complete.__len__() != thread_list.__len__():
                    continue
                else:
                    # This is to break the while loop
                    threads_complete.append(True)
            if threads_complete.__len__() == thread_list.__len__():
                break

        return False not in main_status

    def _get_incident_details(self, **kwargs):
        """
        This is to return ci_list, query, return_fields for db_table incident
        """
        ci_filter = "u_affected_ci_list" if kwargs.get("ci_filter") else None
        query = "state=2^impact=1^ORimpact=2^ORimpact=3"
        return ci_filter, query, incident_projection

    def _get_task_ci_details(self, **kwargs) -> tuple[str, str, str]:
        """
        This is to return ci_list, query, return_fields for db_table task_ci
        Returns:
            tuple[str, str, str]: ci_list, query, return_fields
        """
        logger.info("Inside _get_task_ci_details")

        short_description: bool = kwargs.get("short_description", False)
        short_description_value = kwargs.get("short_description_value", "")
        ci_filter: str = "ci_item" if kwargs.get("ci_filter") else kwargs.get("ci_filter")
        start_date: list = kwargs.get("start_date")
        end_date: list = kwargs.get("end_date")
        query: str = "task.numberSTARTSWITHCHG^task.active=true"
        current_ticket_id = next(
            (ticket_id for ticket_id in add_checks_for_ticket if ticket_id in short_description_value),
            "common",
        )
        for index, state in enumerate(add_checks_for_ticket.get(current_ticket_id, add_checks_for_ticket["common"])):
            if index == 0:
                query += f"^task.state={spark_state_mapping[state]}"
            else:
                query += f"^ORtask.state={spark_state_mapping[state]}"

        query += (
            f"^task.ref_change_request.start_dateBETWEEN"
            f"javascript:gs.dateGenerate('{start_date[0]}','{start_date[1]}')"
            f"@javascript:gs.dateGenerate('{end_date[0]}','{end_date[1]}')^OR"
            f"task.ref_change_request.end_dateBETWEEN"
            f"javascript:gs.dateGenerate('{start_date[0]}','{start_date[1]}')"
            f"@javascript:gs.dateGenerate('{end_date[0]}','{end_date[1]}')"
        )
        if ci_filter is not None:
            for index, sys_id in enumerate(kwargs["sys_id_list"]):
                if index == 0:
                    query = f"{query}^{ci_filter}LIKE{sys_id}"
                else:
                    query += f"^OR{ci_filter}LIKE{sys_id}"
        else:
            query = f"{query}"
        query += (
            "^NQtask.numberSTARTSWITHCHG^task.active=true^task.state=-2^ORtask.state=-1"
            "^task.ref_change_request.start_date<"
            f"javascript:gs.dateGenerate('{start_date[0]}','{start_date[1]}')"
            "^task.ref_change_request.end_date>"
            f"javascript:gs.dateGenerate('{end_date[0]}','{end_date[1]}')"
        )
        return_fields = (
            f"{change_request_projection},task.short_description" if short_description else change_request_projection
        )
        return ci_filter, query, return_fields

    def _get_u_cmdb_ci_circuit_details(self, **kwargs):
        """
        This is to return ci_list, query, return_fields for db_table u_cmdb_ci_circuit
        """
        affected_cis = kwargs.get("affected_cis")
        query_ci = "%5EORnameSTARTSWITH".join(f"{ci}" for ci in affected_cis)
        query_str = f"u_active%3Dtrue%5EnameSTARTSWITH{query_ci}"  # Fix for Wholesale CIDs (IFNL, IFNL20)
        return None, query_str, "u_customer,name"

    def _format_result(self, db_table, result):
        """
        This is to format result for table u_cmdb_ci_circuit
        """
        logger.info("Inside _format_result")
        if db_table != "u_cmdb_ci_circuit":
            return result
        result_object = [
            {
                "circuitID": customer["name"],
                "u_customer": {"displayValue": customer["u_customer"]["display_value"]},
            }
            for customer in result
        ]
        return {"result": result_object}

    def _format_dates_in_kwargs(self, **kwargs):
        """
        This method is to format date fields passed in the kwargs
        """
        logger.info("Inside _format_dates_in_kwargs")
        start_date_in_epoch = kwargs.get("start_date")
        end_date_in_epoch = kwargs.get("end_date")
        if start_date_in_epoch:
            start_date = datetime.fromtimestamp(start_date_in_epoch)
            start_date = (start_date.strftime("%Y-%m-%d"), start_date.strftime("%H:%M:%S"))
        else:
            start_date = (datetime.strftime(datetime.now(), "%Y-%m-%d"), "00:00:00")

        if end_date_in_epoch:
            end_date = datetime.fromtimestamp(end_date_in_epoch)
            end_date = (end_date.strftime("%Y-%m-%d"), end_date.strftime("%H:%M:%S"))
        else:
            end_date = (datetime.strftime(datetime.now() + timedelta(days=3), "%Y-%m-%d"), "23:59:59")
        kwargs["start_date"] = start_date
        kwargs["end_date"] = end_date
        return kwargs

    def service3800(self, **kwargs) -> list:
        # sourcery skip: low-code-quality
        """
        Calling 3800 service from Spark Service Now to find any major incident/changes against listed cis.
        note: spark query has limitation to return 500 records
        kwargs:
            query(string): queryto spark
            db_table(string): name of the spark db to be queried
            ci_list: list of CIs against which major incident/changes need to be find out
        Returns:
            results(list): list of spark records
        """
        logger.info("Entering into Service3800 capability")
        servicenum = "service3800"
        url = self.base_url + servicenum + self.append_url
        db_table = kwargs.get("db_table")
        affected_cis = kwargs.get("affected_cis")
        ticket_number = kwargs.get("ticket_number")
        kwargs = self._format_dates_in_kwargs(**kwargs)

        result = []

        try:
            logger.info(f"Calling Spark Service Now API #{servicenum} : {url}")
            sys_id_list = self.get_sys_id(affected_cis, url, get_single_id=True)
            # syncing code with stage BUGFIX DNE-26715
            affected_ci_mapper = {"u_cmdb_ci_circuit": [], "task_ci": affected_cis, "incident": sys_id_list}
            logger.debug(f"affected_ci_mapper: {affected_ci_mapper}")
            if db_table == "incident" and sys_id_list:
                ci_filter, query, return_fields = self._get_incident_details(**kwargs)
            elif db_table == "u_cmdb_ci_circuit" and affected_cis:
                ci_filter, query, return_fields = self._get_u_cmdb_ci_circuit_details(**kwargs)
            elif db_table == "u_cmdb_ci_circuit":
                result = {"result": []}
            elif db_table == "task_ci" and ticket_number:
                return self.fetch_ci_relationship(url, db_table, ticket_number, sys_id_list, affected_ci_mapper)
            elif db_table == "cmdb_rel_ci" and kwargs.get("ci_filter") in {
                "ci_dependency_map_child",
                "ci_dependency_map_parent",
            }:
                return self.fetch_ci_dependency(
                    url, db_table, hostname=kwargs.get("hostname"), ci_filter=kwargs.get("ci_filter")
                )
            elif db_table == "task_ci" and sys_id_list:
                kwargs["sys_id_list"] = affected_ci_mapper.get(db_table, [])
                ci_filter, query, return_fields = self._get_task_ci_details(**kwargs)
            elif db_table in ["task_ci", "incident"] and not sys_id_list:  # BugFix DNE-32860
                return []
            else:
                raise InvalidRequest(f"The given {db_table} is currently not supported")
            if not result:
                if len(affected_ci_mapper.get(db_table, [])) > self.max_ci_list_length:
                    logger.info(
                        "Running concurrent threads to call SPARK "
                        f"as the maximum CI list length '{self.max_ci_list_length}' is exceeded. "
                        f"Total CI list length is '{len(affected_ci_mapper.get(db_table, []))}'"
                    )
                    query_result = self._execute_sub_queries_in_parallel(
                        url=url,
                        db_table=db_table,
                        sys_id_list=affected_ci_mapper.get(db_table, []),
                        query=query,
                        ci_filter=ci_filter,
                        return_fields=return_fields,
                    )
                else:
                    query_result = self.execute_query(
                        url=url,
                        db_table=db_table,
                        sys_id_list=affected_ci_mapper.get(db_table, []),
                        query=query,
                        ci_filter=ci_filter,
                        return_fields=return_fields,
                    )
                result = self._format_result(db_table, query_result)
                logger.debug(f"query_result:{query_result}, result:{result}")
            logger.info("Exiting into Service3800 capability")
            return result
        except (ValueError, TypeError, AttributeError) as err:
            logger.info(f"Exception raised: {err.args[0]}")
            return False

    def _execute_sub_queries_in_parallel(
        self, url: str, db_table: str, sys_id_list: list, query: str, ci_filter: str, return_fields: str
    ) -> list:
        """
        Function to create multiple threads, each calling the 'thread_worker' function
        with different arguments.
        Returns the results when all threads are completed.
        """
        thread_list = []
        results = []
        lock = threading.Lock()

        broken_down_list = self._break_down_list(list(set(sys_id_list)))
        logger.debug(
            f"Running concurrent threads to call SPARK for each sub list. Broken down CI list: {broken_down_list}"
        )
        for index, sub_sys_id_list in enumerate(broken_down_list):
            args = (url, db_table, sub_sys_id_list, query, ci_filter, return_fields)
            thread = threading.Thread(target=self._thread_worker, args=(args, results, lock))
            thread.start()
            thread_list.append(thread)
            # To ensure spark does not get overloaded except for the last one
            if index < len(broken_down_list) - 1:
                time.sleep(1.25)

        for thread in thread_list:
            thread.join()
        return results

    def _break_down_list(self, input_list: list) -> list:
        """
        Breaks down the given list into a list of lists
        each of which has a maximum of 'self.max_ci_list_length' elements
        """
        return [input_list[i : i + self.max_ci_list_length] for i in range(0, len(input_list), self.max_ci_list_length)]

    def _thread_worker(self, args: tuple, results: list, lock: threading.Lock) -> None:
        """
        Worker function for running 'execute_query' in a separate thread
        and accumulating results
        """
        result = self.execute_query(*args)
        with lock:
            logger.debug("Acquired threading lock to extend results")
            results.extend(result)

    def get_sys_id(self, affected_cis: list[str], url: str, get_single_id: bool = False) -> list[str]:
        """
        Get the sys id for given ci.

        Args:
            affected_cis: list of CI against which any major incident ticket need to be fetched
            url: spark url
            get_single_id: Flag to return first found single sys_id for the given CIs, default is False

        Returns:
            sys_id: Single or List of sys_ids from itsm DB table
        """
        sys_id_list = []

        if affected_cis:
            for ci in affected_cis:
                request = (
                    "db_table="  # noqa: E126
                    + "cmdb_ci"
                    + "&query_filter="
                    + quote(f"active=true^name={ci}")
                    + "&return_fields="
                    + "sys_id,name,operational_status"
                )
                results = self.spark_request("get", url, params=request)
                result = results.get("result")
                if result and "error_details" not in result:
                    logger.debug(f"sys_id against ci {ci} is {result[0]['sys_id']}")
                    logger.info(f"Sys_id list for ci {ci} is {result[0]['sys_id']}")
                    if get_single_id:
                        return [result[0]["sys_id"]]
                    else:
                        sys_id_list.append(result[0]["sys_id"])
        return sys_id_list

    def fetch_ci_dependency(self, url: str, db_table: str, hostname: str, ci_filter: str) -> list:
        """
        This method will fetch all the associated CIs dependency with the ci_filte
        Args:
            url(string): spark url
            db_table(string): name of the spark db to be queried

        Returns:
            list[dict]: list of spark records
        """
        node = "child" if ci_filter == "ci_dependency_map_child" else "parent"
        request = f"db_table={db_table}&query_filter={node}.name%3D{hostname}"
        results = self.spark_request("get", url, params=request)
        result = results.get("result")
        logger.debug(f"request in fetch ci dependency {request} and result {result}")
        return result if result and "error_details" not in result else []

    def fetch_ci_relationship(
        self,
        url: str,
        db_table: str,
        ticket_number: str,
        sys_id_list: list[str] = None,
        affected_ci_mapper: dict[str, str] = None,
    ) -> list:
        """
        This method will fetch all the associated CIs associated with the ticket
        Args:
            url(string): spark url
            db_table(string): name of the spark db to be queried
            ticket_numer(string): change ticket
            sys_id_list(list): list of sys id's for affected ci's
            affected_ci_mapper(dict): maps sys_id to affected hostnames
        Returns:
            list[dict]: list of spark records

        """
        request = f"db_table={db_table}&query_filter=task.number%3D{ticket_number}"
        if sys_id_list:
            sys_id_name_list = affected_ci_mapper.get(db_table, [])
            for index, sys_id in enumerate(sys_id_name_list):
                if index == 0:
                    request = f"{request}^ci_itemLIKE{sys_id}"
                else:
                    request += f"^ORci_itemLIKE{sys_id}"
        results = self.spark_request("get", url, params=request)
        result = results.get("result")
        logger.debug(f"request in fetch ci {request} and result {result}")
        return result if result and "error_details" not in result else []

    def execute_query(self, url, db_table, sys_id_list, query, ci_filter, return_fields, **kwargs):
        """
        This method will prepare query filter for 3800 against all sys_ids in sys_id_list

        Returns:
            list : list of incidents/changes found
        """
        query_string = ""
        if ci_filter is not None:
            for index, sys_id in enumerate(sys_id_list):

                if index == 0:
                    query_string = f"{query}^{ci_filter}LIKE{sys_id}"
                else:
                    query_string += f"^OR{ci_filter}LIKE{sys_id}"
        else:
            query_string = f"{query}"

        logger.info(f"Query filter to be sent to 3800: {query_string}")
        request = (
            "db_table="  # noqa: E126
            + f"{db_table}"
            + "&query_filter="
            + quote(query_string).replace("%27", "'").replace("%28", "(").replace("%29", ")").replace("%25", "%")
            + "&return_fields="
            + f"{return_fields}"
        )
        results = self.spark_request("get", url, params=request)
        result = results.get("result")
        return result if result and "error_details" not in result else []

    def service3020(self, start_date, end_date):
        """
        Calling Spark Service Now 3020 service to retrieve change restrictions.

        Args:
            end_date: end date in epoch
            start_date: start date in epoch

        Returns:
            [Change Restrictions JSONArray]

        Raises:
            Exception

        """
        logger.info("Entering into Service3020 capability")
        servicenum = "service3020"

        if start_date is None or end_date is None:
            raise InvalidRequest("Mandatory parameter `start_date` & `end_date` missing from the request")

        request = {"start_date": start_date, "end_date": end_date}
        url = self.base_url + servicenum + self.append_url
        try:
            logger.info(f"Calling Spark Service Now API #{servicenum} : {url}")
            data = self.spark_request("get", url, params=request)
            result = data.get("result")
            logger.debug(f"Response from Spark for {servicenum} :{result}")
            if "error_details" in result:
                logger.error(f"Response from Spark for {servicenum} :{result}")
                result = []
            elif "details" in result:
                logger.info(f"Response from Spark for {servicenum} :{result}")
                result = []
            logger.info("Exiting into Service3020 capability")
            return result
        except (ValueError, TypeError, AttributeError) as err:
            raise GenericConnectorsException(f"Problem in accessing the ITSM Service 3020: {err.args[0]}") from err

    def service3045(self, **kwargs):
        """
        Calling Spark Service Now 3045 service to add/remove attachments.

        Args:
            ticket_number: Ticket Number for which the attachment needs to be added/removed
            filename: File name of the attachment
            attachment: base64 encoding of the file content
            operation_by: active spark user id
            operation: add/list/remove

        Returns:
            {"result":{"details":"CTASK0042685 (ATTACHMENT ADDED)"}​}

        Raises:
            ResourceServiceNotAvailable

        """
        logger.info("Entering into Service3045 capability")
        servicenum = "service3045"
        logger.debug(f"The kwargs for add/remove/list attachment to ticket is {kwargs}")

        try:
            if kwargs["operation"] == "list":
                request = {"ticket_number": kwargs["ticket_number"]}
            elif kwargs["operation"] == "add":
                request = (
                    "ticket_number="  # noqa: E126
                    + kwargs["ticket_number"]
                    + "&filename="
                    + kwargs["filename"]
                    + "&attachment="
                    + kwargs["attachment"]
                    + "&operation_by="
                    + kwargs["operation_by"]
                    + "&operation="
                    + kwargs["operation"]
                )
            else:
                request = (
                    "ticket_number="  # noqa: E126
                    + kwargs["ticket_number"]
                    + "&filename="
                    + kwargs["filename"]
                    + "&operation="
                    + kwargs["operation"]
                    + "&operation_by="
                    + kwargs["operation_by"]
                )
            logger.debug(f"The request sent to Spark Service Now for {servicenum} is: {request}")
        except KeyError as err:
            raise InvalidRequest(
                f"Mandatory keys missing while add/remove/list attachment to the ticket: " f"{err.args[0]}"
            ) from err

        url = self.base_url + servicenum + self.append_url

        try:
            logger.info(f"Calling Spark Service Now API #{servicenum} : {url}")
            data = self.spark_request("post", url, data=request)
            result = data["result"]
            if any(key in result for key in ("error_details", "conflict_details")):  # Fix for DNE-7606
                logger.error(f"Response from Spark for {servicenum} :{result}")
            else:
                logger.debug(f"Response from Spark for {servicenum} :{result}")
            logger.info("Exiting from Service3045 capability")
            return data

        except JSONDecodeError as err:
            raise SizeLimitExceeded(f"attachment size is too long: {err.args[0]}") from err
        except (ValueError, TypeError, AttributeError) as err:
            raise GenericConnectorsException(f"Problem in accessing the ITSM Service 3045: {err.args[0]}") from err

        except KeyError as err:
            raise ResourceServiceNotAvailable(
                f"Error while getting response from Spark, missing `result` key in " f"payload: {err.args[0]}"
            ) from err

    def service3050(self, **kwargs):
        """
        Calling Spark Service Now 3050 service to add worknotes

        Args:
            ticket_number: Ticket Number for which Worknotes need to be added
            updated_by: active spark user id
            work_notes = Free text up to 4,000 character
        Optional POST Name-Value Pairs:
            comments=[Free text up to 4000 characters (URL encoded)]

        Returns:
            "result": {"details": "CHG0035945 (UPDATED)"

        Raises:
            ResourceServiceNotAvailable

        """
        logger.info("Entering into Service3050 capability")
        servicenum = "service3050"
        logger.debug(f"The kwargs for adding Worknotes to ticket is {kwargs}")

        try:
            request = (
                "ticket_number="  # noqa: E126
                + kwargs["ticket_number"]
                + "&updated_by="
                + kwargs["updated_by"]
                + "&work_notes="
                + kwargs["work_notes"]
            )
            if kwargs.get("comments"):
                request += "&comments=" + kwargs["comments"]
            logger.debug(f"The request sent to Spark Service Now for {servicenum} is: {request}")
        except KeyError as err:
            raise InvalidRequest(
                f"Mandatory keys missing while adding Worknote to the ticket: " f"{err.args[0]}"
            ) from err

        url = self.base_url + servicenum + self.append_url

        try:
            logger.info(f"Calling Spark Service Now API #{servicenum} : {url}")
            data = self.spark_request("post", url, data=request)
            result = data["result"]
            if any(key in result for key in ("error_details", "conflict_details")):  # Fix for DNE-7606
                logger.error(f"Response from Spark for {servicenum} :{result}")
            else:
                logger.debug(f"Response from Spark for {servicenum} :{result}")
            logger.info("Exiting from Service3050 capability")
            return data
        except (ValueError, TypeError, AttributeError) as err:
            raise GenericConnectorsException(f"Problem in accessing the ITSM Service 3050: {err.args[0]}") from err

        except KeyError as err:
            raise ResourceServiceNotAvailable(
                f"Error while getting response from Spark, missing `result` key in " f"payload: {err.args[0]}"
            ) from err

    def service3402(self, **kwargs: dict) -> any:  # noqa: C901
        """
        Calling Spark Service Now 3402 service to Update/Complete Change Ticket.

        Args:
            ticket_number= ticket Number
            updated_by: user detail trying to Update/Complete Change Ticket
            state = [Authorised | Under Implementation | Post Implementation Review]
            assignment_group=[Network Service Operations (NOC- Tier 1) (URL encoded)]
            assigned_to=Spark user_id. Member of Assignment group
            changeType = Update/Complete Change Ticket type
            If  State is set to 'Post Implementation Review':
               implementation_code = [Successful | Successful with issues | Unsuccessful]
               implementation_detail = Implementation detail for Update/Complete Change Ticket
               start_date: start time in seconds since the Epoch
               end_date: end time in seconds since the Epoch
               If implementation_code is Unsuccessful:
                    unsuccessful_reason = Reason to explain Update/Complete Change Ticket,only when unsuccessful
                    cause_of_failure =  Reason for failure
                    backed_out = check if the Change was backed out
                    corrected_plan = Explanation of Correction plan
        Returns:
            Response(successful):
               {"result": {"details": "CHG0049672 (UPDATED)"}}

            Response(not successful):
               {"result":{"error_details":"CHG0049672 state is 'Awaiting Approval'"}?}

        Raises:
            ResourceServiceNotAvailable
        """
        logger.info("Entering into Service3402 Raise to Update/Complete Change Ticket")
        servicenum = "service3402"
        logger.info(f"The kwargs for raising a change ticket are {kwargs}")
        try:
            request = "ticket_number=" + kwargs["ticket_number"] + "&updated_by=" + kwargs["updated_by"]  # noqa: E126
            if kwargs.get("assignment_group"):
                request += "&assignment_group=" + kwargs["assignment_group"]
            if kwargs.get("assigned_to"):
                request += "&assigned_to=" + kwargs["assigned_to"]
            if kwargs.get("state"):
                request += "&state=" + quote(kwargs["state"])
            if kwargs.get("state") == "Post Implementation Review":
                request += (
                    "&implementation_code="  # noqa: E126
                    + kwargs["implementation_code"]
                    + "&implementation_detail= "
                    + kwargs["implementation_detail"]
                    + "&start_date="
                    + str(kwargs["start_date"])
                    + "&end_date="
                    + str(kwargs["end_date"])
                )
                if kwargs["implementation_code"] == "Unsuccessful":
                    request += (
                        "&unsuccessful_reason="  # noqa: E126
                        + kwargs["unsuccessful_reason"]
                        + "&cause_of_failure="
                        + kwargs["cause_of_failure"]
                        + "&backed_out="
                        + kwargs["backed_out"]
                        + "&corrected_plan="
                        + kwargs["corrected_plan"]
                    )
            if kwargs.get("work_notes"):
                request += "&work_notes=" + quote(kwargs["work_notes"])
            if kwargs.get("reschedule"):
                request += (
                    "&reschedule="  # noqa: E126
                    + str(kwargs["reschedule"])
                    + "&reschedule_reason="
                    + kwargs["reschedule_reason"]
                    + "&new_start_date="
                    + str(kwargs["new_start_date"])
                    + "&new_end_date="
                    + str(kwargs["new_end_date"])
                )
            logger.info(f"The request sent to Spark Service Now for {servicenum} is: {request}")
        except KeyError as err:
            raise InvalidRequest(f"Mandatory keys missing while creating the minor change: {err.args[0]}") from err

        url = self.base_url + servicenum + self.append_url

        try:
            logger.info(f"Calling Spark Service Now API #{servicenum} : {url}")
            data = self.spark_request("post", url, data=request)
            result = data["result"]
            if any(key in result for key in ("error_details", "conflict_details")):  # Fix for DNE-7606
                logger.error(f"Response from Spark for {servicenum} :{result}")
            else:
                logger.debug(f"Response from Spark for {servicenum} :{result}")
            logger.info("Exiting from Service3402 capability")
            return data
        except JSONDecodeError as err:
            raise InvalidStateRequest(
                f"Invalid Request as Ticket update goes from "
                f"Authorised to Under Implementation and then to "
                f"Post Implementation Review: {err.args[0]}"
            ) from err

        except (ValueError, TypeError, AttributeError) as err:
            raise GenericConnectorsException(f"Problem in accessing the ITSM Service 3402: {err.args[0]}") from err

        except KeyError as err:
            raise ResourceServiceNotAvailable(
                f"Error while getting response from Spark, missing `result` key in " f"payload: {err.args[0]}"
            ) from err

    def service3030(self, **kwargs):
        """
        Calling Spark Service Now 3030  service to create Ticket for "thirdParty" type

        kwargs:
            ticket_type: type of Ticket to be created
            ticket_number: parent ticket number under which third party Ticket to be created
            third_party: customer name
            impact: impact on creating/not creating ticket
            reason: Short description of the ticket creation

        Returns:
            response: JSON Schema with the ticket details

        Raises:
            InvalidRequest
            GenericConnectorsException
            ResourceServiceNotAvailable

        """
        logger.info("Entering into Service3030 capability")
        servicenum = "service3030"
        try:
            data = (
                "ticket_type="  # noqa: E126
                + kwargs["ticket_type"]
                + "&ticket_number="
                + kwargs["ticket_number"]
                + "&third_party="
                + kwargs["third_party"]
                + "&impact="
                + kwargs["impact"]
                + "&reason="
                + kwargs["reason"]
            )
        except KeyError as err:
            raise InvalidRequest(f"Mandatory key or keys missing from the payload: {err.args[0]}") from err

        url = self.base_url + servicenum + self.append_url

        try:
            logger.info(f"Calling Spark Service Now API #{servicenum} : {url}")
            logger.debug(f"Calling with data {data}")
            spark_response = self.spark_request("post", url, data=data)
            result = spark_response["result"]
            if any(key in result for key in ("error_details", "conflict_details")):  # Fix for DNE-7606
                logger.error(f"Response from Spark for {servicenum} :{result}")
            else:
                logger.debug(f"Response from Spark for {servicenum} :{result}")
            logger.info("Exiting from Service3030 capability")
            return spark_response

        except (ValueError, TypeError, AttributeError) as err:
            raise GenericConnectorsException(f"Problem in accessing the ITSM Service 3030: {err.args[0]}") from err

        except KeyError as err:
            raise ResourceServiceNotAvailable(
                f"Error while getting response from Spark, missing `result` key in " f"payload: {err.args[0]}"
            ) from err
