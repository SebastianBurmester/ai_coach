import asyncio
import os
import sys
from dotenv import load_dotenv
from fastmcp import Client
from google import genai
from google.genai import types
from history_manager import PersistentHistoryManager

# --- 1. Load Configuration ---
load_dotenv()
SERVER_FILE = r"C:\Users\sburm\ai_coach\mcp_server.py"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class Agent:
    def __init__(self, mcp_session):
        if not GEMINI_API_KEY:
            sys.exit("Error: GEMINI_API_KEY missing.")
        
        # Initialize the new 2.0 Client
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.mcp_session = mcp_session
        
        # Initialize your existing History Manager
        # Ensure your PersistentHistoryManager class is imported!
        self.memory = PersistentHistoryManager(self.client, max_messages=20)
        
        # Create Chat with loaded history
        # Note: We pass mcp_session directly into tools. 
        # The SDK handles the loop automatically.
        self.chat = self.client.aio.chats.create(
            model="gemini-2.5-flash",
            history=self.memory.get_loadable_history(),
            config=types.GenerateContentConfig(
                tools=[self.mcp_session],
                temperature=1.0,
                system_instruction="""
                You are a smart fitness coach. You have access to the user's files and Garmin data.
                Always confirm when you read or write data.
                """
            )
        )

    async def run_turn(self, user_input):
        # 1. Manually add user input to your persistent storage
        self.memory.add_message("user", user_input)
        
        # 2. Send to Model (SDK executes MCP tools automatically)
        response = await self.chat.send_message(user_input)
        
        # 3. Add final model response to persistent storage
        self.memory.add_message("model", response.text)
        
        return response.text

# --- 2. Main Execution Loop ---
async def main():
    print("--- Connecting to Fitness MCP Server ---")
    
    async with Client(SERVER_FILE) as mcp_client:
        agent = Agent(mcp_client.session)
        
        print("--- Fitness Coach (Flash 2.5 + MCP + History) ---")
        print("Type 'quit' to exit.\n")

        while True:
            try:
                u_in = input("You: ")
                if u_in.lower() in ['quit', 'exit']:
                    break
                
                if not u_in.strip():
                    continue

                # Run the turn
                response_text = await agent.run_turn(u_in)
                print(f"\nCoach: {response_text}\n")
                
            except Exception as e:
                print(f"An error occurred: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSession ended.")