import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from ..main import app
from ..db.database import db
from ..services.ml_integration import ml_service

client = TestClient(app)

def test_health_check_all_healthy():
    # Mock database and ML services to be healthy
    with patch.object(db, 'execute_query', return_value=True), \
         patch.object(ml_service, 'fraud_model', True), \
         patch.object(ml_service, 'metadata_analyzer', True), \
         patch.object(ml_service, 'matching_model', True):
        
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["database"] == "healthy"
        assert data["ml_services"]["fraud_detection"] == "available"
        assert data["ml_services"]["metadata_analyzer"] == "available"
        assert data["ml_services"]["matching_model"] == "available"

def test_health_check_database_unhealthy():
    # Mock database to be unhealthy but ML services healthy
    with patch.object(db, 'execute_query', side_effect=Exception("DB Error")), \
         patch.object(ml_service, 'fraud_model', True), \
         patch.object(ml_service, 'metadata_analyzer', True), \
         patch.object(ml_service, 'matching_model', True):
        
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "degraded"
        assert data["database"] == "unhealthy"
        assert data["ml_services"]["fraud_detection"] == "available"
        assert data["ml_services"]["metadata_analyzer"] == "available"
        assert data["ml_services"]["matching_model"] == "available"

def test_health_check_ml_services_unhealthy():
    # Mock database healthy but ML services unhealthy
    with patch.object(db, 'execute_query', return_value=True), \
         patch.object(ml_service, 'fraud_model', False), \
         patch.object(ml_service, 'metadata_analyzer', False), \
         patch.object(ml_service, 'matching_model', False):
        
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "degraded"
        assert data["database"] == "healthy"
        assert data["ml_services"]["fraud_detection"] == "unavailable"
        assert data["ml_services"]["metadata_analyzer"] == "unavailable"
        assert data["ml_services"]["matching_model"] == "unavailable"

def test_health_check_partial_degradation():
    # Mock some services healthy and others unhealthy
    with patch.object(db, 'execute_query', return_value=True), \
         patch.object(ml_service, 'fraud_model', True), \
         patch.object(ml_service, 'metadata_analyzer', False), \
         patch.object(ml_service, 'matching_model', True):
        
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "degraded"
        assert data["database"] == "healthy"
        assert data["ml_services"]["fraud_detection"] == "available"
        assert data["ml_services"]["metadata_analyzer"] == "unavailable"
        assert data["ml_services"]["matching_model"] == "available" 