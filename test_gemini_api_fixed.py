import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# Test text models
for model_name in ['gemini-2.0-flash-preview-image-generation', 'gemini-2.5-flash-lite-preview-06-17']:
    try:
        response = client.models.generate_content(model=model_name, contents="Generate a short paragraph about drone technology")
        print(f"✅ {model_name}:")
        print(response.candidates[0].content.parts[0].text)
        break
    except: continue

# Test image generation with new API
try:
    contents = 'Create a professional drone flying over mountains at sunset with a person holding the remote controller in the foreground'
    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=contents,
        config=types.GenerateContentConfig(response_modalities=['TEXT', 'IMAGE'])
    )
    
    for part in response.candidates[0].content.parts:
        if part.text:
            print(f"✅ Image description: {part.text}")
        elif part.inline_data:
            image = Image.open(BytesIO(part.inline_data.data))
            image.save('drone-controller.png')
            image.show()
            print("✅ Drone image generated and displayed")
except Exception as e:
    print(f"Image generation failed: {e}")

print("\n🤖 Type message or 'quit':")
while True:
    user_input = input("You: ")
    if user_input.lower() == 'quit': break
    try:
        # Use the lighter model for chat to avoid quota issues
        response = client.models.generate_content(model="gemini-2.5-flash-lite-preview-06-17", contents=user_input)
        print(f"Gemini: {response.candidates[0].content.parts[0].text}")
    except Exception as e:
        print(f"Error: {e}")
        # Fallback to image generation model if needed
        try:
            response = client.models.generate_content(model="gemini-2.0-flash-preview-image-generation", contents=user_input)
            print(f"Gemini: {response.candidates[0].content.parts[0].text}")
        except:
            print("Both models failed. Check quota or try again later.")
