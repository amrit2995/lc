# Import your libraries
import pyspark
from pyspark.sql import functions as F
from pyspark.sql.window import Window


# Start writing code
lyft_rides_log = (
    lyft_rides_log.alias('lrl')
    .groupBy(['user_id']).agg(F.sum('distance').alias('distance_travelled'))
    .withColumn('rank', F.rank().over(
        Window.orderBy(F.desc('distance_travelled'))
    )).filter(F.col('rank') <= F.lit(10))
    .join(lyft_users.alias('lu'), F.col('lu.id') == F.col('lrl.user_id'))
    .select('user_id', 'name', 'distance_travelled')
)

# To validate your solution, convert your final pySpark df to a pandas df
lyft_rides_log.toPandas()