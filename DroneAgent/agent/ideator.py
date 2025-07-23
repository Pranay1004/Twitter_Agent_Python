"""
Advanced Content Ideation Module
Generates creative, non-repetitive drone industry content using multiple AI backends
"""

import os
import json
import logging
import random
import re
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import requests
from dotenv import load_dotenv

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class ContentConfig:
    """Configuration class for content generation parameters"""
    max_title_length: int = 100
    max_description_length: int = 280
    max_tweet_length: int = 280
    min_tweets_per_thread: int = 5
    max_tweets_per_thread: int = 15
    timeout_seconds: int = 30
    max_retries: int = 3


class APIBackend:
    """Base class for AI API backends"""
    
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    def generate_content(self, prompt: str, system_prompt: str = None) -> str:
        """Generate content using the AI backend"""
        raise NotImplementedError("Subclasses must implement generate_content")


class GeminiBackend(APIBackend):
    """Google Gemini API backend"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-pro"):
        super().__init__(api_key, model_name)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
    
    def generate_content(self, prompt: str, system_prompt: str = None) -> str:
        url = f"{self.base_url}/{self.model_name}:generateContent"
        
        content_parts = []
        if system_prompt:
            content_parts.append({"text": f"System: {system_prompt}\n\nUser: {prompt}"})
        else:
            content_parts.append({"text": prompt})
        
        payload = {
            "contents": [{"parts": content_parts}],
            "generationConfig": {
                "temperature": 0.8,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048,
            }
        }
        
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}
        
        response = requests.post(url, json=payload, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        if "candidates" in data and data["candidates"]:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            raise ValueError("No valid response from Gemini API")


class PerplexityBackend(APIBackend):
    """Perplexity API backend"""
    
    def __init__(self, api_key: str, model_name: str = "llama-3.1-sonar-large-128k-online"):
        super().__init__(api_key, model_name)
        self.base_url = "https://api.perplexity.ai/chat/completions"
    
    def generate_content(self, prompt: str, system_prompt: str = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2048,
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"]


class OpenRouterBackend(APIBackend):
    """OpenRouter API backend"""
    
    def __init__(self, api_key: str, model_name: str = "anthropic/claude-3.5-sonnet"):
        super().__init__(api_key, model_name)
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def generate_content(self, prompt: str, system_prompt: str = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.8,
            "max_tokens": 2048,
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/drone-content-generator",
            "X-Title": "Drone Industry Content Generator"
        }
        
        response = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"]


class ContentDeduplicator:
    """Manages content deduplication and uniqueness tracking"""
    
    def __init__(self):
        self.used_phrases = set()
        self.used_topics = set()
        self.content_hashes = set()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def add_used_content(self, content: str, content_type: str = "general"):
        """Add content to the deduplication tracking"""
        content_hash = hashlib.md5(content.lower().strip().encode()).hexdigest()
        self.content_hashes.add(content_hash)
        
        # Extract key phrases for phrase-level deduplication
        phrases = self._extract_key_phrases(content)
        self.used_phrases.update(phrases)
        
        if content_type == "topic":
            self.used_topics.add(content.lower().strip())
    
    def is_content_unique(self, content: str, similarity_threshold: float = 0.8) -> bool:
        """Check if content is sufficiently unique"""
        content_hash = hashlib.md5(content.lower().strip().encode()).hexdigest()
        if content_hash in self.content_hashes:
            return False
        
        # Check phrase-level similarity
        content_phrases = self._extract_key_phrases(content)
        if not content_phrases:
            return True
        
        overlap_count = sum(1 for phrase in content_phrases if phrase in self.used_phrases)
        similarity = overlap_count / len(content_phrases)
        
        return similarity < similarity_threshold
    
    def _extract_key_phrases(self, content: str) -> List[str]:
        """Extract key phrases from content for deduplication"""
        # Remove common words and extract meaningful phrases
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Clean and tokenize
        clean_content = re.sub(r'[^\w\s]', ' ', content.lower())
        words = clean_content.split()
        
        # Extract 2-3 word phrases that don't consist entirely of stop words
        phrases = []
        for i in range(len(words) - 1):
            phrase = ' '.join(words[i:i+2])
            if not all(word in stop_words for word in words[i:i+2]):
                phrases.append(phrase)
        
        for i in range(len(words) - 2):
            phrase = ' '.join(words[i:i+3])
            if not all(word in stop_words for word in words[i:i+3]):
                phrases.append(phrase)
        
        return phrases


class ContentIdeator:
    """Generates creative content ideas for the drone industry"""
    
    def __init__(self, config: ContentConfig = None):
        self.config = config or ContentConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.deduplicator = ContentDeduplicator()
        self._load_environment()
        self._setup_logging()
    
    def _load_environment(self):
        """Load environment variables from multiple possible locations"""
        env_paths = ['.env', '../.env', '../../.env', os.path.expanduser('~/.env')]
        
        for path in env_paths:
            if os.path.exists(path):
                load_dotenv(path)
                self.logger.info(f"Loaded environment from {path}")
                break
        else:
            self.logger.warning("No .env file found in standard locations")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _get_backend(self, model_name: str) -> APIBackend:
        """Create appropriate backend based on model name"""
        model_lower = model_name.lower()
        
        if 'gemini' in model_lower:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            
            if 'flash' in model_lower:
                return GeminiBackend(api_key, "gemini-1.5-flash")
            else:
                return GeminiBackend(api_key, "gemini-1.5-pro")
        
        elif 'perplexity' in model_lower:
            api_key = os.getenv('PERPLEXITY_API_KEY')
            if not api_key:
                raise ValueError("PERPLEXITY_API_KEY not found in environment variables")
            return PerplexityBackend(api_key)
        
        elif 'openrouter' in model_lower:
            api_key = os.getenv('OPENROUTER_API_KEY')
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY not found in environment variables")
            return OpenRouterBackend(api_key)
        
        else:
            raise ValueError(f"Unsupported model: {model_name}")
    
    def generate_ideas(self, model_name: str = "Gemini Pro", num_ideas: int = 10) -> Dict[str, Any]:
        """Generate creative content ideas using specified model"""
        logger.info(f"Generating {num_ideas} ideas using {model_name}")
        
        try:
            backend = self._get_backend(model_name)
            
            system_prompt = """You are an expert drone industry analyst and content creator. Generate highly specific, technical, and engaging content ideas that provide real value to drone professionals, enthusiasts, and businesses. 

Focus on:
- Latest technological innovations and breakthroughs
- Practical applications and use cases
- Regulatory developments and compliance
- Market trends and business opportunities
- Technical tutorials and educational content
- Industry insights and expert perspectives

Avoid generic advice and focus on actionable, specific insights."""
            
            prompt = f"""Generate {num_ideas} unique and creative content ideas for the drone industry. Each idea should be highly specific, technically accurate, and provide genuine value to the drone community.

Return ONLY a valid JSON array in this exact format:
[
  {{
    "title": "Specific, engaging title (max 100 chars)",
    "description": "Detailed description with technical depth and specific insights (max 280 chars)",
    "category": "One of: Technology, Business, Regulations, Applications, Education, Market Analysis",
    "complexity": "One of: Beginner, Intermediate, Advanced",
    "keywords": ["keyword1", "keyword2", "keyword3"]
  }}
]

Make each idea unique, technically rich, and avoid generic statements. Focus on current trends, emerging technologies, and practical applications."""
            
            response = backend.generate_content(prompt, system_prompt)
            ideas = self._parse_ideas_response(response)
            
            if not ideas:
                self.logger.warning(f"No valid ideas parsed from {model_name}, using fallback")
                return self._generate_fallback_ideas(num_ideas)
            
            # Process and enhance ideas
            processed_ideas = self._process_and_enhance_ideas(ideas)
            
            return {
                'ideas': processed_ideas,
                'total_ideas': len(processed_ideas),
                'model_used': model_name,
                'generated_at': datetime.now().isoformat(),
                'categories': list(set(idea.get('category', 'General') for idea in processed_ideas)),
                'has_technical_content': True
            }
            
        except Exception as e:
            self.logger.error(f"Error generating ideas with {model_name}: {str(e)}")
            return self._generate_fallback_ideas(num_ideas)
    
    def _parse_ideas_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse AI response into structured ideas"""
        try:
            # Clean response to extract JSON
            cleaned_response = self._extract_json_from_response(response)
            ideas = json.loads(cleaned_response)
            
            if not isinstance(ideas, list):
                self.logger.error("Response is not a list")
                return []
            
            valid_ideas = []
            for idea in ideas:
                if isinstance(idea, dict) and 'title' in idea and 'description' in idea:
                    # Ensure required fields exist
                    processed_idea = {
                        'title': str(idea.get('title', ''))[:self.config.max_title_length],
                        'description': str(idea.get('description', ''))[:self.config.max_description_length],
                        'category': idea.get('category', 'General'),
                        'complexity': idea.get('complexity', 'Intermediate'),
                        'keywords': idea.get('keywords', [])
                    }
                    
                    # Check uniqueness
                    if self.deduplicator.is_content_unique(processed_idea['title']):
                        self.deduplicator.add_used_content(processed_idea['title'], 'topic')
                        valid_ideas.append(processed_idea)
            
            return valid_ideas
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Error parsing ideas response: {str(e)}")
            return []
    
    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON array from AI response"""
        # Try to find JSON array in response
        json_patterns = [
            r'\[[\s\S]*\]',  # Match array
            r'\{[\s\S]*\}',  # Match object
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response)
            if matches:
                return matches[0]
        
        # If no JSON found, return the response as-is
        return response.strip()
    
    def _process_and_enhance_ideas(self, ideas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and enhance ideas with additional metadata"""
        enhanced_ideas = []
        
        for idea in ideas:
            # Generate hashtags based on keywords and content
            hashtags = self._generate_hashtags(idea)
            
            # Add metadata
            enhanced_idea = {
                **idea,
                'hashtags': hashtags,
                'estimated_engagement': self._estimate_engagement_potential(idea),
                'content_pillars': self._identify_content_pillars(idea),
                'target_audience': self._identify_target_audience(idea)
            }
            
            enhanced_ideas.append(enhanced_idea)
        
        return enhanced_ideas
    
    def _generate_hashtags(self, idea: Dict[str, Any]) -> List[str]:
        """Generate relevant hashtags for an idea"""
        base_hashtags = ['#drone', '#drones', '#UAV', '#droneindustry']
        
        # Category-specific hashtags
        category_hashtags = {
            'Technology': ['#dronetech', '#innovation', '#technology'],
            'Business': ['#dronebusiness', '#commercialdrones', '#dronesolutions'],
            'Regulations': ['#droneregulations', '#FAA', '#dronesafety'],
            'Applications': ['#droneapplications', '#droneuse', '#dronesolutions'],
            'Education': ['#droneeducation', '#dronetraining', '#learntofly'],
            'Market Analysis': ['#dronemarket', '#droneinvestment', '#dronetrends']
        }
        
        hashtags = base_hashtags.copy()
        category = idea.get('category', 'General')
        if category in category_hashtags:
            hashtags.extend(category_hashtags[category])
        
        # Add keyword-based hashtags
        keywords = idea.get('keywords', [])
        for keyword in keywords[:3]:  # Limit to 3 keyword hashtags
            hashtag = f"#{keyword.lower().replace(' ', '').replace('-', '')}"
            if hashtag not in hashtags:
                hashtags.append(hashtag)
        
        return hashtags[:8]  # Limit total hashtags
    
    def _estimate_engagement_potential(self, idea: Dict[str, Any]) -> str:
        """Estimate engagement potential based on content characteristics"""
        score = 0
        
        # Check for trending keywords
        trending_keywords = [
            'AI', 'autonomous', 'delivery', 'inspection', 'mapping', 
            'agriculture', 'surveillance', 'racing', 'FPV', '4K', '8K'
        ]
        
        content = f"{idea.get('title', '')} {idea.get('description', '')}".lower()
        
        for keyword in trending_keywords:
            if keyword.lower() in content:
                score += 1
        
        # Complexity bonus
        if idea.get('complexity') == 'Advanced':
            score += 2
        elif idea.get('complexity') == 'Intermediate':
            score += 1
        
        # Category bonus
        high_engagement_categories = ['Technology', 'Applications']
        if idea.get('category') in high_engagement_categories:
            score += 1
        
        if score >= 4:
            return "High"
        elif score >= 2:
            return "Medium"
        else:
            return "Low"
    
    def _identify_content_pillars(self, idea: Dict[str, Any]) -> List[str]:
        """Identify content pillars for the idea"""
        pillars = []
        
        content = f"{idea.get('title', '')} {idea.get('description', '')}".lower()
        
        pillar_keywords = {
            'Education': ['tutorial', 'guide', 'learn', 'how to', 'beginner', 'training'],
            'Innovation': ['new', 'latest', 'breakthrough', 'cutting-edge', 'advanced', 'future'],
            'Business': ['roi', 'profit', 'business', 'commercial', 'investment', 'market'],
            'Safety': ['safety', 'regulation', 'compliance', 'legal', 'risk', 'secure'],
            'Entertainment': ['racing', 'fpv', 'photography', 'videography', 'fun', 'hobby']
        }
        
        for pillar, keywords in pillar_keywords.items():
            if any(keyword in content for keyword in keywords):
                pillars.append(pillar)
        
        return pillars if pillars else ['General']
    
    def _identify_target_audience(self, idea: Dict[str, Any]) -> List[str]:
        """Identify target audience for the idea"""
        audiences = []
        
        content = f"{idea.get('title', '')} {idea.get('description', '')}".lower()
        complexity = idea.get('complexity', 'Intermediate')
        
        audience_indicators = {
            'Professionals': ['commercial', 'business', 'professional', 'enterprise', 'industry'],
            'Hobbyists': ['hobby', 'fun', 'recreational', 'personal', 'diy'],
            'Developers': ['software', 'programming', 'code', 'development', 'API'],
            'Pilots': ['pilot', 'flying', 'flight', 'control', 'navigation'],
            'Beginners': ['beginner', 'start', 'introduction', 'basic', 'first time']
        }
        
        for audience, keywords in audience_indicators.items():
            if any(keyword in content for keyword in keywords):
                audiences.append(audience)
        
        # Add based on complexity
        if complexity == 'Beginner' and 'Beginners' not in audiences:
            audiences.append('Beginners')
        elif complexity == 'Advanced' and 'Professionals' not in audiences:
            audiences.append('Professionals')
        
        return audiences if audiences else ['General Audience']
    
    def _generate_fallback_ideas(self, num_ideas: int) -> Dict[str, Any]:
        """Generate fallback ideas when AI fails"""
        fallback_templates = [
            {
                "title": "Advanced Drone Mapping Techniques for {industry}",
                "description": "Explore cutting-edge photogrammetry and LiDAR integration for precision {application} with sub-centimeter accuracy and automated workflow optimization.",
                "category": "Technology",
                "industries": ["Construction", "Agriculture", "Mining", "Infrastructure"],
                "applications": ["surveying", "monitoring", "inspection", "analysis"]
            },
            {
                "title": "ROI Analysis: Commercial Drone Deployment in {sector}",
                "description": "Comprehensive cost-benefit analysis of drone implementation for {use_case}, including equipment costs, training investment, and projected savings.",
                "category": "Business",
                "sectors": ["Real Estate", "Insurance", "Security", "Logistics"],
                "use_cases": ["property assessment", "claims processing", "perimeter monitoring", "inventory management"]
            },
            {
                "title": "Regulatory Update: {regulation} Impact on Drone Operations",
                "description": "Latest {regulation} requirements for commercial drone pilots, including compliance strategies and operational adaptations for continued legal flight operations.",
                "category": "Regulations",
                "regulations": ["Part 107", "Remote ID", "BVLOS", "Urban Air Mobility"]
            },
            {
                "title": "Technical Deep-dive: {technology} in Modern Drones",
                "description": "Engineering analysis of {technology} implementation, performance characteristics, and practical applications in professional drone operations.",
                "category": "Technology",
                "technologies": ["AI-powered obstacle avoidance", "Swarm intelligence", "Edge computing", "Advanced sensor fusion"]
            }
        ]
        
        ideas = []
        for i in range(num_ideas):
            template = random.choice(fallback_templates)
            
            # Fill template with random choices
            title = template["title"]
            description = template["description"]
            
            for key, values in template.items():
                if key in ["title", "description", "category"]:
                    continue
                
                placeholder = f"{{{key[:-1]}}}"  # Remove 's' from plural keys
                if placeholder in title:
                    title = title.replace(placeholder, random.choice(values))
                if placeholder in description:
                    description = description.replace(placeholder, random.choice(values))
            
            idea = {
                "title": title,
                "description": description,
                "category": template["category"],
                "complexity": random.choice(["Intermediate", "Advanced"]),
                "keywords": self._extract_keywords_from_text(f"{title} {description}")
            }
            
            ideas.append(idea)
        
        processed_ideas = self._process_and_enhance_ideas(ideas)
        
        return {
            'ideas': processed_ideas,
            'total_ideas': len(processed_ideas),
            'model_used': 'Fallback Generator',
            'generated_at': datetime.now().isoformat(),
            'categories': list(set(idea.get('category', 'General') for idea in processed_ideas)),
            'has_technical_content': True
        }
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract keywords from text for fallback ideas"""
        drone_keywords = [
            'mapping', 'surveying', 'inspection', 'photography', 'videography',
            'agriculture', 'construction', 'security', 'delivery', 'racing',
            'FPV', 'autonomous', 'AI', 'sensors', 'gimbal', 'battery',
            'regulations', 'Part107', 'commercial', 'professional'
        ]
        
        text_lower = text.lower()
        found_keywords = [kw for kw in drone_keywords if kw.lower() in text_lower]
        
        return found_keywords[:5] if found_keywords else ['drone', 'UAV', 'technology']
            
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
    
    def get_content_statistics(self) -> Dict[str, Any]:
        """Get statistics about generated content"""
        return {
            'total_generated': self.deduplicator.get_usage_count(),
            'unique_topics': len(self.deduplicator.used_content.get('topic', set())),
            'unique_hashtags': len(self.deduplicator.used_content.get('hashtag', set())),
            'backends_used': list(self.backends.keys()),
            'last_generation': getattr(self, '_last_generation_time', None)
        }
    
    def clear_content_history(self) -> None:
        """Clear content history for fresh start"""
        self.deduplicator.clear_history()
        self.logger.info("Content history cleared")
    
    def set_generation_preferences(self, preferences: Dict[str, Any]) -> None:
        """Set user preferences for content generation"""
        if 'categories' in preferences:
            self.config.preferred_categories = preferences['categories']
        if 'complexity' in preferences:
            self.config.preferred_complexity = preferences['complexity']
        if 'max_ideas' in preferences:
            self.config.max_ideas_per_request = preferences['max_ideas']
        
        self.logger.info(f"Updated generation preferences: {preferences}")
    
    def validate_idea_quality(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and score idea quality"""
        score = 0
        issues = []
        
        # Check title quality
        title = idea.get('title', '')
        if len(title) < 10:
            issues.append("Title too short")
        elif len(title) > self.config.max_title_length:
            issues.append("Title too long")
        else:
            score += 1
        
        # Check description quality
        description = idea.get('description', '')
        if len(description) < 20:
            issues.append("Description too brief")
        elif len(description) > self.config.max_description_length:
            issues.append("Description too long")
        else:
            score += 1
        
        # Check for drone relevance
        content = f"{title} {description}".lower()
        drone_terms = ['drone', 'uav', 'quadcopter', 'multirotor', 'aerial', 'flight', 'aviation']
        if any(term in content for term in drone_terms):
            score += 1
        else:
            issues.append("Low drone relevance")
        
        # Check uniqueness
        if self.deduplicator.is_content_unique(title):
            score += 1
        else:
            issues.append("Similar content already generated")
        
        return {
            'score': score,
            'max_score': 4,
            'quality_rating': 'High' if score >= 3 else 'Medium' if score >= 2 else 'Low',
            'issues': issues,
            'passed': score >= 2
        }

# Usage example:
# ideator = ContentIdeator()
# ideas = ideator.generate_ideas(num_ideas=5, model="gemini")
# thread = ideator.generate_thread_content("The Art of Drone Cinematography: Pro Tips")