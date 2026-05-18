# Standard Library
import logging
import sys

# Third Party Library
import connexion

# Sky Library
from isp_config import ConfigManagerException

# DNE Library
from connectors.core.config import connectors_config
from connectors.core.services.itsm.connector import SparkTicketService
from connectors.core.services.itsm.exceptions import InvalidRequest, ResourceServiceNotAvailable
from connectors.core.services.itsm.service_mapping import mapper
from connectors.core.utils.exceptions import RestUtilityException

logger = logging.getLogger(__name__)

try:
    config = connectors_config.ConnectorsConfigManager()
    config.load_config()
except ConfigManagerException:
    sys.exit(1)

service_type = config.get(section="itsm", key="service_type")


def change_restrictions(**kwargs):  # noqa: N802
    """
    Get Spark Service Now Change Restrictions.

    Args:
       start_date: start date to filter the records
       end_date: end date to filter the records

    Returns:
       {
           "event_name": "DE Bank Holiday: Mariä Himmelfahrt",
           "event_start_time": "14/08/2020 22:00:00",
           "event_end_time": "15/08/2020 21:59:59",
           "applies_to": "cmdb_ci_service",
           "condition": "Business areas CONTAINS DE Broadcasting .or. Business areas CONTAINS DE Information Technology
           ",
           "blackout_schedule": "DE - Bank Holidays ",
           "blackout_schedule_type": "Change Freeze"
       }

    Raises:

    """
    try:
        start_date_in_epoch = kwargs.get("start_date")
        end_date_in_epoch = kwargs.get("end_date")

        logger.info(f"Entering into ITSM module to retrieve change restrictions")

        """
        calling spark api for retrieving the change restrictions using service3020
        """

        spark = SparkTicketService()
        spark_response = spark.service3020(start_date=start_date_in_epoch, end_date=end_date_in_epoch)

        service_map = None
        if kwargs.get("serviceType") and service_type in kwargs.get("serviceType"):
            service_map = mapper[kwargs["serviceType"]]["create"]

        logger.debug(f"Value of Service Type is {service_map}")
        change_freeze_list = []
        if spark_response:  # Added as new functionality to facilitate BPM to check for Freeze
            for (index, change_freeze) in enumerate(spark_response):
                if service_map and service_map["config_group"] in change_freeze["condition"]:
                    change_freeze_list.append(change_freeze)
        logger.info(f"Checks for change restrictions completed successfully with {len(change_freeze_list)}")

        logger.info("Exiting ITSM module after sending the response")
        return change_freeze_list

    except (ValueError, KeyError, TypeError, OverflowError, InvalidRequest) as err:
        logger.exception(err)
        return connexion.problem(status=404, title=f"Problem in preparing request", detail=err.args[0])
    except RestUtilityException as err:
        return connexion.problem(
            status=403,
            title=f"Request Exception while accessing the URL",
            detail=err.args[0],
        )
    except ResourceServiceNotAvailable as err:
        logger.exception(err)
        return connexion.problem(status=404, title=f"Error in accessing Spark ticketing system", detail=err.args[0])
    except Exception as err:
        logger.exception(err)
        return connexion.problem(
            status=500, title=f"Connector exception raised while running custom query", detail=err.args[0]
        )
