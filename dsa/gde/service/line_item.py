import pyspark.sql
from gam_daci_etl.service.base_service import BaseServiceEntity
from gam_daci_etl.service.base_lt import BaseLTServiceEntity
from gam_daci_etl.service.base_db_lt_build import BaseBuildLTDBEntity
from gam_daci_etl.service.base_db_build import BaseBuildDBEntity
from gam_daci_etl.service.extra_entitiy_mixins import ExtraEntityMixins
from gam_daci_etl.service.job_status_report import JobStatusReport
from pyspark.sql.types import *
from gam_daci_etl.gam_lt_models import LineItemModel
from googleads import ad_manager
import copy
from gam_daci_etl.service.order import OrderLevel
import pyspark
import os
from pyspark.sql import functions as F

class LineItemLevel(
    ExtraEntityMixins,
    JobStatusReport,
    BaseLTServiceEntity, 
    BaseBuildLTDBEntity, 
    BaseBuildDBEntity
    ):

    gam_entity = "LineItem"
    gam_service_name = 'LineItemService'
    gam_method_name = "getLineItemsByStatement"
    gam_lt_input_model = LineItemModel

    @classmethod
    def build_gam_lt_service_api_statement(cls):

        statement: ad_manager.StatementBuilder = copy.deepcopy(
            (
                ad_manager
                .StatementBuilder(version=cls.JobConfigs.GAM_VERSION)
                .Where(
                    "startDateTime >= :startDateTime "
                )
                .WithBindVariable('startDateTime', cls.earliest_date_acceptable.isoformat())
            )
        )
        return statement

    @classmethod
    def gam_service_input_lt_sync_schema(cls) -> StructType:
        schema_fields = [
            StructField("id", LongType(), False),
            StructField("name", StringType(), False),
            StructField("orderId", LongType(), False),
            StructField("startDateTime", DateType(), True),
            StructField("endDateTime", DateType(), True),
            StructField("totalClicksDelivered", LongType(), True),
            StructField("totalImpressionsDelivered", LongType(), True),
            StructField("unlimitedEndDateTime", BooleanType(), True),
        ]

        return StructType(schema_fields)

    @classmethod
    def get_spark_schema_lt_sync_final(cls) -> StructType:

        schema_fields = [
            StructField("LineItem_ID", LongType(), False),
            StructField("LineItem_Name", StringType(), True),
            StructField("Order_ID", LongType(), False),
            StructField("report_start_date", DateType(), True),
            StructField("report_end_date", DateType(), True),
            StructField("LT_Clicks_Entity_API", LongType(), True),
            StructField("LT_Clicks_Reporting_API", LongType(), True),
            StructField("LT_Impression_Entity_API", LongType(), True),
            StructField("LT_Impression_Reporting_API", LongType(), True),
            StructField("isActive", IntegerType(), True),
            StructField("data_refresh_date", DateType(), False),
        ]
        return StructType(schema_fields)
    
    @classmethod
    def post_entity_lt_processing(cls, spark: pyspark.sql.SparkSession, df: pyspark.sql.DataFrame, gcs_storage_conns) -> pyspark.sql.DataFrame :

        trigger_date_str = cls.trigger_date.strftime("%Y%m%d")
        file_name = f"{cls.JobConfigs.CHANNEL['entities']['OrderLevel']['gcsFileName']}_{trigger_date_str}.csv.gz"
        source = os.path.join(cls.JobConfigs.CHANNEL["gcsBaseFilepath"], file_name)
        destination = os.path.join(os.getcwd(), file_name)

        for gcs_storage_conn in gcs_storage_conns:
            download_success = gcs_storage_conn.download_file(source, destination)
            if download_success:
                break

        order_df: pyspark.sql.DataFrame = (
            spark.read
            .format("csv")
            .option("header", "true")
            .option("inferSchema", "true")
            .load(destination)
        )

        line_items_filtered: pyspark.sql.DataFrame= df.join(
            order_df,
            on='order_id',
            how="left_semi"
        )

        line_items_cleaned = line_items_filtered.filter(
            ~F.col("lineitem_name").rlike("(?i)test")
        )
        line_items_cleaned.show()
        return line_items_cleaned