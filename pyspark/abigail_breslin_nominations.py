# Import your libraries
from pyspark.sql import functions as F

# Start writing code
oscar_nominees = (
    oscar_nominees
    .filter(F.col('nominee') == F.lit('Abigail Breslin'))
    .select(F.countDistinct('movie').alias('n_movies_by_abi'))
    )

# To validate your solution, convert your final pySpark df to a pandas df
oscar_nominees.toPandas()