# Import your libraries
import pyspark
from pyspark.sql import functions as F

# Start writing code
facebook_employees = (
    facebook_employees.alias('fe')
    .join(facebook_hack_survey.alias('fhs'), F.col('fe.id') == F.col('fhs.employee_id'))
    .groupby('location')
    .agg(F.mean('popularity').alias('popularity'))
    .select('location', 'popularity')
    )

# To validate your solution, convert your final pySpark df to a pandas df
facebook_employees.toPandas()