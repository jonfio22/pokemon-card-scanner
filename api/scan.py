from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'success': False,
            'error': 'Python backend cannot be deployed on Vercel due to size limits. Please run locally:',
            'instructions': [
                '1. Clone: git clone https://github.com/jonfio22/pokemon-card-scanner',
                '2. Install: pip install -r requirements.txt',
                '3. Add your Google API key to .env file',
                '4. Run: python web_app.py',
                '5. Open: http://localhost:5000'
            ],
            'identified_card': {
                'name': 'Demo Card',
                'set': 'Run locally for real scanning',
                'number': 'XXX',
                'rarity': 'N/A'
            }
        }
        
        self.wfile.write(json.dumps(response).encode())
        
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()