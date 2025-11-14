from pyspark.sql import functions as F

db_employee_pivot = (
    db_employee.alias('de')
    .join(db_dept.alias('dd'), F.col('de.department_id') == F.col('dd.id'), 'inner')
    .filter(F.col('dd.department').isin(['marketing', 'engineering']))
    .groupBy()  # empty groupBy since we want a single row
    .pivot("dd.department")  # pivot on department name
    .agg(F.max("de.salary"))  # take max salary per department
    .withColumn('salary_difference', F.abs(F.col("engineering") - F.col("marketing")))
    .select('salary_difference')
)

result_pd = db_employee_pivot.toPandas()