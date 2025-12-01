#!/usr/bin/env python3
"""
show_rads.py
Print radiologist users from the local brain_etl.db
"""
import sqlite3
import os

p = r'c:\\Users\\jp74h\\Downloads\\DS5110\\Brain_Tumor_Detection\\MyApp\\brain_etl.db'
if not os.path.exists(p):
    print(f"Database not found: {p}")
    raise SystemExit(1)

conn = sqlite3.connect(p)
cur = conn.execute("SELECT username, role, patient_id, created_on FROM users WHERE role = 'radiologist' ORDER BY username;")
rows = cur.fetchall()
if not rows:
    print("No radiologist users found.")
else:
    for r in rows:
        print(r)
conn.close()
