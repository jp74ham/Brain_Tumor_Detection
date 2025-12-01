import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'brain_etl.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all records
cursor.execute('SELECT rowid, original_path FROM mri_scans')
records = cursor.fetchall()

for rowid, path in records:
    # Extract filename from Colab path
    filename = os.path.basename(path)
    
    # Determine tumor type from path
    if 'glioma_tumor' in path:
        tumor_type = 'glioma_tumor'
    elif 'meningioma_tumor' in path:
        tumor_type = 'meningioma_tumor'
    elif 'pituitary_tumor' in path:
        tumor_type = 'pituitary_tumor'
    else:
        tumor_type = 'no_tumor'
    
    # Create new local path
    new_path = f'static/training_images/{tumor_type}/{filename}'
    
    # Update database
    cursor.execute('UPDATE mri_scans SET original_path = ? WHERE rowid = ?', 
                   (new_path, rowid))

conn.commit()
conn.close()
print("Database paths updated!")