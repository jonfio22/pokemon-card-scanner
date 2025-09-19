// Vercel serverless function wrapper
export default async function handler(req, res) {
  // For now, just serve the frontend
  // The Python backend needs to be deployed separately
  
  if (req.method === 'GET' && req.url === '/api/health') {
    return res.status(200).json({ 
      status: 'ok',
      message: 'Frontend deployed. Run backend locally with: python web_app.py',
      api_key_set: false
    });
  }
  
  if (req.method === 'POST' && req.url === '/api/scan') {
    return res.status(200).json({
      success: false,
      error: 'Backend not deployed. Please run locally with: python web_app.py',
      instructions: [
        '1. Clone the repo: git clone https://github.com/jonfio22/pokemon-card-scanner',
        '2. Install deps: pip install -r requirements.txt', 
        '3. Add API key to .env file',
        '4. Run: python web_app.py'
      ]
    });
  }
  
  res.status(404).json({ error: 'Not found' });
}