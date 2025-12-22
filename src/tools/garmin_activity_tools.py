import logging
from fastmcp import Context
import os

from garminconnect import Garmin

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

def register_garmin_activity_tools(mcp):
    """
    Registers all Garmin-Activity-related tools to the provided MCP server instance.
    """

    @mcp.tool()
    def get_activity_id_and_type_between_dates(start_date_str, end_date_str):
        """
        Fetches activity ID and activity type between two dates (YYYY-MM-DD).
        Maximum 100 activities will be returned.
        """
        logger.info(f"Fetching activities between {start_date_str} and {end_date_str}")

        client = get_api()
        activities = client.get_activities_by_date(start_date_str,end_date_str) 
        activity_dict = {}

        for activity in activities:
            a_id = activity['activityId']
            a_type = activity['activityType']['typeKey']
            activity_dict[a_id] = a_type

        return activity_dict

    @mcp.tool()
    def get_hr_in_time_zones(activity_id, ctx: Context) -> dict:
        """
        Fetches heart rate time in zones for a specific activity by ID.
        """
        logger.info(f"Fetching heart rate in time zones for Activity ID {activity_id}")

        client = get_api()
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

        return {
            f"Zone 1 ({zone_1_lower_bound}-{zone_2_lower_bound} bpm)": time_zone_1,
            f"Zone 2 ({zone_2_lower_bound}-{zone_3_lower_bound} bpm)": time_zone_2,
            f"Zone 3 ({zone_3_lower_bound}-{zone_4_lower_bound} bpm)": time_zone_3,
            f"Zone 4 ({zone_4_lower_bound}-{zone_5_lower_bound} bpm)": time_zone_4,
            f"Zone 5 (>{zone_5_lower_bound} bpm)": time_zone_5
        }
    
    @mcp.tool()
    def get_power_in_time_zones(activity_id, ctx: Context) -> dict:
        """
        Fetches power data in time zones for a specific activity by ID.
        """
        logger.info(f"Fetching power in time zones for Activity ID {activity_id}")

        client = get_api()
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

        return {
            f"Zone 1 ({zone_1_lower_bound}-{zone_2_lower_bound} watts)": time_zone_1,
            f"Zone 2 ({zone_2_lower_bound}-{zone_3_lower_bound} watts)": time_zone_2,
            f"Zone 3 ({zone_3_lower_bound}-{zone_4_lower_bound} watts)": time_zone_3,
            f"Zone 4 ({zone_4_lower_bound}-{zone_5_lower_bound} watts)": time_zone_4,
            f"Zone 5 ({zone_5_lower_bound}-{zone_6_lower_bound} watts)": time_zone_5,
            f"Zone 6 ({zone_6_lower_bound}-{zone_7_lower_bound} watts)": time_zone_6,
            f"Zone 7 (>{zone_7_lower_bound} watts)": time_zone_7
        }

    @mcp.tool()
    def get_activity_weather(activity_id, ctx: Context) -> dict:
        """
        Fetches weather data for a specific activity by ID.
        """
        logger.info(f"Fetching weather data for Activity ID {activity_id}")

        client = get_api()
        weather_data = client.get_activity_weather(activity_id)
        temp = weather_data.get("temp")
        relative_humidity = weather_data.get("relativeHumidity")
        
        return {
            "temperature": temp,
            "relative_humidity": relative_humidity
        }
