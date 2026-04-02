Ximport pandas as pd
import pyodbc
from sklearn.ensemble import IsolationForest

# -------------------------
# Database connection
# -------------------------
conn_str = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost\\SQLEXPRESS;'
    'DATABASE=InsiderThreatDB;'
    'Trusted_Connection=yes;'
)
conn = pyodbc.connect(conn_str)

# -------------------------
# SQL Queries (pre-aggregated)
# -------------------------
email_query = """
SELECT
    user_id,
    COUNT_BIG(*) AS total_emails,
    SUM(CAST(COALESCE(attachment_count, 0) AS BIGINT)) AS total_attachments,
    AVG(CAST(COALESCE(email_size, 0) AS FLOAT)) AS avg_email_size,
    MAX(CAST(COALESCE(recipients_count, 0) AS INT)) AS max_recipients
FROM EmailLogs
GROUP BY user_id
"""


file_query = """
SELECT
    user_id,
    COUNT(*) AS total_file_actions,
    SUM(CAST(to_removable_media AS BIGINT)) AS total_to_rem,
    SUM(CAST(from_removable_media AS BIGINT)) AS total_from_rem,
    SUM(CAST(uses_removable_media AS BIGINT)) AS total_uses_rem,
    AVG(CAST(content_length AS FLOAT)) AS avg_file_size
FROM [File]
GROUP BY user_id
"""

device_query = """
SELECT
    user_id,
    COUNT(*) AS total_device_actions
FROM Device
GROUP BY user_id
"""

logon_query = """
SELECT
    user_id,
    COUNT(*) AS total_logons
FROM Logon
GROUP BY user_id
"""

# -------------------------
# Load data into pandas
# -------------------------
email_df = pd.read_sql(email_query, conn)
file_df = pd.read_sql(file_query, conn)
device_df = pd.read_sql(device_query, conn)
logon_df = pd.read_sql(logon_query, conn)

# -------------------------
# Merge all features
# -------------------------
user_df = email_df.merge(file_df, on='user_id', how='outer') \
                  .merge(device_df, on='user_id', how='outer') \
                  .merge(logon_df, on='user_id', how='outer') \
                  .fillna(0)  # Fill missing values

# -------------------------
# Features for model
# -------------------------
feature_cols = [
    'total_emails', 'total_attachments', 'avg_email_size', 'max_recipients',
    'total_file_actions', 'total_to_rem', 'total_from_rem', 'total_uses_rem', 'avg_file_size',
    'total_device_actions', 'total_logons'
]

X = user_df[feature_cols]

# -------------------------
# Isolation Forest
# -------------------------
clf = IsolationForest(
    n_estimators=50,       # Fewer trees for faster processing
    max_samples='auto',    # Sample from the dataset
    contamination=0.05,    # Adjust based on expected anomaly ratio
    random_state=42
)
user_df['anomaly'] = clf.fit_predict(X)
user_df['anomaly'] = user_df['anomaly'].replace({1: 'normal', -1: 'anomaly'})

# -------------------------
# Save results
# -------------------------
user_df.to_csv('user_anomalies.csv', index=False)
print("User anomalies saved to user_anomalies.csv")
print(user_df.head())
