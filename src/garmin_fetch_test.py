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


def get_resting_hr(client, date_str):
    """
    Fetches the resting heart rate for a specific date (YYYY-MM-DD) and the average over the last 7 days.
    """
    rhr_data = client.get_heart_rates(date_str)
    resting_hr = rhr_data.get("restingHeartRate")
    last_seven_days_avg_rhr = rhr_data.get("lastSevenDaysAvgRestingHeartRate")
    print(f"Resting HR for {date_str}: {resting_hr} bpm. 7-day average: {last_seven_days_avg_rhr} bpm.")
    return resting_hr, last_seven_days_avg_rhr

def get_sleep_data(client, date_str):
    """
    Fetches sleep data for a specific date (YYYY-MM-DD).
    """
    sleep_data = client.get_sleep_data(date_str)

    sleep_start_time = sleep_data.get("dailySleepDTO").get("sleepStartTimestampGMT")
    sleep_end_time = sleep_data.get("dailySleepDTO").get("sleepEndTimestampGMT")

    sleep_seconds = sleep_data.get("dailySleepDTO").get("sleepTimeSeconds")
    deep_sleep_seconds = sleep_data.get("dailySleepDTO").get("deepSleepSeconds")
    light_sleep_seconds = sleep_data.get("dailySleepDTO").get("lightSleepSeconds")
    rem_sleep_seconds = sleep_data.get("dailySleepDTO").get("remSleepSeconds")
    awake_sleep_seconds = sleep_data.get("dailySleepDTO").get("awakeSleepSeconds")

    avg_sleep_hr = sleep_data.get("dailySleepDTO").get("avgHeartRate")
    avg_sleep_stress = sleep_data.get("dailySleepDTO").get("avgSleepStress")
    avg_overnight_hrv = sleep_data.get("avgOvernightHrv")

    print(f"Sleep Data for {date_str}:")
    print(f"  Sleep Start Time: {sleep_start_time}")
    print(f"  Sleep End Time: {sleep_end_time}")
    print(f"  Total Sleep Seconds: {sleep_seconds}")
    print(f"  Deep Sleep Seconds: {deep_sleep_seconds}")
    print(f"  Light Sleep Seconds: {light_sleep_seconds}")
    print(f"  REM Sleep Seconds: {rem_sleep_seconds}")
    print(f"  Awake Sleep Seconds: {awake_sleep_seconds}")
    print(f"  Average Sleep HR: {avg_sleep_hr}")
    print(f"  Average Sleep Stress: {avg_sleep_stress}")
    print(f"  Average Overnight HRV: {avg_overnight_hrv}")
    
    return {
        "sleep_start_time": sleep_start_time,
        "sleep_end_time": sleep_end_time,
        "sleep_seconds": sleep_seconds,
        "deep_sleep_seconds": deep_sleep_seconds,
        "light_sleep_seconds": light_sleep_seconds,
        "rem_sleep_seconds": rem_sleep_seconds,
        "awake_sleep_seconds": awake_sleep_seconds,
        "avg_sleep_hr": avg_sleep_hr,
        "avg_sleep_stress": avg_sleep_stress,
        "avg_overnight_hrv": avg_overnight_hrv
    }

def get_stress_level(client, date_str):
    """
    Fetches the average stress level for a specific date (YYYY-MM-DD).
    """
    stress_data = client.get_all_day_stress(date_str)
    stress_level = stress_data.get("avgStressLevel")
    print(f"Stress Level for {date_str}: {stress_level}")
    return stress_level

def get_hrv_data(client, date_str):
    """
    Fetches HRV data for a specific date (YYYY-MM-DD).
    """
    hrv_data = client.get_hrv_data(date_str)
    weekly_avg_hrv = hrv_data.get("hrvSummary").get("weeklyAvg")
    night_avg_hrv = hrv_data.get("hrvSummary").get("lastNightAvg")
    night_5min_high_hrv = hrv_data.get("hrvSummary").get("lastNight5MinHigh")
    baseline_low_upper = hrv_data.get("hrvSummary").get("baseline").get("lowUpper")
    baseline_balanced_low = hrv_data.get("hrvSummary").get("baseline").get("balancedLow")
    baseline_blanced_upper = hrv_data.get("hrvSummary").get("baseline").get("balancedUpper")
    hrv_status = hrv_data.get("hrvSummary").get("status")

    print(f"HRV Data for {date_str}:")
    print(f"  HRV Status: {hrv_status}")
    print(f"  Weekly Avg HRV: {weekly_avg_hrv}")
    print(f"  Night Avg HRV: {night_avg_hrv}")
    print(f"  Night 5min High HRV: {night_5min_high_hrv}")
    print(f"  Baseline Low Upper: {baseline_low_upper}")
    print(f"  Baseline Balanced Low: {baseline_balanced_low}")
    print(f"  Baseline Balanced Upper: {baseline_blanced_upper}")

    return {
        "hrv_status": hrv_status,
        "weekly_avg_hrv": weekly_avg_hrv,
        "night_avg_hrv": night_avg_hrv,
        "night_5min_high_hrv": night_5min_high_hrv,
        "baseline_low_upper": baseline_low_upper,
        "baseline_balanced_low": baseline_balanced_low,
        "baseline_blanced_upper": baseline_blanced_upper
    }
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

    # 2. Query specific category
    # Common types: 'running', 'cycling', 'swimming', 'strength_training', 'hiking', 'walking', 'virtual_ride'
    target_sport = "virtual_ride"
    
    get_stress_level(client, "2025-12-20")

except Exception as e:
    print(f"Error: {e}")