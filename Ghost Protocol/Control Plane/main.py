from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import models, schemas, database

app = FastAPI(title="Ghost Protocol Control Plane")

# Initialize DB tables on startup
models.Base.metadata.create_all(bind=database.engine)

@app.post("/api/v1/incidents/trigger", response_model=schemas.IncidentResponse)
def trigger_chaos(payload: schemas.IncidentCreate, db: Session = Depends(database.get_db)):
    """ Endpoint for admins/schedulers to launch a surprise attack on infrastructure """
    incident = models.ChaosIncident(
        agent_id=payload.agent_id,
        experiment_type=payload.experiment_type,
        status="triggered",
        triggered_at=datetime.utcnow()
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident

@app.get("/api/v1/agent/{agent_id}/poll")
def agent_poll(agent_id: str, db: Session = Depends(database.get_db)):
    """ Agents continually poll this endpoint to look for active attacks """
    active_incident = db.query(models.ChaosIncident).filter(
        models.ChaosIncident.agent_id == agent_id,
        models.ChaosIncident.status == "triggered"
    ).order_by(models.ChaosIncident.triggered_at.desc()).first()

    if not active_incident:
        return {"action": "sleep"}
        
    return {
        "action": "execute",
        "incident_id": active_incident.id,
        "experiment_type": active_incident.experiment_type
    }

@app.post("/api/v1/webhooks/pagerduty")
def pagerduty_webhook(payload: dict, db: Session = Depends(database.get_db)):
    """ 
    Simulated ingestion endpoint parsing alerts sent from monitoring stacks.
    Tracks human behavior timestamps automatically.
    """
    event = payload.get("event", {})
    action = event.get("action")  # 'acknowledge' or 'resolve'
    incident_id = event.get("custom_incident_id") # Linked internal ID mapping

    incident = db.query(models.ChaosIncident).filter(models.ChaosIncident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident tracking record not found")

    now = datetime.utcnow()

    if action == "acknowledge" and incident.status == "triggered":
        incident.status = "acknowledged"
        incident.acknowledged_at = now
        incident.time_to_acknowledge = (now - incident.triggered_at).total_seconds()
        
    elif action == "resolve" and incident.status == "acknowledged":
        incident.status = "resolved"
        incident.resolved_at = now
        incident.time_to_resolution = (now - incident.triggered_at).total_seconds()
        
        # Gamified Scoring Algorithm Formula:
        # High points for fast reaction times. Base starts at 5000 points.
        tta_penalty = incident.time_to_acknowledge * 2
        ttr_penalty = incident.time_to_resolution * 0.5
        incident.final_score = max(0, int(5000 - (tta_penalty + ttr_penalty)))

    db.commit()
    return {"status": "metrics_updated"}