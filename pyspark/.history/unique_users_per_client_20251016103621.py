from pyspark.sql import functions as F, DataFrame
result = (
        fact_events
        .groupBy(F.col('client_id'), F.month(F.col('time_id')).alias('month'))
        .agg(F.countDistinct(F.col("user_id")).alias('user_count'))
    )

result.toPandas()