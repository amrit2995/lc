# Import your libraries
from pyspark.sql import functions as F, DataFrame

# Start writing code
worker = (
    worker
    .withColumn("joining_date", F.to_date(F.col("joining_date")))
    .filter(F.col('joining_date') >= F.lit('2014-04-01'))
    .groupBy(F.col('department')).agg(F.count('*').alias('num_workers'))
    .orderBy(F.col('num_workers'))
    )

# To validate your solution, convert your final pySpark df to a pandas df
worker.toPandas()