import sqlite3, os, mimetypes
db_path = os.path.join(os.path.dirname(__file__), 'brain_etl.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute('SELECT rowid, original_path, processed_path, label FROM mri_scans LIMIT 5')
rows = cur.fetchall()
for r in rows:
    rid, orig, proc, label = r
    print('\nRow', rid)
    print(' original:', orig)
    print(' processed:', proc)
    possible = [orig, proc, (orig or '').replace('/content/',''), (proc or '').replace('/content/','')]
    possible += [os.path.join('static','training_images', os.path.basename(orig or '')),
                 os.path.join('static','training_images', os.path.basename(proc or ''))]
    found = None
    for p in possible:
        if p and os.path.exists(p):
            found = p
            break
    if not found:
        # search training_images and top-level training_images
        candidates = [os.path.join(os.path.dirname(__file__), 'static', 'training_images'), os.path.join(os.path.dirname(__file__), 'training_images')]
        for c in candidates:
            if os.path.isdir(c):
                for dp, dn, files in os.walk(c):
                    for fname in files:
                        if fname.lower() == os.path.basename(orig).lower():
                            found = os.path.join(dp, fname)
                            break
                    if found: break
            if found: break
    print(' found:', found)
    if found:
        print(' mimetype:', mimetypes.guess_type(found)[0])
conn.close()
