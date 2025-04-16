from fastapi import APIRouter, Depends
from typing import Dict, Any
from pydantic import BaseModel
from ..db.database import db
from ..services.ml_integration import ml_service

router = APIRouter()

class MLServicesStatus(BaseModel):
    fraud_detection: str
    metadata_analyzer: str
    matching_model: str

class HealthStatus(BaseModel):
    status: str
    database: str
    ml_services: MLServicesStatus

@router.get("/health", response_model=HealthStatus)
async def health_check() -> Dict[str, Any]:
    """Check the health of all services."""
    status = {
        "status": "healthy",
        "database": "unhealthy",
        "ml_services": {
            "fraud_detection": "unavailable",
            "metadata_analyzer": "unavailable",
            "matching_model": "unavailable"
        }
    }
    
    # Check database connection
    try:
        db.execute_query("RETURN 1")
        status["database"] = "healthy"
    except Exception:
        status["status"] = "degraded"
    
    # Check ML services
    if ml_service.fraud_model:
        status["ml_services"]["fraud_detection"] = "available"
    else:
        status["status"] = "degraded"
        
    if ml_service.metadata_analyzer:
        status["ml_services"]["metadata_analyzer"] = "available"
    else:
        status["status"] = "degraded"
        
    if ml_service.matching_model:
        status["ml_services"]["matching_model"] = "available"
    else:
        status["status"] = "degraded"
    
    return status 