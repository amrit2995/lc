# Import your libraries
from pyspark.sql import functions as F

# Start writing code
amazon_shipment = (
    amazon_shipment
    .withColumn('year_month', F.date_format(F.col('shipment_date'), 'yyyy-MM'))
    .groupBy(F.col('year_month')).agg(F.count('*').alias('no_of_shipments'))
    .select('year_month', 'no_of_shipments')
    )

# To validate your solution, convert your final pySpark df to a pandas df
amazon_shipment.toPandas()