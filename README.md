# Brain Tumor Detection System

A full-stack web application for brain tumor detection and classification using deep learning. This system provides role-based authentication, patient management, MRI scan analysis, and automated tumor classification using a fine-tuned Xception convolutional neural network.

## 🎯 Project Goal

The goal of this project is to create an end-to-end data management and processing system that:

1. **Automates Brain Tumor Detection**: Uses deep learning to classify MRI scans into four categories (glioma, meningioma, pituitary tumor, or no tumor)
2. **Manages Medical Data**: Provides a secure database system for storing patient information, MRI scans, and classification results
3. **Enables Multi-Role Access**: Implements role-based authentication for administrators, radiologists, and patients
4. **Provides Query Interface**: Offers a database management interface for executing SQL queries and viewing schema

This project demonstrates practical application of data management principles including ETL pipelines, database design, data security, and machine learning model integration.

## 📋 Requirements and Dependencies

### System Requirements
- **Python**: 3.11.9 (recommended for deployment) or 3.12+
- **Operating System**: Windows, macOS, or Linux
- **RAM**: 4GB minimum (8GB recommended for model training)
- **Storage**: 500MB for application and dependencies

### Python Dependencies
```
Flask==3.1.2              # Web framework
Werkzeug==3.1.2           # WSGI utilities
Pillow==11.0.0            # Image processing
numpy<2.0,>=1.23.5        # Numerical computing
opencv-python-headless==4.10.0.84  # Computer vision
tensorflow==2.19.0        # Deep learning framework
protobuf==5.29.5          # Protocol buffers
gunicorn==23.0.0          # Production WSGI server
```

All dependencies are listed in `MyApp/requirements.txt`.

## 🚀 How to Run the Code

### Step 1: Clone the Repository
```bash
git clone https://github.com/jp74ham/Brain_Tumor_Detection.git
cd Brain_Tumor_Detection/MyApp
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

The application will start on `http://127.0.0.1:5000`

### Step 5: Access the System

**Default Login Credentials:**
- **Administrator**: 
  - Username: `admin`
  - Password: `password123`
- **Radiologists**: 
  - Usernames: `rad1`, `rad2`, `rad3`, `rad4`, `rad5`
  - Password: `password123` (for all)

### Step 6: Use the Features

1. **Admin/Radiologist Portal**:
   - Add new patients and upload MRI scans
   - Run tumor classification predictions
   - Search for patient scans by ID
   - Delete patient records
   - Execute database queries

2. **Patient Portal**:
   - View your MRI scans and classification results
   - Check tumor detection outcomes

## 🔬 Approach and Methodology

### 1. Data Collection and Preprocessing
- **Dataset**: Brain MRI images from Kaggle (3000+ images across 4 classes)
- **Preprocessing**: 
  - Resized all images to 299×299 pixels (Xception input size)
  - Normalized pixel values using Xception preprocessing
  - Applied data augmentation (rotation, zoom, flip) during training

### 2. Database Design
**Entity-Relationship Model**:
- **users**: Authentication and role management (PBKDF2-hashed passwords)
- **mri_scans**: Patient information and MRI scan metadata
- **tumor_classification**: Model predictions with confidence scores

**Relationships**:
- One-to-many: users → mri_scans (for patient users)
- One-to-one: mri_scans → tumor_classification (via processed_path)

### 3. Machine Learning Pipeline

**Model Architecture**:
- Base: Xception (pre-trained on ImageNet)
- Fine-tuning: Unfroze top 20 layers
- Custom head: GlobalAveragePooling → BatchNorm → Dense(512) → Dropout → Dense(4)
- Total parameters: ~23 million

**Training Details**:
- Optimizer: Adam with ReduceLROnPlateau
- Loss: Categorical crossentropy
- Epochs: 25 with early stopping
- Callbacks: ModelCheckpoint, EarlyStopping, ReduceLROnPlateau

**ETL Process**:
1. **Extract**: Load raw MRI images from file system
2. **Transform**: 
   - Resize to 299×299
   - Convert to RGB
   - Apply Xception preprocessing
   - Store metadata (dimensions, pixel statistics)
3. **Load**: 
   - Save processed images to `static/uploads/`
   - Insert records into `mri_scans` table
   - Store predictions in `tumor_classification` table

### 4. Web Application Architecture

**Backend** (Flask):
- RESTful API endpoints for all operations
- Session-based authentication
- SQL injection prevention with parameterized queries
- File upload handling with secure filename generation

**Frontend**:
- Responsive HTML/CSS design
- JavaScript for dynamic interactions (modals, AJAX requests, image zoom)
- Accordion UI for organized content display

**Security Features**:
- PBKDF2 password hashing (100,000 iterations)
- Unique salts per user
- Session management
- Input validation (frontend and backend)
- Secure file uploads

## 📊 Results and Outputs

### Model Performance
- **Test Accuracy**: ~70%
- **Inference Speed**: ~2 seconds per image
- **Confidence Threshold**: 80%+ for high-confidence predictions

**Classification Results Example (used images in examples/)**: 
```
Patient ID: 1764626454375
Scan: test.jpg
Prediction: pituitary_tumor
Confidence: 99.99%
Model: xception_optimized_86val_70test
```

### Database Statistics
- **Total Patients**: 15+ test patients
- **Total Scans**: 20+ MRI scans processed
- **Predictions Made**: 100% of uploaded scans classified

## 🌐 Live Deployment

**Production URL**: https://brain-tumor-detection-6equ.onrender.com

Deployed on Render.com with:
- Automatic deployments from GitHub main branch
- Python 3.11.9 runtime
- Gunicorn WSGI server
- Environment variables for sensitive configuration

## 📁 Project Structure

```
Brain_Tumor_Detection/
├── README.md                       # This file
├── .gitignore                      # Git ignore rules
├── .python-version                 # Python version for deployment
│
├── MyApp/                          # Main application directory
│   ├── app.py                      # Flask application
│   ├── requirements.txt            # Python dependencies
│   ├── README.md                   # Detailed app documentation
│   ├── brain_etl.db                # SQLite database
│   │
│   ├── models/
│   │   └── optimized_best.h5      # Trained model
│   │
│   ├── static/
│   │   ├── uploads/                # User-uploaded MRI scans
│   │   ├── images/                 # Static assets (ERD, graphs)
│   │   └── css/
│   │       ├── globals.css
│   │       ├── styleguide.css
│   │       ├── styles.css
│   │       ├── database.css
│   │       ├── script.js
│   │       └── database.js
│   │
│   └── templates/
│       ├── index.html              # Homepage
│       ├── database.html           # Database interface
│       ├── patient_portal.html     # Patient view
│       └── radiologist_portal.html # Radiologist view
│
├── model/
│   └── EDS.ipynb                   # Model training notebook
│
└── ETL_Pipeline (1).ipynb          # Data pipeline notebook
```

## 🔧 Troubleshooting

### Issue: Model not loading ("Invalid dtype: tuple")
**Solution**: The model was trained on macOS and may have compatibility issues on Windows. The application includes graceful fallbacks - all features work except predictions return default values.

### Issue: OpenCV not found
**Solution**: 
```bash
pip install opencv-python-headless==4.10.0.84
```

### Issue: TensorFlow installation errors
**Solution**: Ensure Python 3.11 or 3.12 is installed. For Python 3.13+, some packages may not be compatible yet.

## 📄 License

Educational project for **DS5110 - Essentials of Data Science**  
Northeastern University, Fall 2025

## 📞 Project Resources

- **Dataset**: https://www.kaggle.com/datasets/sartajbhuvaji/brain-tumor-classification-mri
- **GitHub Repository**: https://github.com/jp74ham/Brain_Tumor_Detection
- **Live Demo**: https://brain-tumor-detection-6equ.onrender.com
