#!/usr/bin/env python3
"""
Test the new AI-powered idea generation
"""

import sys
import os
from pathlib import Path

# Add DroneAgent to path
sys.path.insert(0, str(Path(__file__).parent))

from DroneAgent.agent.ideator import ContentIdeator

def test_ai_idea_generation():
    """Test AI-powered idea generation"""
    print("🧠 Testing AI-Powered Idea Generation")
    print("="*60)
    
    ideator = ContentIdeator()
    
    try:
        ideas = ideator.generate_ideas()
        print(f"✅ Generated {len(ideas)} unique ideas")
        
        for i, idea in enumerate(ideas, 1):
            print(f"\n{i}. 💡 {idea['title']}")
            print(f"   📝 {idea['description']}")
            if 'hashtags' in idea:
                print(f"   🏷️ {', '.join(idea['hashtags'])}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    print("\n" + "="*60)
    print("✅ AI Idea Generation Test Complete!")

if __name__ == "__main__":
    test_ai_idea_generation()
