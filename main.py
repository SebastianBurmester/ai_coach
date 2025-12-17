from garminconnect import Garmin
import os
from dotenv import load_dotenv

load_dotenv()

email = os.getenv("GARMIN_EMAIL")
password = os.getenv("GARMIN_PASSWORD")

try:
    # Initialize Garmin client
    client = Garmin(email, password)
    client.login() # This handles the prompt for MFA if needed

    # Example: Get today's stats
    stats = client.get_stats("2025-10-18")
    print(stats)
except Exception as e:
    print(f"Error: {e}")