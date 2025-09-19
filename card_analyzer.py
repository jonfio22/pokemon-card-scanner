"""
Card Analyzer Module - Uses Google Gemini to extract and analyze card information
"""
import os
import base64
from typing import Dict, Any, Optional
import cv2
import numpy as np
from PIL import Image
import PIL.PngImagePlugin  # Ensure PNG plugin is loaded
import io
import json
import google.generativeai as genai
from datetime import datetime

class CardAnalyzer:
    """Uses Google Gemini to analyze card images"""
    
    def __init__(self, api_key: str = None, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialize the card analyzer with Gemini
        
        Args:
            api_key: API key for Google AI
            model_name: Gemini model to use (e.g., gemini-2.0-flash-exp, gemini-1.5-pro, etc.)
        """
        self.api_key = api_key or os.environ.get('GOOGLE_API_KEY')
        self.model_name = model_name
        
        if not self.api_key:
            raise ValueError("API key required. Set GOOGLE_API_KEY environment variable or pass api_key parameter")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
    
    def numpy_to_pil(self, image: np.ndarray) -> Image.Image:
        """Convert numpy array image to PIL Image"""
        # Validate input image
        if image.size == 0:
            raise ValueError("Empty image provided")
        
        if len(image.shape) < 2:
            raise ValueError("Invalid image dimensions")
        
        # Handle different image formats
        if len(image.shape) == 3:
            if image.shape[2] == 3:
                # BGR to RGB conversion
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            elif image.shape[2] == 4:
                # BGRA to RGBA conversion
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
            elif image.shape[2] > 4:
                raise ValueError(f"Unsupported number of channels: {image.shape[2]}")
        
        # Ensure valid data type and range
        if image.dtype != np.uint8:
            image = np.clip(image, 0, 255).astype(np.uint8)
        
        return Image.fromarray(image)
    
    def analyze_card(self, image: np.ndarray, additional_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze a card image using Gemini's vision capabilities
        
        Args:
            image: Card image as numpy array
            additional_context: Any additional context (e.g., from hash matching)
            
        Returns:
            Dictionary with extracted card information
        """
        # Convert numpy array to PIL Image
        pil_image = self.numpy_to_pil(image)
        
        # Build context from hash matching if available
        context = ""
        if additional_context:
            if 'cardname' in additional_context:
                context = f"This appears to be {additional_context['cardname']} based on image matching. "
        
        prompt = f"""Analyze this Pokemon card image and extract the following information:
        
        {context}
        
        Please extract:
        1. Card name
        2. Card number (e.g., "12/113")
        3. Set name and symbol
        4. Rarity (Common, Uncommon, Rare, Holo Rare, etc.)
        5. Card type (Pokemon, Trainer, Energy)
        6. For Pokemon cards:
           - HP
           - Type(s)
           - Evolution stage
           - Attacks with damage
           - Weakness/Resistance
           - Retreat cost
        7. Any special features (First Edition, Shadowless, etc.)
        8. Card condition observations (if visible)
        
        Return the information as a valid JSON object only, with no additional text or markdown.
        """
        
        try:
            # Generate content with Gemini
            print(f"Calling Gemini API with model: {self.model_name}")
            response = self.model.generate_content([prompt, pil_image])
            
            # Extract the text response
            content = response.text.strip()
            print(f"Gemini response received, length: {len(content)} chars")
            
            # Clean up the response if it has markdown code blocks
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Try to parse as JSON
            try:
                card_data = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON: {e}")
                print(f"Raw response: {content[:500]}")  # Show first 500 chars
                # If not valid JSON, create structured data from text
                card_data = {"raw_analysis": content}
            
            card_data['analysis_timestamp'] = datetime.now().isoformat()
            card_data['model_used'] = self.model_name
            
            return card_data
            
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return {
                "error": str(e),
                "analysis_timestamp": datetime.now().isoformat()
            }
    
    def extract_card_details(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Extract structured card details with a more focused prompt
        """
        pil_image = self.numpy_to_pil(image)
        
        prompt = """Extract the following details from this Pokemon card in JSON format:
        {
            "name": "card name",
            "number": "card number/total",
            "set": "set name",
            "rarity": "rarity",
            "type": "Pokemon/Trainer/Energy",
            "hp": "HP value (if Pokemon)",
            "pokemon_type": "Fire/Water/etc (if Pokemon)",
            "attacks": [{"name": "attack name", "damage": "damage"}],
            "market_identifiers": {
                "tcgplayer_name": "exact card name for TCGPlayer search",
                "set_code": "set abbreviation"
            }
        }
        """
        
        try:
            response = self.model.generate_content([prompt, pil_image])
            content = response.text.strip()
            
            # Clean JSON response
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            return json.loads(content.strip())
            
        except Exception as e:
            print(f"Error extracting card details: {e}")
            return {"error": str(e)}