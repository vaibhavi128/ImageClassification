from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from model_utils import precompute_embeddings, get_image_embedding, find_closest_match
from datetime import datetime
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Precompute embeddings at startup
embeddings = precompute_embeddings()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Save the uploaded file temporarily
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        # Get embedding for uploaded image
        query_embedding = get_image_embedding(filepath)
        
        # Find closest match
        result = find_closest_match(query_embedding, embeddings)
        
        return jsonify({
            'name': result['name'],
            'age': result['age'],
            'image_url': result['image_url'],
            'confidence': result['confidence']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up the uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)