"""
Thread Writer Module
Converts content ideas into Twitter threads with live AI generation
"""

import re
import random
import requests
import os
import json
from typing import List, Dict, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import setup_logger
from utils.config import load_config
from google import genai
from google.genai import types

logger = setup_logger(__name__)

class ThreadWriter:
    def __init__(self):
        self.max_tweet_length = 280
        self.hashtag_limit = 2
        self.openrouter_key = os.getenv('OPENROUTER_API_KEY')
            
    def generate_thread_with_ai(self, topic: str, tweet_count: int = 8) -> List[Dict]:
        """Generate thread content using AI APIs"""
        
        prompt = f"""Create a high-quality {tweet_count}-tweet Twitter thread about: {topic}

STRICT REQUIREMENTS:

CONTENT STYLE:

TONE: Professional yet engaging, authoritative but accessible

FORMAT: Return ONLY valid JSON array:
[
  {{"text": "🧵 THREAD: [specific compelling hook with real detail about {topic}] #DroneTech", "type": "intro", "needs_image": true}},
  {{"text": "[unique technical insight with specifics about {topic}] #Innovation", "type": "content", "needs_image": true}},
  {{"text": "[different specific application/case study]", "type": "content", "needs_image": true}},
  {{"text": "[technical specifications or metrics]", "type": "content", "needs_image": true}},
  {{"text": "[industry challenge and solution]", "type": "content", "needs_image": true}},
  {{"text": "[future trend or prediction with data]", "type": "content", "needs_image": true}},
  {{"text": "[practical implementation advice]", "type": "content", "needs_image": true}},
  {{"text": "[conclusion with engaging question or CTA] #Tech", "type": "conclusion", "needs_image": true}}
]

Topic: {topic}"""

        # Try Gemini Pro first
        
        
    def generate_thread_with_ai(self, topic: str, tweet_count: int = 8, model: str = "OpenRouter Pro") -> List[Dict]:
        """Generate thread content using selected AI model"""
        prompt = f"""Create a high-quality {tweet_count}-tweet Twitter thread about: {topic}
STRICT REQUIREMENTS:
...existing prompt...
Topic: {topic}"""
        tweets = []
        if model == "OpenRouter Pro":
            key = os.getenv('OPENROUTER_API_KEY')
            if key:
                try:
                    response = requests.post(
                        "https://openrouter.ai/api/thread",
                        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                        json={"prompt": prompt}
                    )
                    if response.status_code == 200:
                        tweets = response.json().get('tweets', [])
                        return [
                            {'text': tweet, 'type': 'content', 'needs_image': i == 0, 'tweet_number': i + 1}
                            for i, tweet in enumerate(tweets)
                        ]
                except Exception as e:
                    logger.warning(f"OpenRouter thread generation failed: {e}")
        elif model == "Perplexity Pro":
            key = os.getenv('PERPLEXITY_API_KEY')
            if key:
                try:
                    response = requests.post(
                        "https://api.perplexity.ai/chat/completions",
                        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                        json={"model": "sonar", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
                    )
                    if response.status_code == 200:
                        content = response.json()['choices'][0]['message']['content']
                        tweets = json.loads(content)
                        return [
                            {'text': tweet['text'], 'type': tweet.get('type', 'content'), 'needs_image': i == 0, 'tweet_number': i + 1}
                            for i, tweet in enumerate(tweets)
                        ]
                except Exception as e:
                    logger.warning(f"Perplexity thread generation failed: {e}")
        elif model == "Gemini Pro":
            key = os.getenv('GEMINI_API_KEY')
            if key:
                try:
                    import google.genai as genai
                    client = genai.Client(api_key=key)
                    response = client.models.generate_content(
                        model="gemini-2.5-pro",
                        contents=prompt
                    )
                    content = response.candidates[0].content.parts[0].text
                    tweets = json.loads(content)
                    return [
                        {'text': tweet['text'], 'type': tweet.get('type', 'content'), 'needs_image': i == 0, 'tweet_number': i + 1}
                        for i, tweet in enumerate(tweets)
                    ]
                except Exception as e:
                    logger.warning(f"Gemini thread generation failed: {e}")
        # Fallback: minimal static thread
        logger.warning("All AI thread generation failed, using minimal fallback")
        tweets = self.create_fallback_thread(topic, tweet_count)
        return {
            'topic': topic,
            'tweets': tweets,
            'total_tweets': len(tweets),
            'total_characters': sum(len(tweet['text']) for tweet in tweets),
            'hashtags': [],
            'has_images': any(tweet.get('needs_image', False) for tweet in tweets)
        }
    
    def process_ai_tweets(self, raw_tweets: List[Dict]) -> List[Dict]:
        """Process and validate AI-generated tweets"""
        processed_tweets = []
        
        for i, tweet in enumerate(raw_tweets):
            if isinstance(tweet, dict) and 'text' in tweet:
                text = tweet['text']
                
                # Optimize length to 260-280 characters
                text = self.optimize_tweet_length(text, 260, 280)
                
                processed_tweet = {
                    'text': text,
                    'type': tweet.get('type', 'content'),
                    'needs_image': tweet.get('needs_image', i == 0),  # First tweet gets image
                    'tweet_number': i + 1
                }
                processed_tweets.append(processed_tweet)
                logger.info(f"Tweet optimized to {len(text)} characters")
        
        # Add mandatory Gumroad post at the end
        gumroad_post = {
            'text': "Ready to join the cockpit? 🛩️🔗 Check my full story: https://cryomech01.gumroad.com 📧 Get early access + launch updates 🐦 Follow for daily drone insights and build logs Who's ready to architect autonomous systems that actually work? Drop a 🚁 if you're in! #DroneArchitect #Notion",
            'type': 'gumroad',
            'needs_image': True,
            'tweet_number': len(processed_tweets) + 1
        }
        processed_tweets.append(gumroad_post)
        
        return processed_tweets
    
    def create_fallback_thread(self, topic: str, tweet_count: int) -> List[Dict]:
        """Create a high-quality fallback thread if AI fails"""
        tweets = []
        
        # Extract key concept from topic for better content
        key_concept = topic.split(':')[0] if ':' in topic else topic
        
        # Intro tweet
        intro = f"🧵 THREAD: {key_concept} is reshaping the drone industry. Here are the game-changing insights every professional needs to know about this breakthrough technology 🚁"
        tweets.append({
            'text': self.optimize_tweet_length(intro),
            'type': 'intro',
            'needs_image': True,
            'tweet_number': 1
        })
        
        # High-quality content tweets with specific insights
        content_insights = [
            f"Market data shows {key_concept} reduces operational costs by 35-60% while increasing mission success rates to 98.7%. The ROI typically breaks even within 8-12 months of implementation 📊",
            f"Real deployment: Major logistics companies using {key_concept} report 40% faster delivery times and 90% reduction in last-mile costs. UPS alone saved $200M last year 🚚",
            f"Technical breakthrough: Latest {key_concept} systems feature 120-minute flight times, 15km range, and AI-powered obstacle avoidance with 99.9% reliability in urban environments ⚡",
            f"Industry shift: {key_concept} adoption in agriculture increased 300% in 2024. Farmers using precision monitoring see 25% higher yields and 50% less pesticide use 🌾",
            f"Safety revolution: {key_concept} enables remote operations in hazardous environments. Oil & gas inspections now 85% safer with zero worker exposure to dangerous conditions 🛡️",
            f"Future outlook: Analysts predict {key_concept} market will reach $58B by 2027. Early adopters positioning for 10x competitive advantage in next 24 months 📈",
            f"Implementation tip: Start with pilot programs targeting specific use cases. Companies that begin with clear ROI metrics see 3x faster scaling and better stakeholder buy-in 🎯"
        ]
        
        for i in range(1, tweet_count):
            if i-1 < len(content_insights):
                content = content_insights[i-1]
            else:
                # Additional insights if needed
                content = f"Advanced insight: {key_concept} integration with IoT and 5G networks creates unprecedented data collection capabilities, enabling predictive maintenance and real-time optimization 🔮"
            
            tweets.append({
                'text': self.optimize_tweet_length(content),
                'type': 'content', 
                'needs_image': True,
                'tweet_number': i + 1
            })
        
        # Add mandatory Gumroad post at the end
        gumroad_post = {
            'text': "Ready to join the cockpit? 🛩️🔗 Check my full story: https://cryomech01.gumroad.com 📧 Get early access + launch updates 🐦 Follow for daily drone insights and build logs Who's ready to architect autonomous systems that actually work? Drop a 🚁 if you're in! #DroneArchitect #Notion",
            'type': 'gumroad',
            'needs_image': True,
            'tweet_number': len(tweets) + 1
        }
        tweets.append(gumroad_post)
        
        return tweets
        
    def create_thread(self, topic: str, content_tweets: int = 8) -> Dict:
        """Create a complete Twitter thread from a topic using live AI generation"""
        logger.info(f"Creating thread about: {topic} with {content_tweets} content tweets + 1 promotional")
        
        # Use AI to generate exactly 8 content tweets
        tweets = self.generate_thread_with_ai(topic, content_tweets)
        
        # If AI failed, create fallback but still limit to 8
        if not tweets or len(tweets) != content_tweets:
            logger.warning("AI generation failed or returned wrong count, using improved fallback")
            tweets = self.create_fallback_thread(topic, content_tweets)
        
        # Extract hashtags from all tweets
        all_hashtags = []
        for tweet in tweets:
            hashtags = re.findall(r'#\w+', tweet['text'])
            all_hashtags.extend(hashtags)
        
        # Remove duplicates and limit
        unique_hashtags = list(dict.fromkeys(all_hashtags))[:self.hashtag_limit]
        
        return {
            'topic': topic,
            'tweets': tweets,
            'total_tweets': len(tweets),
            'total_characters': sum(len(tweet['text']) for tweet in tweets),
            'hashtags': unique_hashtags,
            'has_images': any(tweet.get('needs_image', False) for tweet in tweets)
        }
    
    def optimize_tweet_length(self, text: str, min_length: int = 260, max_length: int = 280) -> str:
        """Optimize tweet length to fit 260-280 character range with hashtags"""
        
        # First, ensure hashtags are at the end of the text
        hashtags = re.findall(r'#\w+', text)
        clean_text = re.sub(r'#\w+', '', text).strip()
        
        # Limit to 1-2 hashtags and ensure they're short (max 15 chars total)
        if hashtags:
            total_chars = sum(len(tag) for tag in hashtags)
            filtered_hashtags = []
            
            for tag in hashtags[:2]:  # Limit to first 2 hashtags
                if sum(len(t) for t in filtered_hashtags) + len(tag) <= 15:
                    filtered_hashtags.append(tag)
                
            # If we have no hashtags after filtering, keep the shortest one
            if not filtered_hashtags and hashtags:
                filtered_hashtags = [min(hashtags, key=len)]
                
            hashtags = filtered_hashtags
        
        # If no hashtags, add a short one
        if not hashtags:
            hashtags = ["#Drone"]
        
        # Combine hashtags with a space
        hashtag_text = " " + " ".join(hashtags)
        
        # Available space for main content
        available_space = max_length - len(hashtag_text)
        
        # If too long, trim carefully
        if len(clean_text) > available_space:
            # Try to trim at sentence boundary
            sentences = clean_text.split('. ')
            trimmed = sentences[0]
            for sentence in sentences[1:]:
                if len(trimmed + '. ' + sentence) <= available_space - 3:
                    trimmed += '. ' + sentence
                else:
                    break
            
            if len(trimmed) < min_length - len(hashtag_text):
                # If trimming too much, just cut at max available space
                clean_text = clean_text[:available_space-3] + "..."
            else:
                clean_text = trimmed
        
        # If too short, add relevant content
        if len(clean_text) + len(hashtag_text) < min_length:
            # Add descriptive words if still short - avoid generic phrases
            fillers = [
                " Professional applications show measurable ROI.",
                " Technical specifications exceed industry standards.",
                " Implementation requires strategic planning approach."
            ]
            
            for filler in fillers:
                if len(clean_text + filler) + len(hashtag_text) <= max_length:
                    clean_text += filler
                    break
        
        # Combine clean text with hashtags at the end
        result = clean_text.strip() + hashtag_text
        
        # Final length check
        if len(result) > max_length:
            available_space = max_length - len(hashtag_text)
            result = clean_text[:available_space-3].strip() + "..." + hashtag_text
            
        return result
    
    def create_single_tweet(self, topic: str) -> Dict:
        """Create a single tweet about a topic using AI"""
        logger.info(f"Creating single tweet about: {topic}")
        
        result = self.create_single_tweet_ai(topic)
        
        return {
            'topic': topic,
            'tweets': [result],
            'total_tweets': 1,
            'total_characters': len(result['text']),
            'hashtags': result.get('hashtags', []),
            'has_images': result.get('needs_image', True)
        }
    
    def create_single_tweet_ai(self, topic: str) -> Dict:
        """Create a single tweet about a topic using AI"""
        logger.info(f"Creating single tweet about: {topic}")
        
        prompt = f"""Create a single engaging Twitter tweet about: {topic}

REQUIREMENTS:
- 260-280 characters (Twitter optimized)
- Include relevant emojis
- Focus on drone technology from expert perspective
- Make it informative and engaging
- Include 2-3 SHORT hashtags like #AI #Drones #Tech
- Write as aerospace engineer/drone expert

Return just the tweet text, nothing else."""

        # Try Gemini Pro first
        if hasattr(self, 'gemini_client'):
            try:
                response = self.gemini_client.models.generate_content(
                    model="gemini-2.5-pro",
                    contents=prompt
                )
                
                text = response.candidates[0].content.parts[0].text.strip()
                text = self.optimize_tweet_length(text, 260, 280)
                
                return {
                    'text': text,
                    'type': 'single',
                    'needs_image': True,
                    'hashtags': re.findall(r'#\w+', text)
                }
            except Exception as e:
                logger.warning(f"Gemini Pro failed for single tweet: {e}")
                
                # Try Gemini Flash as immediate fallback
                try:
                    logger.info("Trying Gemini Flash as fallback for single tweet...")
                    response = self.gemini_client.models.generate_content(
                        model="gemini-2.0-flash-exp",
                        contents=prompt
                    )
                    
                    text = response.candidates[0].content.parts[0].text.strip()
                    text = self.optimize_tweet_length(text, 260, 280)
                    
                    return {
                        'text': text,
                        'type': 'single',
                        'needs_image': True,
                        'hashtags': re.findall(r'#\w+', text)
                    }
                except Exception as flash_e:
                    logger.warning(f"Gemini Flash fallback for single tweet also failed: {flash_e}")
        
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
                        "temperature": 0.7
                    }
                )
                
                if response.status_code == 200:
                    text = response.json()['choices'][0]['message']['content'].strip()
                    text = self.optimize_tweet_length(text, 260, 280)
                    
                    return {
                        'text': text,
                        'type': 'single',
                        'needs_image': True,
                        'hashtags': re.findall(r'#\w+', text)
                    }
            except Exception as e:
                logger.warning(f"Perplexity failed for single tweet: {e}")
        
        # Final fallback
        fallback_text = f"🚁 Exploring {topic} - the future of drone technology is here! Innovation in aerial systems continues to transform industries worldwide. #DroneTech #Innovation #Future"
        return {
            'text': self.optimize_tweet_length(fallback_text, 260, 280),
            'type': 'single',
            'needs_image': True,
            'hashtags': ['#DroneTech', '#Innovation']
        }
    
    def create_promotional_thread(self) -> Dict:
        """Create a promotional thread using AI"""
        topic = "Professional drone systems and optimization guide"
        tweets = self.generate_thread_with_ai(topic, 4)
        
        # Ensure the last tweet has the Gumroad link
        if tweets:
            tweets[-1]['text'] = "🔗 Get the complete guide: https://cryomech01.gumroad.com\n📧 Early access + updates\n🚁 Join the community of builders!\n\n#Drone #Architect #Notion"
            
        return {
            'topic': 'Promotional Content',
            'tweets': tweets,
            'total_tweets': len(tweets),
            'total_characters': sum(len(tweet['text']) for tweet in tweets),
            'hashtags': ['#Drone', '#Architect', '#Notion'],
            'is_promotional': True,
            'has_images': True
        }
