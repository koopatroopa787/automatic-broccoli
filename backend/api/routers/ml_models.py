"""ML Models Router - Model registry and predictions"""
from fastapi import APIRouter, Depends
from backend.api.routers.auth import get_current_active_user

router = APIRouter()

@router.get("/")
async def list_models(current_user = Depends(get_current_active_user)):
    """List all ML models"""
    return {"models": [], "message": "ML models endpoint"}

@router.post("/{model_id}/predict")
async def predict(model_id: int, current_user = Depends(get_current_active_user)):
    """Make predictions using model"""
    return {"prediction": None, "message": "Prediction endpoint"}
