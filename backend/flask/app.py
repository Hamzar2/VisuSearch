from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import numpy as np
from PIL import Image
from skimage.filters import gabor_kernel
from datetime import datetime
import cv2

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Models
class ImageMetadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    color_histogram = db.Column(db.PickleType)
    dominant_colors = db.Column(db.PickleType)
    gabor_features = db.Column(db.PickleType)
    hu_moments = db.Column(db.PickleType)

# Image Processing Functions

def extract_features(image_path):
    """Extract all image features."""
    img = cv2.imread(image_path)
    
    # Color histogram
    hist = cv2.calcHist([img], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist = cv2.normalize(hist, hist).flatten()
    
    # Dominant colors using K-means
    pixels = img.reshape(-1, 3)
    kmeans = cv2.kmeans(np.float32(pixels), 5, None, 
                        criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2),
                        attempts=10, flags=cv2.KMEANS_RANDOM_CENTERS)[2]
    dominant_colors = kmeans.tolist()
    
    # Gabor features
    kernels = [gabor_kernel(frequency=f) for f in (0.1, 0.2, 0.3, 0.4)]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gabor_features = []
    for kernel in kernels:
        filtered = cv2.filter2D(gray, cv2.CV_8UC3, np.real(kernel))
        gabor_features.extend([filtered.mean(), filtered.var()])
    
    # Hu Moments
    contours, _ = cv2.findContours(cv2.Canny(gray, 100, 200), 
                                  cv2.RETR_EXTERNAL, 
                                  cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        moments = cv2.moments(largest_contour)
        hu_moments = cv2.HuMoments(moments).flatten()
    else:
        hu_moments = np.zeros(7)
    
    return {
        'color_histogram': hist,
        'dominant_colors': dominant_colors,
        'gabor_features': gabor_features,
        'hu_moments': hu_moments
    }

def compute_similarity(query_features, db_features):
    """Compute similarity between two images based on their features."""
    hist_sim = 1 - cv2.compareHist(
        np.array(query_features['color_histogram']),
        np.array(db_features['color_histogram']),
        cv2.HISTCMP_BHATTACHARYYA
    )
    
    gabor_sim = 1 - np.linalg.norm(
        np.array(query_features['gabor_features']) - 
        np.array(db_features['gabor_features'])
    ) / len(db_features['gabor_features'])
    
    hu_sim = 1 - np.linalg.norm(
        np.array(query_features['hu_moments']) - 
        np.array(db_features['hu_moments'])
    ) / 7
    
    # Weighted combination
    return 0.4 * hist_sim + 0.3 * gabor_sim + 0.3 * hu_sim



def extract_image_features(image):
    # Convert PIL Image to OpenCV format
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Extract features (same as before)
    hist = cv2.calcHist([img], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist = cv2.normalize(hist, hist).flatten()
    
    pixels = img.reshape(-1, 3)
    kmeans = cv2.kmeans(np.float32(pixels), 5, None,
                        criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2),
                        attempts=10, flags=cv2.KMEANS_RANDOM_CENTERS)[2]
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernels = [gabor_kernel(frequency=f) for f in (0.1, 0.2, 0.3, 0.4)]
    gabor_features = []
    for kernel in kernels:
        filtered = cv2.filter2D(gray, cv2.CV_8UC3, np.real(kernel))
        gabor_features.extend([filtered.mean(), filtered.var()])
    
    contours, _ = cv2.findContours(cv2.Canny(gray, 100, 200),
                                  cv2.RETR_EXTERNAL,
                                  cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        moments = cv2.moments(largest_contour)
        hu_moments = cv2.HuMoments(moments).flatten()
    else:
        hu_moments = np.zeros(7)
    
    return {
        'color_histogram': hist.tolist(),
        'dominant_colors': kmeans.tolist(),
        'gabor_features': gabor_features,
        'hu_moments': hu_moments.tolist()
    }


# API Routes
@app.route('/api/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    category = request.form.get('category')
    
    if not category:
        return jsonify({'error': 'No category provided'}), 400
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        features = extract_features(filepath)
        
        image_metadata = ImageMetadata(
            filename=filename,
            category=category,
            **features
        )
        
        db.session.add(image_metadata)
        db.session.commit()
        
        return jsonify({
            'id': image_metadata.id,
            'url': f'/uploads/{filename}',
            'category': category
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search_images():
    if 'query_image' not in request.files:
        return jsonify({'error': 'No query image provided'}), 400
    
    file = request.files['query_image']
    use_relevance_feedback = request.form.get('use_relevance_feedback', 'false') == 'true'
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Save query image temporarily
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'query_' + filename)
    file.save(filepath)
    
    try:
        query_features = extract_features(filepath)
        
        # Get all images from database
        images = ImageMetadata.query.all()
        results = []
        
        for img in images:
            similarity = compute_similarity(query_features, {
                'color_histogram': img.color_histogram,
                'dominant_colors': img.dominant_colors,
                'gabor_features': img.gabor_features,
                'hu_moments': img.hu_moments
            })
            
            results.append({
                'id': img.id,
                'url': f'/uploads/{img.filename}',
                'category': img.category,
                'similarity': similarity
            })
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Clean up temporary query image
        os.remove(filepath)
        
        return jsonify(results[:20])  # Return top 20 results
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/features', methods=['POST'])
def extract_features():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Process image and extract features
    image = Image.open(file.stream)
    features = extract_image_features(image)
    
    return jsonify(features)

@app.route('/api/images/relevance_feedback', methods=['POST'])
def relevance_feedback():
    data = request.get_json()
    relevant_ids = data.get('relevant_ids', [])
    irrelevant_ids = data.get('irrelevant_ids', [])
    
    # Implement Bayesian relevance feedback here
    # This would update the weights used in similarity computation
    # based on user feedback
    
    return jsonify({'message': 'Feedback received'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()