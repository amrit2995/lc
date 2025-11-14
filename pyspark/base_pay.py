# Import your libraries
import pyspark
import pyspark.sql.functions as F


# Start writing code
sf_public_salaries = (
    sf_public_salaries
    .filter((F.col('jobtitle').like('%CAPTAIN%')) & (F.col('jobtitle').like('%POLICE%')))
    .select('employeename', 'basepay')
    )

# To validate your solution, convert your final pySpark df to a pandas df
sf_public_salaries.toPandas()