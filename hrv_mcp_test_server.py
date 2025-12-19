import datetime
import os
from fastmcp import FastMCP, Context

import logging

from garminconnect import Garmin

# --- STEP 1: ROBUST LOGGING SETUP ---
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.StreamHandler(), # This goes to stderr by default in MCP
        logging.FileHandler("mcp_server_debug.log") # This saves to your folder
    ]
)
logger = logging.getLogger("mcp_server")
logger.info("Server script started initialized.")

# Initialize the MCP Server
mcp = FastMCP("SimpleGarmin")

def get_api():
    token_dir = os.path.expanduser("~/.garminconnect")
    # 1. Initialize and Login
    client = Garmin() # (email, password) if token expired
    client.login(tokenstore=token_dir)
    
    # Save tokens to the default directory (~/.garminconnect)
    token_dir = os.path.expanduser("~/.garminconnect")
    os.makedirs(token_dir, exist_ok=True)
    client.garth.dump(token_dir)

    return client

@mcp.tool()
async def get_hrv_for_date(date_str: str = None, ctx: Context = None) -> dict:
    """
    Fetches HRV (Heart Rate Variability) data for a specific date.
    :param date_str: Date in ISO format (YYYY-MM-DD). Defaults to today.
    """
    if not date_str:
        date_str = datetime.date.today().isoformat()
    
    logger.info(f"Fetching HRV data for date: {date_str}")

    if ctx:
        await ctx.info(f"Talking to Garmin for date {date_str}...")

    api = get_api()
    # 'get_hrv_data' is the standard method for daily HRV summaries
    hrv_data = api.get_hrv_data(date_str)
    return hrv_data

@mcp.tool()
async def get_workout_by_date_optimized(date_str: str, ctx: Context) -> dict:
    """
    Fetches high-resolution workout data but optimized to stay within token limits.
    """
    await ctx.info(f"Fetching and optimizing data for {date_str}...")
    
    try:
        api = get_api()
        activities = api.get_activities_by_date(date_str, date_str)
        
        if not activities:
            return {"message": "No activities found."}

        optimized_data = []

        for activity in activities:
            details = api.get_activity_details(activity["activityId"])
            
            # 1. EXTRACT SENSOR STREAMS
            # Usually found in metrics or activityDetailMetrics
            metrics = details.get("metrics", [])
            
            # 2. DOWNSAMPLE (Take every 15th second to reduce size by 93%)
            # This turns a 2-hour ride into a manageable few hundred points.
            downsampled_metrics = metrics[::15] 

            # 3. CLEAN DATA (Remove heavy fields like latitude/longitude)
            clean_metrics = []
            for m in downsampled_metrics:
                # Keep only what the AI Coach needs
                clean_metrics.append({
                    "time": m.get("timestamp"),
                    "hr": m.get("heartRate"),
                    "pwr": m.get("power"),
                    "cad": m.get("cadence")
                })

            optimized_data.append({
                "id": activity["activityId"],
                "type": activity.get("activityType", {}).get("typeKey"),
                "summary": {
                    "avg_hr": activity.get("averageHR"),
                    "max_hr": activity.get("maxHR"),
                    "avg_pwr": activity.get("averagePower"),
                    "calories": activity.get("calories")
                },
                "time_series_snapshot": clean_metrics
            })

        return {"date": date_str, "activities": optimized_data}

    except Exception as e:
        logger.error(f"Optimization error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run()