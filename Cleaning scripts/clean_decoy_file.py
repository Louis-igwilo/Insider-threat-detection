import pandas as pd

# -----------------------------
# 1. Load zipped decoy file dataset
# -----------------------------
DATA_PATH = "datasets/decoy_file.csv.zip"
df = pd.read_csv(DATA_PATH, compression="zip")

# -----------------------------
# 2. Standardize column names
# -----------------------------
df.columns = df.columns.str.strip().str.lower()
df.rename(columns={'pc': 'device_id'}, inplace=True)

# -----------------------------
# 3. Trim whitespace
# -----------------------------
df['decoy_filename'] = df['decoy_filename'].str.strip()
df['device_id'] = df['device_id'].str.strip()

# -----------------------------
# 4. Remove duplicates
# -----------------------------
df.drop_duplicates(inplace=True)

# -----------------------------
# 5. Optional: extract file extensions
# -----------------------------
df['file_extension'] = df['decoy_filename'].str.split('.').str[-1].str.lower()

# -----------------------------
# 6. Save cleaned dataset
# -----------------------------
df.to_csv("decoy_file_clean.csv", index=False)

print("✅ decoy_file_clean.csv created successfully")
print(df.head())
