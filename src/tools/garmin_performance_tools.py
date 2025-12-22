import logging
from fastmcp import Context

from garminconnect import Garmin
import os

from garth import client

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

def register_garmin_performance_tools(mcp):
    """
    Registers all Garmin-Performance-related tools to the provided MCP server instance.
    """
    @mcp.tool()
    def get_vo2_max(date_str, ctx: Context) -> dict:
        """
        Fetches VO2 max for a specific date (YYYY-MM-DD).
        """
        logger.info(f"Fetching VO2 max for {date_str}")

        client = get_api()
        max_metrics = client.get_training_status(date_str)
        cycling_vo2max = max_metrics.get("mostRecentVO2Max").get("cycling").get("vo2MaxPreciseValue")
        running_vo2max = max_metrics.get("mostRecentVO2Max").get("generic").get("vo2MaxPreciseValue")

        return {
            "cycling_vo2max": cycling_vo2max,
            "running_vo2max": running_vo2max
        }

    @mcp.tool()
    def get_altitude_acclimation(date_str, ctx: Context) -> dict:
        """
        Fetches altitude acclimation and sleep altitude for a specific date (YYYY-MM-DD).
        """
        logger.info(f"Fetching altitude acclimation for {date_str}")

        client = get_api()
        acclimation_data = client.get_training_status(date_str)
        altitude_acclimation = acclimation_data.get("mostRecentVO2Max").get("heatAltitudeAcclimation").get("altitudeAcclimation")
        current_altitude_meters = acclimation_data.get("mostRecentVO2Max").get("heatAltitudeAcclimation").get("currentAltitude")

        return {
            "altitude_acclimation": altitude_acclimation,
            "current_altitude_meters": current_altitude_meters
        }
    
    @mcp.tool()
    def get_heat_acclimation_percentage(date_str, ctx: Context) -> dict:
        """
        Fetches heat acclimation percentage for a specific date (YYYY-MM-DD).
        """
        logger.info(f"Fetching heat acclimation percentage for {date_str}")

        client = get_api()
        acclimation_data = client.get_training_status(date_str)
        heat_acclimation_percentage = acclimation_data.get("mostRecentVO2Max").get("heatAltitudeAcclimation").get("heatAcclimationPercentage")

        return {
            "heat_acclimation_percentage": heat_acclimation_percentage
        }
    
    @mcp.tool()
    def get_training_readiness(date_str, ctx: Context) -> dict:
        """
        Fetches training readiness score for a specific date (YYYY-MM-DD).
        """
        logger.info(f"Fetching training readiness for {date_str}")

        client = get_api()
        readiness_data = client.get_training_readiness(date_str)
        overall_readiness = readiness_data[0].get("score")

        return {
            "overall_readiness": overall_readiness,
        }
    
    @mcp.tool()
    def get_monthly_training_load(client, date_str):
        """
        Fetches training load data for a specific date (YYYY-MM-DD).
        """
        logger.info(f"Fetching monthly training load for {date_str}")

        client = get_api()
        load_data = client.get_training_status(date_str)
        monthly_low_aerobic_load = load_data.get("mostRecentTrainingLoadBalance").get("metricsTrainingLoadBalanceDTOMap").get("3438848558").get("monthlyLoadAerobicLow")
        monthly_high_aerobic_load = load_data.get("mostRecentTrainingLoadBalance").get("metricsTrainingLoadBalanceDTOMap").get("3438848558").get("monthlyLoadAerobicHigh")
        monthly_anaerobic_load = load_data.get("mostRecentTrainingLoadBalance").get("metricsTrainingLoadBalanceDTOMap").get("3438848558").get("monthlyLoadAnaerobic")

        return {
            "monthly_low_aerobic_load": monthly_low_aerobic_load,
            "monthly_high_aerobic_load": monthly_high_aerobic_load,
            "monthly_anaerobic_load": monthly_anaerobic_load
        }
    
    @mcp.tool()
    def get_training_load(date_str, ctx: Context) -> dict:
        """
        Fetches training load data for a specific date (YYYY-MM-DD).
        """
        logger.info(f"Fetching training load for {date_str}")

        client = get_api()
        load_data = client.get_training_status(date_str)
        daily_acute_load = load_data.get("mostRecentTrainingStatus").get("latestTrainingStatusData").get("3438848558").get("acuteTrainingLoadDTO").get("dailyTrainingLoadAcute")
        daily_chronic_load = load_data.get("mostRecentTrainingStatus").get("latestTrainingStatusData").get("3438848558").get("acuteTrainingLoadDTO").get("dailyTrainingLoadChronic")
        max_training_load_chronic = load_data.get("mostRecentTrainingStatus").get("latestTrainingStatusData").get("3438848558").get("acuteTrainingLoadDTO").get("maxTrainingLoadChronic")
        min_training_load_chronic = load_data.get("mostRecentTrainingStatus").get("latestTrainingStatusData").get("3438848558").get("acuteTrainingLoadDTO").get("minTrainingLoadChronic")
        acute_chronic_ratio = load_data.get("mostRecentTrainingStatus").get("latestTrainingStatusData").get("3438848558").get("acuteTrainingLoadDTO").get("dailyAcuteChronicWorkloadRatio")
        return {
            "daily_acute_load": daily_acute_load,
            "daily_chronic_load": daily_chronic_load,
            "max_training_load_chronic": max_training_load_chronic,
            "min_training_load_chronic": min_training_load_chronic,
            "acute_chronic_ratio": acute_chronic_ratio
        }
    
    @mcp.tool()
    def get_training_status(date_str, ctx: Context) -> dict:
        """
        Fetches garmin training status for a specific date (YYYY-MM-DD).
        """
        logger.info(f"Fetching training status for {date_str}")

        client = get_api()
        load_data = client.get_training_status(date_str)
        daily_status_feedback = load_data.get("mostRecentTrainingStatus").get("latestTrainingStatusData").get("3438848558").get("trainingStatusFeedbackPhrase")
        
        return {
            "daily_status_feedback": daily_status_feedback
        }