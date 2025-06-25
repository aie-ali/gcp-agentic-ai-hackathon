from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import ToolContext
from datetime import datetime, timezone
import random

### Tools ###

# Tool to inject fake sensor data into the state
def inject_fake_slice(tool_context: ToolContext):
        row = {
            "machine_id": "machine-01",
            "ts": datetime.now(timezone.utc).isoformat(),
            "type": "temperature",
            # Creates anomaly score, with any score > 0.8 tripping the detector
            "anomaly_score": random.uniform(0.9, 0.97),
        }
        tool_context.state["current_slice"] = [row]  # Wired to predictive maintenance agent

        return (f"Injected 1 synthetic row → "
                f"score={row['anomaly_score']:.3f}")


### Agents ###

# Factory function to create the FakeDataAgent
def create_fakedata_agent():
    """
    Injects a single sensor row with an obviously high anomaly_score.
    """

    fakedata_agent = LlmAgent(
        name="FakeDataAgent",
        model="gemini-2.0-flash-001",
        tools=[inject_fake_slice],
        instruction="Always call `inject_fake_slice` once then pass onto PredictiveMaintenanceAgent."
    )
    return fakedata_agent

# Expose root_agent for ADK
root_agent = create_fakedata_agent()