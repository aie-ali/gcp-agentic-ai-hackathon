from pydantic import BaseModel
from datetime import datetime
from enum import IntEnum

class Severity(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class AnomalyEvent(BaseModel):
    machine_id: str
    ts: datetime
    anomaly_type: str
    score: float
    severity: Severity