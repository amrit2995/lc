SELECT a.title,
       a.budget,
       CEILING((a.end_date - a.start_date) * (SUM(c.salary) / 365)) AS prorated_employee_expense
FROM linkedin_projects a
INNER JOIN linkedin_emp_projects b ON a.id = b.project_id
INNER JOIN linkedin_employees c ON b.emp_id = c.id
GROUP BY a.title,
         a.budget,
         a.end_date,
         a.start_date
HAVING CEILING((a.end_date - a.start_date) * (SUM(c.salary) / 365)) > a.budget
ORDER BY a.title ASC;