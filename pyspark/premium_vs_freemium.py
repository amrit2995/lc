from pyspark.sql import functions as F

final_metrics = (
    ms_download_facts.alias('mdf')
    .join(ms_user_dimension.alias('mud'), "user_id")
    .join(ms_acc_dimension.alias('mad'), "acc_id")
    .groupBy('date')
    .pivot('paying_customer', ['no', 'yes'])
    .agg(F.sum('downloads'))
    .fillna(0)
    .filter(F.col('no') > F.col('yes'))
    .select(
        F.col('date'),
        F.col('no').alias('non_paying'),
        F.col('yes').alias('paying')
        )
    .orderBy('date')
    )

final_metrics.toPandas()