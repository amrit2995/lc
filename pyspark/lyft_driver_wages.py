# Import your libraries
from pyspark.sql import functions as F, DataFrame

# Start writing code
lyft_drivers

lyft_drivers = (
    lyft_drivers
    .filter((F.col('yearly_salary') <= F.lit(30000)) | (F.col('yearly_salary') >= F.lit(70000)) )
    )


# To validate your solution, convert your final pySpark df to a pandas df
lyft_drivers.toPandas()