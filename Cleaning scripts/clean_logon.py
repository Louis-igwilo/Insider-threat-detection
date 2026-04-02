import pandas as pd

# -----------------------------
# 1. Load zipped logon dataset
# -----------------------------
DATA_PATH = "datasets/logon.csv.zip"
df = pd.read_csv(DATA_PATH, compression="zip")

# -----------------------------
# 2. Rename columns
# -----------------------------
df.rename(columns={
    'id': 'event_id',
    'date': 'timestamp',
    'user': 'user_id',
    'pc': 'device_id'
}, inplace=True)

# -----------------------------
# 3. Parse timestamps
# -----------------------------
df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed', errors='coerce')

# -----------------------------
# 4. Normalize activity
# -----------------------------
df['activity'] = df['activity'].str.strip().str.lower()
df['activity'] = df['activity'].replace({
    'logon': 'logon',
    'logoff': 'logoff'
})

# -----------------------------
# 5. Create derived feature: is_logged_on
# -----------------------------
df['is_logged_on'] = df['activity'] == 'logon'

# -----------------------------
# 6. Remove duplicates
# -----------------------------
df.drop_duplicates(inplace=True)

# -----------------------------
# 7. Reorder columns
# -----------------------------
cols_order = ['event_id', 'timestamp', 'user_id', 'device_id', 'activity', 'is_logged_on']
df = df[[c for c in cols_order if c in df.columns]]

# -----------------------------
# 8. Save cleaned dataset
# -----------------------------
df.to_csv("logon_clean.csv", index=False)

print("✅ logon_clean.csv created successfully")
print(df.head())
