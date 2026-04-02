import pandas as pd

# -----------------------------
# 1. Load dataset
# -----------------------------
DATA_PATH = "datasets/psychometric.csv"
df = pd.read_csv(DATA_PATH)

# -----------------------------
# 2. Standardize column names
# -----------------------------
df.columns = df.columns.str.strip().str.lower()  # lowercase for all columns

# -----------------------------
# 3. Drop unnecessary columns (optional)
# -----------------------------
if 'employee_name' in df.columns:
    df = df.drop(columns=['employee_name'])

# -----------------------------
# 4. Ensure numeric columns are numeric
# -----------------------------
ocean_cols = ['o', 'c', 'e', 'a', 'n']
for col in ocean_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')  # converts invalid values to NaN

# -----------------------------
# 5. Handle missing values
# -----------------------------
df[ocean_cols] = df[ocean_cols].fillna(0)  # fill missing scores with 0 (or choose another strategy)

# -----------------------------
# 6. Save cleaned dataset
# -----------------------------
df.to_csv("psychometric_clean.csv", index=False)

print("✅ psychometric_clean.csv created successfully")
print(df.head())
