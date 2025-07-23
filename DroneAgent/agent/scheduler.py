"""
Post Scheduler Module
Handles timing and scheduling of Twitter posts for optimal engagement
"""

import schedule
import time
import pytz
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import threading
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import setup_logger
from utils.config import load_config
from utils.config import load_config

from .ideator import ContentIdeator
from .writer import ThreadWriter
from .visualizer import ImageVisualizer
from utils.poster import TwitterPoster

logger = setup_logger(__name__)

class PostScheduler:
    def __init__(self):
        self.timezone = pytz.timezone('Asia/Kolkata')  # IST timezone
        self.post_times = ['10:00', '19:00']  # 10am and 7pm IST
        self.is_running = False
        self.scheduler_thread = None
        
        # Initialize components
        self.ideator = ContentIdeator()
        self.writer = ThreadWriter()
        self.visualizer = ImageVisualizer()
        self.poster = TwitterPoster()
        self.poster.authenticate_oauth2()
        
        self.load_schedule_config()
        
    def load_schedule_config(self):
        """Load scheduling configuration"""
        import yaml
        try:
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
                
            scheduling = config.get('scheduling', {})
            self.timezone = pytz.timezone(scheduling.get('timezone', 'Asia/Kolkata'))
            self.post_times = scheduling.get('post_times', ['10:00', '19:00'])
            self.auto_post = scheduling.get('auto_post', False)
            
        except Exception as e:
            logger.warning(f"Could not load schedule config: {e}")
            
    def schedule_daily_posts(self):
        """Set up daily posting schedule"""
        logger.info("Setting up daily posting schedule...")
        
        # Clear existing schedule
        schedule.clear()
        
        # Schedule posts for each time
        for post_time in self.post_times:
            schedule.every().day.at(post_time).do(self._create_and_post_thread)
            logger.info(f"Scheduled daily post at {post_time} IST")
            
        # Start scheduler thread if not running
        if not self.is_running:
            self.start_scheduler()
            
    def start_scheduler(self):
        """Start the background scheduler"""
        if self.is_running:
            logger.warning("Scheduler already running")
            return
            
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("Scheduler started in background thread")
        
    def stop_scheduler(self):
        """Stop the background scheduler"""
        self.is_running = False
        schedule.clear()
        logger.info("Scheduler stopped")
        
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)
                
    def _create_and_post_thread(self):
        """Create and post a thread automatically"""
        try:
            logger.info("🤖 Auto-creating and posting thread...")
            
            # Generate content idea
            ideas = self.ideator.generate_ideas(count=1)
            if not ideas:
                logger.error("No ideas generated")
                return
                
            topic = ideas[0]['title']
            logger.info(f"Selected topic: {topic}")
            
            # Check if we should post promotional content
            if self._should_post_promotional():
                logger.info("Creating promotional thread")
                thread = self.writer.create_promotional_thread()
            else:
                # Create regular thread
                thread = self.writer.create_thread(topic)
                
                # Add images to tweets that need them
                for tweet in thread['tweets']:
                    if tweet.get('needs_image', False):
                        image_data = self.visualizer.get_image(tweet['text'])
                        if image_data:
                            tweet['image'] = image_data
            
            # Post the thread
            success = self.poster.post_thread(thread)
            
            if success:
                logger.info("✅ Scheduled thread posted successfully!")
                self._save_to_history(thread)
                self._update_post_stats()
            else:
                logger.error("❌ Failed to post scheduled thread")
                
        except Exception as e:
            logger.error(f"Error in scheduled posting: {e}")
            
    def _should_post_promotional(self) -> bool:
        """Determine if we should post promotional content"""
        try:
            with open('data/history.json', 'r') as f:
                history = json.load(f)
                
            # Post promotional content every 7th post
            if len(history) % 7 == 0 and len(history) > 0:
                return True
                
        except (FileNotFoundError, json.JSONDecodeError):
            pass
            
        return False
        
    def get_optimal_posting_times(self) -> List[Dict]:
        """Calculate optimal posting times for global engagement"""
        
        # IST times and their global equivalents
        times_analysis = []
        
        for post_time in self.post_times:
            # Parse IST time
            hour, minute = map(int, post_time.split(':'))
            ist_time = self.timezone.localize(
                datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
            )
            
            # Convert to major timezones
            utc_time = ist_time.astimezone(pytz.UTC)
            et_time = ist_time.astimezone(pytz.timezone('US/Eastern'))
            pt_time = ist_time.astimezone(pytz.timezone('US/Pacific'))
            gmt_time = ist_time.astimezone(pytz.timezone('Europe/London'))
            
            analysis = {
                'ist_time': post_time,
                'utc_time': utc_time.strftime('%H:%M'),
                'eastern_time': et_time.strftime('%H:%M'),
                'pacific_time': pt_time.strftime('%H:%M'),
                'london_time': gmt_time.strftime('%H:%M'),
                'engagement_score': self._calculate_engagement_score(ist_time),
                'target_audience': self._get_target_audience(ist_time)
            }
            
            times_analysis.append(analysis)
            
        return times_analysis
        
    def _calculate_engagement_score(self, time: datetime) -> int:
        """Calculate estimated engagement score for a time"""
        hour = time.hour
        
        # Peak engagement hours (based on global Twitter usage)
        peak_hours = {
            6: 70,   # 10am IST = 6am-12am EST (good for US morning)
            7: 75,
            8: 80,
            9: 85,
            13: 90,  # 7pm IST = 1:30pm UTC (good for EU afternoon + US morning)
            14: 85,
            15: 80,
            16: 75
        }
        
        return peak_hours.get(hour, 50)  # Default score of 50
        
    def _get_target_audience(self, time: datetime) -> str:
        """Identify primary target audience for posting time"""
        utc_hour = time.astimezone(pytz.UTC).hour
        
        if 12 <= utc_hour <= 16:
            return "US Morning + EU Afternoon"
        elif 4 <= utc_hour <= 8:
            return "US Evening + Asia Morning"
        elif 20 <= utc_hour <= 23:
            return "EU Evening + US Afternoon"
        else:
            return "Global Mixed"
            
    def schedule_one_time_post(self, delay_minutes: int, topic: str = None):
        """Schedule a one-time post after delay"""
        post_time = datetime.now() + timedelta(minutes=delay_minutes)
        
        def delayed_post():
            self._create_and_post_thread_with_topic(topic)
            
        schedule.every().day.at(post_time.strftime('%H:%M')).do(delayed_post).tag('onetime')
        
        logger.info(f"Scheduled one-time post for {post_time.strftime('%H:%M')}")
        
    def _create_and_post_thread_with_topic(self, topic: str = None):
        """Create and post thread with specific topic"""
        try:
            if topic:
                thread = self.writer.create_thread(topic)
            else:
                ideas = self.ideator.generate_ideas(count=1)
                thread = self.writer.create_thread(ideas[0]['title'])
                
            # Add images
            for tweet in thread['tweets']:
                if tweet.get('needs_image', False):
                    image_data = self.visualizer.get_image(tweet['text'])
                    if image_data:
                        tweet['image'] = image_data
                        
            # Post thread
            success = self.poster.post_thread(thread)
            
            if success:
                logger.info("One-time post successful!")
                self._save_to_history(thread)
            
            # Remove one-time schedule
            schedule.clear('onetime')
            
        except Exception as e:
            logger.error(f"One-time post failed: {e}")
            
    def get_next_post_time(self) -> Optional[datetime]:
        """Get the next scheduled post time"""
        try:
            now = datetime.now(self.timezone)
            today = now.date()
            
            for post_time in self.post_times:
                hour, minute = map(int, post_time.split(':'))
                scheduled_time = self.timezone.localize(
                    datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute))
                )
                
                if scheduled_time > now:
                    return scheduled_time
                    
            # If no more posts today, return first post tomorrow
            tomorrow = today + timedelta(days=1)
            hour, minute = map(int, self.post_times[0].split(':'))
            return self.timezone.localize(
                datetime.combine(tomorrow, datetime.min.time().replace(hour=hour, minute=minute))
            )
            
        except Exception as e:
            logger.error(f"Error calculating next post time: {e}")
            return None
            
    def get_posting_statistics(self) -> Dict:
        """Get posting frequency and timing statistics"""
        try:
            with open('data/history.json', 'r') as f:
                history = json.load(f)
                
            if not history:
                return {'total_posts': 0, 'message': 'No posting history'}
                
            # Analyze posting patterns
            post_times = []
            post_hours = []
            
            for post in history:
                try:
                    timestamp = datetime.fromisoformat(post['timestamp'])
                    post_times.append(timestamp)
                    post_hours.append(timestamp.hour)
                except:
                    continue
                    
            if not post_times:
                return {'total_posts': 0, 'message': 'No valid timestamps'}
                
            # Calculate statistics
            total_posts = len(post_times)
            posts_last_7_days = len([t for t in post_times if (datetime.now() - t).days <= 7])
            posts_last_30_days = len([t for t in post_times if (datetime.now() - t).days <= 30])
            
            # Most common posting hour
            most_common_hour = max(set(post_hours), key=post_hours.count) if post_hours else 0
            
            return {
                'total_posts': total_posts,
                'posts_last_7_days': posts_last_7_days,
                'posts_last_30_days': posts_last_30_days,
                'average_per_day': round(posts_last_30_days / 30, 1),
                'most_common_hour': most_common_hour,
                'posting_consistency': self._calculate_consistency(post_times),
                'next_scheduled': self.get_next_post_time()
            }
            
        except Exception as e:
            logger.error(f"Error getting posting statistics: {e}")
            return {'error': str(e)}
            
    def _calculate_consistency(self, post_times: List[datetime]) -> str:
        """Calculate posting consistency score"""
        if len(post_times) < 7:
            return "Insufficient data"
            
        # Calculate average time between posts
        intervals = []
        for i in range(1, len(post_times)):
            interval = (post_times[i] - post_times[i-1]).total_seconds() / 3600  # hours
            intervals.append(interval)
            
        if intervals:
            avg_interval = sum(intervals) / len(intervals)
            if avg_interval <= 15:  # Less than 15 hours average
                return "Very Consistent"
            elif avg_interval <= 24:  # Less than 24 hours average
                return "Consistent"
            elif avg_interval <= 48:  # Less than 48 hours average
                return "Moderate"
            else:
                return "Inconsistent"
                
        return "Unknown"
        
    def _save_to_history(self, thread: Dict):
        """Save thread to posting history"""
        try:
            with open('data/history.json', 'r') as f:
                history = json.load(f)
        except FileNotFoundError:
            history = []
            
        history.append({
            'timestamp': datetime.now().isoformat(),
            'topic': thread.get('topic', 'Unknown'),
            'tweet_count': len(thread['tweets']),
            'total_chars': sum(len(t['text']) for t in thread['tweets']),
            'hashtags': thread.get('hashtags', []),
            'has_images': any(t.get('image') for t in thread['tweets']),
            'scheduled': True,
            'posting_time': datetime.now(self.timezone).strftime('%H:%M')
        })
        
        with open('data/history.json', 'w') as f:
            json.dump(history, f, indent=2)
            
    def _update_post_stats(self):
        """Update posting statistics"""
        # This could integrate with Twitter API to get actual engagement metrics
        # For now, just log the successful post
        logger.info("📊 Post statistics updated")
