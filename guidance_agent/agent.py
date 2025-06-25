from google.adk import Agent
from google.adk.tools.agent_tool import ToolContext

### Tools ###

def generate_guidance(tool_context: ToolContext) -> str:
    """
    Build five numbered repair steps for the first open incident.
    If no incidents exist, say 'No issues found.'
    """
    incidents = tool_context.state.get("open_incidents", {})
    if not incidents:
        return "No issues found."

    # pick the first incident   
    inc = next(iter(incidents.values()))
    machine = inc["machine_id"]
    type_   = inc["anomaly_type"]
    # For now create generic steps based on machine and type
    steps = [
        f"1. Isolate {machine} and power it down.",
        f"2. Inspect the {type_} sensor wiring for loose connections.",
        "3. Clean any debris or corrosion from the sensor housing.",
        "4. Restart the machine and monitor the sensor reading for 10 minutes.",
        "5. If the anomaly persists, schedule a full calibration procedure.",
    ]
    return "\n".join(steps)


### Agents ###

def create_guidance_agent():
    """
    Creates and returns a GuidanceAgent instance.
    This agent provides repair steps based on the latest notification message.
    """
    guidance_agent = Agent(
        model="gemini-2.0-flash-001",
        name="GuidanceAgent",
        instruction="Call `generate_guidance` exactly once and return its result.",
        tools=[generate_guidance],
        output_key="guidanceSteps"
    )
    return guidance_agent

# Expose root_agent for ADK
root_agent = create_guidance_agent() 