import json
import ast
import requests
from delta_sdk.configs.postie import POSTIE
from delta_sdk.configs.common import CommonConfig
import pytz
from delta_sdk.utils import logging
from datetime import datetime

class Postie:

    @staticmethod
    def send_email_notification(env, postie_hash, emailSchema):
        """To send e-mails via Postie Service
            Args::
                env
                postie_hash
                emailSchema
        """

        
        jsonStr = json.dumps(emailSchema)
        payload = json.dumps(ast.literal_eval(jsonStr))

        logging.info(f"Postie Email Payload: \n {payload}")
        postie_email_endpoint = POSTIE['host'][env] + POSTIE['uri']['postConfig']

        logging.info(f"The Postie Email Endpoint is: {postie_email_endpoint}")

        postie_headers = {
            "Authorization": postie_hash,
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(postie_email_endpoint, data=payload, headers=postie_headers)

            if response.status_code in [200, 202]:

                logging.info(response.status_code)
                logging.info(response.text)
                logging.info('Postie Email Notification Succefully Sent')
                return {"status_code": response.status_code, "text":response.text}
            else:
                logging.info(response.status_code)
                logging.info(response.text)
                logging.info('Error in Postie Email Notification API call')
        except Exception as e:
            logging.info('Exception in Postie Email Notification API call: ', str(e))

    def delta_job_failure_alert(env, postie_hash, job_name, failure_logs, recepients: list):
        """Generic Failure notification common for all jobs.
            Args::
                env
                postie_hash
                job_name : Name of the job.
                failure_logs : Data to be displayed
                recepients
            Note::
                Uses postie template :- delta-job-failure-alerting
        """

        logging.info("Started notification job.")
        timezone = pytz.timezone(CommonConfig.TIMEZONE_CONFIG)

        template_data = {
            "env": env,
            "date": datetime.now(tz=timezone).strftime(format=CommonConfig.DATE_FORMAT),
            "time": datetime.now(tz=timezone).strftime(format=CommonConfig.TIME_FORMAT),
            "exception_data": failure_logs,
            "jobName": job_name
        }

        emailSchema = {
            "appName": "delta-job-failure-alerting",
            "emailName": "delta-job-failure-alerting",
            "to": recepients,
            "subject": f" Job '{job_name}' failed | {env}",
            "templateData": template_data
        }

        logging.info("EmailSchema:")
        logging.info(emailSchema)
        result = Postie.send_email_notification(env=env, postie_hash=postie_hash, emailSchema=emailSchema)
        logging.info(f"Postie Result: {result}")

    def delta_job_success_notification(env, postie_hash, job_name, output_data, recepients: list[str]):
        """Generic Success notification common for all jobs.
            Args::
                env
                postie_hash
                job_name : Name of the job.
                output_data : Data to be displayed
                recepients
            Note::
                Uses postie template :- delta-job-success-notification
        """
        logging.info("Started notification job.")
        timezone = pytz.timezone(CommonConfig.TIMEZONE_CONFIG)

        template_data = {
            "env": env,
            "date": datetime.now(tz=timezone).strftime(format=CommonConfig.DATE_FORMAT),
            "time": datetime.now(tz=timezone).strftime(format=CommonConfig.TIME_FORMAT),
            "output_data": output_data,
            "jobName": job_name
        }

        emailSchema = {
            "appName": "delta-job-success-notification",
            "emailName": "delta-job-success-notification",
            "to": recepients,
            "subject": f" Job '{job_name}' successfully completed | {env}",
            "templateData": template_data
        }

        logging.info("EmailSchema:")
        logging.info(emailSchema)
        result = Postie.send_email_notification(env=env, postie_hash=postie_hash, emailSchema=emailSchema)
        logging.info(f"Postie Result: {result}")

    @staticmethod
    def table_html_formatting(items: dict, columns: list[str]):
        """Generate HTML format of table to be parsed by a HTML page.
            Args::
                items
                columns
        """

        table_html = """
        <table class="line-items-table">
            <tr>
        """

        for col in columns:
            table_html += f"<th>{col}</th>"
        
        table_html += "</tr>"

        for item in items:
            table_html += "<tr>"
            for col in columns:
                table_html += f"<td>{item.get(col, 'N/A')}</td>"
            table_html += "</tr>"

        table_html += """
        </table>
        """
        return table_html