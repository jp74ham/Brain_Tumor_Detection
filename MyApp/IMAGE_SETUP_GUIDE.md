# Setting Up MRI Images for the Website

## Current Status
✓ Code is updated to display images in patient portal
✓ Image serving route created at `/image/<scan_id>`
✓ Placeholder images will be generated automatically if actual images aren't found

## What You Need to Do

### Option 1: Use Your Local Training Images (Recommended)
If you have the Training images downloaded locally:

1. Create a directory structure in MyApp:
   ```
   MyApp/
     static/
       training_images/
   ```

2. Copy your training images to that folder, organized by tumor type:
   ```
   MyApp/
     static/
       training_images/
         glioma_tumor/
         meningioma_tumor/
         pituitary_tumor/
         no_tumor/
   ```

3. Update the database paths or create a simple script to map database paths to local paths

### Option 2: Use Placeholder Images (Current Default)
The system will automatically generate placeholder images that show:
- "MRI Scan" label
- Tumor type
- "Image not available locally" message

This is what's currently happening since your database has Colab paths like:
`/content/Training/Training/glioma_tumor/gg (331).jpg`

### Option 3: Update Database Paths
Run this script to update the database with local paths:

```python
import sqlite3
import os

conn = sqlite3.connect('brain_etl.db')
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
```

## Testing the Setup

1. Install Pillow (if not already installed):
   ```
   pip install Pillow
   ```

2. Start your Flask app:
   ```
   python app.py
   ```

3. Login as a patient (e.g., patient ID: 8270)

4. You should see:
   - If images exist locally: Actual MRI scan images
   - If images don't exist: Gray placeholder images with tumor type

## What's Been Added

### Backend (app.py)
- `/image/<scan_id>` route that:
  - Tries to find the image in multiple possible locations
  - Falls back to generating a placeholder if not found
  - Returns proper image/png response

### Frontend (patient_portal.js)
- Added `<img>` tags to each record card
- Images are clickable and have hover effects
- Image URL is `/image/<rowid>` for each scan

### Styling (patient_portal.css)
- `.record-image` container with gray background
- `.mri-thumbnail` styling with shadow and hover effects
- Images are centered and scale nicely

## Next Steps

1. Decide which option you want to use
2. If using actual images, organize them in static/training_images/
3. The site will automatically display them once they're in the right location
4. For now, placeholders will work fine for testing the portal functionality
