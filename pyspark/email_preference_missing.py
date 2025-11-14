from pyspark.sql import functions as F

library_usage = (
    library_usage
    .filter(
        (F.col('notice_preference_definition') == 'email') &
        (F.col('provided_email_address') == F.lit(False))
    )
    .select('home_library_code')
    .distinct()
)

library_usage.toPandas()
