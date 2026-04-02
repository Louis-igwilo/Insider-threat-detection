import pandas as pd
import joblib
import shap

# =========================
# LOAD DATA
# =========================
df = pd.read_csv("user_risk_scores.csv")

print("✅ Data Loaded:", df.shape)

# =========================
# SELECT CORRECT FEATURES
# =========================
feature_cols = [
    'avg_email_size',
    'total_attachments',
    'avg_recipients',
    'total_file_actions',
    'total_to_rem',
    'total_from_rem',
    'total_uses_rem',
    'avg_file_size',
    'total_device_actions',
    'connected_count',
    'total_logons',
    'o', 'c', 'e', 'a', 'n',
    'employment_duration_days'
]

X = df[feature_cols]

print("✅ Features ready")

# =========================
# LOAD MODEL (NO RETRAINING)
# =========================
model = joblib.load("isolation_forest_model.pkl")

print("✅ Model Loaded")

# =========================
# PREDICT (ONLY IF NEEDED)
# =========================
if "anomaly_label" not in df.columns:
    df["anomaly_label"] = df["anomaly"].map({1:0, -1:1})

print("✅ Predictions ready")

# =========================
# SHAP (EXPLAINABILITY)
# =========================
explainer = shap.Explainer(model, X)
shap_values = explainer(X)

shap.summary_plot(shap_values, X)

print("✅ SHAP Done")

# =========================
# SAVE FINAL OUTPUT
# =========================
df.to_csv("FINAL_insider_results.csv", index=False)

print("✅ FINAL OUTPUT SAVED")