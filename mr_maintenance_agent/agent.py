from google.adk.agents import SequentialAgent, LlmAgent, Agent
#from google.adk.events import Event, EventActions
#from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools.agent_tool import AgentTool, ToolContext
from google.adk.agents.invocation_context import InvocationContext

from typing import List

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
    print(f"Tool: Updated machineID '{machineID}' with '{machineID}'")
    # Return success
    return {"status": "success"}

def send_notification_to_state(
    tool_context: ToolContext,
) -> dict[str, str]:
    """Accesses state["machineID"] and saves to state["notificationMessage"].

    Args:
        Notification [str]: a list of strings to add to the list of notifications for guidance agent in state.

    Returns:
        None
    """
    # Load machineID from state and generate notification message
    machine_ids = tool_context.state.get("machineID", [])
    if not machine_ids:
        notification = "No machineID found"
    else:
        notification = f"Failures detected on {', '.join(machine_ids)}"

    # Save notification to state
    tool_context.state["notificationMessage"] = notification

    return {"status": "success", "notificationMessage": notification}


### Agents ###
predictive_maintenance_agent = Agent(
    model="gemini-2.0-flash-001",
    name="PredictiveMaintenanceAgent",
    instruction=f"""Detect anomalies in the data. 
    If an anomaly is found, use the 'save_machineID_to_state' tool to add the affected machine to the field 'machineID'. 
    For now, flag the machine as 'machine-01. 
    If tool returns 'success', then pass onto notification agent.""",
    tools=[save_machineID_to_state]
)

notification_agent = Agent(
    model="gemini-2.0-flash-001",
    name="NotificationAgent",
    instruction="""Use the 'send_notification_to_state' tool to save the machineID saved in state.
    if the tool returns 'success', then pass onto guidance agent.""",
    tools=[send_notification_to_state]
)

guidance_agent = Agent(
    model="gemini-2.0-flash-001",
    name="GuidanceAgent",
    instruction="""
        Latest notification:
        {notificationMessage}

        Provide five numbered repair steps for the machine(s) mentioned 'notificationMessage'.
        If nothing is set, respond with 'No issues found.'
    """,
    output_key="guidanceSteps"
)


### Main Agent ###
root_agent = LlmAgent(
    name="MixedRealityMaintenanceAgent",
    model="gemini-2.0-flash-001",
    instruction="""Coordinate the system of agents. 
    You will work with sub-agents to provide predictive maintenance insights, notification escalation, and provide operator guidance. 
    Predictive_maintenance agent will detect anomalies in the telemetry data and save the machine ID to state. 
    Notification agent will send a notification to guidance agent with the machine ID. 
    Guidance agent will provide steps to fix the issue.""",
    sub_agents=[predictive_maintenance_agent, notification_agent, guidance_agent]

)
