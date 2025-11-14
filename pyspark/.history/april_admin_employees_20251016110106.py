from pyspark.sql import functions as F, DataFrame

worker = (
    worker
    .withColumn('month', F.month(F.col('joining_date')))
    .filter((F.col('month') <= F.lit(4)) & (F.col('department') == F.lit('Admin')))
    .agg(F.count('*').alias('admin_count'))
    )

worker.toPandas()