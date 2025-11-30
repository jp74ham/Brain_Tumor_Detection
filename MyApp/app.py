from flask import Flask, render_template, request, jsonify, g, session, redirect, url_for, send_file
import os
import sqlite3
from werkzeug.utils import secure_filename
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config["DATABASE"] = os.path.join(os.path.dirname(__file__), "brain_etl.db")
app.secret_key = 'your-secret-key-change-this-in-production'  # Change this to a random secret key

# Simple credentials (in production, use hashed passwords and a database)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password123'  # Change this!

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        print("Connected to the database")
    return g.db

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
                return send_file(path, mimetype='image/png')
        
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
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['logged_in'] = True
        session['username'] = username
        session['user_type'] = 'admin'
        return jsonify({'success': True, 'redirect': '/database'})
    else:
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/patient_login', methods=['POST'])
def patient_login():
    data = request.get_json()
    patient_id = data.get('patient_id', '').strip()
    
    if not patient_id:
        return jsonify({'success': False, 'error': 'Patient ID is required'}), 400
    
    # Check if patient ID exists in database
    try:
        db = get_db()
        cursor = db.execute("SELECT DISTINCT patient_id FROM mri_scans WHERE patient_id = ?", (patient_id,))
        patient = cursor.fetchone()
        
        if patient:
            session['logged_in'] = True
            session['patient_id'] = patient_id
            session['user_type'] = 'patient'
            return jsonify({'success': True, 'redirect': '/patient_portal'})
        else:
            return jsonify({'success': False, 'error': 'Patient ID not found'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': 'Database error'}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/database')
def database():
    if not session.get('logged_in') or session.get('user_type') != 'admin':
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



