from modules.analytics import load_master, headcount, attrition_rate, avg_salary, gender_mix

df = load_master()
print("Headcount:", headcount(df))
print("Attrition rate:", attrition_rate(df))
print("Average Salary:", avg_salary(df))
print("Gender Mix:", gender_mix(df))
