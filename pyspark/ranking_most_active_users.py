# Import your libraries
import pyspark
from pyspark.sql import functions as F
from pyspark.sql import Window

# Start writing code
airbnb_contacts = (
    airbnb_contacts
    .groupBy(F.col('id_guest')).agg(F.sum('n_messages').alias('cum_messages'))
    .withColumn('ranking', F.dense_rank().over(Window.orderBy(F.desc('cum_messages'))).cast('int'))
    .select('ranking', 'id_guest', 'cum_messages')
    )

# To validate your solution, convert your final pySpark df to a pandas df
airbnb_contacts.toPandas()