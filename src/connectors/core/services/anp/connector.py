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

# Third Party Library
import requests

# DNE Library
from connectors.core.config.connectors_config import config
from connectors.core.services.anp.exceptions import DataUnavailable, InvalidRequest
from connectors.core.utils.exceptions import RestUtilityException
from connectors.core.utils.rest_api_utility import RestUtility

logger = logging.getLogger(__name__)

anp_prod_url = config.get(section="anp", key="prod_url")
anp_uat_url = config.get(section="anp", key="uat_url")
anp_environment = config.get(section="anp", key="environment")


class CommonOperations:
    # -- Public Functions
    def _print_str(self, data, exception=False):
        if exception:
            logger.error(data)
        else:
            logger.debug(data)

    def get(self, session, url, params=None, data=None):
        response = session.get(url, params=params, data=json.dumps(data))
        data = response.json()
        return data

    def post(self, session, url, params=None, data=None):
        response = session.post(url, params=params, data=json.dumps(data))
        data = response.json()
        return data

    def put(self, session, url, params=None, data=None):
        response = session.put(url, params=params, data=json.dumps(data))
        data = response.json()
        return data

    def login(self, url, username, password):
        sso_url = url + "/sso"
        payload = {"username": username, "password": password}
        response = requests.post(sso_url, headers={"content-type": "application/json"}, data=json.dumps(payload))
        data = response.json()
        self._print_str("Logging into {0}\n\n{1}".format(url, json.dumps(data, indent=4)))
        return data["token"]


class UpdateTGService(CommonOperations):
    def __init__(self, request_body, username, password):
        """
        updates TG reference
        Args:
            request_body:
                            {
                              "comment": "changing delivery date",
                              "deliveryDate": "2022-07-20",
                              "domain": "metro,cdn,core,enterprise",
                              "environment": "qa/production",
                              "projectName": "Bluebird OLT",
                              "requiredDate": "2021-07-20",
                              "status": "allowed values are, cancelled,delivered,completed,ok,new,risk",
                              "tgReference": "TG9989"
                            }

            username: restricted application account login name (starts with SVC-APP-xxx)
            password: restricted application account login password
        """

        logger.info("Initializing anp Service")
        self.environment = request_body["environment"]
        self.domain = request_body["domain"]
        self.projectName = request_body["projectName"]
        self.requiredDate = request_body["requiredDate"]
        self.deliveryDate = request_body["deliveryDate"]
        self.status = request_body["status"]
        self.comment = request_body["comment"]
        self.tgReference = request_body["tgReference"]
        self.username = username
        self.password = password
        if "production" in self.environment.lower():
            self.url = anp_prod_url
        else:
            self.url = anp_uat_url

    def update_tg(self):  # noqa: C901
        """
        main function
        :return: responseobject{}
        """

        url = self.url
        responseobject = {}

        # login
        try:
            token = self.login(url, self.username, self.password)
        except:  # noqa: E722
            responseobject["success"] = False
            responseobject["message"] = "Login to A&P failed"
            return responseobject

        # ========================================================
        # set up the http session along with appropriate headers
        # ========================================================
        session = requests.Session()
        session.headers.update({"accept": "application/hal+json"})
        session.headers.update({"content-type": "application/json"})
        session.headers.update({"Authorization": "Bearer {0}".format(token)})

        # ========================================================
        # Get the URLs for the project of interest
        # ========================================================

        project_data = {}
        try:
            project_data = self.get_project_data(session, url, self.domain, self.projectName)
        except:  # noqa: E722
            responseobject["success"] = False
            responseobject["message"] = (
                "Could not get project data for domain '{0}' and project '{1}' "
                "Make sure the credentials you used have checkout permissions in A&P portal".format(
                    self.domain, self.projectName
                )
            )
            return responseobject

        if not project_data:
            self._print_str(
                "Project '{0}' doesn't seem to exist in domain '{1}'".format(self.projectName, self.domain),
                exception=True,
            )
            responseobject["success"] = False
            responseobject["message"] = "Project {0} doesn't seem to exist in domain {1}".format(
                self.projectName, self.domain
            )
            return responseobject

        deliverables_url = project_data["_links"]["deliverables"]["href"]
        try:
            deliverable_data = self.update_deliverable(session, deliverables_url, self.tgReference)
        except:  # noqa: E722
            self._print_str(
                "Failed to update {0}  in project {1}".format(self.tgReference, self.projectName), exception=True
            )
            responseobject["success"] = False
            responseobject["message"] = "Failed to update {0} in project {1}".format(self.tgReference, self.projectName)
            return responseobject

        if deliverable_data:
            self._print_str(json.dumps(deliverable_data, indent=4))

        # check the project back in
        try:
            project_checkin = self.post(session, project_data["_links"]["actions"]["checkin"]["href"])
            self._print_str(json.dumps(project_checkin, indent=4))
            if "error" in project_checkin:
                responseobject["success"] = False
                responseobject[
                    "message"
                ] = "Failed to check in '{0}' to project '{1}' in A&P after update,  " "contact A&P admin".format(
                    self.tgReference, self.projectName
                )
                return responseobject

        except:  # noqa: E722
            responseobject["success"] = False
            responseobject[
                "message"
            ] = "Failed to check in '{0}' to project '{1}' in A&P after update,  " "contact A&P admin".format(
                self.tgReference, self.projectName
            )
            return responseobject

        responseobject["message"] = "OK"
        responseobject["success"] = True
        return responseobject

    def get_project_data(self, session, url, domain, project_name):
        """
        Query the project and obtain the project data to gain entry into the deliverables
        """

        # Get the Upgrade Tracker Data
        ut_url = url + "/ut"
        ut_url_data = self.get(session, ut_url)
        self._print_str("Querying the Upgrade Tracker URL {0}\n\n{1}".format(ut_url, json.dumps(ut_url_data, indent=4)))

        # Get the Domain Data
        domain_url = ut_url_data["_links"][domain]["href"]
        domain_url_data = self.get(session, domain_url)
        self._print_str(
            "Querying the domain URL {0}\n\n\n{1}".format(domain_url, json.dumps(domain_url_data, indent=4))
        )

        # Get the Project Data
        projects_url = domain_url_data["_links"]["projects"]["href"]
        projects_data = self.get(session, projects_url)
        self._print_str(
            "Querying the projects data {0}\n\n{1}".format(projects_url, json.dumps(projects_data, indent=4))
        )

        for project_data in projects_data["projects"]:
            if project_data["name"] == project_name:
                self._print_str(
                    "Querying the projects URL {0}\n\n{1}".format(projects_url, json.dumps(project_data, indent=4))
                )
                self._print_str("Checking out the project so edits can be made")
                project_checkout = self.post(session, project_data["_links"]["actions"]["checkout"]["href"])
                self._print_str(json.dumps(project_checkout, indent=4))
                if "error" in project_checkout.keys():
                    raise Exception

                return project_data

        return None

    def update_deliverable(self, session, deliverables_url, reference):
        deliverables_data = self.get(session, deliverables_url)
        self._print_str(
            "Querying deliverables URL {0}\n\n{1}".format(deliverables_url, json.dumps(deliverables_data, indent=4))
        )

        deliverable_url = None
        for deliverable_data in deliverables_data["deliverables"]:
            if deliverable_data["reference"] == reference:
                deliverable_url = deliverable_data["_links"]["self"]["href"]

        # if the deliverable exists
        if deliverable_url:
            deliverable_data = self.get(session, deliverable_url)
            self._print_str(
                "Querying deliverable URL {0}\n\n{1}".format(deliverable_url, json.dumps(deliverable_data, indent=4))
            )

            # ===================================================
            # create the payload to send to the deliverable URL
            # ===================================================
            payload = dict()
            payload.update({"data": {}})
            payload["data"].update({"dates": {}})
            payload["data"].update({"status": self.status})  # options "delivered" or "cancelled"
            payload["data"]["dates"].update(
                {"delivery": self.deliveryDate}
            )  # can only be set by someone from Project Management team
            payload["data"]["dates"].update(
                {"required": self.requiredDate}
            )  # can only be set by someone from Project Management team
            payload.update({"comment": self.comment})  # this is mandatory when making any change at all
            self._print_str(
                "Updating deliverable url {0} with {1}".format(deliverable_url, json.dumps(payload, indent=4))
            )
            # now update the deliverable
            deliverable_update = self.put(session, deliverable_url, data=payload)
            return deliverable_update

        return None


class ReadTGService:
    def __init__(self, query_params, username, password):
        """
        Read meta data and user space data based on the request
        Args:
            query_params:
                            {
                              "domain": "core",
                              "projectName": "Sacramento",
                              "tgReference": "TG9999"
                              "userSpace": ["NDDS", "Tx Design"]
                            }

            username: restricted application account login name (starts with SVC-APP-xxx)
            password: restricted application account login password
        """
        logger.info("Initializing anp ReadTGService")
        self.domain = query_params["domain"]
        self.projectName = query_params["projectName"]
        self.tgReference = query_params["tgReference"]
        self.payloadUserSpaces = query_params.get("userSpace")
        self.username = username
        self.password = password
        self.rest = RestUtility()
        if "production" in anp_environment.lower():
            self.url = anp_prod_url
        else:
            self.url = anp_uat_url

    def get_token(self, url):
        try:
            response = self.rest.post(
                url + "/sso",
                headers={"content-type": "application/json"},
                data=json.dumps({"username": self.username, "password": self.password}),
            )
            return response["token"]
        except RestUtilityException as err:
            logger.error(f"Failed to login to A&P portal: {err.args[0]}")

    def read_tg(self):  # noqa: C901
        """
        main function
        :return: success - meta data or user space data based on the user request
                 failure - return appropriate error msg with error code
        """
        url = self.url

        # login
        try:
            logger.info("Generating token")
            token = self.get_token(url)
        except (ValueError, TypeError, AttributeError, KeyError) as err:
            logger.error(f"login to A&P portal failed: {err.args[0]}")
            return {
                "status": "failure",
                "errors": [
                    {
                        "code": "ERR-005-006-0001",
                        "message": f"Login to A &  P Portal - {anp_environment} failed. "
                        f"Make sure that credentials are ok",
                    }
                ],
            }

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer {0}".format(token),
        }

        meta_data = self.read_meta_data(headers, url, self.domain, self.projectName)

        if not meta_data["success"]:
            logger.info(f"metadata is not found for the given payload {meta_data}")
            return {
                "status": "failure",
                "errors": [
                    {
                        "code": "ERR-005-006-1001",
                        "message": meta_data["message"],
                    }
                ],
                "metadata": {"tgReference": self.tgReference, "domain": self.domain, "project": self.projectName},
            }

        if not self.payloadUserSpaces:
            del meta_data["data"]["_links"]
            del meta_data["data"]["deliverables"][0]["_links"]
            meta_data["data"]["deliverables"][0].update({"domain": self.domain, "project": self.projectName})
            return {"status": "success", "metadata": meta_data["data"]["deliverables"][0]}

        user_space_data = self.read_user_space_data(headers, self.projectName, self.payloadUserSpaces, meta_data)
        if not user_space_data["success"]:
            return {
                "status": "failure",
                "errors": [
                    {
                        "code": "ERR-005-006-1001",
                        "message": user_space_data["message"],
                    }
                ],
                "metadata": {"tgReference": self.tgReference, "domain": self.domain, "project": self.projectName},
            }
        else:
            return user_space_data["data"]

    def read_meta_data(self, headers, url, domain, project_name):
        """
        :return:
        """
        ut_url = url + "/ut"
        response_object = {}

        # Get the Domain Data
        try:
            ut_url_data = self.rest.get(ut_url, headers=headers)
            domain_url = ut_url_data["_links"][domain]["href"]
        except RestUtilityException as err:
            logger.error(f"Failed to get ut url data :  {err.args[0]}")
            raise DataUnavailable(f"Could not get ut url data: {err.args[0]}")
        except (ValueError, TypeError, AttributeError, IndexError, KeyError) as err:
            logger.error(f"Failed to get domain url :  {err.args[0]}")
            raise InvalidRequest(f"Invalid domain {domain} provided")

        try:
            domain_url_data = self.rest.get(domain_url, headers=headers)
            tg_ref_deliverables_url = domain_url_data["_links"]["deliverables"]["href"]
        except RestUtilityException as err:
            logger.error(f"Could not get domain url data :  {err.args[0]}")
            raise DataUnavailable(f"Could not get domain url data: {err.args[0]}")
        except (ValueError, TypeError, AttributeError, IndexError, KeyError) as err:
            logger.error(f"Failed to get deliverables :  {err.args[0]}")
            raise InvalidRequest(f"Failed to get deliverables for domain {domain} provided")

        try:
            tg_ref_data = self.rest.get(
                tg_ref_deliverables_url, headers=headers, params={"reference": self.tgReference}
            )
            uid = tg_ref_data["deliverables"][0]["uid"]
            parent_projects_url = tg_ref_data["deliverables"][0]["_links"]["parent"]["href"]
        except RestUtilityException as err:
            logger.error(f"Provided tgReference is invalid: {err.args[0]}")
            raise DataUnavailable(f"Invalid tgReference {self.tgReference} provided")
        except (ValueError, TypeError, AttributeError, IndexError, KeyError) as err:
            logger.error(f"Failed to get deliverables for provided tgReference : {err.args[0]}")
            raise InvalidRequest(f"Invalid tgReference {self.tgReference} provided")

        try:
            parent_projects_data = self.rest.get(parent_projects_url, headers=headers)
            if parent_projects_data["name"] == project_name:
                response_object["success"] = True
                response_object["data"] = tg_ref_data
                response_object["uid"] = uid
        except RestUtilityException as err:
            logger.error(
                f"Failed to get parent project data for domain: {domain}, "
                f"tgReference: {self.tgReference}, project: {project_name}: {err.args[0]}"
            )
            raise DataUnavailable(f"Invalid project {project_name} provided")

        return response_object

    def read_user_space_data(self, headers, project_name, payload_user_spaces, meta_data):
        """
        :return: user space data
        """
        response_object = {}
        row_data_schema = {}
        user_space_row_data_url = ""
        user_space_url = meta_data["data"]["deliverables"][0]["_links"]["userspaces"]["href"]
        del meta_data["data"]["_links"]
        del meta_data["data"]["deliverables"][0]["_links"]
        metadata = meta_data["data"]["deliverables"][0]
        try:
            user_space_data = self.rest.get(user_space_url, headers=headers)
        except RestUtilityException as err:
            logger.error(f"Failed to get user space data for {project_name}: {err.args[0]}")
            response_object["success"] = False
            response_object["message"] = "Failed to get user space data for {0} ".format(project_name)
            response_object["details"] = err.args[0]
            return response_object

        row_data = []
        for user_space in user_space_data["userspaces"]:
            if user_space["name"].strip() in payload_user_spaces:
                user_space_row_data_url = user_space["_links"]["cells"]["href"]
                row_data.append(
                    self.get_cell_data(user_space_row_data_url, user_space["name"], meta_data["uid"], headers)
                )
        if not user_space_row_data_url:
            logger.info(f"Could not able to find data for requested user spaces : {payload_user_spaces}")
            response_object["success"] = False
            response_object["message"] = "Could not able to find data for requested user spaces:" "{0}".format(
                payload_user_spaces
            )
            return response_object

        # get activity ids
        activity_ids = set()
        rows = [row for sublist in row_data for row in sublist]
        for row in rows:
            for k, v in row.items():
                activity_ids.add(v["activity"])

        final_row_data = []
        for activity_id in activity_ids:
            for row in rows:
                for k, v in row.items():
                    if activity_id == v["activity"]:
                        row_data_schema[k] = v["cells"]
            final_row_data.append(row_data_schema.copy())

        if len(final_row_data) == len(payload_user_spaces):
            status = "success"
        else:
            status = "partial success"
        metadata.update({"rows": final_row_data})
        response_object["success"] = True
        response_object["data"] = {"status": status, "metadata": metadata}
        return response_object

    def get_cell_data(self, user_space_row_data_url, user_space_name, uid, headers):
        try:
            cell_data = self.rest.get(user_space_row_data_url, headers=headers)
            rows = [{user_space_name: row} for row in cell_data["rows"] if row["deliverable"] == uid]
            for row in rows:
                for userspace_name, userspace_details in row.items():
                    for column_name in userspace_details["cells"].keys():
                        userspace_details["cells"][column_name] = userspace_details["cells"][column_name]["value"]
            return rows
        except RestUtilityException as err:
            logger.error(f"Failed to get cell data: {err.args[0]}")
