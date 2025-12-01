import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'brain_etl.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('Tables:', tables)

# Get mri_scans structure
cursor.execute('PRAGMA table_info(mri_scans)')
print('\nmri_scans columns:')
for row in cursor.fetchall():
    print(f"  {row[1]} ({row[2]})")

# Get sample data
cursor.execute('SELECT * FROM mri_scans LIMIT 3')
columns = [description[0] for description in cursor.description]
print('\nSample data (first 3 rows):')
print('Columns:', columns)
for row in cursor.fetchall():
    print(row)

# Get distinct patient_ids
cursor.execute('SELECT DISTINCT patient_id FROM mri_scans LIMIT 5')
print('\nSample patient IDs:')
for row in cursor.fetchall():
    print(f"  {row[0]}")

conn.close()