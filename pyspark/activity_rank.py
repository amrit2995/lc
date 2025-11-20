import pyspark.sql.functions as F
from pyspark.sql.window import Window

google_gmail_emails_fixed = (
    google_gmail_emails
    .withColumnRenamed("from_user", "user_id")
    .groupby('user_id').agg(F.count('*').alias('total_emails'))
    .withColumn("activity_rank", F.row_number().over(Window.orderBy(F.desc("total_emails"), F.col("user_id"))))
    .orderBy(F.desc("total_emails"), F.col("user_id"))
)

google_gmail_emails_fixed.toPandas()
