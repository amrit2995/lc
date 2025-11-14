# Import your libraries
import pyspark
from pyspark.sql import functions as F

# Start writing code
loans = (
    loans
    .filter(F.col('type').isin(['Refinance', 'InSchool']))
    .groupBy(F.col('type'), F.col('user_id'))
    .agg(F.count('*').alias('type_count'))
    .filter(F.col('type_count') > 0)
    .groupBy(F.col('user_id'))
    .agg(F.count('*').alias('t_count'))
    .filter(F.col('t_count')>=2)
    .select('user_id')
    )

# To validate your solution, convert your final pySpark df to a pandas df
loans.toPandas()