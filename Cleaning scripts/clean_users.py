import pandas as pd

# Load raw data
DATA_PATH = "datasets/users.csv"
df = pd.read_csv(DATA_PATH)

# -----------------------------
# 1. Standardize text columns
# -----------------------------
df['email'] = df['email'].str.lower().str.strip()
df['role'] = df['role'].str.strip()

# -----------------------------
# 2. Handle missing values
# -----------------------------
df['projects'] = df['projects'].fillna('None')

# -----------------------------
# 3. Convert dates
# -----------------------------
df['start_date'] = pd.to_datetime(df['start_date'], dayfirst=True)
df['end_date'] = pd.to_datetime(df['end_date'], dayfirst=True)

# -----------------------------
# 4. Create useful features
# -----------------------------
df['employment_duration_days'] = (df['end_date'] - df['start_date']).dt.days
df['is_active'] = df['end_date'].isna()

# -----------------------------
# 5. Split coded columns
# -----------------------------
def split_code(col):
    return df[col].str.split(' - ', expand=True)

df[['functional_unit_id', 'functional_unit_name']] = split_code('functional_unit')
df[['department_id', 'department_name']] = split_code('department')
df[['team_id', 'team_name']] = split_code('team')

# -----------------------------
# 6. Drop noisy columns
# -----------------------------
df = df.drop(columns=[
    'employee_name',
    'functional_unit',
    'department',
    'team'
])

# -----------------------------
# 7. Save cleaned data
# -----------------------------
df.to_csv("users_clean.csv", index=False)

print("✅ users_clean.csv created successfully")
print(df.head())
