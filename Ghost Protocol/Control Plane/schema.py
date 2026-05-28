from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class IncidentCreate(BaseModel):
    agent_id: str
    experiment_type: str

class IncidentResponse(BaseModel):
    id: int
    agent_id: str
    experiment_type: str
    status: str
    triggered_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    final_score: Optional[int] = None

    class Config:
        from_attributes = True