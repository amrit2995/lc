# airflow_dags/kafka_to_gcp_dataflow_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.google.cloud.operators.dataflow import DataflowStartFlexTemplateOperator
from airflow.providers.google.cloud.sensors.dataflow import DataflowJobStatusSensor
from airflow.operators.python import PythonOperator
from google.cloud import storage

default_args = {
    'owner': 'data-eng',
    'depends_on_past': False,
    'email_on_failure': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

PROJECT_ID = 'my-gcp-project'
REGION = 'us-central1'
FLEX_TEMPLATE_GCS_PATH = 'gs://my-templates/dataflow/kafka-consumer-flex-template.json'  # flex template metadata
JOB_NAME_PREFIX = 'kafka-consumer'
TEMP_LOCATION = 'gs://my-dataflow-temp/tmp'
STAGING_LOCATION = 'gs://my-dataflow-temp/staging'

with DAG(
    dag_id='kafka_to_gcp_dataflow',
    default_args=default_args,
    schedule_interval='@hourly',       # or None for event/triggered runs
    start_date=datetime(2025, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=['data-engineering', 'kafka'],
) as dag:

    def validate_schema(**ctx):
        # Optional: check schema registry or schema compatibility
        # raise Exception if not compatible
        return True

    check_schema = PythonOperator(
        task_id='check_schema',
        python_callable=validate_schema,
    )

    start_dataflow = DataflowStartFlexTemplateOperator(
        task_id='start_dataflow_flex',
        body={
            "launchParameter": {
                "jobName": f"{JOB_NAME_PREFIX}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
                "containerSpecGcsPath": FLEX_TEMPLATE_GCS_PATH,
                "environment": {
                    "tempLocation": TEMP_LOCATION,
                    "stagingLocation": STAGING_LOCATION,
                    "zone": "us-central1-a",
                    "serviceAccountEmail": "dataflow-sa@my-gcp-project.iam.gserviceaccount.com",
                },
                "parameters": {
                    # Template parameters exposed by your flex template
                    "bootstrapServers": "kafka01:9092,kafka02:9092",
                    "kafkaTopic": "events-topic",
                    "schemaRegistryUrl": "https://schema-registry:8081",
                    "gcs_output_path": "gs://my-bucket/bronze/events/",
                    "bq_dataset": "analytics_bronze",
                    "bq_table": "events_staging",
                    "window_interval_seconds": "60",
                    "max_num_workers": "10"
                }
            }
        },
        project_id=PROJECT_ID,
        region=REGION,
        do_xcom_push=True,
    )

    # Wait for Dataflow job to reach terminal state or success
    wait_for_dataflow = DataflowJobStatusSensor(
        task_id='wait_for_dataflow',
        location=REGION,
        job_id="{{ task_instance.xcom_pull(task_ids='start_dataflow_flex')['job_id'] }}",
        project_id=PROJECT_ID,
        poke_interval=60,
        timeout=60 * 60 * 6,  # 6 hours
        allowed_states=['JOB_STATE_DONE', 'JOB_STATE_CANCELLED', 'JOB_STATE_FAILED'],
    )

    def postprocess(**ctx):
        # e.g., run partitioning, update metadata/catalog, trigger downstream jobs
        # call API to register partition in metastore or run BQ vacuum
        return True

    post_proc = PythonOperator(
        task_id='postprocess',
        python_callable=postprocess,
    )

    check_schema >> start_dataflow >> wait_for_dataflow >> post_proc
