from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from PIL import Image
from skimage.filters import gabor_kernel
import cv2
import base64
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from io import BytesIO
import requests
import logging

app = Flask(__name__)
CORS(app)


# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Logs all levels of messages (INFO, WARNING, ERROR, DEBUG)
logger = logging.getLogger(__name__)


def generate_color_histogram(image_url):
    """
    Downloads the image from the URL, generates a color histogram, and dominant color plot.
    """
    try:
        logger.info(f"Attempting to fetch image from URL: {image_url}")
        
        # If the URL is a relative path, prepend it with the base URL
        if not image_url.startswith(('http://', 'https://')):
            base_url = 'http://localhost:8000'  # Replace with your base URL
            image_url = f"{base_url}{image_url}"

        # Fetch the image from the URL
        response = requests.get(image_url)

        # Check if the response is successful
        if response.status_code != 200:
            logger.error(f"Failed to fetch image. Status code: {response.status_code}")
            return jsonify({"error": "Failed to fetch image from URL"}), 400
        
        image_data = np.asarray(bytearray(response.content), dtype=np.uint8)
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

        if image is None:
            logger.error("Failed to decode image")
            return jsonify({"error": "Failed to decode image"}), 400
        
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Plot color histograms
        hist_fig = plot_color_histogram(image_rgb)

        # Plot dominant colors
        dominant_colors_fig = plot_dominant_colors(image_rgb)

        # Plot Hu moments
        hu_moments_fig = plot_hu_moments(image)

        # Plot Gabor features
        gabor_features_fig = plot_gabor_features(image)

        logger.info("Histogram, dominant color, Hu moments, and Gabor feature generation successful.")
        
        # Convert the matplotlib plots to base64 strings
        hist_base64 = plot_to_base64(hist_fig)
        dominant_colors_base64 = plot_to_base64(dominant_colors_fig)
        hu_moments_base64 = plot_to_base64(hu_moments_fig)
        gabor_features_base64 = plot_to_base64(gabor_features_fig)

        return jsonify({
            "color_histogram_plot": hist_base64,
            "dominant_colors_plot": dominant_colors_base64,
            "hu_moments_plot": hu_moments_base64,
            "gabor_features_plot": gabor_features_base64
        })

    except Exception as e:
        logger.error(f"Error generating color histogram: {str(e)}")
        return jsonify({"error": "Error processing image"}), 500

def plot_color_histogram(image):
    """
    Generates and plots a color histogram for the image using matplotlib.
    """
    fig, ax = plt.subplots(figsize=(10, 5))  # Create a Figure and Axes object
    colors = ['red', 'green', 'blue']
    channels = cv2.split(image)
    
    for i, color in enumerate(colors):
        hist = cv2.calcHist([channels[i]], [0], None, [256], [0, 256])
        ax.plot(hist, color=color)
    
    ax.set_title('Color Histogram')
    ax.set_xlabel('Pixel Intensity')
    ax.set_ylabel('Frequency')
    ax.legend(colors)
    
    return fig

def plot_dominant_colors(image, k=5):
    """
    Identifies dominant colors using KMeans clustering and plots the dominant colors.
    """
    # Reshape the image to a 2D array of pixels
    pixels = image.reshape(-1, 3)
    
    # Perform KMeans clustering to find dominant colors
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(pixels)
    dominant_colors = kmeans.cluster_centers_

    # Plot dominant colors
    fig, ax = plt.subplots(figsize=(10, 2))  # Create a Figure and Axes object
    ax.imshow([dominant_colors.astype(int)])
    ax.axis('off')
    ax.set_title(f"Top {k} Dominant Colors")
    
    return fig

def plot_hu_moments(image):
    """
    Computes and plots the logarithm of absolute values of Hu moments.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    moments = cv2.moments(gray)
    hu_moments = cv2.HuMoments(moments).flatten()
    log_hu_moments = -np.sign(hu_moments) * np.log10(np.abs(hu_moments) + 1e-10)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(range(1, 8), log_hu_moments)
    ax.set_title('Logarithm of Absolute Hu Moments')
    ax.set_xlabel('Hu Moment Index')
    ax.set_ylabel('Log10 Value')
    return fig


def plot_gabor_features(image, kernel_size=(21, 21), frequencies=[0.1, 0.2, 0.3], thetas=[0, np.pi/4, np.pi/2]):
    """
    Applies Gabor filters with various parameters and plots the feature maps.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fig, axes = plt.subplots(len(frequencies), len(thetas), figsize=(10, 5))

    for i, freq in enumerate(frequencies):
        for j, theta in enumerate(thetas):
            # Create Gabor kernel
            kernel = cv2.getGaborKernel(kernel_size, sigma=5, theta=theta, lambd=1/freq, gamma=0.5, psi=0)
            filtered = cv2.filter2D(gray, cv2.CV_32F, kernel)
            ax = axes[i, j]
            ax.imshow(filtered, cmap='gray')
            ax.set_title(f"Freq: {freq}, Theta: {theta:.2f}")
            ax.axis('off')

    plt.tight_layout()
    return fig

def plot_to_base64(figure):
    """
    Converts a matplotlib figure to a base64 string.
    """
    buf = BytesIO()
    figure.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(figure)  # Close the figure to avoid memory issues
    return img_str

@app.route('/api/generate-plots', methods=['POST'])
def generate_plots():
    """
    Accepts a JSON payload with the image URL, generates color histograms for each channel, 
    and dominant color plots. Returns the base64-encoded images of the plots.
    """
    if not request.is_json:
        logger.error("Invalid request format, JSON required.")
        return jsonify({"error": "Invalid request format, JSON required"}), 400

    data = request.get_json()

    # Extract image URL from the request payload
    image_url = data.get("image_url")

    if not image_url:
        logger.error("Missing image URL in request.")
        return jsonify({"error": "Missing image URL"}), 400

    # Generate the color histogram and dominant color plots
    plot_data = generate_color_histogram(image_url)

    return plot_data





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


def transform_image(image_bytes, transformation, parameters):
    try:
        img = Image.open(BytesIO(image_bytes))

        if transformation == 'crop':
            x, y, width, height = parameters.get('x'), parameters.get('y'), parameters.get('width'), parameters.get('height')
            img = img.crop((x, y, x + width, y + height))  # Correction: x+width, y+height
        elif transformation == 'resize':
            width, height = parameters.get('width'), parameters.get('height')
            img = img.resize((width, height))
        elif transformation == 'rotate':
            angle = parameters.get('angle')
            img = img.rotate(angle)
        elif transformation == 'grayscale':
            img = img.convert("L")
        elif transformation == 'flip_horizontal': # Retournement horizontal
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        elif transformation == 'flip_vertical': # Retournement vertical
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
       # ... autres transformations

        # Convertir l'image PIL en bytes pour la réponse
        buffered = BytesIO()
        img.save(buffered, format=img.format or "PNG") # Sauvegarde au format original ou PNG par défaut
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return {'transformed_image': img_str}, 200

    except Exception as e:
        return {'message': str(e)}, 500


@app.route('/api/transform', methods=['POST'])
def transform_route():
    if 'image' not in request.files:
        return jsonify({'message': 'No image provided'}), 400

    image_file = request.files['image']
    image_bytes = image_file.read()
    transformation = request.form.get('transformation')
    
    # Extraction des paramètres en fonction de la transformation
    parameters = {}
    if transformation == 'crop':
        parameters['x'] = int(request.form.get('x', 0))
        parameters['y'] = int(request.form.get('y', 0))
        parameters['width'] = int(request.form.get('width', 0))
        parameters['height'] = int(request.form.get('height', 0))
    elif transformation in ('resize', 'rotate'): # Les deux nécessitent width/height ou angle
        try: # Gère les erreurs de conversion en entier
            if transformation == 'resize':
                parameters['width'] = int(request.form.get('width', 0))
                parameters['height'] = int(request.form.get('height', 0))
            elif transformation == 'rotate':
                parameters['angle'] = int(request.form.get('angle', 0))

        except ValueError as e: # Retourne un message d'erreur spécifique
            return jsonify({'message': "Invalid width, height or angle. Must be integers"}), 400

    return jsonify(transform_image(image_bytes, transformation, parameters))


if __name__ == "__main__":
    app.run()



