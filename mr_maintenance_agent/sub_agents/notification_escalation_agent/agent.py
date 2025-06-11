from google.adk import Agent

notification_agent = Agent(
    model="gemini-2.0-flash-001",
    name="NotificationAgent",
    instruction="Send a notification stating that state['machineId'] is broken to guidance agent",
    output_key="notificationMessage"
    # tools=[sendNotification]
)