# Pokemon Card Scanner 🎴

AI-powered Pokemon card scanner that identifies cards and fetches real-time market prices.

## Features
- 📷 Scan cards with camera or upload images
- 🤖 AI card identification using Google Gemini 2.0
- 💰 Real-time pricing from TCGPlayer and eBay
- 🎯 Works with ANY Pokemon card (not limited to specific sets)
- 🌐 Beautiful web interface with Tailwind CSS

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/pokemon-card-scanner
cd pokemon-card-scanner
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your API key
Create a `.env` file:
```
GOOGLE_API_KEY=your-gemini-api-key-here
```

Get your free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### 4. Run the app
```bash
python web_app.py
```

Open http://localhost:5000 in your browser

## How it Works

1. **Upload/Capture** - Use the web interface to upload a card image
2. **AI Analysis** - Google Gemini identifies the card and extracts details
3. **Price Lookup** - Fetches current market prices from multiple sources
4. **Display Results** - Shows card info and pricing in a clean interface

## Tech Stack
- **Backend**: Python, Flask
- **AI**: Google Gemini 2.0 Flash
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Image Processing**: OpenCV, Pillow
- **Web Scraping**: BeautifulSoup, Requests

## Project Structure
```
pokemon-card-scanner/
├── web_app.py              # Flask web server
├── standalone_scanner.py   # Core scanning logic
├── card_analyzer.py        # Gemini AI integration
├── price_scraper.py        # Web scraping for prices
├── templates/
│   └── index.html         # Web interface
├── requirements.txt        # Python dependencies
└── .env                   # Your API key (create this)
```

## Deployment

For local use only. For production deployment:
- Consider using official APIs instead of web scraping
- Add rate limiting and caching
- Use a proper database for price history

## Contributing
Feel free to open issues or submit PRs!

## License
MIT