from pyspark.sql.functions import col, count

# Assuming `fb_friend_requests` is a PySpark DataFrame already loaded

# Filter sent and accepted requests into separate DataFrames
sent_df = fb_friend_requests.filter(col("action") == "sent").alias("sent")
accepted_df = fb_friend_requests.filter(col("action") == "accepted").alias("accepted")

# Perform a left join between sent_df and accepted_df
joined_df = sent_df.join(
    accepted_df,
    (col("sent.user_id_sender") == col("accepted.user_id_sender")) &
    (col("sent.user_id_receiver") == col("accepted.user_id_receiver")),
    "left"
).select(
    col("sent.date").alias("request_date"),
    col("sent.user_id_sender").alias("sent_user_id_sender"),
    col("accepted.user_id_receiver").alias("accepted_user_id_receiver")
)

# Aggregate by request_date to calculate acceptance rate
result_df = joined_df.groupBy("request_date").agg(
    count("accepted_user_id_receiver").alias("accepted_count"),
    count("sent_user_id_sender").alias("sent_count")
).withColumn(
    "percentage_acceptance",
    col("accepted_count") / col("sent_count")
)

# Sort the results by request_date and select required columns
output_df = result_df.select("request_date", "percentage_acceptance").orderBy("request_date")

# Convert to Pandas DataFrame
output_pd = output_df.toPandas()