import asyncio
import os
import sys
from dotenv import load_dotenv
from fastmcp import Client
from google import genai
from google.genai import types
from ..history_manager import PersistentHistoryManager

import datetime

import logging

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

logging.basicConfig(
    filename='thoughts_health_specialist.log',
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    filemode='a' # 'a' to append, 'w' to overwrite each session
)
logger = logging.getLogger("ThoughtLogger")

class HealthSpecialistAgent:
    def __init__(self, mcp_session):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.mcp_session = mcp_session
        self.memory = PersistentHistoryManager(self.client, max_messages=20, filename="memory/health_specialist.json")
        
        self.chat = self.client.aio.chats.create(
            model="gemini-2.5-flash",
            history=self.memory.get_loadable_history(),
            config=types.GenerateContentConfig(
                tools=[self.mcp_session],
                temperature=1.0,
                system_instruction="""
                ### ROLE
                You are a Cycling World Tour Sports Physician. Your goal is to analyze the athlete's biometrics (HRV, RHR, Sleep, Body Battery) via Garmin tools and provide a Health Clearance assessment.

                ### STRATEGIC WORKFLOW
                1. DATA FETCH: Use tools to check trends for the last 14 days.
                2. CLARIFY: If you see red flags (e.g., low HRV, high RHR), you MUST ask the user about subjective symptoms (fatigue, illness, stress, muscle pain).
                3. EVALUATE: Based on data and user feedback, determine the health status and ask any follow-up questions if needed.
                4. ASSESS: Once you have the data and user feedback, provide the final Clearance JSON.

                ### OUTPUT RULES
                - For questions: Brief, professional, conversational text.
                - For final assessment: Return ONLY the JSON object.

                ### JSON STRUCTURE
                {
                    "health_status": "Green/Yellow/Red",
                    "readiness_score (0-100)": int,
                    "biometric_red_flags": [],
                    "coach_restrictions": "Explicit constraints for the training coach"
                }
                """
            )
        )

    async def analyze_health(self, user_input=None):
        """Interactive loop for health clearance."""
        if user_input is None:
            prompt = "Please analyze my health data for the last 14 days. Use your tools to check HRV, RHR, and Sleep."
        else:
            prompt = user_input

        # 1. Send the message
        response = await self.chat.send_message(prompt)
        
        # 2. Safety check: Ensure candidates and content exist
        if not response.candidates or not response.candidates[0].content:
            # This happens if the model is only doing a tool call with no text preamble
            # The SDK usually handles the tool loop, but we need to return something
            return "Thinking... (Tool call in progress)"

        full_text = ""
        # 3. Iterate safely through parts
        parts = response.candidates[0].content.parts
        if parts:
            for part in parts:
                if part.thought:
                    logger.info(f"THOUGHT: {part.text}")
                if part.text:
                    full_text += part.text
        
        # If the model didn't return text but did a tool call, 
        # full_text might be empty. Return the clean output of what we have.
        return self._clean_output(full_text)
    
    def _clean_output(self, text):
        """
        Extracts JSON from the response if present, 
        otherwise returns the raw text (for clarifying questions).
        """
        text = text.strip()
        # Look for the JSON block
        if "```json" in text:
            return text.split("```json")[1].split("```")[0].strip()
        elif text.startswith("{"):
            return text
        return text # This will be the clarifying questions