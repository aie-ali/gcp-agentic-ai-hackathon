from google.adk import Agent


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

predictive_maintenance_agent = Agent(
    model="gemini-2.0-flash-001",
    name="PredictiveMaintenanceAgent",
    instruction=f"Detect anomalies in the data. Flag the machine id as 'machine-01' and save to state",
    output_key="machineId",
)
