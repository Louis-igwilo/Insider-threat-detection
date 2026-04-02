import pandas as pd
import pyodbc
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# -------------------------
# Database connection
# -------------------------
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=InsiderThreatDB;"
    "Trusted_Connection=yes;"
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# -------------------------
# Cleaning and insert function
# -------------------------
def clean_and_insert_csv(csv_path):
    print(f"Processing CSV: {csv_path}")
    chunksize = 10000
    for chunk in pd.read_csv(csv_path, chunksize=chunksize):
        # Map CSV → SQL columns
        chunk["event_id"] = chunk["email_id"]
        chunk["event_time"] = pd.to_datetime(chunk["timestamp"])
        chunk["recipients_count"] = (
            chunk["to_count"].fillna(0)
            + chunk["cc_count"].fillna(0)
            + chunk["bcc_count"].fillna(0)
        )
        chunk["attachment_count"] = chunk["has_attachment"].astype(int)
        chunk["email_size"] = chunk["email_length"]

        # Keep only required columns
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

        # Batch insert using executemany
        records = [
            (
                row.event_id,
                row.event_time,
                row.user_id,
                row.pc,
                int(row.recipients_count),
                int(row.attachment_count),
                int(row.email_size)
            )
            for _, row in chunk.iterrows()
        ]

        cursor.executemany("""
            INSERT INTO EmailLogs (
                event_id,
                event_time,
                user_id,
                pc,
                recipients_count,
                attachment_count,
                email_size
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, records)

        conn.commit()
        print(f"Inserted {len(chunk)} rows from chunk...")

    print(f"Finished processing: {csv_path}")

# -------------------------
# Watch folder for new CSVs
# -------------------------
class CSVHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(".csv"):
            clean_and_insert_csv(event.src_path)

folder_to_watch = r"C:\FYP\incoming_csvs"  # <-- put new CSVs here
observer = Observer()
observer.schedule(CSVHandler(), folder_to_watch, recursive=False)
observer.start()
print(f"Watching folder for new CSVs: {folder_to_watch}")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()

cursor.close()
conn.close()