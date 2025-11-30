import sqlite3
import os

conn = sqlite3.connect('brain_etl.db')
cursor = conn.cursor()

cursor.execute('SELECT original_path, processed_path FROM mri_scans LIMIT 5')
print('Sample image paths from database:')
for row in cursor.fetchall():
    print(f'  Original: {row[0]}')
    print(f'  Processed: {row[1]}')
    print()

# Check if Training directory exists
training_dirs = [
    '../Training',
    '../../Training',
    '../../../Training'
]

print('\nChecking for Training directory:')
for dir_path in training_dirs:
    abs_path = os.path.abspath(dir_path)
    print(f'  {abs_path}: {"EXISTS" if os.path.exists(abs_path) else "NOT FOUND"}')

conn.close()
