# Import your libraries
import pyspark
from pyspark.sql import functions as F

# Start writing code
facebook_web_log

facebook_web_log_with_date = (
    facebook_web_log
    .withColumn("date", F.to_date(F.col("timestamp")))
    )

# facebook_web_log_with_date.toPandas()
load_log = (
    facebook_web_log_with_date
    .filter(F.col('action') == 'page_load')
    .groupBy(F.col('user_id'), F.col('date'))
    .agg(F.max('timestamp').alias('load_ts'))
    )
exit_log = (
    facebook_web_log_with_date
    .filter(F.col('action') == 'page_exit')
    .groupBy(F.col('user_id'), F.col('date'))
    .agg(F.min('timestamp').alias('exit_ts'))
    )

facebook_web_log = (
    load_log.alias('ll')
    .join(
        exit_log.alias('el'),
        (F.col('ll.user_id') == F.col('el.user_id')) & (F.col('ll.date') == F.col('el.date'))
        )
    .withColumn('ts_diff', F.col('exit_ts') - F.col('load_ts'))
    .groupBy('ll.user_id')
    .agg(F.avg('ts_diff').alias('avg_ts'))
    )


# final_log
# load_log.toPandas()
# exit_log.toPandas()
# # To validate your solution, convert your final pySpark df to a pandas df
facebook_web_log.toPandas()