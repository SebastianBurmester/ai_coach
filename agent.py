import os
import google.generativeai as genai
from dotenv import load_dotenv
from garminconnect import Garmin
from history_manager import PersistentHistoryManager

# 1. Setup
load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# --- Define Your Tools (The "Skills" your agent has) ---

def get_latest_activity_stats(activity_type: str = "running"):
    """
    Fetches the distance and duration of the user's latest activity 
    for a specific sport type (running, cycling, etc.).
    """
    try:
        # Connect to Garmin (using env vars)
        email = os.getenv("GARMIN_EMAIL")
        password = os.getenv("GARMIN_PASSWORD")
        client = Garmin(email, password)
        client.login()

        # Fetch last 10 activities to find the right type
        activities = client.get_activities(0, 10)
        
        for act in activities:
            # Check if this activity matches the requested type
            if act['activityType']['typeKey'] == activity_type:
                # Found it! Extract useful data
                dist_km = round(act['distance'] / 1000, 2)
                duration_min = round(act['duration'] / 60, 2)
                date = act['startTimeLocal']
                return {
                    "date": date,
                    "type": activity_type,
                    "distance_km": dist_km,
                    "duration_minutes": duration_min
                }
        return "No recent activity found for that type."
        
    except Exception as e:
        return f"Error fetching data: {e}"

# --- Create the Agent ---

# 1. Create a dictionary of tools
tools_list = [get_latest_activity_stats]

# 2. Initialize the model with tools
# We use 'gemini-1.5-flash' because it's fast and free-tier friendly
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    tools=tools_list,
    system_instruction="You are a helpful fitness coach. You have access to the user's Garmin data. Use it to give specific advice."
)

# 3. Start a chat session with automatic function calling enabled
# This does the magic: Model decides to call function -> Python runs it -> Model gets result
# ... (Previous imports and setup) ...

# Initialize
# We pass the 'coach_model' so the manager can use it to generate summaries
history_manager = PersistentHistoryManager(model=model, max_messages=10, summary_batch_size=2) # Set to 10 for testing

print("Agent ready. Type 'quit' to exit.")

while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ['quit', 'exit']:
        break

    # 1. Add User Input to History
    history_manager.add_message("user", user_input)

    # 2. Re-build the chat session with the full context (Summary + Recent History)
    # We create a fresh chat instance every turn to inject the updated history perfectly
    current_history = history_manager.get_full_context()
    chat_session = model.start_chat(history=current_history, enable_automatic_function_calling=True)

    # 3. Get Response
    # Note: We send the *last* message again because start_chat loads context but doesn't trigger a reply
    response = chat_session.send_message(user_input) 
    
    # 4. Add AI Response to History
    history_manager.add_message("model", response.text)
    
    print(f"Coach: {response.text}")