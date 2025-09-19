# Enhanced Pokemon Card Scanner

This enhanced version adds AI-powered card analysis and real-time price fetching to the original Pokemon card scanner.

## New Features

1. **AI Card Analysis** - Uses Google Gemini 2.0 to extract detailed card information
2. **Price Fetching** - Scrapes current market prices from TCGPlayer and eBay
3. **Enhanced Display** - Shows card details, rarity, and market value in real-time
4. **Price History** - Tracks price data over time (database feature)

## Setup

1. Install new dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Google API key:
   - Get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a `.env` file (copy from `.env.example`)
   - Add your API key to the `.env` file

3. Run the enhanced scanner:
```bash
python enhanced_main.py
```

## Usage

### Running the Enhanced Scanner

1. Select option 2 from the main menu
2. Point your camera at a Pokemon card
3. Use these controls:
   - `e` - Toggle enhanced view (shows pricing info)
   - `p` - Show detailed pricing breakdown
   - `s` - Save scan results to JSON file
   - `q` - Quit

### How It Works

1. **Visual Matching** - First tries to match against known Evolutions cards using image hashing
2. **AI Analysis** - Gemini analyzes the card image to extract:
   - Card name, number, and set
   - Rarity and condition
   - Pokemon stats (HP, type, attacks)
   - Special features (1st edition, shadowless, etc.)
3. **Price Lookup** - Searches multiple sources:
   - TCGPlayer for current market prices
   - eBay for recent sold listings
   - Calculates average, min, and max values

### API Limits

- Google Gemini free tier: 60 requests per minute
- Web scraping: Respectful delays between requests
- Results are cached for 1 hour to minimize API usage

## Extending to Other Card Sets

The system currently focuses on Pokemon Evolutions but can be extended:

1. Remove hash matching constraint in `enhanced_scanner.py`
2. The AI will still identify cards from any Pokemon set
3. Price lookup works for all Pokemon cards

## Troubleshooting

- **API Key Error**: Make sure your Google API key is set correctly
- **No Prices Found**: Some cards may not have exact name matches; the scraper tries its best
- **Slow Performance**: AI analysis takes 1-2 seconds per card

## Future Enhancements

- Support for other TCGs (Magic, Yu-Gi-Oh)
- Integration with official TCGPlayer API
- Batch scanning mode
- Collection management features