# Import your libraries
from pyspark.sql import functions as F

# Start writing code
final = (
    car_launches
    .filter(F.col('year').isin('2019', '2020'))
    .groupBy('company_name')
    .pivot('year', ['2019', '2020'])
    .agg(F.count('*'))
    .withColumn('net_diff', F.col('2020') - F.col('2019'))
    .select('company_name', 'net_diff')
)

final.toPandas()
