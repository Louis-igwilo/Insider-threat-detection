import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# -----------------------------
# Step 1: Generate synthetic dataset
# -----------------------------
np.random.seed(42)
N = 5000  # total users
features = ['avg_email_size', 'total_attachments', 'avg_recipients', 'total_file_actions',
            'total_to_rem', 'total_from_rem', 'total_uses_rem', 'avg_file_size',
            'total_device_actions', 'connected_count', 'total_logons']

# Generate normal users
df = pd.DataFrame(np.random.normal(0, 1, size=(N, len(features))), columns=features)

# Assign 10% malicious users with anomalies in certain features
malicious_indices = np.random.choice(df.index, size=int(0.1*N), replace=False)
for col in ['total_attachments', 'total_file_actions', 'total_device_actions']:
    df.loc[malicious_indices, col] += np.random.uniform(5, 10, size=len(malicious_indices))

# Add user_id
df['user_id'] = range(N)

# Rule-based synthetic alerts
df['rule_alert_count'] = 0
df.loc[malicious_indices, 'rule_alert_count'] = np.random.randint(2, 5, size=len(malicious_indices))
RULE_THRESHOLD = 2
df['rule_binary'] = (df['rule_alert_count'] >= RULE_THRESHOLD).astype(int)

# Ground truth
df['true_label'] = 0
df.loc[malicious_indices, 'true_label'] = 1

# -----------------------------
# Step 2: Train Isolation Forest
# -----------------------------
iso_forest = IsolationForest(n_estimators=200, contamination=0.1, random_state=42)
iso_forest.fit(df[features])
df['iso_score'] = iso_forest.decision_function(df[features])
df['anomaly'] = (df['iso_score'] < np.percentile(df['iso_score'], 10)).astype(int)

# Hybrid
df['hybrid'] = ((df['anomaly']==1) | (df['rule_binary']==1)).astype(int)

# -----------------------------
# Step 3: Metrics
# -----------------------------
def print_metrics(y_true, y_pred, name="Model"):
    print(f"--- {name} ---")
    print(f"Accuracy: {accuracy_score(y_true, y_pred)*100:.2f}%")
    print(f"Precision: {precision_score(y_true, y_pred)*100:.2f}%")
    print(f"Recall: {recall_score(y_true, y_pred)*100:.2f}%")
    print(f"F1 Score: {f1_score(y_true, y_pred)*100:.2f}%\n")

print_metrics(df['true_label'], df['anomaly'], name="Isolation Forest Only")
print_metrics(df['true_label'], df['rule_binary'], name="Rule-Based Only")
print_metrics(df['true_label'], df['hybrid'], name="Hybrid (Rule + Isolation Forest)")

# -----------------------------
# Step 4: Save CSV
# -----------------------------
df.to_csv("user_risks_synthetic_final.csv", index=False)
print("✅ Metrics calculated and synthetic CSV saved.")