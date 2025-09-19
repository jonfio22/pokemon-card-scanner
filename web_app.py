"""
Flask Web App for Pokemon Card Scanner
Simple web interface for card scanning and price lookup
"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import base64
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import os
from dotenv import load_dotenv

from standalone_scanner import StandaloneCardScanner

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize scanner
scanner = StandaloneCardScanner(google_api_key=os.environ.get('GOOGLE_API_KEY'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scan', methods=['POST'])
def scan_card():
    try:
        # Get image data from request
        try:
            data = request.json
        except Exception as e:
            return jsonify({'error': 'Invalid JSON in request'}), 400
            
        if data is None:
            return jsonify({'error': 'Invalid JSON in request'}), 400
        
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Decode base64 image
        image_data = image_data.split(',')[1]  # Remove data:image/jpeg;base64,
        image_bytes = base64.b64decode(image_data)
        
        # Convert to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Process the card
        results = scanner.process_card(image)
        
        # Create display image
        display = scanner.create_display(image, results)
        
        # Convert display to base64
        _, buffer = cv2.imencode('.jpg', display)
        display_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Add display image to results
        results['display_image'] = f"data:image/jpeg;base64,{display_base64}"
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'api_key_set': bool(os.environ.get('GOOGLE_API_KEY'))})

if __name__ == '__main__':
    app.run(debug=True, port=5000)