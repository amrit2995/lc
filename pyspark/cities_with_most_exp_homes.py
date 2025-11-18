import pyspark.sql.functions as F

df_city = zillow_transactions.groupby('city').agg(F.mean('mkt_price').alias('avg_price_by_city'))
df_avg_price = zillow_transactions.select(F.mean('mkt_price')).first()[0]
df1 = df_city.filter(df_city['avg_price_by_city'] > df_avg_price).sort('city')
result = df1.select('city').toPandas()
result