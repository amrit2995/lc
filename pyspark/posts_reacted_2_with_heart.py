import pyspark.sql.functions as F

heart = facebook_reactions.filter(F.col('reaction') == 'heart').select('post_id')
result = heart.join(facebook_posts, on='post_id').dropDuplicates(['post_id'])
result.toPandas()