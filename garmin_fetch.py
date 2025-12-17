import os
from dotenv import load_dotenv
from garminconnect import Garmin

# Load environment variables
load_dotenv()

def get_recent_activities_by_type(client, activity_type, count=3):
    """
    Fetches the last 'count' activities of a specific type (e.g., 'running').
    """
    filtered_activities = []
    start = 0
    batch_size = 20  # Fetch 20 at a time to be efficient
    
    print(f"Searching for last {count} activities of type: '{activity_type}'...")

    while len(filtered_activities) < count:
        # Fetch a batch of mixed activities
        activities = client.get_activities(start, batch_size)
        
        # If no more data exists, stop
        if not activities:
            break

        # Filter the batch
        for activity in activities:
            # Check the activity type (case-insensitive)
            # Structure is usually: activity['activityType']['typeKey']
            act_type_key = activity['activityType']['typeKey']
            
            if act_type_key == activity_type:
                filtered_activities.append(activity)
                
                # Stop immediately if we have enough
                if len(filtered_activities) == count:
                    break
        
        # Move the cursor for the next batch
        start += batch_size

    return filtered_activities

# --- Main Execution ---
try:
    token_dir = os.path.expanduser("~/.garminconnect")
    # 1. Initialize and Login
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")
    client = Garmin() # (email, password) if token expired
    client.login(tokenstore=token_dir)
    
    # Save tokens to the default directory (~/.garminconnect)
    token_dir = os.path.expanduser("~/.garminconnect")
    os.makedirs(token_dir, exist_ok=True)
    client.garth.dump(token_dir)

    print(f"Success! Tokens saved to: {token_dir}")

    # 2. Query specific category
    # Common types: 'running', 'cycling', 'swimming', 'strength_training', 'hiking', 'walking', 'virtual_ride'
    target_sport = "virtual_ride"
    
    last_activities = get_recent_activities_by_type(client, target_sport, count=10)

    # 3. Print the results
    print(f"\nFound {len(last_activities)} {target_sport} activities:")
    print(f"{'Date':<20} | {'Distance (km)':<15} | {'Duration (min)':<15} | {'Avg HR'}")
    print("-" * 70)

    for act in last_activities:
        # Extract data safely (some fields might be missing)
        date = act['startTimeLocal']
        dist_km = round(act['distance'] / 1000, 2)
        duration_min = round(act['duration'] / 60, 2)
        avg_hr = act.get('averageHR', 'N/A') # Use .get() in case HR is missing

        print(f"{date:<20} | {dist_km:<15} | {duration_min:<15} | {avg_hr}")

except Exception as e:
    print(f"Error: {e}")