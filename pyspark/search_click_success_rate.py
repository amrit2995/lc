from pyspark.sql import functions as F
from pyspark.sql.window import Window
from datetime import timedelta

max_event_date = search_events.agg(F.max('event_timestamp')).collect()[0][0]
cutoff_date = max_event_date - timedelta(days=30)

accounts_with_segment = accounts.withColumn(
    'user_segment',
    F.when(F.col('registration_date') >= F.lit(cutoff_date), 'new').otherwise(
        'existing'
    ),
)

searches = search_events.filter(F.col('event_type') == 'search').select(
    'user_id',
    'query',
    'session_id',
    F.col('event_timestamp').alias('search_timestamp'),
)

clicks = search_events.filter(F.col('event_type') == 'click').select(
    'user_id',
    'query',
    'session_id',
    F.col('event_timestamp').alias('click_timestamp'),
)

window_spec = Window.partitionBy('user_id', 'query', 'session_id').orderBy(
    'click_timestamp'
)
clicks = clicks.withColumn('click_rank', F.row_number().over(window_spec))
first_clicks = clicks.filter(F.col('click_rank') == 1).drop('click_rank')

search_with_clicks = searches.join(
    first_clicks, on=['user_id', 'query', 'session_id'], how='left'
)

search_with_clicks = search_with_clicks.filter(
    F.col('click_timestamp').isNull()
    | (F.col('click_timestamp') >= F.col('search_timestamp'))
)

search_with_clicks = search_with_clicks.withColumn(
    'time_diff_seconds',
    F.when(
        F.col('click_timestamp').isNotNull(),
        (
            F.col('click_timestamp').cast('long')
            - F.col('search_timestamp').cast('long')
        ),
    ),
)

search_with_clicks = search_with_clicks.join(
    accounts_with_segment.select('user_id', 'user_segment'),
    on='user_id',
    how='inner',
)

search_with_clicks = search_with_clicks.withColumn(
    'is_successful',
    F.when(
        F.col('time_diff_seconds').isNotNull()
        & (F.col('time_diff_seconds') <= 30),
        1,
    ).otherwise(0),
)

result = search_with_clicks.groupBy('user_segment').agg(
    F.count('*').alias('total_searches'),
    F.sum('is_successful').alias('successful_searches'),
)

result = result.withColumn(
    'success_rate', F.col('successful_searches') / F.col('total_searches')
)

result.toPandas()