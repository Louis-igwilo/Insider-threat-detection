import pandas as pd

EMAIL_ZIP_PATH = "datasets/email.csv.zip"

# Read only first 10 rows from zipped CSV
df = pd.read_csv(
    EMAIL_ZIP_PATH,
    compression="zip",
    nrows=10
)

print("First 10 rows:")
print(df)

print("\nColumn names:")
print(list(df.columns))

