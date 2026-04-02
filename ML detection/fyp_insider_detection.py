import pandas as pd
import pyodbc
from sklearn.ensemble import IsolationForest
import joblib

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
# Chunked loader function
# -------------------------
def load_sql_in_chunks(query, chunk_size=10000):
    chunks = []
    for chunk in pd.read_sql(query, conn, chunksize=chunk_size):
        chunks.append(chunk)
    return pd.concat(chunks, ignore_index=True)

# -------------------------
# Queries (with casts to prevent overflow)
# -------------------------

# EmailLogs
email_query = """
SELECT
    user_id,
    AVG(CAST(ISNULL(email_size,0) AS FLOAT)) AS avg_email_size,
    SUM(CAST(ISNULL(attachment_count,0) AS BIGINT)) AS total_attachments,
    AVG(CAST(ISNULL(recipients_count,0) AS FLOAT)) AS avg_recipients
FROM [EmailLogs]
GROUP BY user_id
"""

# File
file_query = """
SELECT
    user_id,
    COUNT(*) AS total_file_actions,
    SUM(CAST(ISNULL(to_removable_media,0) AS BIGINT)) AS total_to_rem,
    SUM(CAST(ISNULL(from_removable_media,0) AS BIGINT)) AS total_from_rem,
    SUM(CAST(ISNULL(uses_removable_media,0) AS BIGINT)) AS total_uses_rem,
    AVG(CAST(ISNULL(content_length,0) AS FLOAT)) AS avg_file_size
FROM [File]
GROUP BY user_id
"""

# Device
device_query = """
SELECT
    user_id,
    COUNT(*) AS total_device_actions,
    SUM(CAST(ISNULL(is_connected,0) AS BIGINT)) AS connected_count
FROM [Device]
GROUP BY user_id
"""

# Logon
logon_query = """
SELECT
    user_id,
    COUNT(*) AS total_logons
FROM [Logon]
GROUP BY user_id
"""

# Decoy_file
decoy_query = """
SELECT
    device_id,
    COUNT(*) AS total_decoy_accesses
FROM [Decoy_file]
GROUP BY device_id
"""

# Psychometric
psychometric_query = """
SELECT
    user_id,
    o, c, e, a, n
FROM [Psychometric]
"""

# Users metadata
users_query = """
SELECT
    user_id,
    email,
    role,
    projects,
    business_unit,
    supervisor,
    start_date,
    end_date,
    employment_duration_days,
    is_active,
    functional_unit_id,
    functional_unit_name,
    department_id,
    department_name,
    team_id,
    team_name
FROM [Users]
"""

# -------------------------
# Load data
# -------------------------
email_df = load_sql_in_chunks(email_query)
file_df = load_sql_in_chunks(file_query)
device_df = load_sql_in_chunks(device_query)
logon_df = load_sql_in_chunks(logon_query)
decoy_df = load_sql_in_chunks(decoy_query)
psychometric_df = load_sql_in_chunks(psychometric_query)
users_df = load_sql_in_chunks(users_query)

# -------------------------
# Merge features
# -------------------------
# Merge email, file, device, logon by user_id
user_df = email_df.merge(file_df, on='user_id', how='outer') \
                  .merge(device_df, on='user_id', how='outer') \
                  .merge(logon_df, on='user_id', how='outer') \
                  .fillna(0)  # Fill missing values

# Merge psychometric
user_df = user_df.merge(psychometric_df, on='user_id', how='left').fillna(0)

# Merge user metadata
user_df = user_df.merge(users_df, on='user_id', how='left').fillna(0)

# -------------------------
# Features for Isolation Forest
# -------------------------
feature_cols = [
    'avg_email_size', 'total_attachments', 'avg_recipients',
    'total_file_actions', 'total_to_rem', 'total_from_rem', 'total_uses_rem', 'avg_file_size',
    'total_device_actions', 'connected_count', 'total_logons',
    'o', 'c', 'e', 'a', 'n'
]

X = user_df[feature_cols]

# -------------------------
# Isolation Forest
# -------------------------
clf = IsolationForest(
    n_estimators=100,
    max_samples='auto',
    contamination=0.05,
    random_state=42
)
user_df['anomaly'] = clf.fit_predict(X)
user_df['anomaly'] = user_df['anomaly'].replace({1: 'normal', -1: 'anomaly'})

# -------------------------
# Save results
# -------------------------
user_df.to_csv('user_anomalies.csv', index=False)
joblib.dump(clf, 'isolation_forest_model.joblib')

print("✅ User anomalies saved to user_anomalies.csv")
print("✅ Isolation Forest model saved to isolation_forest_model.joblib")
print(user_df.head())