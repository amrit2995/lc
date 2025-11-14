from pyspark.sql import Functions as F, DataFrame

customers = DataFrame()

filtered_customer_df = customers.filter(customers.first_name.isin(['Jill', 'Eva']))