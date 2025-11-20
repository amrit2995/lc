from pyspark.sql import functions as F

cities_population = (
    cities_population
    .withColumn('density', F.round(F.col('population')/F.col('area'), 2))
)

max_density = (
    cities_population
    .select(
        F.max('density')
        )
    ).collect()[0][0]
    
min_density = (
    cities_population
    .select(
        F.min('density')
        )
    ).collect()[0][0]

cities_population = (
    cities_population
    .filter(
        F.col('density').isin(max_density, min_density)
    )
    .select(
        'city',
        'country',
        'density'
        )
)

cities_population.toPandas()