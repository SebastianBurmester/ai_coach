from google import genai
import os
from dotenv import load_dotenv 

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)

response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="Explain how AI works in a few words",
)

print(response.text)