from delta_sdk.utils import logging
from googleads import ad_manager
from gam_daci_etl.configs import JobConfigs
from datetime import datetime, timedelta
from delta_sdk.utils.common import RateLimiter, CommonUtils
import pytz
import zeep
import pyspark


class BaseServiceEntity:

    @classmethod
    def init_service_class(cls):
        cls.gam_pagination_limit = 500
        cls.gam_batch = 0
        cls.JobConfigs = JobConfigs

        cls.statement: ad_manager.StatementBuilder = (
            ad_manager
            .StatementBuilder(version=cls.JobConfigs.GAM_VERSION)
            )

    @classmethod
    def show_user(cls, gam_client):
        userService = gam_client.GetService('UserService', version=cls.JobConfigs.GAM_VERSION)
        currentUser = userService.getCurrentUser()
        return currentUser

    @classmethod
    @CommonUtils.retry_connection(
        max_retries=4, delay=1, delay_type='exponential',
        rate_limiter=RateLimiter(
            name='gam_lt_service', mode=RateLimiter.mode.BY_CEILING,
            ceiling=15, time_window=60
            ))
    def fetch_service(cls, mongo_client=None, gam_client=None,  *args, **kwargs):
        """Fetch records for respective entities from GAM.
        Args::
            gam_client
        Response::
            Yielding records in batches as configured.
        Note::
        """
        logging.info("inside 'fetch' block.")

        service = gam_client.GetService(service_name=cls.gam_service_name, version=JobConfigs.GAM_VERSION)

        cls.start_date: datetime = datetime(2022, 1, 1, 0, 0, 0, tzinfo=pytz.timezone(JobConfigs.TIME_ZONE))
        cls.end_date: datetime = datetime.now(tz=pytz.timezone(JobConfigs.TIME_ZONE))

        cls.build_service_statement(gam_client=gam_client)
        service_method = getattr(service, cls.gam_method_name)
        logging.info(f"Method to be called:- {cls.gam_service_name }.{cls.gam_method_name}")

        offset = 0
        while True:
            statement_query = cls.statement.ToStatement()
            logging.info(f'Statement Query: {statement_query}')
            response = service_method(statement_query)
            response = zeep.helpers.serialize_object(response)
            if result := response.get('results'):
                yield result
                offset += cls.gam_pagination_limit
                cls.statement.Offset(offset)
                cls.gam_batch += 1
            else:
                logging.info(f"No more {cls.__name__} to fetch.")
                cls.gam_batch = 0
                break
        logging.info(f"Fetching from {cls.__name__} complete")

    @classmethod
    def service_sync(cls, gam_client, *args, **kwargs):
        """Generic sync if no custom sync provided in the child class.
        Args::
            mongo_client: 
            gam_client: 
            synched_entities: List of entities already synched.

        Note:: Triggers the flow as follows :- 
            -> Fetch from GAM as per the statement.
            -> Massage data as per the model.
            -> Write to respective mongo coll. of the Child class.
        """

        cls.init_service_class()
        sync_status = False
        error_message = ''
        try:
            for gam_records in cls.fetch_service(gam_client=gam_client):
                logging.info(len(gam_records))
            sync_status = True

        except Exception as e:

            logging.error(f"Failed during the sync of {cls.__name__}")
            error_message = f"{type(e).__name__}: {e}"
            logging.error(error_message)
            sync_status = False

        finally:
            return sync_status