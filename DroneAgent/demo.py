#!/usr/bin/env python3
"""
Sample Content Generator
Demonstrates DroneAgent's content creation capabilities
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agent.ideator import ContentIdeator
from agent.writer import ThreadWriter
from agent.visualizer import ImageVisualizer

def main():
    print("🚁 DroneAgent Sample Content Generation")
    print("=" * 50)
    
    # Initialize components
    ideator = ContentIdeator()
    writer = ThreadWriter()
    visualizer = ImageVisualizer()
    
    print("\n💡 Generating Sample Content Ideas...")
    print("-" * 30)
    
    # Generate sample ideas
    ideas = ideator.generate_ideas(count=3)
    
    for i, idea in enumerate(ideas, 1):
        print(f"\n🧠 Idea {i}:")
        print(f"Title: {idea['title']}")
        print(f"Description: {idea['description']}")
        print(f"Hashtags: {', '.join(idea['hashtags'])}")
    
    print("\n" + "=" * 50)
    print("✍️ Writing Sample Thread...")
    print("-" * 30)
    
    # Write a thread for the first idea
    sample_topic = ideas[0]['title']
    thread = writer.create_thread(sample_topic)
    
    print(f"\n📖 Thread: {sample_topic}")
    print(f"Total tweets: {len(thread['tweets'])}")
    print(f"Total characters: {sum(len(tweet['text']) for tweet in thread['tweets'])}")
    
    for i, tweet in enumerate(thread['tweets'], 1):
        print(f"\n🐦 Tweet {i}/{len(thread['tweets'])}")
        print(f"Characters: {len(tweet['text'])}/280")
        print(f"Text: {tweet['text']}")
        if tweet.get('needs_image'):
            print("🖼️  Needs image: Yes")
    
    print("\n" + "=" * 50)
    print("🖼️ Sample Image Metadata...")
    print("-" * 30)
    
    # Get sample image metadata
    image_data = visualizer.get_image("FPV racing drone in action")
    if image_data:
        print(f"Source: {image_data['source']}")
        print(f"Description: {image_data['description']}")
        print(f"URL: {image_data['url']}")
        print(f"Credit: {image_data['credit']}")
        print(f"Alt text: {visualizer.generate_alt_text(image_data, 'FPV racing content')}")
    
    print("\n" + "=" * 50)
    print("🎯 Promotional Content Sample...")
    print("-" * 30)
    
    # Generate promotional thread
    promo_thread = writer.create_promotional_thread()
    
    for i, tweet in enumerate(promo_thread['tweets'], 1):
        print(f"\n📢 Promo Tweet {i}/{len(promo_thread['tweets'])}")
        print(f"Text: {tweet['text']}")
    
    print("\n" + "=" * 50)
    print("✅ Sample content generation complete!")
    print("\nTo run DroneAgent:")
    print("  GUI: python main.py --gui")
    print("  CLI: python main.py --ideate")

if __name__ == "__main__":
    main()
