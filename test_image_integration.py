import os
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

load_dotenv()

# Test Pexels API
try:
    response = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": os.getenv('PEXELS_API_KEY')},
        params={"query": "octacopter flying hexacopter", "per_page": 1}
    )
    photo_url = response.json()['photos'][0]['src']['medium']
    print(f"✅ Pexels: {photo_url}")
except: print("❌ Pexels failed")

# Test Unsplash API
try:
    response = requests.get(
        "https://api.unsplash.com/search/photos",
        headers={"Authorization": f"Client-ID {os.getenv('UNSPLASH_ACCESS_KEY')}"},
        params={"query": "drone swarm", "per_page": 1}
    )
    photo_url = response.json()['results'][0]['urls']['small']
    print(f"✅ Unsplash: {photo_url}")
except: print("❌ Unsplash failed")

# Test Gemini Flash Image Generation
try:
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents="swarm of drones",
        config=types.GenerateContentConfig(response_modalities=['IMAGE', 'TEXT'])
    )
    
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            image = Image.open(BytesIO(part.inline_data.data))
            image.save('gemini-drone.png')
            image.show()
            print("✅ Gemini Flash: Image generated and saved as gemini-drone.png")
            break
except Exception as e:
    print(f"❌ Gemini Flash failed: {e}")

print("\nImage integration test complete!")

# Run the test and display results
if __name__ == "__main__":
    print("\n" + "="*50)
    print("IMAGE INTEGRATION TEST RESULTS")
    print("="*50)
    print("Pexels API: ✅ Working" if 'pexels' in locals() else "Pexels API: Status shown above")
    print("Unsplash API: ✅ Working" if 'unsplash' in locals() else "Unsplash API: Status shown above") 
    print("Gemini Flash: ✅ Working" if 'gemini' in locals() else "Gemini Flash: Status shown above")
    print("="*50)
