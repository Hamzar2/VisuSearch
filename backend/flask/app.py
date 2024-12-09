from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from PIL import Image
from skimage.filters import gabor_kernel
import cv2

app = Flask(__name__)
CORS(app)


def extract_image_features(image):
    
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



@app.route('/api/features', methods=['POST'])
def extract_features():
    app.logger.info("Headers: %s", request.headers)
    app.logger.info("Files: %s", request.files)
    app.logger.info("Form Data: %s", request.form)

    if 'image' not in request.files:
        app.logger.error("No 'image' key in request.files")
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    if file.filename == '':
        app.logger.error("File provided but filename is empty")
        return jsonify({'error': 'No selected file'}), 400

    # Process and extract features
    image = Image.open(file.stream)
    features = extract_image_features(image)
    return jsonify(features)



