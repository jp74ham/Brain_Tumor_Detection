from flask import Flask, render_template, request, jsonify, g, session, redirect, url_for, send_file
import os
import sqlite3
from werkzeug.utils import secure_filename
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import mimetypes
import hashlib
import binascii
import secrets
import shutil
from datetime import datetime
import sys

# Optional ML dependencies (graceful fallback if unavailable)
try:
    import numpy as np
    import cv2
    CV2_AVAILABLE = True
    print("✓ OpenCV loaded successfully")
except Exception as e:
    print(f"⚠️  OpenCV not available: {e}")
    print("   App will run without model prediction support.")
    CV2_AVAILABLE = False
    np = None
    cv2 = None

try:
    from tensorflow.keras.models import load_model
    from tensorflow.keras.applications.xception import preprocess_input
    TF_AVAILABLE = True
    print("✓ TensorFlow loaded successfully")
except Exception as e:
    print(f"⚠️  TensorFlow not available: {e}")
    print("   Model prediction disabled.")
    TF_AVAILABLE = False
    load_model = None
    preprocess_input = None

MODEL_PATH = 'models/optimized_best.h5'
TUMOR_CLASSES = ['glioma_tumor', 'meningioma_tumor', 'no_tumor', 'pituitary_tumor']

tumor_model = None
if TF_AVAILABLE:
    try:
        tumor_model = load_model(MODEL_PATH)
        print(f"✓ Loaded tumor detection model from {MODEL_PATH}")
    except Exception as e:
        print(f"⚠️  Could not load model: {e}")

def predict_tumor(image_path):
    """Run actual model prediction on MRI image"""
    if not CV2_AVAILABLE or not TF_AVAILABLE:
        print("⚠️ ML dependencies unavailable, returning default")
        return 'no_tumor', 0.0
    
    if tumor_model is None:
        print("⚠️ Model not loaded, returning default")
        return 'no_tumor', 0.0
    
    try:
        # Preprocess image
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (299, 299))
        img = preprocess_input(img)
        img_batch = np.expand_dims(img, axis=0)
        
        # Run prediction
        predictions = tumor_model.predict(img_batch, verbose=0)
        class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][class_idx])
        predicted_class = TUMOR_CLASSES[class_idx]
        
        print(f"✓ Predicted: {predicted_class} with {confidence:.2%} confidence")
        return predicted_class, confidence
        
    except Exception as e:
        print(f"⚠️  Prediction error: {e}")
        return 'no_tumor', 0.0
    
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config["DATABASE"] = os.path.join(os.path.dirname(__file__), "brain_etl.db")
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')  # Use env var in production

# NOTE: we will use a `users` table in the database for authentication.
# The script `create_users_table.py` can be used to populate patient users.
DEFAULT_ADMIN_PASSWORD = 'password123'
    
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        print("Connected to the database")
    return g.db


def _hash_password(password: str, salt=None, iterations: int = 100_000):
    if salt is None:
        salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    return binascii.hexlify(dk).decode('ascii'), binascii.hexlify(salt).decode('ascii'), iterations


def _verify_password(stored_hash_hex: str, stored_salt_hex: str, iterations: int, candidate_password: str) -> bool:
    try:
        salt = binascii.unhexlify(stored_salt_hex)
        dk = hashlib.pbkdf2_hmac('sha256', candidate_password.encode('utf-8'), salt, iterations)
        return binascii.hexlify(dk).decode('ascii') == stored_hash_hex
    except Exception:
        return False


def _backup_db(db_path: str) -> str:
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    backup = f"{db_path}.bak.{ts}"
    try:
        shutil.copy2(db_path, backup)
    except Exception:
        return ''
    return backup


def ensure_users_table_and_defaults():
    """Create `users` table if missing and ensure admin + radiologist accounts exist."""
    db_path = app.config.get('DATABASE')
    if not db_path or not os.path.exists(db_path):
        return

    # backup db
    _backup_db(db_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            password_salt TEXT NOT NULL,
            iterations INTEGER NOT NULL,
            role TEXT NOT NULL,
            patient_id INTEGER,
            created_on TEXT NOT NULL
        )
    ''')

    # ensure admin user exists
    cur.execute('SELECT 1 FROM users WHERE username = ?', ('admin',))
    if not cur.fetchone():
        pwd_hash, salt_hex, iters = _hash_password(DEFAULT_ADMIN_PASSWORD)
        cur.execute('INSERT INTO users (username, password_hash, password_salt, iterations, role, patient_id, created_on) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    ('admin', pwd_hash, salt_hex, iters, 'admin', None, datetime.utcnow().isoformat()))

    # ensure radiologist users rad1..rad5 exist
    for i in range(1, 6):
        uname = f'rad{i}'
        cur.execute('SELECT 1 FROM users WHERE username = ?', (uname,))
        if not cur.fetchone():
            pwd_hash, salt_hex, iters = _hash_password('password123')
            cur.execute('INSERT INTO users (username, password_hash, password_salt, iterations, role, patient_id, created_on) VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (uname, pwd_hash, salt_hex, iters, 'radiologist', None, datetime.utcnow().isoformat()))

    conn.commit()
    conn.close()


# Ensure users table exists before first request / before serving.
# Flask 3.0+ may not provide `before_first_request`; prefer `before_serving`
# when available. Fall back to calling the initializer immediately.
if hasattr(app, 'before_first_request'):
    @app.before_first_request
    def _ensure_users_table_on_start():
        ensure_users_table_and_defaults()
elif hasattr(app, 'before_serving'):
    @app.before_serving
    def _ensure_users_table_on_start():
        ensure_users_table_and_defaults()
else:
    # Final fallback: call at import time (safe and idempotent)
    ensure_users_table_and_defaults()

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()
        
# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'mri-upload' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['mri-upload']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # TODO: Add your ML model prediction here
        # For now, returning mock data
        result = {
            'success': True,
            'filename': filename,
            'filepath': f'/static/uploads/{filename}',
            'tumor': 'Yes',
            'type': 'Glioma'
        }
        
        return jsonify(result)
    
    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/submit_patient_scan', methods=['POST'])
def submit_patient_scan():
    """Accepts multipart form with patient attributes and an MRI image file.
    Creates a patient user (username auto-generated), saves the image, inserts a mri_scans row,
    and returns patient_id and scan_id. The actual ML prediction is a separate step.
    """
    try:
        # Validate file
        if 'mri_file' not in request.files:
            return jsonify({'success': False, 'error': 'No MRI file provided'}), 400

        file = request.files['mri_file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid or missing file'}), 400

        # Read form fields
        age = request.form.get('age')
        gender = request.form.get('gender') or None
        hospital_unit = request.form.get('hospital_unit') or None

        # Save file
        filename = secure_filename(file.filename)
        ts = datetime.utcnow().strftime('%Y%m%dT%H%M%S')
        filename_on_disk = f"{ts}_{filename}"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename_on_disk)
        file.save(save_path)

        # Compute simple image stats
        try:
            img = Image.open(save_path).convert('RGB')
            orig_w, orig_h = img.size
            # basic mean/std across channels
            from PIL import ImageStat
            stat = ImageStat.Stat(img)
            mean_pixel = float(sum(stat.mean) / len(stat.mean))
            std_pixel = float(sum(stat.stddev) / len(stat.stddev))
        except Exception:
            orig_w = None
            orig_h = None
            mean_pixel = None
            std_pixel = None

        # Create a new patient user record in `users` with auto-generated id
        db = get_db()
        cur = db.cursor()

        patient_id = int(datetime.utcnow().timestamp() * 1000)
        username = f"patient_{patient_id}"
        pwd_hash, salt_hex, iters = _hash_password('changeme')
        created_on = datetime.utcnow().isoformat()

        try:
            cur.execute('INSERT INTO users (username, password_hash, password_salt, iterations, role, patient_id, created_on) VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (username, pwd_hash, salt_hex, iters, 'patient', patient_id, created_on))
        except sqlite3.IntegrityError:
            # fallback: if username exists, append random suffix
            username = f"patient_{patient_id}_{secrets.token_hex(4)}"
            cur.execute('INSERT INTO users (username, password_hash, password_salt, iterations, role, patient_id, created_on) VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (username, pwd_hash, salt_hex, iters, 'patient', patient_id, created_on))

        # Insert into mri_scans table
        ingest_ts = datetime.utcnow().isoformat()
        scan_date = ingest_ts
        original_path = save_path
        processed_path = save_path
        label = None

        cur.execute('''INSERT INTO mri_scans (original_path, processed_path, label, orig_width, orig_height, proc_width, proc_height, mean_pixel, std_pixel, ingest_timestamp, patient_id, age, gender, hospital_unit, scan_date)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (original_path, processed_path, label, orig_w, orig_h, orig_w, orig_h, mean_pixel, std_pixel, ingest_ts, patient_id, age, gender, hospital_unit, scan_date))

        db.commit()

        scan_id = cur.lastrowid

        return jsonify({'success': True, 'patient_id': patient_id, 'username': username, 'scan_id': scan_id, 'filepath': f'/static/uploads/{filename_on_disk}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/predict_scan', methods=['POST'])
def predict_scan():
    """Run ACTUAL model prediction for a given scan_id"""
    data = request.get_json() or {}
    scan_id = data.get('scan_id')
    if not scan_id:
        return jsonify({'success': False, 'error': 'scan_id required'}), 400

    try:
        db = get_db()
        cur = db.cursor()
        row = cur.execute('SELECT processed_path FROM mri_scans WHERE rowid = ?', (scan_id,)).fetchone()
        if not row:
            return jsonify({'success': False, 'error': 'scan not found'}), 404

        processed_path = row[0]

        predicted_label, confidence = predict_tumor(processed_path)
        model_name = 'xception_optimized_86val_70test'
        classified_on = datetime.utcnow().isoformat()

        cur.execute('INSERT INTO tumor_classification (processed_path, predicted_label, confidence, model_name, classified_on) VALUES (?, ?, ?, ?, ?)',
                    (processed_path, predicted_label, confidence, model_name, classified_on))

        # Update mri_scans.label with prediction
        cur.execute('UPDATE mri_scans SET label = ? WHERE rowid = ?', (predicted_label, scan_id))

        db.commit()

        class_id = cur.lastrowid
        
        return jsonify({
            'success': True, 
            'classification_id': class_id, 
            'predicted_label': predicted_label, 
            'confidence': confidence
        })
        
    except Exception as e:
        print(f" Error in predict_scan: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/image/<int:scan_id>')
def get_image(scan_id):
    """Serve MRI scan image or generate placeholder if not available"""
    try:
        db = get_db()
        cursor = db.execute("""
            SELECT original_path, processed_path, label 
            FROM mri_scans 
            WHERE rowid = ?
        """, (scan_id,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({'error': 'Scan not found'}), 404
        
        # Try to find the image file locally
        # Check multiple possible locations
        original_path = row[0]
        processed_path = row[1]
        label = row[2]
        
        # Try to find the image in local directories
        possible_paths = [
            original_path,
            processed_path,
            original_path.replace('/content/', ''),
            processed_path.replace('/content/', ''),
            os.path.join('static', 'training_images', os.path.basename(original_path)),
            os.path.join('static', 'training_images', os.path.basename(processed_path))
        ]
        
        image_found = False
        for path in possible_paths:
            if path and os.path.exists(path):
                mtype = mimetypes.guess_type(path)[0] or 'application/octet-stream'
                return send_file(path, mimetype=mtype)

        # If images are organized under `static/training_images/<tumor>/<file>`
        # search recursively for a file matching the basename of the stored path.
        try:
            # search both `static/training_images` and top-level `training_images`
            candidates = [
                os.path.join(os.path.dirname(__file__), 'static', 'training_images'),
                os.path.join(os.path.dirname(__file__), 'training_images')
            ]
            base_dir = None
            for c in candidates:
                if os.path.isdir(c):
                    base_dir = c
                    break

            target_names = set()
            if original_path:
                target_names.add(os.path.basename(original_path).lower())
            if processed_path:
                target_names.add(os.path.basename(processed_path).lower())

            if base_dir and os.path.isdir(base_dir):
                for dp, dn, files in os.walk(base_dir):
                    for fname in files:
                        if fname.lower() in target_names:
                            found_path = os.path.join(dp, fname)
                            mtype = mimetypes.guess_type(found_path)[0] or 'application/octet-stream'
                            return send_file(found_path, mimetype=mtype)
        except Exception:
            pass
        
        # If no image found, generate a placeholder
        img = Image.new('RGB', (224, 224), color=(240, 240, 245))
        draw = ImageDraw.Draw(img)
        
        # Draw text on placeholder
        text_lines = [
            "MRI Scan",
            f"Type: {label.replace('_', ' ').title()}",
            "Image not available",
            "locally"
        ]
        
        # Draw centered text
        y_pos = 60
        for line in text_lines:
            # Simple text rendering (PIL default font)
            bbox = draw.textbbox((0, 0), line)
            text_width = bbox[2] - bbox[0]
            x_pos = (224 - text_width) // 2
            draw.text((x_pos, y_pos), line, fill=(100, 100, 120))
            y_pos += 30
        
        # Draw border
        draw.rectangle([(10, 10), (214, 214)], outline=(200, 200, 210), width=2)
        
        # Return the image
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')
        
    except Exception as e:
        # Return a simple error placeholder
        img = Image.new('RGB', (224, 224), color=(255, 240, 240))
        draw = ImageDraw.Draw(img)
        draw.text((60, 100), "Error loading", fill=(200, 50, 50))
        draw.text((80, 120), "image", fill=(200, 50, 50))
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'success': False, 'error': 'Username and password required'}), 400

    try:
        db = get_db()
        cur = db.execute('SELECT password_hash, password_salt, iterations, role, patient_id FROM users WHERE username = ?', (username,))
        row = cur.fetchone()
        if not row:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

        stored_hash, stored_salt, iterations, role, patient_id = row
        if _verify_password(stored_hash, stored_salt, iterations, password):
            session.clear()
            session['logged_in'] = True
            session['username'] = username
            session['user_type'] = role
            if role == 'patient':
                session['patient_id'] = patient_id

            # Redirect based on role
            if role in ('admin', 'radiologist'):
                return jsonify({'success': True, 'redirect': '/database'})
            if role == 'patient':
                return jsonify({'success': True, 'redirect': '/patient_portal'})
            if role == 'patient':
                return jsonify({'success': True, 'redirect': '/patient_portal'})

            return jsonify({'success': True, 'redirect': '/'})

        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    except Exception:
        return jsonify({'success': False, 'error': 'Authentication error'}), 500

@app.route('/patient_login', methods=['POST'])
def patient_login():
    data = request.get_json() or {}

    # Accept either { username, password } (preferred) or legacy { patient_id }
    username = data.get('username') or data.get('patient_id')
    password = data.get('password')

    if username and password:
        try:
            db = get_db()
            cur = db.execute('SELECT password_hash, password_salt, iterations, role, patient_id FROM users WHERE username = ?', (str(username),))
            row = cur.fetchone()
            if not row:
                return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
            stored_hash, stored_salt, iterations, role, patient_id = row
            if _verify_password(stored_hash, stored_salt, iterations, password):
                session.clear()
                session['logged_in'] = True
                session['username'] = str(username)
                session['user_type'] = role
                if role == 'patient':
                    session['patient_id'] = patient_id
                return jsonify({'success': True, 'redirect': '/patient_portal'})
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        except Exception:
            return jsonify({'success': False, 'error': 'Database error'}), 500

    # Legacy behavior: accept patient_id only (no password)
    patient_id = str(data.get('patient_id', '')).strip()
    if not patient_id:
        return jsonify({'success': False, 'error': 'Patient ID is required'}), 400
    try:
        db = get_db()
        cursor = db.execute("SELECT DISTINCT patient_id FROM mri_scans WHERE patient_id = ?", (patient_id,))
        patient = cursor.fetchone()
        if patient:
            session.clear()
            session['logged_in'] = True
            session['patient_id'] = patient_id
            session['user_type'] = 'patient'
            return jsonify({'success': True, 'redirect': '/patient_portal'})
        else:
            return jsonify({'success': False, 'error': 'Patient ID not found'}), 401
    except Exception:
        return jsonify({'success': False, 'error': 'Database error'}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/database')
def database():
    # Allow both admins and radiologists to access the DB console
    if not session.get('logged_in') or session.get('user_type') not in ('admin', 'radiologist'):
        return redirect(url_for('index'))
    return render_template('database.html')

@app.route('/patient_portal')
def patient_portal():
    if not session.get('logged_in') or session.get('user_type') != 'patient':
        return redirect(url_for('index'))
    return render_template('patient_portal.html', patient_id=session.get('patient_id'))

@app.route('/patient_records')
def patient_records():
    if not session.get('logged_in') or session.get('user_type') != 'patient':
        return jsonify({'error': 'Unauthorized'}), 401
    
    patient_id = session.get('patient_id')
    
    try:
        db = get_db()
        cursor = db.execute("""
            SELECT rowid, * FROM mri_scans 
            WHERE patient_id = ? 
            ORDER BY scan_date DESC
        """, (patient_id,))
        
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            record = dict(zip(columns, row))
            # Add image URL
            record['image_url'] = f"/image/{record['rowid']}"
            results.append(record)
        
        return jsonify({
            'success': True,
            'patient_id': patient_id,
            'records': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/find_scans_by_patient', methods=['POST'])
def find_scans_by_patient():
    """Search MRI scans by patient_id (parameterized) and return results.
    Accessible to logged-in admins and radiologists.
    """
    if not session.get('logged_in') or session.get('user_type') not in ('admin', 'radiologist'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    data = request.get_json() or {}
    patient_id = str(data.get('patient_id', '')).strip()
    if not patient_id:
        return jsonify({'success': False, 'error': 'patient_id is required'}), 400

    try:
        db = get_db()
        cursor = db.execute("SELECT rowid, * FROM mri_scans WHERE patient_id = ? ORDER BY scan_date DESC", (patient_id,))
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        results = []
        for row in rows:
            record = dict(zip(columns, row))
            record['image_url'] = f"/image/{record.get('rowid')}"
            results.append(record)

        return jsonify({
            'success': True,
            'columns': columns,
            'data': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/delete_scans_by_patient', methods=['POST'])
def delete_scans_by_patient():
    """Delete all MRI scans (and related classification rows/files) for a given patient_id.
    Restricted to admin users only.
    """
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    data = request.get_json() or {}
    patient_id = str(data.get('patient_id', '')).strip()
    if not patient_id:
        return jsonify({'success': False, 'error': 'patient_id is required'}), 400

    try:
        db = get_db()
        cur = db.cursor()

        # Find affected scans
        cur.execute('SELECT rowid, original_path, processed_path FROM mri_scans WHERE patient_id = ?', (patient_id,))
        rows = cur.fetchall()
        if not rows:
            return jsonify({'success': True, 'deleted_count': 0, 'deleted_scan_ids': []})

        scan_ids = [r[0] for r in rows]
        processed_paths = [r[2] for r in rows if r[2]]
        original_paths = [r[1] for r in rows if r[1]]

        # Delete related tumor_classification rows that reference these processed paths
        if processed_paths:
            placeholders = ','.join('?' for _ in processed_paths)
            cur.execute(f"DELETE FROM tumor_classification WHERE processed_path IN ({placeholders})", tuple(processed_paths))

        # Delete scans
        cur.execute('DELETE FROM mri_scans WHERE patient_id = ?', (patient_id,))
        deleted_count = cur.rowcount

        db.commit()

        # Attempt to remove files from disk (best-effort)
        removed_files = []
        for p in processed_paths + original_paths:
            try:
                if p and os.path.exists(p):
                    os.remove(p)
                    removed_files.append(p)
            except Exception:
                pass

        return jsonify({'success': True, 'deleted_count': deleted_count, 'deleted_scan_ids': scan_ids, 'removed_files': removed_files})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/execute_query', methods=['POST'])
def execute_query():
    if not session.get('logged_in') or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    # Only allow SELECT queries for safety
    if not query.upper().startswith('SELECT'):
        return jsonify({'error': 'Only SELECT queries are allowed'}), 400
    
    try:
        db = get_db()
        cursor = db.execute(query)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        # Convert rows to list of dictionaries
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        
        return jsonify({
            'success': True,
            'columns': columns,
            'data': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)



