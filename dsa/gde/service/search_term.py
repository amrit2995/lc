from gam_daci_etl.service.base_report import BaseReportEntity
from gam_daci_etl.service.extra_entitiy_mixins import ExtraEntityMixins
from gam_daci_etl.service.job_status_report import JobStatusReport
import logging
from datetime import datetime, timedelta
import pandas as pd

__all__ = ["SearchTermLevel"]

class SearchTermLevel(
    ExtraEntityMixins, 
    JobStatusReport, 
    BaseReportEntity
    ):

    @classmethod
    def build_report_statement(cls, *args, **kwargs):

        # customCriteria = JobConfigs.CHANNEL["entities"][cls.__name__]["customCriteria"]
        advertiserFilters = cls.configs['gam']["advertiserFilters"]

        cls.statement = (
            cls.statement
            .Where(f"NOT ADVERTISER_ID IN ({','.join(advertiserFilters)})")
        )

    @classmethod
    def custom_process_report(cls, df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        logging.info('Report processing started.')

        logging.info("filterting out only the Search_terms")

        df = df[df["Dimension.CUSTOM_CRITERIA"].str.contains("search_term", na=False)]

        df = df.rename(columns={"Dimension.CUSTOM_CRITERIA": "search_term"})
        return df