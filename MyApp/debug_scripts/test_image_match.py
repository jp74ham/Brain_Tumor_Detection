import sqlite3, os

db_path = os.path.join(os.path.dirname(__file__), 'brain_etl.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute('SELECT rowid, original_path, processed_path FROM mri_scans LIMIT 10')
rows = cur.fetchall()

base = os.path.abspath('training_images')
print('training_images dir:', base, 'exists=', os.path.isdir(base))

if not os.path.isdir(base):
    print('No training_images here; aborting')
else:
    # build fileset
    fileset = set()
    for dp, dn, files in os.walk(base):
        for f in files:
            fileset.add(f)
    for r in rows:
        rid = r[0]
        b1 = os.path.basename(r[1]) if r[1] else ''
        b2 = os.path.basename(r[2]) if r[2] else ''
        print('\nrowid', rid)
        print(' original basename:', b1, '->', 'FOUND' if b1 in fileset else 'MISSING')
        print(' processed basename:', b2, '->', 'FOUND' if b2 in fileset else 'MISSING')

conn.close()
