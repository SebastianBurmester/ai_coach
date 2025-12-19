import asyncio
from fastmcp import Client
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

# Path to the file you just saved
SERVER_FILE = r"C:\Users\sburm\ai_coach\hrv_mcp_test_server.py"

gemini_api_key = os.getenv("GEMINI_API_KEY")  # Ensure your API key is set in the environment

async def main():
    # Pass the env vars directly into the client
    async with Client(
        SERVER_FILE
    ) as mcp_client:

        client = genai.Client(api_key=gemini_api_key)
        
        # Now ask Gemini!
        response = await client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents="What was my HRV last night? What is the value?",
            config=genai.types.GenerateContentConfig(
                tools=[mcp_client.session]
            )
        )
        print(response.text)

if __name__ == "__main__":
    asyncio.run(main())