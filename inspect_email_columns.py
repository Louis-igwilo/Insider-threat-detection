import pandas as pd

EMAIL_ZIP_PATH = "datasets/email.csv.zip"

df = pd.read_csv(
    EMAIL_ZIP_PATH,
    compression="zip",
    nrows=5
)

print("Columns in email.csv:")
for col in df.columns:
    print("-", col)
