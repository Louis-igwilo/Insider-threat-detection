import pandas as pd

# -----------------------------
# 1. Load zipped dataset
# -----------------------------
DATA_PATH = "datasets/device.csv.zip"
df = pd.read_csv(DATA_PATH, compression="zip")

# -----------------------------
# 2. Rename columns for consistency
# -----------------------------
df.rename(columns={
    'id': 'event_id',
    'date': 'timestamp',
    'user': 'user_id',
    'pc': 'device_id'
}, inplace=True)

# -----------------------------
# 3. Parse mixed datetime formats
# -----------------------------
df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed', errors='coerce')

# -----------------------------
# 4. Standardize activity
# -----------------------------
df['activity'] = df['activity'].str.strip().str.lower()
df['activity'] = df['activity'].replace({
    'connect': 'connect',
    'disconnect': 'disconnect'
})

# -----------------------------
# 5. Handle file_tree
# -----------------------------
# Split file_tree paths into a list for analysis
df['file_tree_paths'] = df['file_tree'].fillna('').str.split(';')

# Count number of paths accessed in this event
df['file_tree_count'] = df['file_tree_paths'].apply(lambda x: 0 if x == [''] else len(x))


# -----------------------------
# 6. Remove duplicates
# -----------------------------
df.drop_duplicates(subset=[c for c in df.columns if c != 'file_tree_paths'], inplace=True)


# -----------------------------
# 7. Optional: Flag if device is active during this event
# -----------------------------
df['is_connected'] = df['activity'] == 'connect'

# -----------------------------
# 8. Reorder columns
# -----------------------------
cols_order = [
    'event_id',
    'timestamp',
    'user_id',
    'device_id',
    'activity',
    'is_connected',
    'file_tree',
    'file_tree_paths',
    'file_tree_count'
]
df = df[[c for c in cols_order if c in df.columns]]

# -----------------------------
# 9. Save cleaned device dataset
# -----------------------------
df.to_csv("device_clean.csv", index=False)

print("✅ device_clean.csv created successfully")
print(df.head())
