"""
Improved Content Ideation Module
Generates coherent, non-repetitive drone-related Twitter threads
"""

import os
from typing import List, Dict, Optional
import requests
import json
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ContentIdeator:
    def __init__(self):
        self.load_config()
        self.setup_apis()
        self.used_phrases = set()  # Track used phrases to avoid repetition
        
    def load_config(self):
        """Load configuration from environment variables"""
        from dotenv import load_dotenv
        import os
        from pathlib import Path
        
        # Try to load from project root and multiple possible locations
        env_paths = [
            Path('.env'),  # Current directory
            Path('../.env'),  # One directory up
            Path('../../.env'),  # Two directories up
            Path(os.path.dirname(os.path.abspath(__file__)) + '/../.env'),  # Relative to this file
            Path(os.path.dirname(os.path.abspath(__file__)) + '/../../.env'),  # Relative to this file, one more level up
            Path('d:/OneDrive - Amity University/Desktop/Twitter Auto/.env')  # Absolute path
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(dotenv_path=env_path)
                logger.info(f"Loaded environment variables from {env_path}")
                break
        
        self.perplexity_key = os.getenv('PERPLEXITY_API_KEY')
        if not self.perplexity_key:
            logger.warning("PERPLEXITY_API_KEY environment variable not found")
        
    def setup_apis(self):
        """Initialize API clients"""
        try:
            if not self.perplexity_key or self.perplexity_key == "your_perplexity_api_key_here":
                logger.warning("No valid Perplexity API key found")
        except Exception as e:
            logger.warning(f"API setup error: {e}")
    
    def generate_ideas(self) -> List[Dict]:
        """Generate fresh content ideas using AI based on drone engineering expertise"""
        logger.info("Generating content ideas")
        
        # Try AI generation first
        ai_ideas = self._generate_ai_ideas()
        if ai_ideas:
            return ai_ideas
        
        # Fallback only if AI completely fails
        logger.warning("AI idea generation failed, using minimal fallback")
        return self._get_minimal_fallback_ideas()
    
    def _generate_ai_ideas(self) -> List[Dict]:
        """Generate ideas using AI APIs"""
        prompt = f"""As a Drone Enthusiast and Industry Expert, generate 8 unique Twitter thread ideas.

EXPERTISE AREAS:
- Drone Applications in Everyday Life
- Emerging Drone Technologies
- Creative Uses for Drones
- Business and Hobbyist Insights

REQUIREMENTS:
- Each idea must be unique and engaging
- Focus on creativity and practical applications
- Appeal to a broad audience, including hobbyists and professionals
- Avoid overly technical jargon

FORMAT: Return as JSON array:
[
  {{"title": "Creative topic", "description": "Engaging description for a broad audience"}},
  ...
]

Generate ideas covering: creative projects, market trends, fun applications, and future possibilities."""

        # Try Gemini first (better AI model)
        try:
            import google.genai as genai
            client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=prompt
            )
            
            content = response.candidates[0].content.parts[0].text
            # Extract JSON from response
            json_start = content.find('[')
            json_end = content.rfind(']') + 1
            if json_start != -1 and json_end != -1:
                json_str = content[json_start:json_end]
                ideas = json.loads(json_str)
                logger.info(f"Generated {len(ideas)} ideas using Gemini Pro")
                return self._process_ai_ideas(ideas)
        except Exception as e:
            logger.warning(f"Gemini Pro idea generation failed: {e}")
            
            # Try Gemini Flash as immediate fallback
            try:
                logger.info("Trying Gemini Flash as fallback for idea generation...")
                import google.genai as genai
                client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
                response = client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=prompt
                )
                
                content = response.candidates[0].content.parts[0].text
                # Extract JSON from response
                json_start = content.find('[')
                json_end = content.rfind(']') + 1
                if json_start != -1 and json_end != -1:
                    json_str = content[json_start:json_end]
                    ideas = json.loads(json_str)
                    logger.info(f"Generated {len(ideas)} ideas using Gemini Flash (fallback)")
                    return self._process_ai_ideas(ideas)
            except Exception as flash_e:
                logger.warning(f"Gemini Flash fallback also failed: {flash_e}")

        # Fallback to Perplexity
        if self.perplexity_key:
            try:
                response = requests.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.perplexity_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "sonar",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.8
                    }
                )
                
                if response.status_code == 200:
                    content = response.json()['choices'][0]['message']['content']
                    # Extract JSON from response
                    json_start = content.find('[')
                    json_end = content.rfind(']') + 1
                    if json_start != -1 and json_end != -1:
                        json_str = content[json_start:json_end]
                        ideas = json.loads(json_str)
                        logger.info(f"Generated {len(ideas)} ideas using Perplexity")
                        return self._process_ai_ideas(ideas)
            except Exception as e:
                logger.warning(f"Perplexity idea generation failed: {e}")
        
        return None
    
    def _process_ai_ideas(self, raw_ideas: List[Dict]) -> List[Dict]:
        """Process and validate AI-generated ideas"""
        processed_ideas = []
        
        for idea in raw_ideas:
            if isinstance(idea, dict) and 'title' in idea and 'description' in idea:
                processed_idea = {
                    'title': idea['title'][:80],  # Limit title length
                    'description': idea['description'][:150],  # Limit description length
                    'hashtags': self._generate_hashtags_for_idea(idea['title'])
                }
                processed_ideas.append(processed_idea)
        
        return processed_ideas[:8]  # Return max 8 ideas
    
    def _generate_hashtags_for_idea(self, title: str) -> List[str]:
        """Generate relevant hashtags for an idea"""
        title_lower = title.lower()
        hashtags = []
        
        # Technical hashtags based on content
        if any(word in title_lower for word in ['ai', 'artificial intelligence', 'machine learning']):
            hashtags.extend(['#DroneAI', '#MachineLearning'])
        if any(word in title_lower for word in ['swarm', 'coordination', 'fleet']):
            hashtags.extend(['#DroneSwarm', '#Coordination'])
        if any(word in title_lower for word in ['racing', 'fpv', 'sport']):
            hashtags.extend(['#FPVRacing', '#DroneRacing'])
        if any(word in title_lower for word in ['commercial', 'business', 'enterprise']):
            hashtags.extend(['#CommercialDrones', '#Business'])
        if any(word in title_lower for word in ['delivery', 'logistics']):
            hashtags.extend(['#DroneDelivery', '#Logistics'])
        if any(word in title_lower for word in ['security', 'surveillance', 'monitoring']):
            hashtags.extend(['#DroneSecurity', '#Surveillance'])
        if any(word in title_lower for word in ['agriculture', 'farming', 'crop']):
            hashtags.extend(['#AgriTech', '#PrecisionAg'])
        
        # Always include core drone hashtags
        if not hashtags:
            hashtags = ['#DroneTech', '#UAV']
        else:
            hashtags.insert(0, '#DroneTech')
        
        return hashtags[:3]  # Max 3 hashtags
    
    def _get_minimal_fallback_ideas(self) -> List[Dict]:
        """Minimal fallback ideas if AI fails"""
        return [
            {
                "title": "Advanced Drone Swarm Algorithms in 2025",
                "description": "Latest coordination protocols for multi-drone operations",
                "hashtags": ["#DroneSwarm", "#AI", "#Coordination"]
            },
            {
                "title": "Building Custom FPV Racing Frames",
                "description": "Engineering lightweight carbon fiber designs for competitive racing",
                "hashtags": ["#FPVRacing", "#DroneBuilding", "#Engineering"]
            }
        ]
        
        # If we have Perplexity API, enhance with AI-generated ideas
        # NOTE: This code is disabled until API issues are resolved
        """
        if self.perplexity_key:
            try:
                prompt = '''Generate 6 unique, specific drone content ideas for Twitter threads. 
                Focus on technical aspects, new developments in 2025, and practical applications.
                Format as JSON list of objects with "title" and "description" fields.
                Keep titles under 60 chars and descriptions under 120 chars.'''
                
                raw_content = self._query_perplexity(prompt)
                
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', raw_content, re.DOTALL)
                if json_match:
                    ai_themes = json.loads(json_match.group(1))
                    if isinstance(ai_themes, list) and len(ai_themes) > 0:
                        return ai_themes
                else:
                    logger.warning("Could not extract JSON from Perplexity response, using default themes")
            except Exception as e:
                logger.error(f"Error generating AI ideas: {e}")
        """
            
    def generate_thread_content(self, theme: str, tweet_count: int = 10) -> Dict:
        """Generate a complete Twitter thread with coherent flow"""
        logger.info(f"Generating {tweet_count}-tweet thread about: {theme}")
        
        # Create a focused prompt for thread generation
        prompt = self._create_thread_prompt(theme, tweet_count)
        
        try:
            # Get AI-generated content
            if self.perplexity_key:
                raw_content = self._query_perplexity(prompt)
                thread_data = self._parse_thread_response(raw_content, theme)
            else:
                thread_data = self._generate_fallback_thread(theme, tweet_count)
                
            # Post-process to ensure quality
            thread_data = self._improve_thread_quality(thread_data)
            
            return thread_data
            
        except Exception as e:
            logger.error(f"Error generating thread: {e}")
            return self._generate_fallback_thread(theme, tweet_count)
    
    def _create_thread_prompt(self, theme: str, tweet_count: int) -> str:
        """Create a focused prompt for generating coherent thread content"""
        
        return f"""
        Create a {tweet_count}-tweet Twitter thread about "{theme}" for drone enthusiasts and professionals.

        CRITICAL REQUIREMENTS:
        1. Each tweet must be unique - NO repeated phrases or sentences
        2. Create a logical flow from tweet 1 to tweet {tweet_count}
        3. Keep each tweet under 280 characters
        4. Be educational first, promotional last
        5. Include specific technical details and real examples
        6. Use conversational, engaging tone
        7. End with a clear call-to-action in the final tweet

        THREAD STRUCTURE:
        - Tweet 1: Hook with surprising fact or statistic
        - Tweets 2-3: Context and current state
        - Tweets 4-7: Specific techniques, tips, or insights
        - Tweets 8-9: Future trends or advanced concepts
        - Tweet {tweet_count}: Call-to-action with promotional link

        CONTENT FOCUS FOR "{theme}":
        - Share 3-4 specific, actionable techniques
        - Include real-world examples or case studies
        - Mention current 2025 technology trends
        - Avoid generic marketing language
        - Each tweet should teach something new

        OUTPUT FORMAT:
        Tweet 1: [content]
        Tweet 2: [content]
        ...
        Tweet {tweet_count}: [content]

        FINAL TWEET MUST INCLUDE:
        "🔗 Full guide: https://cryomech01.gumroad.com
        📧 Get early access + updates
        🐦 Follow for daily drone insights
        Drop a 🚁 if you're ready to level up!"
        """
    
    def _query_perplexity(self, prompt: str) -> str:
        """Query Perplexity API using the working pattern"""
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json"
        }
        
        # Combine system and user prompts for better results
        full_prompt = f"""You are an expert drone engineer, have profound knowledge in unmanned aerial systems, PHD in aerospace engineering, have skills of FPV flying, drone building, IOT+Drone systems, cinematography and content creation. Create engaging, educational Twitter threads with unique insights and zero repetition.

{prompt}"""
        
        data = {
            "model": "sonar",  # Using the working model from your example
            "messages": [{"role": "user", "content": full_prompt}],
            "max_tokens": 2000  # Increased for longer thread content
        }
        
        try:
            # Log the API request (without showing the full key)
            masked_key = self.perplexity_key[:8] + "..." if self.perplexity_key and len(self.perplexity_key) > 10 else "[None]"
            logger.info(f"Calling Perplexity API with key: {masked_key}")
            
            response = requests.post(url, json=data, headers=headers, timeout=45)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"Perplexity API error: Status {response.status_code}")
                return f"Error: {response.status_code}"
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Perplexity API request failed: {e}")
            raise
        except (KeyError, json.JSONDecodeError) as e:
            logger.error(f"Unexpected Perplexity API response format: {e}")
            raise
        except Exception as e:
            logger.error(f"Unknown error during Perplexity API call: {e}")
            raise
    
    def _parse_thread_response(self, raw_content: str, theme: str) -> Dict:
        """Parse AI response into structured thread data"""
        tweets = []
        lines = raw_content.strip().split('\n')
        
        current_tweet = ""
        tweet_number = 0
        
        for line in lines:
            line = line.strip()
            
            # Look for tweet markers
            if line.startswith(('Tweet ', 'tweet ', f'{tweet_number + 1}:', f'Tweet {tweet_number + 1}:')):
                # Save previous tweet if exists
                if current_tweet and tweet_number > 0:
                    tweets.append({
                        'number': tweet_number,
                        'content': current_tweet.strip(),
                        'character_count': len(current_tweet.strip()),
                        'needs_image': self._should_include_image(current_tweet, tweet_number)
                    })
                
                # Start new tweet
                tweet_number += 1
                # Extract content after the tweet marker
                content_start = line.find(':')
                if content_start != -1:
                    current_tweet = line[content_start + 1:].strip()
                else:
                    current_tweet = ""
                    
            elif line and not line.startswith('#') and tweet_number > 0:
                # Continue current tweet content
                if current_tweet:
                    current_tweet += " " + line
                else:
                    current_tweet = line
        
        # Don't forget the last tweet
        if current_tweet and tweet_number > 0:
            tweets.append({
                'number': tweet_number,
                'content': current_tweet.strip(),
                'character_count': len(current_tweet.strip()),
                'needs_image': self._should_include_image(current_tweet, tweet_number)
            })
        
        # Ensure we have the right number of tweets
        if len(tweets) == 0:
            # Fallback parsing - split by sentences or paragraphs
            tweets = self._fallback_parse(raw_content)
        
        return {
            'theme': theme,
            'tweets': tweets,
            'total_tweets': len(tweets),
            'generated_at': datetime.now().isoformat(),
            'ai_generated': True
        }
    
    def _fallback_parse(self, content: str) -> List[Dict]:
        """Fallback parsing when structured parsing fails"""
        # Split content into roughly tweet-sized chunks
        sentences = content.replace('\n', ' ').split('. ')
        tweets = []
        current_tweet = ""
        tweet_number = 1
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Check if adding this sentence would exceed Twitter limit
            test_tweet = current_tweet + (" " if current_tweet else "") + sentence
            
            if len(test_tweet) <= 250:  # Leave room for formatting
                current_tweet = test_tweet
            else:
                # Save current tweet and start new one
                if current_tweet:
                    tweets.append({
                        'number': tweet_number,
                        'content': current_tweet.strip() + ("." if not current_tweet.endswith('.') else ""),
                        'character_count': len(current_tweet.strip()),
                        'needs_image': tweet_number % 3 == 1  # Every 3rd tweet gets an image
                    })
                    tweet_number += 1
                    current_tweet = sentence
        
        # Add the last tweet
        if current_tweet:
            tweets.append({
                'number': tweet_number,
                'content': current_tweet.strip() + ("." if not current_tweet.endswith('.') else ""),
                'character_count': len(current_tweet.strip()),
                'needs_image': tweet_number % 3 == 1
            })
        
        return tweets[:10]  # Limit to 10 tweets
    
    def _should_include_image(self, content: str, tweet_number: int) -> bool:
        """Determine if a tweet should include an image"""
        # Include images for:
        # - First tweet (hook)
        # - Every 3rd tweet
        # - Tweets with specific keywords
        image_keywords = ['technique', 'tip', 'example', 'show', 'look', 'see', 'visual', 'photo', 'shot']
        
        return (
            tweet_number == 1 or 
            tweet_number % 3 == 0 or
            any(keyword in content.lower() for keyword in image_keywords)
        )
    
    def _improve_thread_quality(self, thread_data: Dict) -> Dict:
        """Post-process thread to improve quality and remove repetition"""
        tweets = thread_data.get('tweets', [])
        improved_tweets = []
        
        for tweet in tweets:
            content = tweet['content']
            
            # Remove common repetitive phrases
            repetitive_phrases = [
                "Includes premium carrying case for safe transport",
                "Volume discounts available for businesses",
                "Industry-leading warranty covers all components",
                "Limited production run selling out fast",
                "Free training session with every purchase",
                "Compatible with all standard mounting equipment"
            ]
            
            # Remove repetitive content
            for phrase in repetitive_phrases:
                content = content.replace(phrase, "").strip()
            
            # Clean up extra spaces and punctuation
            content = ' '.join(content.split())  # Remove extra whitespace
            content = content.rstrip('.') + '.'  # Ensure proper ending
            
            # Update character count
            tweet['content'] = content
            tweet['character_count'] = len(content)
            
            # Only keep tweets with substantial content
            if len(content) > 50:
                improved_tweets.append(tweet)
        
        thread_data['tweets'] = improved_tweets
        thread_data['total_tweets'] = len(improved_tweets)
        
        return thread_data
    
    def _generate_fallback_thread(self, theme: str, tweet_count: int) -> Dict:
        """Generate high-quality fallback thread when AI fails"""
        
        # Theme-specific expert content
        expert_threads = {
            "The Art of Drone Cinematography: Pro Tips": [
                "🎬 Drone cinematography has evolved from novelty to necessity. What once required $100k helicopter rentals now fits in your backpack. Here's what separates amateur footage from cinematic gold...",
                
                "First rule: Motion tells the story. Static hovering shots scream 'amateur.' Professional pilots use reveal shots - starting close, pulling back to show scale and context.",
                
                "Camera settings matter more than your drone. Shoot in D-Log or flat profiles, 24fps for cinematic feel, 1/48 shutter speed. Always shoot in 4K even if delivering 1080p.",
                
                "Master the 'invisible' movements: slow accelerations, gentle curves, purposeful height changes. Jerky movements break immersion instantly.",
                
                "Lighting is everything. Golden hour isn't just prettier - it's forgiving. Harsh midday sun creates unflattering shadows and blown highlights.",
                
                "Pre-plan your shots with apps like Litchi or DroneDeploy. Knowing your flight path saves battery and ensures smooth, repeatable movements.",
                
                "Sound design matters too. Drone footage needs audio - wind, environment, music. The propeller buzz should never make it to your final edit.",
                
                "Learn these essential shots: dolly zoom, orbital, dronie, tilt reveal, top-down pattern shots. Each serves a specific storytelling purpose.",
                
                "Post-production is where magic happens. Color grading flat profiles, stabilization in post, speed ramping for dramatic effect.",
                
                "Ready to master aerial storytelling? 🚁\n🔗 Full cinematic guide: https://cryomech01.gumroad.com\n📧 Get pro techniques + presets\n🐦 Follow for daily tips\n\nDrop a 🎬 if you're ready!"
            ]
        }
        
        # Get expert content or generate generic
        if theme in expert_threads:
            tweet_contents = expert_threads[theme]
        else:
            tweet_contents = self._generate_generic_thread(theme, tweet_count)
        
        # Structure the response
        tweets = []
        for i, content in enumerate(tweet_contents[:tweet_count], 1):
            tweets.append({
                'number': i,
                'content': content,
                'character_count': len(content),
                'needs_image': i == 1 or i % 3 == 0
            })
        
        return {
            'theme': theme,
            'tweets': tweets,
            'total_tweets': len(tweets),
            'generated_at': datetime.now().isoformat(),
            'ai_generated': False
        }
    
    def _generate_generic_thread(self, theme: str, count: int) -> List[str]:
        """Generate generic but quality thread content"""
        # This would be expanded based on theme
        return [f"Expert insight #{i} about {theme}..." for i in range(1, count + 1)]

# Usage example:
# ideator = ImprovedContentIdeator()
# thread = ideator.generate_thread_content("The Art of Drone Cinematography: Pro Tips")