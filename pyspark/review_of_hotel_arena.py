# Import your libraries
import pyspark
from pyspark.sql import functions as F

# Start writing code
hotel_reviews = (
    hotel_reviews
    .filter(F.col('hotel_name') == F.lit('Hotel Arena'))
    .groupBy(F.col('hotel_name'), F.col('reviewer_score'))
    .agg(F.count('*').alias('no_of_reviewers'))
    )

# To validate your solution, convert your final pySpark df to a pandas df
hotel_reviews.toPandas()