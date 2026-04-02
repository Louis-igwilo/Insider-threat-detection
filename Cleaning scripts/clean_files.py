import pandas as pd

# -----------------------------
# 1. Load zipped file dataset
# -----------------------------
DATA_PATH = "datasets/file.csv.zip"   # adjust name if needed
df = pd.read_csv(DATA_PATH, compression="zip")

# -----------------------------
# 2. Rename columns
# -----------------------------
df.rename(columns={
    'id': 'event_id',
    'date': 'timestamp',
    'pc': 'pc_id'
}, inplace=True)

df.rename(columns={'user': 'user_id'}, inplace=True)
# -----------------------------
# 3. Parse datetime
# -----------------------------
df['timestamp'] = pd.to_datetime(
    df['timestamp'],
    format='mixed',
    errors='coerce'
)

# -----------------------------
# 4. Standardize activity
# -----------------------------
df['activity'] = (
    df['activity']
    .str.lower()
    .str.replace('file ', '', regex=False)
    .str.strip()
)

# -----------------------------
# 5. Convert TRUE/FALSE to boolean
# -----------------------------
bool_cols = ['to_removable_media', 'from_removable_media']
for col in bool_cols:
    df[col] = (
        df[col]
        .astype(str)
        .str.upper()
        .map({'TRUE': True, 'FALSE': False})
    )

# -----------------------------
# 6. Extract file information
# -----------------------------
df['file_name'] = df['filename'].str.split('\\').str[-1]
df['file_ext'] = df['file_name'].str.split('.').str[-1].str.lower()
df['file_path'] = df['filename'].str.rsplit('\\', n=1).str[0]

# -----------------------------
# 7. Handle content safely
# -----------------------------
df['content_length'] = df['content'].fillna('').str.len()
df.drop(columns=['content'], inplace=True)

# -----------------------------
# 8. Security feature
# -----------------------------
df['uses_removable_media'] = (
    df['to_removable_media'] | df['from_removable_media']
)

# -----------------------------
# 9. Reorder columns
# -----------------------------
df = df[[
    'event_id',
    'user_id',         
    'pc_id',
    'file_path',
    'file_name',
    'file_ext',
    'activity',
    'to_removable_media',
    'from_removable_media',
    'uses_removable_media',
    'content_length'
]]


# -----------------------------
# 10. Save cleaned file
# -----------------------------
df.to_csv("file_clean.csv", index=False)

print("✅ file_clean.csv created successfully")
print(df.head())
