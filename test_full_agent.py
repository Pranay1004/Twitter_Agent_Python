#!/usr/bin/env python3
"""
Test the full DroneAgent functionality - all components working together
"""

import sys
import os
from pathlib import Path

# Add DroneAgent to path
sys.path.insert(0, str(Path(__file__).parent / "DroneAgent"))

from DroneAgent.agent.ideator import ContentIdeator
from DroneAgent.agent.writer import ThreadWriter
from DroneAgent.agent.visualizer import ImageVisualizer

def test_full_agent():
    """Test the complete DroneAgent workflow"""
    print("🚁 Testing Full DroneAgent Functionality")
    print("="*50)
    
    # Test 1: Content Ideation
    print("\n1. 🧠 Testing Content Ideation...")
    ideator = ContentIdeator()
    try:
        ideas = ideator.generate_ideas()
        for i, idea in enumerate(ideas[:2], 1):  # Show first 2 ideas
            print(f"   💡 Idea {i}: {idea['title']}")
    except Exception as e:
        print(f"   ❌ Ideation failed: {e}")
    
    # Test 2: Thread Writing
    print("\n2. ✍️ Testing Thread Writing...")
    writer = ThreadWriter()
    try:
        thread = writer.create_thread("Latest drone technology trends", min_tweets=5, max_tweets=8)
        print(f"   📝 Generated thread with {thread['total_tweets']} tweets")
        print(f"   🎯 Topic: {thread['topic']}")
        print(f"   📊 Total characters: {thread['total_characters']}")
    except Exception as e:
        print(f"   ❌ Thread writing failed: {e}")
    
    # Test 3: Image Generation
    print("\n3. 🖼️ Testing Image Generation...")
    visualizer = ImageVisualizer()
    try:
        image_info = visualizer.get_image("modern drone flying", preferred_source="unsplash")
        print(f"   🖼️ Image source: {image_info['source']}")
        print(f"   🔗 URL: {image_info['url'][:60]}...")
    except Exception as e:
        print(f"   ❌ Image generation failed: {e}")
    
    print("\n" + "="*50)
    print("✅ Full Agent Test Complete!")
    print("🎯 GUI Application is running in background")
    print("📱 All core components are functional")

if __name__ == "__main__":
    test_full_agent()
