import json
import sys
import os
from dotenv import load_dotenv
from fastmcp import Client
from google import genai
from google.genai import types
from ..history_manager import PersistentHistoryManager


class SeasonContentCheckerAgent:
    def __init__(self):
        load_dotenv()
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            sys.exit("Error: GEMINI_API_KEY missing.") 
        self.client = genai.Client(api_key=gemini_api_key)
        self.model_id = "gemini-2.5-flash"

    async def check_plan(self, season_plan_json, athlete_history_summary):
        """
        Compares the proposed plan against actual history to detect hallucinations.
        """
        prompt = f"""
        ### ROLE
        You are a World-Tour Physiologist. Your job is to FACT-CHECK a proposed Season Macrocycle.

        ### INPUT DATA
        1. PROPOSED PLAN: {json.dumps(season_plan_json)}
        2. ATHLETE HISTORY (Ground Truth): {json.dumps(athlete_history_summary)}

        ### VALIDATION CRITERIA
        - LOAD SPIKE: Does any phase increase weekly hours too rapidly?
        - OBJECTIVE MISMATCH: Does the plan align with the stated main race goal?
        - HALLUCINATION: Does the plan reference stats (like a VO2 max or FTP) that are NOT in the history?

        ### OUTPUT FORMAT
        Return a JSON object:
        {{
            "is_valid": bool,
            "safety_score": int (1-10),
            "flags": ["list of specific issues found"],
            "recommendation": "Brief fix for the Season Planner"
        }}
        """
        
        response = await self.client.aio.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0, # Zero temperature for consistent fact-checking
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)