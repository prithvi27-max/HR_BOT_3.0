import pandas as pd
from sqlalchemy import create_engine

# 🔹 1. Load CSV file
df = pd.read_csv("data/hr_master_10000.csv")

print("Rows in CSV:", len(df))
print(df.head())

# 🔹 2. MySQL connection (local instance, no password)
engine = create_engine(
    "mysql+mysqlconnector://root:mysql123@localhost/hr_analytics_db"
)

# 🔹 3. Load data into MySQL
df.to_sql(
    name="hr_master",
    con=engine,
    if_exists="replace",
    index=False
)

print("✅ Data successfully loaded into MySQL (hr_master table)")
