import pandas as pd
import pyodbc

csv_path = r"C:\Users\user\Documents\2026\FYP\email_clean.csv"

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=.\SQLEXPRESS;"
    "DATABASE=InsiderThreatDB;"
    "Trusted_Connection=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

chunksize = 10000

for chunk in pd.read_csv(csv_path, chunksize=chunksize):

    # 1️⃣ Map CSV → SQL columns
    chunk["event_id"] = chunk["email_id"]
    chunk["event_time"] = pd.to_datetime(chunk["timestamp"])
    chunk["recipients_count"] = (
        chunk["to_count"].fillna(0)
        + chunk["cc_count"].fillna(0)
        + chunk["bcc_count"].fillna(0)
    )
    chunk["attachment_count"] = chunk["has_attachment"].astype(int)
    chunk["email_size"] = chunk["email_length"]

    # 2️⃣ Keep ONLY what SQL needs
    chunk = chunk[
        [
            "event_id",
            "event_time",
            "user_id",
            "pc",
            "recipients_count",
            "attachment_count",
            "email_size",
        ]
    ]

    # 3️⃣ Insert row by row
    for _, row in chunk.iterrows():
        cursor.execute(
            """
            INSERT INTO EmailLogs (
                event_id,
                event_time,
                user_id,
                pc,
                recipients_count,
                attachment_count,
                email_size
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            row.event_id,
            row.event_time,
            row.user_id,
            row.pc,
            int(row.recipients_count),
            int(row.attachment_count),
            int(row.email_size),
        )

    conn.commit()
    print(f"Inserted {len(chunk)} rows...")

cursor.close()
conn.close()
