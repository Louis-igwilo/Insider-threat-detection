import pyodbc
import pandas as pd

# ---------------------------
# 1. Load anomaly CSV first
# ---------------------------
anomaly_path = r"C:\Users\user\Documents\2026\FYP\user_anomalies.csv"
anomalies = pd.read_csv(anomaly_path)

print("Loaded anomalies:", len(anomalies))

# ensure string type
anomalies["user_id"] = anomalies["user_id"].astype(str)

# ---------------------------
# 2. Connect to SQL Server
# ---------------------------
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=InsiderThreatDB;"
    "Trusted_Connection=yes;"
)

print("Connected to SQL Server")

# ---------------------------
# 3. Only request alerts for anomaly users
# ---------------------------
user_list = "','".join(anomalies["user_id"].unique())

query = f"""
SELECT
    user_id,
    rule_name,
    severity,
    description
FROM RuleAlerts
WHERE user_id IN ('{user_list}')
"""

alerts = pd.read_sql(query, conn)

print("Loaded filtered alerts:", len(alerts))

# ---------------------------
# 4. Aggregate alerts per user
# ---------------------------
alerts_summary = (
    alerts.groupby("user_id")
    .size()
    .reset_index(name="rule_alert_count")
)

# ---------------------------
# 5. Merge with anomaly data
# ---------------------------
merged = anomalies.merge(alerts_summary, on="user_id", how="left")

merged["rule_alert_count"] = merged["rule_alert_count"].fillna(0)

# ---------------------------
# 6. Simple Risk Score
# ---------------------------
merged["risk_score"] = merged["rule_alert_count"]

# ---------------------------
# 7. Save output
# ---------------------------
output = r"C:\Users\user\Documents\2026\FYP\user_risk_scores.csv"

merged.to_csv(output, index=False)

print("Saved risk scores ->", output)