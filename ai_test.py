import os
from google import genai
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ API key not found in .env file")
    print("Make sure you have a .env file with: GEMINI_API_KEY=AIzaSyDbu6YJ7iG3BVInqyX6GC7WXb_Cp0c4K5U")
else:
    try:
        # Initialize the client
        client = genai.Client(api_key=api_key)
        
        # Test the API
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents="What is the best business idea for a student?"
        )
        
        print("✅ API is working!\n")
        print("Response:")
        print(response.text)
        
    except Exception as e:
        print(f"❌ Error: {e}")