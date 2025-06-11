from google.adk import Agent

guidance_agent = Agent(
    model="gemini-2.0-flash-001",
    name="GuidanceAgent",
    instruction="make up 5 steps to fix state['notificationMessage']",
)