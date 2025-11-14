# Import your libraries
from pyspark.sql import functions as F, DataFrame

# Start writing code
sf_restaurant_health_violations = (
    sf_restaurant_health_violations
    .withColumn('year', F.year(F.col('inspection_date')))
    .filter(F.col('business_name') == F.lit('Roxanne Cafe'))
    .groupBy(F.col('year')).agg(F.count('*').alias('violations_count'))
    )

# To validate your solution, convert your final pySpark df to a pandas df
sf_restaurant_health_violations.toPandas()