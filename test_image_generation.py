"""
Test script to verify Gemini image generation works
"""

import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Add the project directory to the path
sys.path.append("DroneAgent")

from DroneAgent.agent.visualizer import ImageVisualizer

def main():
    print("🧪 Testing image generation...")
    
    # Load environment variables
    load_dotenv()
    
    # Initialize the visualizer
    visualizer = ImageVisualizer()
    
    # Test Gemini image generation directly
    print("\n🤖 Testing Gemini image generation:")
    gemini_image = visualizer._generate_gemini_image("drone flying over mountains at sunset")
    
    if gemini_image:
        print(f"✅ Gemini image generation successful!")
        print(f"🖼️ Image saved at: {gemini_image['url']}")
    else:
        print("❌ Gemini image generation failed")
    
    # Test Unsplash image retrieval
    print("\n📸 Testing Unsplash image retrieval:")
    unsplash_image = visualizer._search_unsplash("drone flying over mountains")
    
    if unsplash_image:
        print(f"✅ Unsplash image retrieval successful!")
        print(f"🖼️ Image URL: {unsplash_image['url']}")
    else:
        print("❌ Unsplash image retrieval failed")
    
    # Test Pexels image retrieval
    print("\n📸 Testing Pexels image retrieval:")
    pexels_image = visualizer._search_pexels("drone flying over mountains")
    
    if pexels_image:
        print(f"✅ Pexels image retrieval successful!")
        print(f"🖼️ Image URL: {pexels_image['url']}")
    else:
        print("❌ Pexels image retrieval failed")
    
    # Test complete image distribution
    print("\n🔄 Testing image distribution for a thread:")
    
    # Create a mock thread with 10 tweets
    mock_thread = [
        {"text": f"Tweet {i} about drones", "needs_image": True}
        for i in range(1, 11)
    ]
    
    # Get images for the thread
    thread_with_images = visualizer.get_images_for_thread(mock_thread)
    
    # Count sources
    sources = {}
    for tweet in thread_with_images:
        if "image" in tweet:
            source = tweet["image"].get("source", "unknown")
            sources[source] = sources.get(source, 0) + 1
    
    print(f"🔢 Image source distribution: {sources}")
    
    print("\n✅ Testing complete!")

if __name__ == "__main__":
    main()
