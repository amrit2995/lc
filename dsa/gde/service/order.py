import pyspark.sql
from gam_daci_etl.service.base_report import BaseReportEntity
from gam_daci_etl.service.base_lt import BaseLTServiceEntity
from gam_daci_etl.service.base_db_lt_build import BaseBuildLTDBEntity
from gam_daci_etl.service.base_db_build import BaseBuildDBEntity
from gam_daci_etl.service.extra_entitiy_mixins import ExtraEntityMixins
from gam_daci_etl.service.job_status_report import JobStatusReport
from gam_daci_etl.gam_lt_models import OrderLevelModel
from pyspark.sql.types import *
from pyspark.sql import functions as F
import pyspark
import pandas as pd
import logging
from googleads import ad_manager
import copy
import os

__all__ = ["OrderLevel"]

class OrderLevel(
    ExtraEntityMixins, 
    JobStatusReport,
    BaseReportEntity,
    BaseLTServiceEntity,
    BaseBuildLTDBEntity,
    BaseBuildDBEntity
    ):

    gam_entity = "order"
    gam_service_name = 'OrderService'
    gam_method_name = 'getOrdersByStatement'
    gam_lt_input_model = OrderLevelModel

    @classmethod
    def build_gam_lt_service_api_statement(cls):

        advertiserFilters = cls.JobConfigs.CHANNEL["advertiserFilters"]

        statement: ad_manager.StatementBuilder = copy.deepcopy(
            (
                ad_manager
                .StatementBuilder(version=cls.JobConfigs.GAM_VERSION)
                .Where(
                    "startDateTime >= :startDateTime "
                    f"AND NOT advertiserId IN ({','.join(advertiserFilters)})"
                )
                .WithBindVariable('startDateTime', cls.earliest_date_acceptable.isoformat())
            )
        )
        return statement
    
    # @classmethod
    # def build_gam_lt_report_api_statement(cls):

    #     advertiserFilters = cls.JobConfigs.CHANNEL["advertiserFilters"]

    #     statement: ad_manager.StatementBuilder = copy.deepcopy(
    #         (
    #             ad_manager
    #             .StatementBuilder(version=cls.JobConfigs.GAM_VERSION)
    #             .Where(
    #                 f"NOT advertiserId IN ({','.join(advertiserFilters)})"
    #             )
    #         )
    #     )
    #     return statement

    @classmethod
    def gam_service_input_lt_sync_schema(cls) -> StructType:
        schema_fields = [
            StructField("id", LongType(), False),
            StructField("name", StringType(), False),                
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
            StructField("Order_ID", LongType(), False),
            StructField("Order_Name", StringType(), True),
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
    def build_report_statement(cls, *args, **kwargs):

        customCriteria = cls.configs['gam']["customCriteria"]
        advertiserFilters = cls.configs['gam']["advertiserFilters"]

        cls.statement = (
            cls.statement
            .Where(f"CUSTOM_TARGETING_VALUE_ID IN ({','.join(customCriteria)}) AND NOT ADVERTISER_ID IN ({','.join(advertiserFilters)})")
        )

    @classmethod
    def custom_process_report(cls, df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        logging.info('Report processing started.')

        def combine_ad_units(*ad_units):
            filtered_units = [str(unit) for unit in ad_units if pd.notna(unit) and str(unit).strip() not in ("-", "", "nan", "None", "<NA>")]
            return " > ".join(filtered_units)

        logging.info("AdUnit Ids combined.")
        ad_unit_name_cols = ['Ad unit 1', 'Ad unit 2', 'Ad unit 3', 'Ad unit 4', 'Ad unit 5']
        ad_unit_id_cols = ['Ad unit ID 1', 'Ad unit ID 2', 'Ad unit ID 3', 'Ad unit ID 4', 'Ad unit ID 5']
        df["Ad unit ID 1"] = pd.to_numeric(df["Ad unit ID 1"], errors="coerce").astype("Int64").astype(str)
        df["Ad unit ID 2"] = pd.to_numeric(df["Ad unit ID 2"], errors="coerce").astype("Int64").astype(str)
        df["Ad unit ID 3"] = pd.to_numeric(df["Ad unit ID 3"], errors="coerce").astype("Int64").astype(str)
        df["Ad unit ID 4"] = pd.to_numeric(df["Ad unit ID 4"], errors="coerce").astype("Int64").astype(str)
        df["Ad unit ID 5"] = pd.to_numeric(df["Ad unit ID 5"], errors="coerce").astype("Int64").astype(str)
        df["ad_unit_name"] = df.apply(lambda row: combine_ad_units(*[row[col] for col in ad_unit_name_cols]), axis=1)
        df["ad_unit_id"] = df.apply(lambda row: combine_ad_units(*[row[col] for col in ad_unit_id_cols]), axis=1)
        return df

    @classmethod
    def post_entity_lt_processing(cls, spark, df, *args, **kwargs):
        filtered_orders_df = df.filter(
            ~F.col("order_name").rlike("(?i)test")
        )

        return filtered_orders_df