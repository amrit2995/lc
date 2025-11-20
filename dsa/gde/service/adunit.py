# from pyspark.sql import SparkSession
# from pyspark.sql.functions import col, udf
from gam_daci_etl.service.base_report import BaseReportEntity
from gam_daci_etl.service.extra_entitiy_mixins import ExtraEntityMixins
from gam_daci_etl.service.job_status_report import JobStatusReport
import pandas as pd
import logging


__all__ = ["AdUnitLevel"]

class AdUnitLevel(
    ExtraEntityMixins,
    JobStatusReport,
    BaseReportEntity
    ):

    @classmethod
    def build_report_statement(cls,  *args, **kwargs):

        customCriteria = [ str(cc) for cc in cls.configs["gam"]["customCriteria"] ]
        advertiserFilters = [ str(cc) for cc in cls.configs["gam"]["advertiserFilters"] ]

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