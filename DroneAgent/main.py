#!/usr/bin/env python3
"""
DroneAgent - AI-powered Twitter drone content automation
CLI Entry Point
"""

import argparse
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.logger import setup_logger
from agent.ideator import ContentIdeator
from agent.writer import ThreadWriter
from agent.visualizer import ImageVisualizer
from agent.scheduler import PostScheduler
from utils.poster import TwitterPoster
import json
import matplotlib.pyplot as plt
from datetime import datetime

logger = setup_logger(__name__)

class DroneAgentCLI:
    def __init__(self):
        self.ideator = ContentIdeator()
        self.writer = ThreadWriter()
        self.visualizer = ImageVisualizer()
        self.scheduler = PostScheduler()
        self.poster = TwitterPoster()
        
    def ideate_content(self):
        """Generate new content ideas"""
        logger.info("🧠 Generating new drone content ideas...")
        ideas = self.ideator.generate_ideas()
        
        for i, idea in enumerate(ideas, 1):
            print(f"\n💡 Idea {i}: {idea['title']}")
            print(f"📝 Description: {idea['description']}")
            print(f"🏷️  Tags: {', '.join(idea['hashtags'])}")
            
        return ideas
    
    def write_thread(self, topic=None):
        """Write a complete Twitter thread with 10-15 tweets"""
        if not topic:
            ideas = self.ideator.generate_ideas(count=1)
            topic = ideas[0]['title']
            
        logger.info(f"✍️ Writing thread about: {topic}")
        thread = self.writer.create_thread(topic, min_tweets=10, max_tweets=15)
        
        print(f"\n📖 Thread Topic: {topic}")
        print("=" * 50)
        print(f"Total tweets: {len(thread['tweets'])} (10-15 required)")
        
        for i, tweet in enumerate(thread['tweets'], 1):
            print(f"\n🐦 Tweet {i}/{len(thread['tweets'])}")
            print(f"Characters: {len(tweet['text'])}/280")
            print(f"Text: {tweet['text']}")
            print(f"Type: {tweet.get('type', 'standard')}")
            print(f"Image: {'Required' if tweet.get('needs_image', False) else 'Optional'}")
            if tweet.get('image'):
                print(f"🖼️  Image: {tweet['image'].get('description', 'No description')}")
                
        return thread
        
    def write_single_tweet(self, topic=None):
        """Write a single optimized tweet in the 250-275 character range"""
        if not topic:
            ideas = self.ideator.generate_ideas(count=1)
            topic = ideas[0]['title']
            
        logger.info(f"✍️ Creating optimized single tweet about: {topic}")
        result = self.writer.create_single_tweet(topic)
        tweet = result['tweets'][0]
        
        print(f"\n📖 Tweet Topic: {topic}")
        print("=" * 50)
        print(f"\n🐦 Optimized Tweet")
        print(f"Characters: {len(tweet['text'])}/280")
        print(f"Text: {tweet['text']}")
        
        return result
    
    def post_now(self, topic=None):
        """Create and post a thread immediately"""
        logger.info("🚀 Creating and posting thread now...")
        
        # Generate content
        thread = self.write_thread(topic)
        
        # Get images
        for tweet in thread['tweets']:
            if tweet.get('needs_image', False):
                image_data = self.visualizer.get_image(tweet['text'])
                tweet['image'] = image_data
        
        # Post thread
        if input("\n🤔 Post this thread? (y/N): ").lower() == 'y':
            success = self.poster.post_thread(thread)
            if success:
                logger.info("✅ Thread posted successfully!")
                self._save_to_history(thread)
            else:
                logger.error("❌ Failed to post thread")
        else:
            logger.info("🛑 Thread posting cancelled")
    
    def schedule_posts(self):
        """Schedule posts for optimal times"""
        logger.info("⏰ Scheduling posts for optimal times...")
        self.scheduler.schedule_daily_posts()
        print("📅 Posts scheduled for 10am and 7pm IST daily")
        print("🌍 Optimized for global audience engagement")
        
    def backtest(self):
        """Show analytics and historical performance"""
        logger.info("📊 Generating backtest analytics...")
        
        try:
            with open('data/history.json', 'r') as f:
                history = json.load(f)
        except FileNotFoundError:
            print("❌ No posting history found")
            return
            
        if not history:
            print("📈 No posts in history yet")
            return
            
        # Basic analytics
        total_posts = len(history)
        total_chars = sum(len(post.get('text', '')) for post in history)
        avg_chars = total_chars / total_posts if total_posts > 0 else 0
        
        print(f"\n📊 DroneAgent Analytics")
        print("=" * 30)
        print(f"Total Posts: {total_posts}")
        print(f"Average Characters: {avg_chars:.1f}")
        print(f"Total Characters: {total_chars:,}")
        
        # Plot posting frequency
        dates = [datetime.fromisoformat(post['timestamp']) for post in history]
        if dates:
            plt.figure(figsize=(12, 6))
            plt.hist([d.date() for d in dates], bins=30, alpha=0.7)
            plt.title('DroneAgent Posting Frequency')
            plt.xlabel('Date')
            plt.ylabel('Posts')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
            
    def _save_to_history(self, thread):
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
            'has_images': any(t.get('image') for t in thread['tweets'])
        })
        
        with open('data/history.json', 'w') as f:
            json.dump(history, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description='DroneAgent - AI Twitter Automation')
    parser.add_argument('--ideate', action='store_true', help='Generate content ideas')
    parser.add_argument('--write', type=str, metavar='TOPIC', help='Write thread about topic')
    parser.add_argument('--single-tweet', type=str, metavar='TOPIC', help='Write single optimized tweet (250-275 chars)')
    parser.add_argument('--post-now', action='store_true', help='Create and post immediately')
    parser.add_argument('--schedule', action='store_true', help='Setup scheduled posting')
    parser.add_argument('--backtest', action='store_true', help='Show analytics')
    parser.add_argument('--gui', action='store_true', help='Launch GUI interface')
    
    args = parser.parse_args()
    
    cli = DroneAgentCLI()
    
    if args.ideate:
        cli.ideate_content()
    elif args.write:
        cli.write_thread(args.write)
    elif args.single_tweet:
        cli.write_single_tweet(args.single_tweet)
    elif args.post_now:
        cli.post_now()
    elif args.schedule:
        cli.schedule_posts()
    elif args.backtest:
        cli.backtest()
    elif args.gui:
        from gui import DroneAgentGUI
        import sys
        from PyQt5.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        gui = DroneAgentGUI()
        gui.show()
        sys.exit(app.exec_())
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
