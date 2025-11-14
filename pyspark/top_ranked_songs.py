from pyspark.sql import functions as F, DataFrame


spotify_worldwide_daily_song_ranking = (
    spotify_worldwide_daily_song_ranking
    .filter(F.col('position') == 1)
    .groupBy('trackname').agg(F.count('*').alias('times_top1'))
    .orderBy(F.desc('times_top1'))
    )


spotify_worldwide_daily_song_ranking.toPandas()