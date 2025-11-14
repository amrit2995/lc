# Import your libraries
import pyspark
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Start writing code
forbes_global_2010_2014 = (
    forbes_global_2010_2014
    .filter(F.col('sector') == F.lit("Financials"))
    .withColumn("rank", F.rank().over(Window.partitionBy().orderBy(F.col("profits").desc())))
    .filter(F.col('rank') == F.lit(1))
    .select("company", "continent")
    )

# To validate your solution, convert your final pySpark df to a pandas df
forbes_global_2010_2014.toPandas()