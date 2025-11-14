# Import your libraries
from pyspark.sql import functions as F, DataFrame

# Start writing code
spotify_worldwide_daily_song_ranking = (
    spotify_worldwide_daily_song_ranking
    .groupBy(F.col("artist")).agg(F.count('*').alias('freq'))
    .orderBy(F.desc('freq'))
    )

# To validate your solution, convert your final pySpark df to a pandas df
spotify_worldwide_daily_song_ranking.toPandas()