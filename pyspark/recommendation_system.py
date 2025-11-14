from pyspark.sql import functions as F

# Step 1: Join users_friends with users_pages to get all friend page follows
user_recommendations_all = (
    users_friends.alias('uf')
    .join(
        users_pages.alias('up'),
        F.col('uf.friend_id') == F.col('up.user_id'),
        'inner'
    )
    .select(
        F.col('uf.user_id').alias('user_id'),
        F.col('up.page_id').alias('page_id')
    )
    .distinct()
)

# Step 2: Remove pages that the user already follows (NOT EXISTS)
user_final_recommendations = (
    user_recommendations_all.alias('ura')
    .join(
        users_pages.alias('up'),
        (F.col('ura.user_id') == F.col('up.user_id')) &
        (F.col('ura.page_id') == F.col('up.page_id')),
        'left_anti'   # Equivalent to SQL NOT EXISTS
    )
)

# Optional: display or convert to Pandas
user_final_recommendations.show()
