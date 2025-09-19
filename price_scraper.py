"""
Price Scraper Module - Fetches card prices from various marketplaces
"""
import requests
from bs4 import BeautifulSoup
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import time
import re
from urllib.parse import quote_plus
from fake_useragent import UserAgent

class CardPriceScraper:
    """Scrapes card prices from TCGPlayer, eBay, and other sources"""
    
    def __init__(self):
        """Initialize the price scraper with rotating user agents"""
        self.ua = UserAgent()
        self.session = requests.Session()
        
    def _get_headers(self) -> Dict[str, str]:
        """Get randomized headers for requests"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def scrape_tcgplayer(self, card_name: str, set_name: str = None) -> Dict[str, Any]:
        """
        Scrape prices from TCGPlayer
        
        Args:
            card_name: Name of the card
            set_name: Optional set name for more accurate results
            
        Returns:
            Dictionary with pricing information
        """
        search_query = f"{card_name} {set_name}" if set_name else card_name
        encoded_query = quote_plus(search_query)
        
        # TCGPlayer search URL
        url = f"https://www.tcgplayer.com/search/pokemon/product?productLineName=pokemon&q={encoded_query}"
        
        try:
            response = self.session.get(url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            prices = {
                'source': 'TCGPlayer',
                'search_query': search_query,
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'results': []
            }
            
            # Parse search results (TCGPlayer structure may vary)
            # This is a simplified example - actual implementation would need to handle dynamic content
            product_items = soup.find_all('div', class_='search-result')
            
            for item in product_items[:5]:  # Top 5 results
                try:
                    name = item.find('span', class_='product-name')
                    price = item.find('span', class_='product-price')
                    condition = item.find('span', class_='condition')
                    
                    if name and price:
                        prices['results'].append({
                            'name': name.text.strip(),
                            'price': self._parse_price(price.text.strip()),
                            'condition': condition.text.strip() if condition else 'Unknown',
                            'link': item.find('a')['href'] if item.find('a') else None
                        })
                except Exception as e:
                    continue
            
            # If no results from parsing, try API approach
            if not prices['results']:
                prices['note'] = "Direct scraping failed, consider using TCGPlayer API for production"
                
            return prices
            
        except Exception as e:
            return {
                'source': 'TCGPlayer',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def scrape_ebay(self, card_name: str, set_name: str = None) -> Dict[str, Any]:
        """
        Scrape prices from eBay sold listings
        
        Args:
            card_name: Name of the card
            set_name: Optional set name for more accurate results
            
        Returns:
            Dictionary with pricing information
        """
        search_query = f"{card_name} {set_name} pokemon card" if set_name else f"{card_name} pokemon card"
        encoded_query = quote_plus(search_query)
        
        # eBay sold listings URL
        url = f"https://www.ebay.com/sch/i.html?_nkw={encoded_query}&_sacat=0&LH_Sold=1&LH_Complete=1"
        
        try:
            response = self.session.get(url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            prices = {
                'source': 'eBay',
                'search_query': search_query,
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'sold_listings': []
            }
            
            # Parse eBay results
            items = soup.find_all('div', class_='s-item__wrapper')
            
            for item in items[:10]:  # Top 10 sold listings
                try:
                    title = item.find('h3', class_='s-item__title')
                    price = item.find('span', class_='s-item__price')
                    date = item.find('span', class_='s-item__endedDate')
                    
                    if title and price:
                        price_text = price.text.strip()
                        prices['sold_listings'].append({
                            'title': title.text.strip(),
                            'price': self._parse_price(price_text),
                            'sold_date': date.text.strip() if date else 'Unknown',
                            'shipping': self._extract_shipping(item)
                        })
                except Exception as e:
                    continue
            
            # Calculate average sold price
            if prices['sold_listings']:
                valid_prices = [p['price'] for p in prices['sold_listings'] if p['price'] > 0]
                if valid_prices:
                    prices['average_sold_price'] = sum(valid_prices) / len(valid_prices)
                    prices['min_sold_price'] = min(valid_prices)
                    prices['max_sold_price'] = max(valid_prices)
            
            return prices
            
        except Exception as e:
            return {
                'source': 'eBay',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def scrape_cardmarket(self, card_name: str, set_name: str = None) -> Dict[str, Any]:
        """
        Scrape prices from Cardmarket (European market)
        Note: Cardmarket has strict anti-scraping measures
        """
        return {
            'source': 'Cardmarket',
            'note': 'Cardmarket scraping requires API access',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_all_prices(self, card_name: str, set_name: str = None, card_number: str = None) -> Dict[str, Any]:
        """
        Get prices from all available sources
        
        Args:
            card_name: Name of the card
            set_name: Optional set name
            card_number: Optional card number for more precise matching
            
        Returns:
            Consolidated pricing information from all sources
        """
        results = {
            'card_name': card_name,
            'set_name': set_name,
            'card_number': card_number,
            'timestamp': datetime.now().isoformat(),
            'sources': {}
        }
        
        # Add delay between requests to be respectful
        delay = 1  # seconds
        
        # TCGPlayer
        results['sources']['tcgplayer'] = self.scrape_tcgplayer(card_name, set_name)
        time.sleep(delay)
        
        # eBay
        results['sources']['ebay'] = self.scrape_ebay(card_name, set_name)
        time.sleep(delay)
        
        # Cardmarket
        results['sources']['cardmarket'] = self.scrape_cardmarket(card_name, set_name)
        
        # Calculate overall metrics
        self._calculate_summary_stats(results)
        
        return results
    
    def _parse_price(self, price_text: str) -> float:
        """Extract numeric price from text"""
        if not price_text:
            return 0.0
            
        # Look for first price pattern in the text
        # Matches patterns like $12.99, €15.50, USD 25.00, etc.
        price_pattern = r'[\$€£]?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'
        match = re.search(price_pattern, price_text)
        
        if match:
            price_str = match.group(1).replace(',', '')
            try:
                return float(price_str)
            except ValueError:
                pass
        
        # Fallback to old method
        cleaned = re.sub(r'[^\d.,]', '', price_text)
        cleaned = cleaned.replace(',', '')
        
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0
    
    def _extract_shipping(self, item) -> str:
        """Extract shipping cost from eBay item"""
        shipping = item.find('span', class_='s-item__shipping')
        if shipping:
            return shipping.text.strip()
        return 'Unknown'
    
    def _calculate_summary_stats(self, results: Dict[str, Any]) -> None:
        """Calculate summary statistics across all sources"""
        all_prices = []
        
        # Collect all valid prices
        for source, data in results['sources'].items():
            if 'error' not in data:
                if source == 'tcgplayer' and 'results' in data:
                    all_prices.extend([r['price'] for r in data['results'] if r.get('price', 0) > 0])
                elif source == 'ebay' and 'sold_listings' in data:
                    all_prices.extend([r['price'] for r in data['sold_listings'] if r.get('price', 0) > 0])
        
        if all_prices:
            results['summary'] = {
                'average_price': sum(all_prices) / len(all_prices),
                'min_price': min(all_prices),
                'max_price': max(all_prices),
                'price_range': max(all_prices) - min(all_prices),
                'sample_size': len(all_prices)
            }


class PriceDatabase:
    """Store and manage historical price data"""
    
    def __init__(self, db_connection=None):
        """Initialize price database"""
        self.db = db_connection
        self.cache = {}
        
    def save_price_data(self, card_id: str, price_data: Dict[str, Any]) -> None:
        """Save price data to database"""
        # Implementation would save to MySQL database
        self.cache[card_id] = price_data
        
    def get_price_history(self, card_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical price data for a card"""
        # Implementation would query from database
        return []
        
    def get_latest_price(self, card_id: str) -> Optional[Dict[str, Any]]:
        """Get most recent price data for a card"""
        return self.cache.get(card_id)