# Brain Tumor Detection System

A Flask-based web application for brain tumor detection and classification using deep learning. Features role-based authentication, patient management, MRI scan uploads, and automated tumor classification using a trained Xception model.

## Features

- **Role-Based Authentication**: Admin, radiologist, and patient portals with PBKDF2-hashed passwords
- **Patient Management**: Add, search, and delete patient records with MRI scans
- **Database Query Interface**: Execute SQL queries and view database schema
- **Tumor Classification**: Automated detection and classification of brain tumors (glioma, meningioma, pituitary, or no tumor)
- **Audit History**: Track all patient additions and deletions with timestamps
- **Responsive Design**: Modern UI with interactive elements and image zoom capabilities

## Technology Stack

- **Backend**: Flask 3.1.2, SQLite
- **ML/AI**: TensorFlow 2.19.0, OpenCV, NumPy
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Gunicorn (production WSGI server)

## Quickstart

### Local Development

```bash
# 1) Create and activate a virtual environment
python -m venv .venv

# Reactivate virtual environment:
# Windows:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Run the development server
python app.py

# 4) Visit http://127.0.0.1:5000/
```

### Default Credentials

- **Admin**: `admin` / `password123`
- **Radiologists**: `rad1` through `rad5` / `password123`

## Database Schema

### Tables

**users**
- `username` (TEXT, PRIMARY KEY)
- `password_hash`, `password_salt`, `iterations` (PBKDF2 authentication)
- `role` (admin, radiologist, patient)
- `patient_id` (INTEGER, links to patient records)
- `created_on` (TEXT)

**mri_scans**
- `patient_id`, `age`, `gender`, `hospital_unit`
- `original_path`, `processed_path`, `label`
- Image metadata: dimensions, pixel statistics
- `scan_date`, `ingest_timestamp`

**tumor_classification**
- `classification_id` (INTEGER, PRIMARY KEY)
- `processed_path` (links to mri_scans)
- `predicted_label`, `confidence`
- `model_name`, `classified_on`

**audit_log**
- `log_id` (INTEGER, PRIMARY KEY)
- `action_type` (ADD_PATIENT, DELETE_SCANS)
- `patient_id`, `scan_id`, `details`
- `performed_by`, `timestamp`

## Project Structure

```
MyApp/
 app.py                          # Main Flask application
 requirements.txt                # Python dependencies
 brain_etl.db                    # SQLite database
 .python-version                 # Python version for deployment
 README.md                       # This file

 models/
    optimized_best.h5          # Trained Xception model

 static/
    uploads/                   # Uploaded MRI scans
    images/                    # Static images (ERD, graphs)
    css/
        globals.css
        styleguide.css
        styles.css
        database.css
        script.js              # Main JavaScript
        database.js            # Database UI JavaScript

 templates/
     index.html                 # Homepage with login
     database.html              # Database query interface
     patient_portal.html        # Patient view
     radiologist_portal.html    # Radiologist view
```

## API Endpoints

### Authentication
- `POST /login` - Admin/radiologist login
- `POST /patient_login` - Patient login

### Database Operations
- `GET /database` - Database query interface
- `POST /execute_query` - Execute SQL queries
- `POST /find_scans_by_patient` - Search scans by patient ID
- `POST /delete_scans_by_patient` - Delete patient scans
- `GET /audit_history` - Retrieve audit log

### Patient Management
- `POST /submit_patient_scan` - Upload patient scan
- `POST /predict_scan` - Run tumor classification
- `GET /image/<scan_id>` - Retrieve scan image

## Model Information

- **Architecture**: Xception (23M parameters)
- **Input**: 299x299 RGB images
- **Classes**: Glioma, Meningioma, Pituitary tumor, No tumor
- **Training**: 25 epochs with data augmentation
- **Performance**: ~70% test accuracy, 80%+ confidence on predictions

## Deployment

Deployed on Render.com with:
- Python 3.11.9 runtime
- Gunicorn WSGI server
- Environment variable for `SECRET_KEY`

### Environment Variables
```bash
SECRET_KEY=<your-secret-key>  # Required for production
```

## Troubleshooting

### macOS OpenCV Issues
If encountering segmentation faults with OpenCV:
```bash
pip uninstall opencv-python opencv-python-headless
pip install opencv-python-headless==4.10.0.84
```

### Model Loading Errors
The model requires TensorFlow 2.18+ and was trained on macOS. If you encounter "Invalid dtype: tuple" errors, the app will run with graceful fallbacks (predictions return default values).

## Contributors

- Frontend/Backend Development
- ML Model Training (Xception fine-tuning)
- Database Design & ETL Pipeline

## License

Educational project for DS5110 - Data Management and Processing