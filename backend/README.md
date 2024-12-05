# Image Search Backend

This is the Flask backend for the image search system. It provides:

- Image upload and storage
- Feature extraction (color histograms, dominant colors, Gabor features, Hu moments)
- Image similarity search
- Relevance feedback processing

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python app.py
```

The server will start on http://localhost:5000

## API Endpoints

- POST /api/upload - Upload an image with category
- POST /api/search - Search for similar images
- POST /api/relevance_feedback - Process relevance feedback

## Database

The application uses SQLite with SQLAlchemy for storing image metadata and features.