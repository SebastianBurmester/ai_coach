import logging
from fastmcp import Context
import os

from garminconnect import Garmin
import calendar
import datetime

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
    def get_activity_summary(activity_id):
        """
        Fetches summary data for a specific activity by ID.
        """
        logger.info(f"Fetching summary for Activity ID {activity_id}")

        client = get_api()
        summary_data = client.get_activity(activity_id)
        activity_name = summary_data.get("activityName")
        start_time = summary_data.get("summaryDTO").get("startTimeLocal")
        distance_meters = summary_data.get("summaryDTO").get("distance")
        duration_seconds = summary_data.get("summaryDTO").get("duration")
        moving_duration_seconds = summary_data.get("summaryDTO").get("movingDuration")
        elevation_gain_meters = summary_data.get("summaryDTO").get("elevationGain")
        elevation_loss_meters = summary_data.get("summaryDTO").get("elevationLoss")
        max_elevation = summary_data.get("summaryDTO").get("maxElevation")
        averageMovingSpeed_mps = summary_data.get("summaryDTO").get("averageMovingSpeed")
        calories = summary_data.get("summaryDTO").get("calories")
        average_heart_rate = summary_data.get("summaryDTO").get("averageHR")
        max_heart_rate = summary_data.get("summaryDTO").get("maxHR")
        average_cadence = summary_data.get("summaryDTO").get("averageBikeCadence")
        average_power = summary_data.get("summaryDTO").get("averagePower")
        max_power_twenty_min = summary_data.get("summaryDTO").get("maxPowerTwentyMinutes")
        normalized_power = summary_data.get("summaryDTO").get("normalizedPower")
        training_stress_score = summary_data.get("summaryDTO").get("trainingStressScore")
        activity_training_load = summary_data.get("summaryDTO").get("activityTrainingLoad")
        aerobic_training_effect = summary_data.get("summaryDTO").get("trainingEffect")
        anaerobic_training_effect = summary_data.get("summaryDTO").get("anaerobicTrainingEffect")

        return {
            "activity_name": activity_name,
            "start_time": start_time,
            "distance_meters": distance_meters,
            "duration_seconds": duration_seconds,
            "moving_duration_seconds": moving_duration_seconds,
            "elevation_gain_meters": elevation_gain_meters,
            "elevation_loss_meters": elevation_loss_meters,
            "max_elevation": max_elevation,
            "average_moving_speed (m/s)": averageMovingSpeed_mps,
            "calories": calories,
            "average_heart_rate": average_heart_rate,
            "max_heart_rate": max_heart_rate,
            "average_cadence": average_cadence if average_cadence is not None else "Not Available for this activity",
            "average_power": average_power,
            "max_power_twenty_minutes": max_power_twenty_min if max_power_twenty_min is not None else "Not Available for this activity",
            "normalized_power": normalized_power,
            "training_stress_score": training_stress_score if training_stress_score is not None else "Not Available for this activity",
            "activity_training_load": activity_training_load,
            "aerobic_training_effect": aerobic_training_effect,
            "anaerobic_training_effect": anaerobic_training_effect
        }

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

    @mcp.tool()
    def get_monthly_training_summary(year, month, ctx: Context):
        """
        Fetches monthly training summary for a specific month and year.
        Args:
            year (int): e.g., 2024
            month (int): e.g., 3 for March
        """
        # 1. Determine the last day of the given month/year
        # calendar.monthrange returns (first_day_weekday, number_of_days)
        logger.info(f"Fetching monthly training summary for {year}-{month:02d}")
        
        client = get_api()

        _, last_day = calendar.monthrange(year, month)
        
        # 2. Format the date strings for the API
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-{last_day}"

        # 3. Fetch activity list
        activities = client.get_activities_by_date(start_date,end_date) 
        activity_dict = {}

        for activity in activities:
            a_id = activity['activityId']
            a_type = activity['activityType']['typeKey']
            activity_dict[a_id] = a_type
        
        monthly_summary = {}

        for activity_id, activity_type in activity_dict.items():
            # Fetch detailed data
            full_data = client.get_activity(activity_id)
            summary_dto = full_data.get("summaryDTO", {})

            # Extract metrics (with null safety)
            duration = summary_dto.get("duration", 0) or 0
            distance = summary_dto.get("distance", 0) or 0
            load = summary_dto.get("activityTrainingLoad", 0) or 0
            calories = summary_dto.get("calories", 0) or 0
            avg_heart_rate = summary_dto.get("averageHR", 0) or 0
            avg_power = summary_dto.get("averagePower", 0) or 0

            # Initialize or update the activity type category
            if activity_type not in monthly_summary:
                monthly_summary[activity_type] = {
                    "total_duration_sec": 0,
                    "total_distance_m": 0,
                    "total_training_load": 0,
                    "calories": 0,
                    "average_heart_rate": 0,
                    "average_power": 0,
                    "count": 0
                }

            monthly_summary[activity_type]["total_duration_sec"] += duration
            monthly_summary[activity_type]["total_distance_m"] += distance
            monthly_summary[activity_type]["total_training_load"] += load
            monthly_summary[activity_type]["calories"] += calories
            monthly_summary[activity_type]["average_heart_rate"] += avg_heart_rate
            monthly_summary[activity_type]["average_power"] += avg_power
            monthly_summary[activity_type]["count"] += 1

        # Finalize average calculations
        for activity_type, data in monthly_summary.items():
            count = data["count"]
            if count > 0:
                data["average_heart_rate"] /= count
                data["average_power"] /= count
        
        return monthly_summary

    @mcp.tool()
    def get_weekly_training_summary_by_date(date_str, ctx: Context):
        """
        Fetches weekly training summary for the week containing the provided date.
        The week is defined as Monday through Sunday.
        Args:
            date_str (str): Date in 'YYYY-MM-DD' format.
        """
        logger.info(f"Fetching weekly training summary for date: {date_str}")
        client = get_api()

        # 1. Parse the input date
        input_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

        # 2. Find Monday and Sunday of that week
        # weekday() returns 0 for Monday, 6 for Sunday
        days_since_monday = input_date.weekday()
        monday_date = input_date - datetime.timedelta(days=days_since_monday)
        sunday_date = monday_date + datetime.timedelta(days=6)

        start_date = monday_date.strftime("%Y-%m-%d")
        end_date = sunday_date.strftime("%Y-%m-%d")

        logger.info(f"Week Range: {start_date} to {end_date}")

        # 3. Fetch activity list
        activities = client.get_activities_by_date(start_date, end_date) 
        
        weekly_summary = {}

        for activity in activities:
            activity_id = activity['activityId']
            activity_type = activity['activityType']['typeKey']
            
            # 4. Fetch detailed data per activity
            full_data = client.get_activity(activity_id)
            summary_dto = full_data.get("summaryDTO", {})

            # Extract metrics
            duration = summary_dto.get("duration", 0) or 0
            distance = summary_dto.get("distance", 0) or 0
            load = summary_dto.get("activityTrainingLoad", 0) or 0
            calories = summary_dto.get("calories", 0) or 0
            avg_heart_rate = summary_dto.get("averageHR", 0) or 0
            avg_power = summary_dto.get("averagePower", 0) or 0

            if activity_type not in weekly_summary:
                weekly_summary[activity_type] = {
                    "total_duration_sec": 0,
                    "total_distance_m": 0,
                    "total_training_load": 0,
                    "calories": 0,
                    "avg_hr_sum": 0,
                    "avg_power_sum": 0,
                    "count": 0
                }

            stats = weekly_summary[activity_type]
            stats["total_duration_sec"] += duration
            stats["total_distance_m"] += distance
            stats["total_training_load"] += load
            stats["calories"] += calories
            stats["avg_hr_sum"] += avg_heart_rate
            stats["avg_power_sum"] += avg_power
            stats["count"] += 1

        # 5. Finalize average calculations
        for activity_type, data in weekly_summary.items():
            count = data["count"]
            if count > 0:
                data["average_heart_rate"] = data.pop("avg_hr_sum") / count
                data["average_power"] = data.pop("avg_power_sum") / count
        
        return weekly_summary