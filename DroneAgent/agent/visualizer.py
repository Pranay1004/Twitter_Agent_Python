"""
Image Visualizer Module
Fetches and generates drone-related images for Twitter threads
"""

import os
import re
import requests
import random
from typing import Dict, Optional, List
from pathlib import Path
import json
from datetime import datetime
from io import BytesIO

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ImageVisualizer:
    def __init__(self):
        self.load_config()
        self.setup_apis()
        self.image_cache_dir = Path("data/images")
        
        # Create parent directory first if it doesn't exist
        self.image_cache_dir.parent.mkdir(exist_ok=True)
        self.image_cache_dir.mkdir(exist_ok=True)
        
        # Create AI_GENERATED_IMAGES directory for standardized naming
        self.ai_images_dir = Path("AI_GENERATED_IMAGES")
        self.ai_images_dir.mkdir(exist_ok=True)
        
        # Track post number for consistent naming
        self.current_post_number = 1
        
    def load_config(self):
        """Load configuration from environment variables"""
        from dotenv import load_dotenv
        load_dotenv()
        
        self.unsplash_key = os.getenv('UNSPLASH_ACCESS_KEY')
        self.unsplash_secret = os.getenv('UNSPLASH_SECRET_KEY')
        self.unsplash_app_name = os.getenv('UNSPLASH_APP_NAME', 'DroneAgent_Twitter_Bot')
        self.unsplash_attribution_required = os.getenv('UNSPLASH_ATTRIBUTION_REQUIRED', 'true').lower() == 'true'
        self.unsplash_max_per_hour = int(os.getenv('UNSPLASH_MAX_IMAGES_PER_HOUR', '50'))
        self.unsplash_download_tracking = os.getenv('UNSPLASH_DOWNLOAD_TRACKING', 'true').lower() == 'true'
        self.pexels_key = os.getenv('PEXELS_API_KEY')
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        self.gemini_project_id = os.getenv('GEMINI_PROJECT_ID', 'your-project-id')
        
    def setup_apis(self):
        """Initialize API clients"""
        self.unsplash_headers = {
            'Authorization': f'Client-ID {self.unsplash_key}',
            'User-Agent': f'{self.unsplash_app_name}/1.0'
        } if self.unsplash_key else None
        
        self.pexels_headers = {
            'Authorization': self.pexels_key
        } if self.pexels_key else None
        
        # Setup Gemini API
        try:
            if self.gemini_key and self.gemini_key != "your_gemini_api_key_here":
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                logger.info("Gemini API configured successfully")
        except Exception as e:
            logger.warning(f"Failed to configure Gemini API: {e}")
        
    def get_images_for_thread(self, thread_tweets: List[Dict], user_images: Dict[int, str] = None) -> List[Dict]:
        """Get images for an entire thread with distribution: 50% Gemini, 25% Pexels, 25% Unsplash"""
        logger.info(f"Getting images for thread with {len(thread_tweets)} tweets")
        
        # Reset post number for this thread
        self.current_post_number = 1
        
        # Find tweets that need images
        image_tweets = [i for i, tweet in enumerate(thread_tweets) if tweet.get('needs_image', False)]
        total_images_needed = len(image_tweets)
        
        if total_images_needed == 0:
            return thread_tweets
            
        print(f"📸 Generating {total_images_needed} images for thread...")
        
        # Track used search terms to ensure uniqueness
        used_search_terms = set()
        used_image_urls = set()
        
        # Check if Gemini API is available
        if self.gemini_key:
            # Updated distribution: 50% Gemini, 25% Pexels, 25% Unsplash
            gemini_count = max(1, int(total_images_needed * 0.5))
            pexels_count = max(1, int(total_images_needed * 0.25))
            unsplash_count = total_images_needed - gemini_count - pexels_count
            
            # Always use Gemini for the first tweet when available
            sources = (['gemini'] * gemini_count + 
                      ['pexels'] * pexels_count + 
                      ['unsplash'] * unsplash_count)
            
            # Ensure first image is always Gemini when available
            if 'gemini' in sources:
                # Move one Gemini to the first position
                sources.remove('gemini')
                sources.insert(0, 'gemini')
            
            logger.info(f"Prioritizing Gemini: {gemini_count} Gemini, {pexels_count} Pexels, {unsplash_count} Unsplash")
        else:
            # Fall back to regular distribution if Gemini isn't available
            gemini_count = 0
            pexels_count = max(1, int(total_images_needed * 0.5))
            unsplash_count = total_images_needed - pexels_count
            
            sources = (['pexels'] * pexels_count + 
                      ['unsplash'] * unsplash_count)
            
            # Shuffle the sources for random distribution
            random.shuffle(sources)
            
            logger.info(f"Gemini unavailable, using: {gemini_count} Gemini, {pexels_count} Pexels, {unsplash_count} Unsplash")
        logger.info(f"First tweet will use {sources[0]} for image generation")
        
        # Process each tweet that needs an image
        for idx, tweet_index in enumerate(image_tweets):
            tweet = thread_tweets[tweet_index]
            
            # Check if user provided image for this tweet
            if user_images and tweet_index in user_images:
                image_data = self._process_user_image(user_images[tweet_index], tweet_index)
                if image_data:
                    tweet['image'] = image_data
                    print(f"✅ Tweet {tweet_index + 1}: User-provided image")
                    continue
            
            # Use assigned source
            source = sources[idx] if idx < len(sources) else 'unsplash'
            content = tweet.get('text', '')
            
            # Generate a unique search term from the content
            # Use the full tweet text for prompt uniqueness
            search_term = content
            
            # Ensure the search term is unique
            original_term = search_term
            attempt = 1
            while search_term in used_search_terms and attempt < 5:
                # Add qualifiers to make it unique
                qualifiers = ["detailed", "advanced", "professional", "modern", "aerial", "close-up"]
                search_term = f"{original_term} {random.choice(qualifiers)} {attempt}"
                attempt += 1
            
            # Mark this search term as used
            used_search_terms.add(search_term)
            
            print(f"🔄 Tweet {tweet_index + 1}: Getting image from {source.title()} using term: {search_term}")
            
            # Get image with the unique search term
            image_data = self._get_image_from_source(search_term, source, self.current_post_number)
            
            # Check if this URL has already been used
            if image_data and image_data.get('url') in used_image_urls:
                print(f"⚠️ Tweet {tweet_index + 1}: Duplicate image detected, regenerating...")
                image_data = None
            
            if image_data:
                # Mark this URL as used
                used_image_urls.add(image_data.get('url'))
                tweet['image'] = image_data
                print(f"✅ Tweet {tweet_index + 1}: {source.title()} image obtained as Post{self.current_post_number}")
                self.current_post_number += 1
            else:
                print(f"⚠️ Tweet {tweet_index + 1}: {source.title()} failed, trying fallback...")
                # Try fallback sources with unique terms
                fallback_term = f"{original_term} alternative view"
                fallback_image = self._get_fallback_image(fallback_term, self.current_post_number)
                if fallback_image and fallback_image.get('url') not in used_image_urls:
                    used_image_urls.add(fallback_image.get('url'))
                    tweet['image'] = fallback_image
                    print(f"✅ Tweet {tweet_index + 1}: Fallback image obtained as Post{self.current_post_number}")
                    self.current_post_number += 1
        
        return thread_tweets
    
    def _get_image_from_source(self, content: str, source: str, post_number: int = 1) -> Optional[Dict]:
        """Get image from specific source"""
        keywords = self._extract_keywords(content)
        search_query = self._build_search_query(keywords)
        
        if source == 'gemini' and self.gemini_key:
            return self._generate_gemini_image(search_query, post_number)
        elif source == 'pexels' and self.pexels_key:
            return self._search_pexels(search_query, post_number)
        elif source == 'unsplash' and self.unsplash_key:
            return self._search_unsplash(search_query, post_number)
        
        return None
    
    def _get_fallback_image(self, content: str, post_number: int = 1) -> Optional[Dict]:
        """Try all sources as fallback"""
        keywords = self._extract_keywords(content)
        search_query = self._build_search_query(keywords)
        
        # Try in order of preference
        sources = ['unsplash', 'pexels', 'gemini']
        
        for source in sources:
            if source == 'gemini' and self.gemini_key:
                image_data = self._generate_gemini_image(search_query, post_number)
            elif source == 'pexels' and self.pexels_key:
                image_data = self._search_pexels(search_query, post_number)
            elif source == 'unsplash' and self.unsplash_key:
                image_data = self._search_unsplash(search_query, post_number)
            else:
                continue
                
            if image_data:
                return image_data
        
        return None
        
    def get_image(self, topic: str) -> Optional[Dict]:
        """Get a single image for a topic - used by ContentGenerationThread"""
        # Extract keywords from topic
        keywords = self._extract_keywords(topic)
        search_query = self._build_search_query(keywords)
        
        logger.info(f"Getting image for topic: {topic}")
        
        # ALWAYS try Gemini first for testing purposes
        if self.gemini_key:
            logger.info("Attempting to use Gemini for image generation")
            image_data = self._generate_gemini_image(search_query)
            if image_data:
                logger.info("Successfully generated image with Gemini")
                return image_data
            logger.warning("Gemini image generation failed, falling back to other sources")
        
        # If Gemini fails, try Unsplash or Pexels
        if random.random() < 0.5:
            sources = ['unsplash', 'pexels']
        else:
            sources = ['pexels', 'unsplash']
            
        for source in sources:
            logger.info(f"Trying {source} for image")
            image_data = self._get_image_from_source(search_query, source)
            if image_data:
                logger.info(f"Successfully got image from {source}")
                return image_data
            
        # If all API sources fail, try one more time with Gemini
        if self.gemini_key:
            logger.info("All API sources failed, trying Gemini one more time")
            image_data = self._generate_gemini_image(search_query)
            if image_data:
                logger.info("Successfully generated image with Gemini on second attempt")
                return image_data
        
        # Last resort - use placeholder
        logger.warning("All image sources failed, using placeholder")
        return self._get_placeholder_image(search_query)
    
    def _process_user_image(self, image_path: str, tweet_index: int) -> Optional[Dict]:
        """Process user-provided image"""
        try:
            # Check if it's a URL or file path
            if image_path.startswith('http'):
                # Download the image
                response = requests.get(image_path)
                if response.status_code == 200:
                    local_path = self.image_cache_dir / f"user_image_{tweet_index}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    with open(local_path, 'wb') as f:
                        f.write(response.content)
                    
                    return {
                        'url': image_path,
                        'local_path': str(local_path),
                        'source': 'user_url',
                        'alt_text': f'User-provided image for tweet {tweet_index + 1}',
                        'attribution': 'User provided'
                    }
            else:
                # Local file path
                if os.path.exists(image_path):
                    return {
                        'url': f'file://{image_path}',
                        'local_path': image_path,
                        'source': 'user_file',
                        'alt_text': f'User-provided image for tweet {tweet_index + 1}',
                        'attribution': 'User provided'
                    }
        except Exception as e:
            logger.warning(f"Failed to process user image {image_path}: {e}")
        
        return None
        print("ℹ️ Using placeholder image as API sources unavailable")
        return self._get_placeholder_image(search_query)
        
    def _extract_search_term(self, content: str) -> str:
        """Extract a relevant search term from tweet content for unique image generation"""
        # Remove hashtags
        clean_content = re.sub(r'#\w+', '', content)
        
        # Define drone-specific keywords to look for
        drone_keywords = ["drone", "UAV", "quadcopter", "aerial", "DJI", "flying", "flight", "camera"]
        
        # Check if content contains drone keywords
        has_drone_term = any(keyword.lower() in clean_content.lower() for keyword in drone_keywords)
        
        # If content doesn't explicitly mention drones, add "drone" to ensure relevance
        if not has_drone_term:
            prefix = "drone"
        else:
            prefix = ""
            
        # Extract key nouns and adjectives (simplified approach)
        words = clean_content.split()
        important_words = []
        
        for word in words:
            word = word.strip().lower()
            # Skip short words and common filler words
            if len(word) > 3 and word not in ["with", "that", "this", "then", "than", "from", "your", "will", "they", "them"]:
                important_words.append(word)
        
        # Select a few important words
        selected_words = important_words[:3] if important_words else ["aerial", "photography"]
        
        # Combine with prefix if needed
        if prefix:
            search_term = f"{prefix} {' '.join(selected_words)}"
        else:
            search_term = ' '.join(selected_words)
            
        return search_term[:50]  # Limit length for API compatibility

    def _extract_keywords(self, content: str) -> List[str]:
        """Extract relevant keywords for image search"""
        # Drone-related keywords
        drone_keywords = {
            'fpv': ['fpv racing', 'racing drone', 'first person view'],
            'diy': ['drone building', 'diy drone', 'drone parts'],
            'commercial': ['commercial drone', 'industry drone', 'professional drone'],
            'military': ['military drone', 'uav', 'surveillance drone'], 
            'photography': ['aerial photography', 'drone camera', 'aerial view'],
            'agriculture': ['agricultural drone', 'farming drone', 'crop monitoring'],
            'delivery': ['delivery drone', 'package delivery', 'drone logistics'],
            'racing': ['drone racing', 'fpv racing', 'racing quadcopter'],
            'technology': ['drone technology', 'quadcopter', 'autonomous drone'],
            'build': ['drone build', 'quadcopter assembly', 'drone components'],
            'history': ['vintage drone', 'early drone', 'drone evolution'],
            'future': ['future drone', 'advanced drone', 'ai drone']
        }
        
        content_lower = content.lower()
        keywords = []
        
        # Find matching categories
        for category, terms in drone_keywords.items():
            if any(term in content_lower for term in [category] + terms):
                keywords.extend(terms[:2])  # Add top 2 terms
                
        # Default drone terms if no specific match
        if not keywords:
            keywords = ['drone', 'quadcopter', 'aerial']
            
        return keywords[:3]  # Limit to 3 keywords
        
    def _build_search_query(self, keywords: List[str]) -> str:
        """Build search query from keywords"""
        if not keywords:
            return "drone"
            
        # Use most specific keyword
        return keywords[0]
        
    def _search_unsplash(self, query: str, post_number: int = 1) -> Optional[Dict]:
        """Search Unsplash for images"""
        if not self.unsplash_headers:
            logger.warning("Unsplash API key not configured")
            return None
            
        try:
            url = "https://api.unsplash.com/search/photos"
            params = {
                'query': query,
                'per_page': 10,
                'orientation': 'landscape',
                'content_filter': 'high',
                'order_by': 'relevant'
            }
            
            response = requests.get(url, headers=self.unsplash_headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('results'):
                image = random.choice(data['results'][:5])  # Pick from top 5
                
                # Track download if enabled (required by Unsplash API guidelines)
                if self.unsplash_download_tracking:
                    try:
                        # Check if download_location exists in the response
                        download_url = image.get('links', {}).get('download_location')
                        if download_url:
                            download_response = requests.get(
                                download_url,
                                headers=self.unsplash_headers,
                                timeout=5
                            )
                            if download_response.status_code == 200:
                                logger.info(f"Download tracked for Unsplash image: {image['id']}")
                            else:
                                logger.warning(f"Download tracking failed with status: {download_response.status_code}")
                        else:
                            # For newer Unsplash API versions, use the dedicated tracking endpoint
                            download_response = requests.get(
                                f"https://api.unsplash.com/photos/{image['id']}/download",
                                headers=self.unsplash_headers,
                                timeout=5
                            )
                            logger.info(f"Download tracked for Unsplash image: {image['id']} using dedicated endpoint")
                    except Exception as e:
                        logger.warning(f"Failed to track download: {e}")
                
                # Download and save image with Post naming
                image_url = image['urls']['regular']
                filename = f"Post{post_number}.jpg"
                filepath = os.path.abspath(os.path.join(self.ai_images_dir, filename))
                
                # Download the image
                img_response = requests.get(image_url, timeout=10)
                img_response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)
                
                logger.info(f"Successfully downloaded Unsplash image: {filepath}")
                
                # Prepare attribution based on configuration
                attribution = f"Photo by {image['user']['name']} on Unsplash" if self.unsplash_attribution_required else ""
                
                return {
                    'url': filepath,  # Use local path
                    'thumbnail_url': filepath,
                    'description': image.get('alt_description', f'{query} drone image'),
                    'credit': attribution,
                    'credit_url': image['links']['html'],
                    'source': 'unsplash',
                    'width': image['width'],
                    'height': image['height'],
                    'image_id': image['id'],
                    'photographer': image['user']['name'],
                    'photographer_url': image['user']['links']['html']
                }
                
        except Exception as e:
            logger.error(f"Unsplash search failed: {e}")
            
        return None
        
    def _search_pexels(self, query: str, post_number: int = 1) -> Optional[Dict]:
        """Search Pexels for images"""
        if not self.pexels_headers:
            logger.warning("Pexels API key not configured")
            return None
            
        try:
            url = "https://api.pexels.com/v1/search"
            params = {
                'query': query,
                'per_page': 10,
                'orientation': 'landscape'
            }
            
            response = requests.get(url, headers=self.pexels_headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('photos'):
                image = random.choice(data['photos'][:5])  # Pick from top 5
                
                # Download and save image with Post naming
                image_url = image['src']['large']
                filename = f"Post{post_number}.jpg"
                filepath = os.path.abspath(os.path.join(self.ai_images_dir, filename))
                
                # Download the image
                img_response = requests.get(image_url, timeout=10)
                img_response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)
                
                logger.info(f"Successfully downloaded Pexels image: {filepath}")
                
                return {
                    'url': filepath,  # Use local path
                    'thumbnail_url': filepath,
                    'description': f'{query} drone image',
                    'credit': f"Photo by {image['photographer']} on Pexels",
                    'credit_url': image['url'],
                    'source': 'pexels',
                    'width': image['width'],
                    'height': image['height']
                }
                
        except Exception as e:
            logger.error(f"Pexels search failed: {e}")
            
        return None
        
    def _get_placeholder_image(self, query: str) -> Dict:
        """Generate placeholder image data"""
        placeholder_images = {
            'fpv racing': {
                'description': 'FPV racing drone in action',
                'url': 'https://via.placeholder.com/800x600/1DA1F2/FFFFFF?text=FPV+Racing+Drone',
                'alt_text': 'FPV racing drone flying at high speed through gates'
            },
            'drone building': {
                'description': 'DIY drone build components',
                'url': 'https://via.placeholder.com/800x600/FF6B6B/FFFFFF?text=Drone+Build+Components',
                'alt_text': 'Drone building components laid out for assembly'
            },
            'commercial drone': {
                'description': 'Professional commercial drone',
                'url': 'https://via.placeholder.com/800x600/4ECDC4/FFFFFF?text=Commercial+Drone',
                'alt_text': 'Professional commercial drone for industrial use'
            },
            'aerial photography': {
                'description': 'Drone capturing aerial footage',
                'url': 'https://via.placeholder.com/800x600/45B7D1/FFFFFF?text=Aerial+Photography',
                'alt_text': 'Drone with camera capturing aerial photography'
            },
            'drone technology': {
                'description': 'Advanced drone technology',
                'url': 'https://via.placeholder.com/800x600/96CEB4/FFFFFF?text=Drone+Technology',
                'alt_text': 'Advanced drone showcasing latest technology'
            }
        }
        
        # Find best matching placeholder
        for key, data in placeholder_images.items():
            if key in query.lower():
                return {
                    'url': data['url'],
                    'thumbnail_url': data['url'],
                    'description': data['description'],
                    'alt_text': data['alt_text'],
                    'credit': 'Generated placeholder image',
                    'credit_url': None,
                    'source': 'placeholder',
                    'width': 800,
                    'height': 600
                }
                
        # Default placeholder
        return {
            'url': 'https://via.placeholder.com/800x600/333333/FFFFFF?text=Drone+Image',
            'thumbnail_url': 'https://via.placeholder.com/400x300/333333/FFFFFF?text=Drone+Image',
            'description': f'Drone related to {query}',
            'alt_text': f'Drone image related to {query}',
            'credit': 'Generated placeholder image',
            'credit_url': None,
            'source': 'placeholder',
            'width': 800,
            'height': 600
        }
        
    def _generate_gemini_image(self, query: str, post_number: int = 1) -> Optional[Dict]:
        """Generate image using Gemini 2 Flash using direct API approach"""
        try:
            import base64
            from io import BytesIO
            from datetime import datetime
            from PIL import Image
            from google import genai
            from google.genai import types

            # Make sure we have the API key
            if not self.gemini_key:
                logger.error("Gemini API key not found")
                return None

            # Ensure AI_GENERATED_IMAGES directory exists
            self.ai_images_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Generating image with Gemini 2 Flash for query: {query}")
            
            # Initialize the client
            client = genai.Client(api_key=self.gemini_key)

            # Enhance the prompt for better results
            # Use the full tweet text for a unique, post-specific prompt
            import hashlib
            tweet_hash = hashlib.md5(query.encode()).hexdigest()[:8]
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            unique_info = f" | UniqueID: {post_number}-{tweet_hash}-{timestamp}"
            enhanced_prompt = f"Create a professional, high-quality, photorealistic image for this Twitter post: '{query}'. The image should visually represent the content and mood of the tweet, with beautiful lighting and environment. Make it look like a professional drone photograph.{unique_info}"

            try:
                # Generate the image using the direct API method
                response = client.models.generate_content(
                    model="gemini-2.0-flash-preview-image-generation",
                    contents=enhanced_prompt,
                    config=types.GenerateContentConfig(response_modalities=['TEXT', 'IMAGE'])
                )
                
                # Process the response
                for part in response.candidates[0].content.parts:
                    if part.inline_data:  # This is the image data
                        # Generate a unique filename using timestamp
                        from datetime import datetime
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"Post_{post_number}_{timestamp}.png"
                        
                        # Create absolute path for the image in AI_GENERATED_IMAGES
                        filepath = os.path.abspath(os.path.join(self.ai_images_dir, filename))
                        
                        # Save to file
                        image = Image.open(BytesIO(part.inline_data.data))
                        image.save(filepath)
                        
                        # Get image dimensions
                        width, height = image.size
                        
                        # Use direct file path without file:// scheme
                        logger.info(f"Successfully generated Gemini 2 Flash image: {filepath}")
                        return {
                            'url': filepath,  # Use direct file path for local file access
                            'thumbnail_url': filepath,
                            'description': f'AI generated image of {query}',
                            'alt_text': f'AI generated image showing {query}',
                            'credit': 'Generated by Google Gemini 2 Flash',
                            'credit_url': None,
                            'source': 'gemini2flash',
                            'width': width,
                            'height': height
                        }
                    elif part.text:
                        logger.info(f"Gemini provided text: {part.text[:100]}...")
                
                logger.error("No image data found in Gemini response")
                return None
                
            except Exception as inner_e:
                logger.error(f"Gemini image generation API call failed: {inner_e}")
                import traceback
                logger.error(f"Detailed API error: {traceback.format_exc()}")
                return None
                
        except Exception as e:
            logger.error(f"Gemini 2 Flash image generation failed: {e}")
            import traceback
            logger.error(f"Detailed error: {traceback.format_exc()}")
            return None
        
    def download_image(self, image_data: Dict) -> Optional[str]:
        """Download image to local cache"""
        if not image_data or image_data['source'] == 'placeholder':
            return None
            
        try:
            url = image_data['url']
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"drone_image_{timestamp}.jpg"
            filepath = self.image_cache_dir / filename
            
            # Save image
            with open(filepath, 'wb') as f:
                f.write(response.content)
                
            logger.info(f"Downloaded image: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to download image: {e}")
            return None
            
    def generate_alt_text(self, image_data: Dict, content: str) -> str:
        """Generate descriptive alt text for accessibility"""
        if image_data.get('alt_text'):
            return image_data['alt_text']
            
        # Extract context from content
        content_lower = content.lower()
        
        alt_components = []
        
        # Drone type
        if 'racing' in content_lower or 'fpv' in content_lower:
            alt_components.append('Racing drone')
        elif 'commercial' in content_lower or 'professional' in content_lower:
            alt_components.append('Commercial drone')
        elif 'military' in content_lower:
            alt_components.append('Military drone')
        else:
            alt_components.append('Drone')
            
        # Activity/context
        if 'flying' in content_lower or 'flight' in content_lower:
            alt_components.append('in flight')
        elif 'build' in content_lower or 'assembly' in content_lower:
            alt_components.append('being assembled')
        elif 'photography' in content_lower or 'camera' in content_lower:
            alt_components.append('with camera equipment')
        elif 'technology' in content_lower:
            alt_components.append('showcasing advanced technology')
            
        # Environment
        if 'outdoor' in content_lower or 'sky' in content_lower:
            alt_components.append('outdoors against sky')
        elif 'indoor' in content_lower or 'workshop' in content_lower:
            alt_components.append('in workshop setting')
            
        return ' '.join(alt_components) + ', ' + image_data.get('description', 'drone-related image')
        
    def create_image_collage(self, images: List[Dict], title: str) -> Optional[Dict]:
        """Create a collage from multiple images (placeholder implementation)"""
        logger.info(f"Creating image collage: {title}")
        
        # This would use PIL/Pillow to create actual collages
        # For now, return metadata for a collage
        return {
            'url': f'https://via.placeholder.com/1200x800/1DA1F2/FFFFFF?text={title.replace(" ", "+")}',
            'thumbnail_url': f'https://via.placeholder.com/600x400/1DA1F2/FFFFFF?text={title.replace(" ", "+")}',
            'description': f'Collage: {title}',
            'alt_text': f'Image collage showing {title.lower()}',
            'credit': 'Generated collage',
            'credit_url': None,
            'source': 'generated',
            'width': 1200,
            'height': 800,
            'is_collage': True,
            'source_images': len(images)
        }
        
    def get_trending_drone_images(self) -> List[Dict]:
        """Get trending drone-related images"""
        trending_queries = [
            'latest drone technology',
            'fpv racing 2025',
            'commercial drone applications',
            'drone photography',
            'autonomous drones'
        ]
        
        images = []
        for query in trending_queries:
            image = self.get_image(query)
            if image:
                images.append(image)
                
        return images
    
    def check_unsplash_rate_limit(self) -> Dict:
        """Check current Unsplash API rate limit status"""
        if not self.unsplash_headers:
            return {'error': 'Unsplash API not configured'}
            
        try:
            # Use a public endpoint to check rate limits - /photos is always accessible
            url = "https://api.unsplash.com/photos"
            params = {'per_page': 1}  # Minimize data transfer
            response = requests.get(url, headers=self.unsplash_headers, params=params, timeout=5)
            
            rate_limit_info = {
                'remaining': response.headers.get('X-Ratelimit-Remaining', 'Unknown'),
                'limit': response.headers.get('X-Ratelimit-Limit', 'Unknown'),
                'reset_time': response.headers.get('X-Ratelimit-Reset', 'Unknown'),
                'status': 'OK' if response.status_code == 200 else f'Error: {response.status_code}'
            }
            
            logger.info(f"Unsplash API rate limit: {rate_limit_info['remaining']}/{rate_limit_info['limit']}")
            return rate_limit_info
            
        except Exception as e:
            logger.error(f"Failed to check Unsplash rate limit: {e}")
            return {'error': str(e)}
    
    def get_unsplash_stats(self) -> Dict:
        """Get Unsplash API usage statistics"""
        stats = {
            'app_name': self.unsplash_app_name,
            'attribution_required': self.unsplash_attribution_required,
            'max_per_hour': self.unsplash_max_per_hour,
            'download_tracking': self.unsplash_download_tracking,
            'api_configured': bool(self.unsplash_key)
        }
        
        # Add rate limit info
        rate_limit = self.check_unsplash_rate_limit()
        stats.update(rate_limit)
        
        return stats
        
    def validate_image_url(self, url: str) -> bool:
        """Validate that image URL is accessible"""
        try:
            response = requests.head(url, timeout=10)
            return response.status_code == 200
        except:
            return False
            
    def get_image_stats(self) -> Dict:
        """Get statistics about cached images"""
        image_files = list(self.image_cache_dir.glob("*.jpg"))
        
        total_size = sum(f.stat().st_size for f in image_files)
        
        return {
            'total_images': len(image_files),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_directory': str(self.image_cache_dir),
            'oldest_image': min((f.stat().st_mtime for f in image_files), default=0),
            'newest_image': max((f.stat().st_mtime for f in image_files), default=0)
        }
        
    def test_unsplash_connection(self) -> Dict:
        """Test the Unsplash API connection and return status"""
        if not self.unsplash_headers:
            return {
                'status': 'error',
                'message': 'Unsplash API key not configured',
                'working': False
            }
            
        try:
            # Test with a simple search query
            test_query = 'drone'
            url = "https://api.unsplash.com/search/photos"
            params = {
                'query': test_query,
                'per_page': 1
            }
            
            logger.info(f"Testing Unsplash API connection...")
            response = requests.get(url, headers=self.unsplash_headers, params=params, timeout=10)
            
            # Check rate limit headers
            rate_limit = {
                'limit': response.headers.get('X-Ratelimit-Limit'),
                'remaining': response.headers.get('X-Ratelimit-Remaining')
            }
            
            if response.status_code == 200:
                data = response.json()
                total_results = data.get('total', 0)
                
                return {
                    'status': 'success',
                    'message': f'API connection successful. Found {total_results} results for "drone"',
                    'rate_limit': rate_limit,
                    'working': True
                }
            else:
                return {
                    'status': 'error',
                    'message': f'API returned status code {response.status_code}',
                    'rate_limit': rate_limit,
                    'working': False
                }
                
        except Exception as e:
            logger.error(f"Unsplash API test failed: {e}")
            return {
                'status': 'error',
                'message': f'Connection error: {str(e)}',
                'working': False
            }
