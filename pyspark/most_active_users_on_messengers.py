# Import your libraries
import pyspark
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Start writing code
sent_users = (
    fb_messages
    .groupBy('user1').agg(F.sum('msg_count').alias('sent_msg_count'))
    )
    
receiver_users = (
    fb_messages
    .groupBy('user2').agg(F.sum('msg_count').alias('received_msg_count'))
    )

user_metrics = (
    sent_users.alias('su')
    .join(
        receiver_users.alias('ru'),
        F.col('su.user1') == F.col('ru.user2'),
        'outer'
    )
    .withColumn('userm', F.coalesce(F.col('su.user1'), F.col('ru.user2')))
    .withColumn('msg_count', F.coalesce(F.col('su.sent_msg_count'), F.lit(0))+F.coalesce(F.col('ru.received_msg_count'), F.lit('0')))
    .withColumn('rank_user', F.rank().over(
        Window.orderBy(F.desc('msg_count')))
        )
    .filter(F.col('rank_user')<=F.lit('10'))
    .select(
        'userm', 'msg_count'
        )
    )


# To validate your solution, convert your final pySpark df to a pandas df
user_metrics.toPandas()