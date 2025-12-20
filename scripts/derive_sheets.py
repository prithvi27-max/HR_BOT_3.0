import pandas as pd

df = pd.read_csv("data/hr_master_10000.csv")

# 1️⃣ EMPLOYEES MASTER (Core Workforce)
employees = df[[
    "Employee_ID", "Gender", "Age", "Department", "Job_Level",
    "Hire_Date", "Termination_Date", "Status", "Location"
]]
employees.to_csv("data/employees_master.csv", index=False)

# 2️⃣ ATTRITION TABLE
attrition = df[df["Status"] == "Resigned"][[
    "Employee_ID", "Department", "Location", "Termination_Date", "Experience_Years"
]]
attrition.rename(columns={"Termination_Date": "Exit_Date"}, inplace=True)
attrition.to_csv("data/attrition.csv", index=False)

# 3️⃣ COMPENSATION TABLE
compensation = df[[
    "Employee_ID", "Department", "Salary", "Job_Level", "Location"
]]
compensation.to_csv("data/compensation.csv", index=False)

# 4️⃣ PERFORMANCE TABLE
performance = df[[
    "Employee_ID", "Performance_Rating", "Last_Promotion_Year", "Job_Level", "Department"
]]
performance.to_csv("data/performance.csv", index=False)

# 5️⃣ ENGAGEMENT TABLE
engagement = df[[
    "Employee_ID", "Engagement_Score", "Department", "Location"
]]
engagement.to_csv("data/engagement.csv", index=False)

# 6️⃣ EXPERIENCE / TENURE TABLE
tenure = df[[
    "Employee_ID", "Experience_Years", "Department", "Job_Level"
]]
tenure.to_csv("data/experience.csv", index=False)

print("All derived sheets generated successfully!")
