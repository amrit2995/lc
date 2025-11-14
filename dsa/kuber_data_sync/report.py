from delta_sdk.utils.postie import Postie
from datetime import datetime
import pytz
from delta_sdk.utils import logging
from kuber_data_sync.configs import CommonConfigs, MongoConfigs

class Report:
    report_data = {}
    RECEPIENTS = ['@email.com']
    POSTIE_HASH = '<hash>'

    @classmethod
    def update_entity_mongo_stats(cls, entity: str, data: dict):
        """To log the stats of mongo insert, upsert, etc."""
        try:
            if not cls.report_data.get('entities'):
                cls.report_data['entities'] = {}

            if not cls.report_data['entities'].get(entity):
                cls.report_data['entities'][entity] = {}

            for key in {'nInserted', 'nUpserted', 'nMatched', 'nModified', 'nRemoved'}:
                cls.report_data['entities'][entity][key] = cls.report_data['entities'][entity].get(key, 0) + data.get(key, 0)

        except Exception as e:
            logging.error("Error during Report creation.")
            logging.error(f"{type(e).__name__}: {e}")

    @classmethod
    def update_entity_sync_status(cls, entity, status, error_message=''):
        """Sets sync-status once it completes"""
        try:

            if not cls.report_data.get('entities'):
                cls.report_data['entities'] = {}

            if not cls.report_data['entities'].get(entity):
                cls.report_data['entities'][entity] = {}

            cls.report_data['entities'][entity]['sync-status'] = status
            if error_message:
                cls.report_data['entities'][entity]['error-message'] = error_message

        except Exception as e:
            logging.error(f"Error during updating sync status.")
            logging.error(f"{type(e).__name__}: {e}")

    @classmethod
    def show_entity_report(cls, entity):
        """Only for logging purpose to tract entity-wise stats."""
        if not cls.report_data.get('entities'):
            logging.info("No Entities report.")
        if not cls.report_data['entities'].get(entity):
            logging.info(f"no report for Entity: {entity}.")

        entity_report = cls.report_data['entities'][entity]
        logging.info(f"Report for entity {entity} := {entity_report}")

    @classmethod
    def start(cls):
        """Starts setting the config. of the job in report."""
        cls.report_data['startTime'] = datetime.now(tz=pytz.timezone(CommonConfigs.TIMEZONE)).strftime(CommonConfigs.DATE_TIME_FORMAT)
        cls.report_data['cluster-name'] = MongoConfigs.CLUSTER_NAME
        cls.report_data['db-name'] = MongoConfigs.DB_NAME
        cls.report_data['sync-mode'] = CommonConfigs.SYNC_MODE
        cls.report_data['time-zone'] = CommonConfigs.TIMEZONE

    @classmethod
    def generate_report(cls):
        """Returns data in JSON Format."""
        cls.report_data["endTime"] =  datetime.now(tz=pytz.timezone(CommonConfigs.TIMEZONE)).strftime(CommonConfigs.DATE_TIME_FORMAT)
        import json
        json_data = json.dumps(cls.report_data, indent=4)
        # logging.info(json_data)
        return json_data

    @classmethod
    def generate_html_parsed_report(cls):
        json_data = cls.generate_report()
        return "<pre>" + json_data + "</pre>"

    @classmethod
    def send_postie_email(cls, env):
        """To send e-mail notification."""
        try:
            html_parsed_data = cls.generate_html_parsed_report()
            Postie.delta_job_success_notification(
                env=env, job_name=f'kuber-data-sync', 
                recepients=cls.RECEPIENTS,
                postie_hash=cls.POSTIE_HASH,
                output_data=html_parsed_data
            )
        except Exception as e:
            logging.error("Error during Success e-mail.")
            logging.error(f"{type(e).__name__}: {e}")


    @classmethod
    def send_failure_alert(cls, env, exception_log):
        """To send failure e-mail notification. Only when the whole script fails."""
        try:
            html_parsed_data = cls.generate_html_parsed_report()
            Postie.delta_job_failure_alert(
                env=env, job_name=f'kuber-data-sync', 
                recepients=cls.RECEPIENTS,
                postie_hash=cls.POSTIE_HASH,
                failure_logs=f"{exception_log} \n\n Report:- {html_parsed_data}"
            )
        except Exception as e:
            logging.error("Error during Alert Mail.")
            logging.error(f"{type(e).__name__}: {e}")