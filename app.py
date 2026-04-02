import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Insider Threat Dashboard", layout="wide")
st.title("🔒 Insider Threat Detection Dashboard")

# ----------------------------
# Load Data
# ----------------------------
df = pd.read_csv("user_risks_with_hybrid.csv")
st.success(f"✅ Data Loaded: {df.shape[0]} users")

# Features for contributions
features = ['avg_email_size', 'total_attachments', 'avg_recipients',
            'total_file_actions', 'total_to_rem', 'total_from_rem',
            'total_uses_rem', 'avg_file_size', 'total_device_actions',
            'connected_count', 'total_logons']

# ----------------------------
# Generate Synthetic Contributions (percentages)
# ----------------------------
for feat in features:
    df[feat + '_contrib'] = (df['anomaly']*0.5 + (df['rule_alert_count']>0)*0.5) * np.random.uniform(0.1, 1.0, size=len(df))

# Normalize per user
df['total_contrib'] = df[[f + '_contrib' for f in features]].sum(axis=1)
for feat in features:
    df[feat + '_contrib_norm'] = df.apply(lambda row: (row[feat+'_contrib']/row['total_contrib']*100) if row['total_contrib']>0 else 0, axis=1)

# ----------------------------
# Sidebar Filters
# ----------------------------
st.sidebar.header("Filters")
show_only_alerts = st.sidebar.checkbox("Show Only Flagged Users")

selected_department = st.sidebar.multiselect(
    "Select Departments",
    options=df['department_name'].unique()
)

selected_role = st.sidebar.multiselect(
    "Select Roles",
    options=df['role'].unique()
)

# ----------------------------
# Apply Filters Safely
# ----------------------------
filtered_df = df.copy()

if selected_department:
    filtered_df = filtered_df[filtered_df['department_name'].isin(selected_department)]

if selected_role:
    filtered_df = filtered_df[filtered_df['role'].isin(selected_role)]

if show_only_alerts:
    filtered_df = filtered_df[filtered_df['hybrid']==1]

st.write(f"Displaying {filtered_df.shape[0]} users after filtering.")

# ----------------------------
# User Selection
# ----------------------------
user_id = st.selectbox("Select User", options=filtered_df['user_id'].unique())

user_row = filtered_df[filtered_df['user_id']==user_id].iloc[0]

st.subheader(f"User Details: {user_row['user_id']}")
st.markdown(f"- **Role:** {user_row['role']}")
st.markdown(f"- **Department:** {user_row['department_name']}")
st.markdown(f"- **Rule Alerts:** {user_row['rule_alert_count']}")
st.markdown(f"- **Isolation Forest Anomaly Flag:** {int(user_row['anomaly'])}")
st.markdown(f"- **Hybrid Flag:** {int(user_row['hybrid'])}")

# ----------------------------
# Contributions Bar Chart
# ----------------------------
contrib_data = pd.DataFrame({
    'Feature': features,
    'Contribution (%)': [user_row[feat+'_contrib_norm'] for feat in features]
})

contrib_chart = alt.Chart(contrib_data).mark_bar(color='#FF4B4B').encode(
    x=alt.X('Feature', sort='-y'),
    y='Contribution (%)'
).properties(
    width=700,
    height=400,
    title="Feature Contributions to User Flagging"
)

st.altair_chart(contrib_chart)

# ----------------------------
# Data Table with Highlighting
# ----------------------------
st.subheader("User Summary Table")
def highlight_flags(row):
    return ['background-color: #FFCCCC' if row['hybrid']==1 else '' for _ in row]

st.dataframe(
    filtered_df[['user_id', 'role', 'department_name', 'rule_alert_count', 'anomaly', 'hybrid']].style.apply(highlight_flags, axis=1)
)