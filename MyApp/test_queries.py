import sqlite3

conn = sqlite3.connect('brain_etl.db')
cursor = conn.cursor()

# Test patient query
print("Testing patient portal query for patient 8270:")
cursor.execute("""
    SELECT patient_id, label, age, gender, hospital_unit, scan_date, 
           orig_width, orig_height, proc_width, proc_height, 
           mean_pixel, std_pixel
    FROM mri_scans 
    WHERE patient_id = 8270 
    ORDER BY scan_date DESC
    LIMIT 3
""")

for row in cursor.fetchall():
    print(f"  Patient: {row[0]}, Label: {row[1]}, Age: {row[2]}, Gender: {row[3]}")
    print(f"    Hospital: {row[4]}, Scan Date: {row[5]}")
    print(f"    Original: {row[6]}x{row[7]}, Processed: {row[8]}x{row[9]}")
    print(f"    Mean Pixel: {row[10]:.4f}, Std: {row[11]:.4f}")
    print()

# Test admin query - total cases by tumor type
print("\nTesting admin query - Total cases by tumor type:")
cursor.execute("""
    SELECT label, COUNT(*) as count
    FROM mri_scans
    GROUP BY label
    ORDER BY count DESC
""")

for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} cases")

conn.close()
print("\n✓ All queries work correctly with brain_etl.db!")
