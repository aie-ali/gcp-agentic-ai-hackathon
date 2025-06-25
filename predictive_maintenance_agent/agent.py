from google.adk import Agent
from google.adk.tools.agent_tool import AgentTool, ToolContext
from typing import List
from contracts import AnomalyEvent, Severity
from google.adk.tools import VertexAiSearchTool
import os
from dotenv import load_dotenv

load_dotenv()

telemetry = {
    "eventTime": "2025-06-01T00:00:00Z",
    "dimensions": [
        {"name": "measure", "stringVal": "SENSOR"},
        {"name": "machine_id", "stringVal": "Machine-01"},
        {"name": "temperature", "doubleVal": 49.71},
        {"name": "pressure", "doubleVal": 4.91},
        {"name": "current", "doubleVal": 9.87},
    ],
}


### Tools ### 
rag_tool = VertexAiSearchTool(data_store_id=os.getenv('DATASTORE_ID'))


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

def detect_anomalies(tool_context: ToolContext):
        """ Detects anomalies in the telemetry data stored in state["current_slice"].

        Anomalies are identified based on a threshold of anomaly_score.

        If an anomaly is detected, it creates an AnomalyEvent and saves it to state["events"].

        """

        rows = tool_context.state["current_slice"] # From fake data agent
        events = []
        for r in rows:
            if r["anomaly_score"] > tool_context.state["anomaly_criteria"]:
                sev = Severity.CRITICAL if r["anomaly_score"]>0.95 else Severity.HIGH
                events.append(AnomalyEvent(
                    machine_id=r["machine_id"],
                    ts=r["ts"],
                    anomaly_type=r["type"],
                    score=r["anomaly_score"],
                    severity=sev,
                ))
        tool_context.state["events"] = events # Save events to state for notification agent

        return f"{len(events)} anomalies"





def create_predictive_maintenance_agent():
    """Creates and returns a PredictiveMaintenanceAgent instance.
    
    This agent detects anomalies in telemetry data and saves affected machine IDs to state.
    """

    predictive_maintenance_agent = Agent(
    model="gemini-2.0-flash-001",
    name="PredictiveMaintenanceAgent",
    instruction=f"""Detect anomalies in the data.
    First identify anomaly criteria using rag_tool. Set that value in state["anomaly_criteria"]. Next 
    Call detect_anomalies tool to analyse the telemetry data in state["current_slice"]. 
    If an anomaly is found, use the 'save_machineID_to_state' tool to add the affected machine to the field 'machineID'.  
    If tool returns 'success', then pass onto notification agent.""",
    tools=[detect_anomalies, save_machineID_to_state, rag_tool]
    )
    return predictive_maintenance_agent

# Expose root_agent for ADK
root_agent = create_predictive_maintenance_agent() 
