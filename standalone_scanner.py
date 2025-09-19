"""
Standalone Pokemon Card Scanner - No Database Required
Works with any Pokemon card using Gemini AI
"""
import cv2
import numpy as np
from typing import Dict, Any, Optional
import os
from datetime import datetime
import json

from card_analyzer import CardAnalyzer
from price_scraper import CardPriceScraper


class StandaloneCardScanner:
    """Card scanner that uses only AI and web scraping - no database needed"""
    
    def __init__(self, google_api_key: str = None, gemini_model: str = "gemini-2.0-flash-exp"):
        """Initialize the scanner with Gemini API"""
        self.analyzer = CardAnalyzer(api_key=google_api_key, model_name=gemini_model)
        self.price_scraper = CardPriceScraper()
        self.scan_cache = {}
        
    def process_card(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Process a card image: analyze with AI and fetch prices
        
        Args:
            image: Card image as numpy array
            
        Returns:
            Complete analysis with card details and pricing
        """
        result = {
            'timestamp': datetime.now().isoformat(),
            'success': False
        }
        
        # Step 1: AI Analysis with Gemini
        try:
            print("Analyzing card with Gemini AI...")
            ai_analysis = self.analyzer.analyze_card(image)
            result['card_details'] = ai_analysis
            
            # Check if AI analysis had an error
            if 'error' in ai_analysis:
                result['error'] = f"AI analysis failed: {ai_analysis['error']}"
                return result
            
            # Extract key information with multiple fallbacks
            card_name = (ai_analysis.get('name') or 
                        ai_analysis.get('card_name') or 
                        ai_analysis.get('cardname') or
                        ai_analysis.get('pokemon_name'))
            
            set_name = (ai_analysis.get('set') or 
                       ai_analysis.get('set_name') or
                       ai_analysis.get('expansion'))
            
            card_number = (ai_analysis.get('number') or 
                          ai_analysis.get('card_number') or
                          ai_analysis.get('card_id'))
            
            rarity = ai_analysis.get('rarity')
            
            # More detailed error checking
            if not card_name and 'raw_analysis' not in ai_analysis:
                result['error'] = "Could not identify card name from AI analysis"
                result['debug_info'] = {
                    'ai_response_keys': list(ai_analysis.keys()),
                    'ai_response_sample': str(ai_analysis)[:200] + "..." if len(str(ai_analysis)) > 200 else str(ai_analysis)
                }
                return result
                
            result['identified_card'] = {
                'name': card_name,
                'set': set_name,
                'number': card_number,
                'rarity': rarity
            }
            
            # Step 2: Price Lookup
            print(f"Looking up prices for: {card_name}")
            
            # Check cache first
            cache_key = f"{card_name}_{set_name if set_name else 'unknown'}"
            if cache_key in self.scan_cache:
                cached = self.scan_cache[cache_key]
                if (datetime.now() - datetime.fromisoformat(cached['timestamp'])).seconds < 3600:
                    result['pricing'] = cached
                    result['pricing']['from_cache'] = True
                    result['success'] = True
                    return result
            
            # Fetch fresh prices
            pricing = self.price_scraper.get_all_prices(card_name, set_name, card_number)
            result['pricing'] = pricing
            self.scan_cache[cache_key] = pricing
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
            print(f"Error processing card: {e}")
            
        return result
    
    def create_display(self, image: np.ndarray, results: Dict[str, Any]) -> np.ndarray:
        """Create a visual display of results"""
        display = image.copy()
        height, width = display.shape[:2]
        
        # Create info panel
        panel_width = 500
        info_panel = np.ones((height, panel_width, 3), dtype=np.uint8) * 255
        
        y_offset = 30
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        if results.get('success'):
            # Card name
            card_info = results.get('identified_card', {})
            cv2.putText(info_panel, f"Card: {card_info.get('name', 'Unknown')}", 
                       (10, y_offset), font, 0.7, (0, 0, 0), 2)
            y_offset += 35
            
            # Set and number
            if card_info.get('set'):
                cv2.putText(info_panel, f"Set: {card_info.get('set')}", 
                           (10, y_offset), font, 0.6, (0, 0, 0), 1)
                y_offset += 30
            
            if card_info.get('number'):
                cv2.putText(info_panel, f"Number: {card_info.get('number')}", 
                           (10, y_offset), font, 0.6, (0, 0, 0), 1)
                y_offset += 30
                
            # Rarity
            if card_info.get('rarity'):
                cv2.putText(info_panel, f"Rarity: {card_info.get('rarity')}", 
                           (10, y_offset), font, 0.6, (0, 0, 0), 1)
                y_offset += 30
            
            # Pricing
            if 'pricing' in results and 'summary' in results['pricing']:
                y_offset += 20
                cv2.putText(info_panel, "Market Prices:", 
                           (10, y_offset), font, 0.7, (0, 0, 255), 2)
                y_offset += 35
                
                summary = results['pricing']['summary']
                cv2.putText(info_panel, f"Average: ${summary['average_price']:.2f}", 
                           (30, y_offset), font, 0.6, (0, 128, 0), 2)
                y_offset += 30
                
                cv2.putText(info_panel, f"Range: ${summary['min_price']:.2f} - ${summary['max_price']:.2f}", 
                           (30, y_offset), font, 0.5, (0, 0, 0), 1)
                y_offset += 30
                
                # Show source info
                y_offset += 10
                if results['pricing']['sources'].get('ebay', {}).get('average_sold_price'):
                    cv2.putText(info_panel, f"eBay Avg: ${results['pricing']['sources']['ebay']['average_sold_price']:.2f}", 
                               (30, y_offset), font, 0.5, (0, 0, 0), 1)
                    y_offset += 25
        else:
            # Error message
            cv2.putText(info_panel, "Error analyzing card", 
                       (10, y_offset), font, 0.7, (0, 0, 255), 2)
            if 'error' in results:
                y_offset += 35
                # Word wrap error message
                error_msg = results['error']
                words = error_msg.split()
                line = ""
                for word in words:
                    test_line = line + word + " "
                    if len(test_line) > 40:
                        cv2.putText(info_panel, line.strip(), 
                                   (10, y_offset), font, 0.5, (0, 0, 0), 1)
                        y_offset += 25
                        line = word + " "
                    else:
                        line = test_line
                if line:
                    cv2.putText(info_panel, line.strip(), 
                               (10, y_offset), font, 0.5, (0, 0, 0), 1)
        
        # Combine images
        return np.hstack([display, info_panel])


def detect_and_transform_card(frame: np.ndarray) -> Optional[np.ndarray]:
    """
    Detect card in frame and return transformed image
    
    Args:
        frame: Input image
        
    Returns:
        Transformed card image or None if no card detected
    """
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Edge detection
    edges = cv2.Canny(blurred, 50, 150)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Find largest rectangular contour
    for contour in sorted(contours, key=cv2.contourArea, reverse=True):
        # Approximate contour to polygon
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        # Check if it's a quadrilateral
        if len(approx) == 4:
            # Get corner points
            points = approx.reshape(4, 2)
            
            # Order points: top-left, top-right, bottom-right, bottom-left
            rect = np.zeros((4, 2), dtype="float32")
            
            # Top-left has smallest sum, bottom-right has largest sum
            s = points.sum(axis=1)
            rect[0] = points[np.argmin(s)]
            rect[2] = points[np.argmax(s)]
            
            # Top-right has smallest difference, bottom-left has largest difference
            diff = np.diff(points, axis=1)
            rect[1] = points[np.argmin(diff)]
            rect[3] = points[np.argmax(diff)]
            
            # Calculate destination points (standard card ratio 2.5:3.5)
            width = 350
            height = 490
            
            dst = np.array([
                [0, 0],
                [width - 1, 0],
                [width - 1, height - 1],
                [0, height - 1]
            ], dtype="float32")
            
            # Get perspective transform
            M = cv2.getPerspectiveTransform(rect, dst)
            
            # Apply transform
            warped = cv2.warpPerspective(frame, M, (width, height))
            
            return warped
    
    return None


def main():
    """Main function for testing the scanner"""
    # Get API key
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        print("Please set GOOGLE_API_KEY environment variable")
        api_key = input("Or enter your Google API key: ").strip()
    
    # Initialize scanner
    scanner = StandaloneCardScanner(google_api_key=api_key)
    
    # Camera setup
    print("\nPokemon Card Scanner (Standalone)")
    print("=================================")
    print("Hold a Pokemon card up to the camera")
    print("Press 'q' to quit, 'c' to capture and analyze")
    print()
    
    cap = cv2.VideoCapture(0)  # Use default camera
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Show live feed
        cv2.imshow("Pokemon Card Scanner", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            print("\nCapturing and processing card...")
            
            # Try to detect and transform card
            card_image = detect_and_transform_card(frame)
            
            if card_image is not None:
                # Process the card
                results = scanner.process_card(card_image)
                
                # Display results
                display = scanner.create_display(card_image, results)
                cv2.imshow("Analysis Results", display)
                
                # Save results
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                cv2.imwrite(f"scan_{timestamp}.jpg", card_image)
                with open(f"scan_{timestamp}.json", 'w') as f:
                    json.dump(results, f, indent=2)
                
                print("Results saved!")
                print("Press any key to continue scanning...")
                cv2.waitKey(0)
            else:
                print("No card detected. Please try again.")
    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()