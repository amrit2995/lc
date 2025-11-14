from pyspark.sql import functions as F, DataFrame

filtered_customer_df = (
    customers.alias("c")
    .join(orders.alias("o"), F.col("c.id") == F.col("o.cust_id"), "inner")
    .filter(F.col("c.first_name").isin(["Jill", "Eva"]))
    .select("first_name", "order_date", "order_details", "total_order_cost")
)

filtered_customer_df.toPandas()