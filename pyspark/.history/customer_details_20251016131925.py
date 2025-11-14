# Import your libraries
from pyspark.sql import functions as F

# Start writing code
customers = (
    customers.alias('c')
    .join(orders.alias('o'), F.col('c.id') == F.col('o.cust_id'), how='left')
    .select('c.first_name', 'c.last_name', 'c.city', 'o.order_details')
    .orderBy(F.asc('c.first_name'), F.asc('o.order_details'))
    )

# To validate your solution, convert your final pySpark df to a pandas df
customers.toPandas()