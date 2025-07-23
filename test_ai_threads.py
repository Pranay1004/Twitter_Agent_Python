#!/usr/bin/env python3
"""
Test the new AI-powered thread generation
"""

import sys
import os
from pathlib import Path

# Add DroneAgent to path
sys.path.insert(0, str(Path(__file__).parent))

from DroneAgent.agent.writer import ThreadWriter

def test_ai_thread_generation():
    """Test AI-powered thread generation"""
    print("🤖 Testing AI-Powered Thread Generation")
    print("="*50)
    
    writer = ThreadWriter()
    
    # Test topics
    topics = [
        "Drone swarm coordination algorithms",
        "Commercial drone delivery systems",
        "FPV racing drone builds"
    ]
    
    for i, topic in enumerate(topics, 1):
        print(f"\n{i}. Testing: {topic}")
        try:
            thread = writer.create_thread(topic, content_tweets=7)
            print(f"   ✅ Generated {thread['total_tweets']} tweets")
            print(f"   📝 Characters: {thread['total_characters']}")
            print(f"   🎯 First tweet: {thread['tweets'][0]['text'][:100]}...")
            print(f"   🏷️ Hashtags: {thread['hashtags']}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    print("\n" + "="*50)
    print("✅ AI Thread Generation Test Complete!")

if __name__ == "__main__":
    test_ai_thread_generation()
