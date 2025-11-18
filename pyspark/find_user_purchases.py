from pyspark.sql import functions as F, Window


amazon_transactions = (
    amazon_transactions
    .withColumn('purchase_date', F.to_date(F.col('created_at')))
    .withColumn('rn', F.row_number().over(Window.partitionBy('user_id').orderBy('purchase_date')))
    .filter(F.col('rn')<=2)
    .groupBy("user_id").agg(
        F.max(F.when(F.col("rn") == 1, F.col("purchase_date"))).alias("first_date"),
        F.max(F.when(F.col("rn") == 2, F.col("purchase_date"))).alias("second_date")
        )
    .where(
        F.col("second_date").isNotNull() &
        F.datediff("second_date", "first_date").between(1,7)
        )
    .select("user_id")
    )

amazon_transactions.toPandas()