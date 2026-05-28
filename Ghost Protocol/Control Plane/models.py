from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Float
from database import Base

class ChaosIncident(Base):
    __tablename__ = "chaos_incidents"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, index=True)
    experiment_type = Column(String)  # e.g., "cpu_hog", "service_stop"
    status = Column(String, default="triggered") # triggered, acknowledged, resolved
    
    # Precise timestamps for gamified telemetry
    triggered_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Calculated scores
    time_to_acknowledge = Column(Float, nullable=True) # in seconds
    time_to_resolution = Column(Float, nullable=True)  # in seconds
    final_score = Column(Integer, nullable=True)