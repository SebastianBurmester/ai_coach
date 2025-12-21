import logging
from fastmcp import Context

from garminconnect import Garmin
import os

logger = logging.getLogger(__name__)

def get_api():
    token_dir = os.path.expanduser("~/.garminconnect")
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")
    # 1. Initialize and Login
    client = Garmin() # (email, password) if token expired
    client.login(tokenstore=token_dir)
    
    # Save tokens to the default directory (~/.garminconnect)
    token_dir = os.path.expanduser("~/.garminconnect")
    os.makedirs(token_dir, exist_ok=True)
    client.garth.dump(token_dir)

    return client

def register_garmin_health_tools(mcp):
    """
    Registers all Garmin-Health-related tools to the provided MCP server instance.
    """
    @mcp.tool()
    def get_resting_hr(date_str, ctx: Context) -> str:
        """
        Fetches the resting heart rate for a specific date (YYYY-MM-DD) and the average over the last 7 days.
        """
        logger.info(f"Fetching resting heart rate for {date_str}")
        client = get_api()
        rhr_data = client.get_heart_rates(date_str)
        resting_hr = rhr_data.get("restingHeartRate")
        last_seven_days_avg_rhr = rhr_data.get("lastSevenDaysAvgRestingHeartRate")
        return (f"Resting HR for {date_str}: {resting_hr} bpm. "f"7-day average: {last_seven_days_avg_rhr} bpm.")

    @mcp.tool()
    def get_stress_level(date_str, ctx: Context) -> str:
        """
        Fetches the average stress level for a specific date (YYYY-MM-DD).
        """
        client = get_api()
        stress_data = client.get_all_day_stress(date_str)
        stress_level = stress_data.get("avgStressLevel")

        return f"Stress Level for {date_str}: {stress_level}"

    @mcp.tool()
    def get_sleep_data(date_str, ctx: Context) -> dict:
        """
        Fetches sleep data for a specific date (YYYY-MM-DD).
        """

        logger.info(f"Fetching sleep data for {date_str}")

        client = get_api()
        sleep_data = client.get_sleep_data(date_str)

        sleep_start_time = sleep_data.get("dailySleepDTO").get("sleepStartTimestampLocal")
        sleep_end_time = sleep_data.get("dailySleepDTO").get("sleepEndTimestampLocal")

        sleep_seconds = sleep_data.get("dailySleepDTO").get("sleepTimeSeconds")
        deep_sleep_seconds = sleep_data.get("dailySleepDTO").get("deepSleepSeconds")
        light_sleep_seconds = sleep_data.get("dailySleepDTO").get("lightSleepSeconds")
        rem_sleep_seconds = sleep_data.get("dailySleepDTO").get("remSleepSeconds")
        awake_sleep_seconds = sleep_data.get("dailySleepDTO").get("awakeSleepSeconds")

        avg_sleep_hr = sleep_data.get("dailySleepDTO").get("avgHeartRate")
        avg_sleep_stress = sleep_data.get("dailySleepDTO").get("avgSleepStress")
        avg_overnight_hrv = sleep_data.get("avgOvernightHrv")
        
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

    @mcp.tool()
    def get_hrv_data(date_str, ctx: Context) -> dict:
        """
        Fetches HRV data for a specific date (YYYY-MM-DD).
        """
        logger.info(f"Fetching HRV data for {date_str}")

        client = get_api()
        hrv_data = client.get_hrv_data(date_str)
        weekly_avg_hrv = hrv_data.get("hrvSummary").get("weeklyAvg")
        night_avg_hrv = hrv_data.get("hrvSummary").get("lastNightAvg")
        night_5min_high_hrv = hrv_data.get("hrvSummary").get("lastNight5MinHigh")
        baseline_low_upper = hrv_data.get("hrvSummary").get("baseline").get("lowUpper")
        baseline_balanced_low = hrv_data.get("hrvSummary").get("baseline").get("balancedLow")
        baseline_blanced_upper = hrv_data.get("hrvSummary").get("baseline").get("balancedUpper")
        hrv_status = hrv_data.get("hrvSummary").get("status")

        return {
            "hrv_status": hrv_status,
            "weekly_avg_hrv": weekly_avg_hrv,
            "night_avg_hrv": night_avg_hrv,
            "night_5min_high_hrv": night_5min_high_hrv,
            "baseline_low_upper": baseline_low_upper,
            "baseline_balanced_low": baseline_balanced_low,
            "baseline_blanced_upper": baseline_blanced_upper
        }
