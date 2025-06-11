from google.adk.agents import SequentialAgent, Agent
# from google.adk.tools.agent_tool import AgentTool

# from sub_agents.guidance_agent.agent import guidance_agent
# from sub_agents.predictive_maintenance_agent.agent import predictive_maintenance_agent
# from sub_agents.notification_escalation_agent.agent import notification_agent

root_agent = Agent(
    name="MixedRealityMaintenanceAgent",
    model="gemini-2.0-flash-001",
    instruction="say hello world"

)
