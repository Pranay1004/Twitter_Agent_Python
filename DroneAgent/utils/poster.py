"""
Twitter Poster Module
Handles posting tweets and threads to Twitter using the Twitter API v2
"""

import os
import tweepy
from typing import List, Dict, Optional
import time
import requests
from pathlib import Path

from .logger import setup_logger, log_thread_post, log_api_usage

logger = setup_logger(__name__)

class TwitterPoster:
    def __init__(self):
        self.load_credentials()
        self.setup_api()
        
    def load_credentials(self):
        """Load Twitter/X API credentials from environment"""
        from dotenv import load_dotenv
        load_dotenv()
        self.x_client_id = os.getenv('X_CLIENT_ID')
        self.x_client_secret = os.getenv('X_CLIENT_SECRET')
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        # Validate credentials
        missing_creds = []
        for name, value in [
            ('X_CLIENT_ID', self.x_client_id),
            ('X_CLIENT_SECRET', self.x_client_secret),
            ('API_KEY', self.api_key),
            ('API_SECRET', self.api_secret),
            ('ACCESS_TOKEN', self.access_token),
            ('ACCESS_TOKEN_SECRET', self.access_token_secret),
            ('BEARER_TOKEN', self.bearer_token)
        ]:
            if not value:
                missing_creds.append(name)
        if missing_creds:
            logger.warning(f"Missing Twitter/X credentials: {', '.join(missing_creds)}")

    def authenticate_oauth2(self):
        """Authenticate with Twitter/X API using OAuth 2.0 Client ID/Secret"""
        token_url = "https://api.twitter.com/oauth2/token"
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.x_client_id,
            'client_secret': self.x_client_secret
        }
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            token_info = response.json()
            self.bearer_token = token_info.get('access_token')
            logger.info("Authenticated with Twitter/X using OAuth 2.0 client credentials.")
        else:
            logger.error(f"OAuth 2.0 authentication failed: {response.text}")
            
    def setup_api(self):
        """Initialize Twitter API clients"""
        try:
            # Twitter API v2 client
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )
            
            # Twitter API v1.1 for media upload (required for images)
            auth = tweepy.OAuth1UserHandler(
                self.api_key,
                self.api_secret,
                self.access_token,
                self.access_token_secret
            )
            
            self.api_v1 = tweepy.API(auth, wait_on_rate_limit=True)
            
            logger.info("Twitter API clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API: {e}")
            self.client = None
            self.api_v1 = None
            
    def test_connection(self) -> bool:
        """Test Twitter API connection"""
        if not self.client:
            return False
            
        try:
            start_time = time.time()
            user = self.client.get_me()
            response_time = time.time() - start_time
            
            if user and user.data:
                logger.info(f"Connected as @{user.data.username}")
                log_api_usage("Twitter", "get_me", True, response_time)
                return True
            else:
                log_api_usage("Twitter", "get_me", False, response_time)
                return False
                
        except Exception as e:
            logger.error(f"Twitter connection test failed: {e}")
            log_api_usage("Twitter", "get_me", False)
            return False
            
    def post_thread(self, thread_data: Dict, dry_run: bool = False) -> bool:
        """Post a complete thread to Twitter"""
        if not self.client:
            logger.error("Twitter client not initialized")
            return False
            
        if dry_run:
            logger.info("🧪 DRY RUN: Thread would be posted")
            self._log_thread_preview(thread_data)
            return True
            
        try:
            tweets = thread_data.get('tweets', [])
            if not tweets:
                logger.error("No tweets in thread data")
                return False
                
            logger.info(f"🚀 Posting thread with {len(tweets)} tweets...")
            
            posted_tweets = []
            reply_to_id = None
            
            for i, tweet_data in enumerate(tweets):
                try:
                    # Handle image upload if needed
                    media_ids = None
                    if tweet_data.get('image'):
                        media_ids = self._upload_image(tweet_data['image'])
                        
                    # Post tweet
                    tweet_text = tweet_data['text']
                    
                    # Add image credit if needed
                    if tweet_data.get('image') and tweet_data['image'].get('credit'):
                        credit = tweet_data['image']['credit']
                        if len(tweet_text + f"\n\n{credit}") <= 280:
                            tweet_text += f"\n\n{credit}"
                    
                    response = self.client.create_tweet(
                        text=tweet_text,
                        in_reply_to_tweet_id=reply_to_id,
                        media_ids=media_ids
                    )
                    
                    if response.data:
                        posted_tweets.append(response.data)
                        reply_to_id = response.data['id']
                        logger.info(f"✅ Posted tweet {i+1}/{len(tweets)}")
                        
                        # Wait between tweets to avoid rate limits
                        if i < len(tweets) - 1:
                            time.sleep(2)
                    else:
                        logger.error(f"❌ Failed to post tweet {i+1}")
                        break
                        
                except Exception as e:
                    logger.error(f"Error posting tweet {i+1}: {e}")
                    break
                    
            success = len(posted_tweets) == len(tweets)
            
            if success:
                logger.info(f"🎉 Successfully posted complete thread ({len(posted_tweets)} tweets)")
                first_tweet_url = f"https://twitter.com/user/status/{posted_tweets[0]['id']}"
                logger.info(f"🔗 Thread URL: {first_tweet_url}")
            else:
                logger.warning(f"⚠️ Partial thread posted ({len(posted_tweets)}/{len(tweets)} tweets)")
                
            log_thread_post(thread_data, success)
            return success
            
        except Exception as e:
            logger.error(f"Failed to post thread: {e}")
            log_thread_post(thread_data, False)
            return False
            
    def _upload_image(self, image_data: Dict) -> Optional[List[str]]:
        """Upload image and return media IDs"""
        if not self.api_v1:
            logger.warning("Twitter API v1.1 not available for image upload")
            return None
            
        try:
            image_url = image_data.get('url')
            if not image_url:
                return None
                
            # Handle different image sources
            if image_url.startswith('file://'):
                image_path = image_url[7:]
            elif image_url.startswith('http'):
                response = requests.get(image_url, timeout=30)
                response.raise_for_status()
                temp_file = Path("data/images/temp_upload.jpg")
                temp_file.parent.mkdir(parents=True, exist_ok=True)
                with open(temp_file, 'wb') as f:
                    f.write(response.content)
                image_path = str(temp_file)
            else:
                image_path = image_url
                
            # Validate file exists
            if not os.path.exists(image_path):
                logger.error(f"Image file not found for upload: {image_path}")
                return None
                
            # Upload to Twitter
            media = self.api_v1.media_upload(image_path)
            
            # Add alt text if available
            alt_text = image_data.get('alt_text') or image_data.get('description')
            if alt_text and len(alt_text) <= 1000:  # Twitter alt text limit
                self.api_v1.create_media_metadata(
                    media.media_id,
                    alt_text=alt_text[:1000]
                )
                
            logger.info(f"📸 Uploaded image: {media.media_id}")
            
            # Clean up temp file
            if image_url.startswith('http') and temp_file.exists():
                temp_file.unlink()
                
            return [media.media_id]
            
        except Exception as e:
            logger.error(f"Failed to upload image: {e}")
            return None
            
    def post_single_tweet(self, text: str, image_url: str = None, dry_run: bool = False) -> Optional[str]:
        """Post a single tweet"""
        if not self.client:
            logger.error("Twitter client not initialized")
            return None
            
        if dry_run:
            logger.info(f"🧪 DRY RUN: Would post tweet: {text[:50]}...")
            return "dry_run_tweet_id"
            
        try:
            media_ids = None
            
            if image_url:
                image_data = {'url': image_url}
                media_ids = self._upload_image(image_data)
                
            response = self.client.create_tweet(
                text=text,
                media_ids=media_ids
            )
            
            if response.data:
                tweet_id = response.data['id']
                logger.info(f"✅ Posted single tweet: {tweet_id}")
                return tweet_id
            else:
                logger.error("Failed to post single tweet")
                return None
                
        except Exception as e:
            logger.error(f"Error posting single tweet: {e}")
            return None
            
    def get_account_info(self) -> Optional[Dict]:
        """Get current account information"""
        if not self.client:
            return None
            
        try:
            user = self.client.get_me(
                user_fields=['public_metrics', 'created_at', 'verified']
            )
            
            if user and user.data:
                return {
                    'username': user.data.username,
                    'name': user.data.name,
                    'id': user.data.id,
                    'followers': user.data.public_metrics['followers_count'],
                    'following': user.data.public_metrics['following_count'],
                    'tweets': user.data.public_metrics['tweet_count'],
                    'verified': user.data.verified,
                    'created_at': user.data.created_at
                }
                
        except Exception as e:
            logger.error(f"Failed to get account info: {e}")
            
        return None
        
    def get_recent_tweets(self, count: int = 10) -> List[Dict]:
        """Get recent tweets from account"""
        if not self.client:
            return []
            
        try:
            # Get current user ID
            me = self.client.get_me()
            if not me or not me.data:
                return []
                
            user_id = me.data.id
            
            # Get recent tweets
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=min(count, 100),
                tweet_fields=['created_at', 'public_metrics', 'context_annotations']
            )
            
            if tweets and tweets.data:
                return [
                    {
                        'id': tweet.id,
                        'text': tweet.text,
                        'created_at': tweet.created_at,
                        'retweets': tweet.public_metrics['retweet_count'],
                        'likes': tweet.public_metrics['like_count'],
                        'replies': tweet.public_metrics['reply_count']
                    }
                    for tweet in tweets.data
                ]
                
        except Exception as e:
            logger.error(f"Failed to get recent tweets: {e}")
            
        return []
        
    def _log_thread_preview(self, thread_data: Dict):
        """Log thread preview for dry run"""
        tweets = thread_data.get('tweets', [])
        
        logger.info(f"📖 Thread Preview: {thread_data.get('topic', 'Unknown')}")
        logger.info("=" * 50)
        
        for i, tweet in enumerate(tweets, 1):
            logger.info(f"Tweet {i}/{len(tweets)} ({len(tweet['text'])} chars)")
            logger.info(f"Text: {tweet['text'][:100]}...")
            if tweet.get('image'):
                logger.info(f"Image: {tweet['image'].get('description', 'Included')}")
            logger.info("-" * 30)
            
    def delete_tweet(self, tweet_id: str) -> bool:
        """Delete a tweet by ID"""
        if not self.client:
            return False
            
        try:
            response = self.client.delete_tweet(tweet_id)
            if response.data and response.data.get('deleted'):
                logger.info(f"🗑️ Deleted tweet: {tweet_id}")
                return True
            else:
                logger.error(f"Failed to delete tweet: {tweet_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting tweet {tweet_id}: {e}")
            return False
            
    def get_api_limits(self) -> Dict:
        """Get current API rate limit status"""
        # This would require additional API calls to check limits
        # For now, return placeholder data
        return {
            'tweet_limit': '300 per 15 minutes',
            'upload_limit': '300 per 15 minutes',
            'current_usage': 'Unknown',
            'reset_time': 'Unknown'
        }
