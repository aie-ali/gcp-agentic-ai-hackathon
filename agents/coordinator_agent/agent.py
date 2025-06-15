from google.adk.agents import SequentialAgent, LlmAgent, Agent
#from google.adk.events import Event, EventActions
#from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools.agent_tool import AgentTool, ToolContext
from google.adk.agents.invocation_context import InvocationContext

from typing import List

# Sub-agent factories
from guidance_agent.agent import create_guidance_agent
from predictive_maintenance_agent.agent import create_predictive_maintenance_agent
from notification_escalation_agent.agent import create_notification_agent
from bigquery_agent.agent import create_bigquery_agent
from fakedata_agent.agent import create_fakedata_agent
import os
from contextlib import AsyncExitStack
from dotenv import load_dotenv
# Load environment variables (for GOOGLE_API_KEY)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))


def create_coordinator_agent():
    """Creates the Coordinator agent that delegates to predictive, notification, and guidance sub-agents."""

    # Instantiate predictive maintenance agent
    predictive_maintenance_agent = create_predictive_maintenance_agent()

    # Instantiate notification agent
    notification_agent = create_notification_agent()

    # Instantiate guidance agent
    guidance_agent = create_guidance_agent()

    # Instantiate bigquery agent
    #bigquery_agent = create_bigquery_agent()
    fakedata_agent = create_fakedata_agent()


    ### Main Agent ###
    coordinator_agent = Agent(
        name="CoordinatorAgent",
        model="gemini-2.0-flash-001",
        instruction="""Coordinate the system of agents. 
        You will work with sub-agents to provide predictive maintenance insights, notification escalation, and provide operator guidance. 
        Run fake data agent to generate telemetry data then pass onto PredictiveMaintenanceAgent.
        Predictive_maintenance agent will detect anomalies in the telemetry data and save the machine ID to state. 
        Notification agent will send a notification to guidance agent with the machine ID. 
        Guidance agent will provide steps to fix the issue.

        """,
        sub_agents=[fakedata_agent, predictive_maintenance_agent, notification_agent, guidance_agent] #bigquery_agent]

    )
    return coordinator_agent

root_agent = create_coordinator_agent()