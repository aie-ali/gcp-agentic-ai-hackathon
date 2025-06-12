from google.adk.agents import SequentialAgent, LlmAgent, Agent
#from google.adk.events import Event, EventActions
#from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools.agent_tool import AgentTool

#from sub_agents.guidance_agent.agent import guidance_agent
#from sub_agents.predictive_maintenance_agent.agent import predictive_maintenance_agent
#from sub_agents.notification_escalation_agent.agent import notification_agent


### Tools ### 
def save_machineID_to_state(
    tool_context: ToolContext,
    machineID: List[str]
) -> dict[str, str]:
    """Saves the machineID state["machineID"].

    Args:
        machineID [str]: a list of strings to add to the list of machineIDs in state.

    Returns:
        None
    """
    # Load existing affected machines from state. If none exist, start an empty list
    existing_machines = tool_context.state.get("machineID", [])

    # When the tool is run, ADK will create an event and make
    # corresponding updates in the session's state.
    tool_context.state["machineID"] = existing_machines + machineID
    # Return success
    return {"status": "success"}

### Agents ###
predictive_maintenance_agent = Agent(
    model="gemini-2.0-flash-001",
    name="PredictiveMaintenanceAgent",
    instruction=f"Detect anomalies in the data. If an anomaly is found, use the 'save_machineID_to_state' tool to add the affected machine to the field 'machineID'. For now, flag the machine as 'machine-01",
    #output_key="machineID",
    tools=[save_machineID_to_state]
)

notification_agent = Agent(
    model="gemini-2.0-flash-001",
    name="NotificationAgent",
    instruction="Send a notification stating that state['machineID'] is broken to guidance agent",
    output_key="notificationMessage"
    # tools=[sendNotification]
)

guidance_agent = Agent(
    model="gemini-2.0-flash-001",
    name="GuidanceAgent",
    instruction="make up 5 steps to fix state['notificationMessage']",
    output_key="guidanceSteps"
)


### Main Agent ###
root_agent = LlmAgent(
    name="MixedRealityMaintenanceAgent",
    model="gemini-2.0-flash-001",
    instruction="Coordinate the system of agents. You will work with sub-agents to provide predictive maintenance insights, notification escalation, and provide operator guidance. Predictive_maintenance agent will detect anomalies in the telemetry data and save the machine ID to state. Notification agent will send a notification to guidance agent with the machine ID. Guidance agent will provide steps to fix the issue.",
    sub_agents=[predictive_maintenance_agent, notification_agent, guidance_agent]

)
