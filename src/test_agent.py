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
current_dir = os.path.dirname(os.path.abspath(__file__))
SERVER_FILE = os.path.join(current_dir, "mcp_server.py")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ... (Previous imports remain same)

class Agent:
    def __init__(self, mcp_session):
        if not GEMINI_API_KEY:
            sys.exit("Error: GEMINI_API_KEY missing.")
        
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.mcp_session = mcp_session
        self.memory = PersistentHistoryManager(self.client, max_messages=30)
        
        # 1. Enable Thinking in the Config
        # include_thoughts=True allows us to see the reasoning parts.
        self.chat = self.client.aio.chats.create(
            model="gemini-2.5-flash",
            history=self.memory.get_loadable_history(),
            config=types.GenerateContentConfig(
                tools=[self.mcp_session],
                temperature=1.0, 
                thinking_config=types.ThinkingConfig(
                    include_thoughts=True,
                    # Optional: budget_tokens=1024 # How much it's allowed to "think"
                ),
                system_instruction="""
                You are a world-tour professional cycling coach. You base yourself on the most modern training science to help your athlete improve.
                You have access to a variety of tools to fetch Garmin data for your athlete.
                """
            )
        )

    async def run_turn(self, user_input):
        self.memory.add_message("user", user_input)
        
        full_response_text = ""
        
        # 2. Use Streaming to catch thoughts
        # We use await for the stream object, then 'async for' through it.
        stream = await self.chat.send_message_stream(user_input)
        
        print("\n[Coach Thinking...]")
        async for chunk in stream:
            # Check for thought parts (Reasoning)
            for part in chunk.candidates[0].content.parts:
                if part.thought:
                    # Print thoughts in a different style (e.g., dim or italic)
                    print(f"\033[3m   > {part.text}\033[0m", end="", flush=True)
                
                if part.text and not part.thought:
                    # Collect and print the actual response
                    full_response_text += part.text

        self.memory.add_message("model", full_response_text)
        return full_response_text

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