import pyspark.sql.functions as F
from pyspark.sql import Window

df = linkedin_projects.join(linkedin_emp_projects, linkedin_projects.id == linkedin_emp_projects.project_id, "inner") \
    .join(linkedin_employees, linkedin_emp_projects.emp_id == linkedin_employees.id, "inner")

df = df.withColumn("project_duration", (F.to_date(df.end_date) - F.to_date(df.start_date)).cast("integer"))

df_expense = df.groupBy("title").agg(F.sum("salary").alias("expense"))
df_budget_expense = df.join(df_expense, "title", "left")

df_budget_expense = df_budget_expense.withColumn("prorated_expense", F.ceil(df_budget_expense.expense * df_budget_expense.project_duration / 365))
df_budget_expense = df_budget_expense.withColumn("budget_diff", df_budget_expense.prorated_expense - df_budget_expense.budget)

df_over_budget = df_budget_expense.filter(df_budget_expense.budget_diff > 0)

window = Window.partitionBy("title").orderBy("title")
result = df_over_budget.select("title", "budget", "prorated_expense").distinct().orderBy("title").withColumn("row_num", F.row_number().over(window)).filter(F.col("row_num") == 1).drop("row_num")

result.toPandas()