from google.adk import Agent
from google.adk.tools.agent_tool import AgentTool, ToolContext
from contracts import AnomalyEvent, Severity
from datetime import datetime, timezone


### Tools ###

def send_notification_to_state(tool_context: ToolContext) -> dict[str, str]:
    """Write a dashboard message based on ALL open incidents."""

    incidents = tool_context.state.get("open_incidents", {})
    if not incidents:
        msg = "No active incidents"
    else:
        ids = {inc["machine_id"] for inc in incidents.values()}
        msg = f"Failures detected on {', '.join(sorted(ids))}"

    tool_context.state["notificationMessage"] = msg
    return {"status": "success", "notificationMessage": msg}


def merge_and_escalate(tool_context: ToolContext) -> str:
    """
    Merge new anomaly events into the open-incidents ledger.
    Each entry has an `sms_sent` flag (initially False) for escalating messages.
    """
    new_events: list[AnomalyEvent] = tool_context.state.get("events", [])

    # Ledger initialisation
    open_incidents = tool_context.state.get("open_incidents")
    if open_incidents is None:
        open_incidents = {}
        tool_context.state["open_incidents"] = open_incidents

    for ev in new_events:
        key = f"{ev.machine_id}:{ev.anomaly_type}"

        entry = {
            "machine_id": ev.machine_id,
            "anomaly_type": ev.anomaly_type,
            "score": ev.score,
            "severity": int(ev.severity),
            "ts": ev.ts.isoformat(),   
            "sms_sent": False,  # For escalation      
        }

        prev = open_incidents.get(key)
        if prev is None or ev.severity > Severity(prev["severity"]):
            open_incidents[key] = entry

    return f"{len(new_events)} events merged"


def send_sms_notifications(tool_context: ToolContext) -> str:
    """
    Send SMS for each unsent incident whose severity is CRITICAL 
    or has been open ≥ 10 min. Marks `sms_sent=True` after sending.
    """
    incidents = tool_context.state.get("open_incidents", {})
    if not incidents:
        return "No incidents in ledger."

    now = datetime.now(timezone.utc)
    count = 0

    for inc in incidents.values():
        if inc.get("sms_sent"):
            continue  # already notified

        # parse ISO timestamp back to aware datetime
        inc_ts = datetime.fromisoformat(inc["ts"])
        age = (now - inc_ts).total_seconds()

        if inc["severity"] >= Severity.CRITICAL or age >= 600:
            body = (f"[{Severity(inc['severity']).name}] "
                    f"{inc['machine_id']} – {inc['anomaly_type']} "
                    f"score={inc['score']:.2f} @ {inc['ts']}")
            print(f"[{datetime.utcnow().isoformat()}] SMS → {body}")
            inc["sms_sent"] = True
            count += 1

    return f"{count} SMS sent"


### Agent ###

def create_notification_agent():
    """Creates and returns a NotificationAgent instance.
    This agent sends notifications based on the anomaly events
    and escalates them to the state for further processing.
    """

    notification_agent = Agent(
        model="gemini-2.0-flash-001",
        name="NotificationAgent",
        instruction="""
        Run the tools in this order:
        1. Merge_and_escalate
        2. send_notification_to_state
        3. send_sms_notifications
        Now pass onto GuidanceAgent.""",
        tools=[merge_and_escalate, send_notification_to_state, send_sms_notifications]
    )
    return notification_agent

# Expose root_agent for ADK
root_agent = create_notification_agent() 