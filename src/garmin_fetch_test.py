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
    stress_data = client.get_stress_data(date_str)
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

def get_vo2_max(client, date_str):
    """
    Fetches maximum metrics for a specific date (YYYY-MM-DD).
    """
    max_metrics = client.get_training_status(date_str)
    cycling_vo2max = max_metrics.get("mostRecentVO2Max").get("cycling").get("vo2MaxPreciseValue")
    running_vo2max = max_metrics.get("mostRecentVO2Max").get("generic").get("vo2MaxPreciseValue")

    print(f"Max Metrics for {date_str}:")
    print(f"  Cycling VO2Max: {cycling_vo2max}")
    print(f"  Running VO2Max: {running_vo2max}")
    return 

def get_altitude_acclimation(client, date_str):
    """
    Fetches altitude acclimation data for a specific date (YYYY-MM-DD).
    """
    acclimation_data = client.get_training_status(date_str)
    altitude_acclimation = acclimation_data.get("mostRecentVO2Max").get("heatAltitudeAcclimation").get("altitudeAcclimation")
    current_altitude_meters = acclimation_data.get("mostRecentVO2Max").get("heatAltitudeAcclimation").get("currentAltitude")
    heat_acclimation_percentage = acclimation_data.get("mostRecentVO2Max").get("heatAltitudeAcclimation").get("heatAcclimationPercentage")

    print(f"Altitude Acclimation for {date_str}:")
    print(f"  Acclimation Level: {altitude_acclimation}")
    print(f"  Current Altitude (m): {current_altitude_meters}")
    print(f"  Heat Acclimation Percentage: {heat_acclimation_percentage}%")

    return {

    }
def get_weight(client, date_str):
    """
    Fetches weight data for a specific date (YYYY-MM-DD).
    """
    weight_data = client.get_daily_weigh_ins(date_str)
    weight = weight_data.get("totalAverage").get("weight")
    bmi = weight_data.get("totalAverage").get("bmi")

    print(f"Weight Data for {date_str}:")
    print(f"  Weight (g): {weight}")

    return {
        "weight_g": weight,
    }

def get_training_readiness(client, date_str):
    """
    Fetches training readiness data for a specific date (YYYY-MM-DD).
    """
    readiness_data = client.get_training_readiness(date_str)
    overall_readiness = readiness_data[0].get("score")


    print(f"Training Readiness for {date_str}:")
    print(f"  Overall Readiness: {overall_readiness}")

    return {
        "overall_readiness": overall_readiness,
    }


def get_monthly_training_load(client, date_str):
    """
    Fetches training load data for a specific date (YYYY-MM-DD).
    """
    load_data = client.get_training_status(date_str)
    monthly_low_aerobic_load = load_data.get("mostRecentTrainingLoadBalance").get("metricsTrainingLoadBalanceDTOMap").get("3438848558").get("monthlyLoadAerobicLow")
    monthly_high_aerobic_load = load_data.get("mostRecentTrainingLoadBalance").get("metricsTrainingLoadBalanceDTOMap").get("3438848558").get("monthlyLoadAerobicHigh")
    monthly_anearobic_load = load_data.get("mostRecentTrainingLoadBalance").get("metricsTrainingLoadBalanceDTOMap").get("3438848558").get("monthlyLoadAnaerobic")

    print(f"Training Load for {date_str}:")
    print(f"  Monthly Low Aerobic Load: {monthly_low_aerobic_load}")
    print(f"  Monthly High Aerobic Load: {monthly_high_aerobic_load}")
    print(f"  Monthly Anaerobic Load: {monthly_anearobic_load}")
    return {
    }

def get_training_load(client, date_str):
    """
    Fetches training load data for a specific date (YYYY-MM-DD).
    """
    load_data = client.get_training_status(date_str)
    daily_acute_load = load_data.get("mostRecentTrainingStatus").get("latestTrainingStatusData").get("3438848558").get("acuteTrainingLoadDTO").get("dailyTrainingLoadAcute")
    print(f"  Daily Acute Load: {daily_acute_load}")
    daily_chronic_load = load_data.get("mostRecentTrainingStatus").get("latestTrainingStatusData").get("3438848558").get("acuteTrainingLoadDTO").get("dailyTrainingLoadChronic")
    print(f"  Daily Chronic Load: {daily_chronic_load}")
    max_training_load_chronic = load_data.get("mostRecentTrainingStatus").get("latestTrainingStatusData").get("3438848558").get("acuteTrainingLoadDTO").get("maxTrainingLoadChronic")
    print(f"  Max Training Load Chronic: {max_training_load_chronic}")
    min_training_load_chronic = load_data.get("mostRecentTrainingStatus").get("latestTrainingStatusData").get("3438848558").get("acuteTrainingLoadDTO").get("minTrainingLoadChronic")
    print(f"  Min Training Load Chronic: {min_training_load_chronic}")
    acute_chronic_ratio = load_data.get("mostRecentTrainingStatus").get("latestTrainingStatusData").get("3438848558").get("acuteTrainingLoadDTO").get("dailyAcuteChronicWorkloadRatio")
    print(f"  Acute Chronic Ratio: {acute_chronic_ratio}")
    daily_status_feedback = load_data.get("mostRecentTrainingStatus").get("latestTrainingStatusData").get("3438848558").get("trainingStatusFeedbackPhrase")
    print(f"  Daily Status Feedback: {daily_status_feedback}")
    

    
    return {
    }

def get_activity_dict_between_dates(client, start_date_str, end_date_str):
    """
    Fetches activity ID and type dictionary between two dates (YYYY-MM-DD).
    """
    activities = client.get_activities_by_date(start_date_str,end_date_str)  # Fetch a large number to cover the range
    activity_dict = {}

    for activity in activities:
        a_id = activity['activityId']
        a_type = activity['activityType']['typeKey']
        activity_dict[a_id] = a_type

    print(activity_dict)
    return activity_dict


def get_hr_in_time_zones(client, activity_id):
    """
    Fetches heart rate data in time zones for a specific activity by ID.
    """
    hr_in_time_zones = client.get_activity_hr_in_timezones(activity_id)
    time_zone_1 = hr_in_time_zones[0].get("secsInZone")
    zone_1_lower_bound = hr_in_time_zones[0].get("zoneLowBoundary")
    time_zone_2 = hr_in_time_zones[1].get("secsInZone")
    zone_2_lower_bound = hr_in_time_zones[1].get("zoneLowBoundary")
    time_zone_3 = hr_in_time_zones[2].get("secsInZone")
    zone_3_lower_bound = hr_in_time_zones[2].get("zoneLowBoundary")
    time_zone_4 = hr_in_time_zones[3].get("secsInZone")
    zone_4_lower_bound = hr_in_time_zones[3].get("zoneLowBoundary")
    time_zone_5 = hr_in_time_zones[4].get("secsInZone")
    zone_5_lower_bound = hr_in_time_zones[4].get("zoneLowBoundary")

    print(f"  Zone 1 (<{zone_2_lower_bound} bpm): {time_zone_1} sec")

def get_power_in_time_zones(client, activity_id):
    """
    Fetches power data in time zones for a specific activity by ID.
    """

    time_in_power_zones = client.get_activity_power_in_timezones(activity_id)
    time_zone_1 = time_in_power_zones[0].get("secsInZone")
    zone_1_lower_bound = time_in_power_zones[0].get("zoneLowBoundary")
    time_zone_2 = time_in_power_zones[1].get("secsInZone")
    zone_2_lower_bound = time_in_power_zones[1].get("zoneLowBoundary")
    time_zone_3 = time_in_power_zones[2].get("secsInZone")
    zone_3_lower_bound = time_in_power_zones[2].get("zoneLowBoundary")
    time_zone_4 = time_in_power_zones[3].get("secsInZone")
    zone_4_lower_bound = time_in_power_zones[3].get("zoneLowBoundary")
    time_zone_5 = time_in_power_zones[4].get("secsInZone")
    zone_5_lower_bound = time_in_power_zones[4].get("zoneLowBoundary")  
    time_zone_6 = time_in_power_zones[5].get("secsInZone")
    zone_6_lower_bound = time_in_power_zones[5].get("zoneLowBoundary")
    time_zone_7 = time_in_power_zones[6].get("secsInZone")
    zone_7_lower_bound = time_in_power_zones[6].get("zoneLowBoundary")

    print(time_in_power_zones)


def get_activity_weather(client, activity_id):
    """
    Fetches weather data for a specific activity by ID.
    """
    
    weather_data = client.get_activity_weather(activity_id)
    temp = weather_data.get("temp")
    relative_humidity = weather_data.get("relativeHumidity")
    print(temp)
    print(relative_humidity)


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
    

    get_activity_dict_between_dates(client, "2024-05-15", "2024-06-22")  # Replace with a valid activity ID

except Exception as e:
    print(f"Error: {e}")