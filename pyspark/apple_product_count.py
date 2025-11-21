from pyspark.sql import functions as F

final_metrics = (
    playbook_events.alias('pe')
    .join(
        playbook_users.alias('pu'),
        F.col('pe.user_id') == F.col('pu.user_id')
    )
    .groupBy(F.col('pu.language'))
    .agg(
        # count distinct ONLY for selected devices
        F.countDistinct(
            F.when(
                F.col('device').isin(["macbook pro", "iphone 5s", "ipad air"]),
                F.col('pe.user_id')
            )
        ).alias("a_users"),

        # total distinct users
        F.countDistinct("pu.user_id").alias("t_users")
    )
)

final_metrics.toPandas()
