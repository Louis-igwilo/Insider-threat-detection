import pandas as pd
import numpy as np

# Load the normal aggregated user results from your existing pipeline
df = pd.read_csv('user_anomalies.csv')

# Add label column for demo/testing
df['true_label'] = 0

# Choose 5% of users to make suspicious
num_anomalies = int(0.05 * len(df))
anomaly_indices = np.random.choice(df.index, num_anomalies, replace=False)

# Inject suspicious behaviour
for idx in anomaly_indices:
    scenario = np.random.choice([
        'mass_file_access',
        'usb_exfiltration',
        'email_leak',
        'combined_attack'
    ])

    if scenario == 'mass_file_access':
        df.at[idx, 'total_file_actions'] *= 10
        df.at[idx, 'avg_file_size'] *= 3

    elif scenario == 'usb_exfiltration':
        df.at[idx, 'connected_count'] += 5
        df.at[idx, 'total_device_actions'] += 30
        df.at[idx, 'total_to_rem'] += 100

    elif scenario == 'email_leak':
        df.at[idx, 'avg_recipients'] *= 8
        df.at[idx, 'total_attachments'] *= 5
        df.at[idx, 'avg_email_size'] *= 4

    elif scenario == 'combined_attack':
        df.at[idx, 'total_file_actions'] *= 10
        df.at[idx, 'connected_count'] += 5
        df.at[idx, 'total_device_actions'] += 30
        df.at[idx, 'avg_recipients'] *= 8
        df.at[idx, 'total_attachments'] *= 5

    df.at[idx, 'true_label'] = 1

# Save demo dataset
df.to_csv('user_anomalies_demo.csv', index=False)

print(f"Injected {num_anomalies} suspicious users into user_anomalies_demo.csv")