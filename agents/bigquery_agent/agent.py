from google.adk.agents import Agent
from toolbox_core import ToolboxSyncClient, ToolboxClient
from google.adk.tools.agent_tool import AgentTool, ToolContext


def create_bigquery_agent():
    """A database agent that interacts with BigQuery to perform data operations.
    This agent is designed to handle tasks such as querying, inserting, and updating data in BigQuery.
    """
    toolbox = ToolboxSyncClient("http://127.0.0.1:5000")
    tools   = toolbox.load_tool("bigquery_get_dataset_info")

    bigquery_agent = Agent(
        model="gemini-2.0-flash-001",
        name="BigQueryAgent",
        instruction="""This agent interacts with BigQuery to perform data operations.
        It can execute queries, insert new records, and update existing data.
        Use the tools provided to perform these operations.
        Ensure to handle errors gracefully and return appropriate responses.""",
        tools=[tools]  # Provide the list of tools to the Agent
    
    )
    return bigquery_agent

# Expose root_agent for ADK
root_agent = create_bigquery_agent()