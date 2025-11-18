"""Data Sources Router - Manage data source connections"""
from fastapi import APIRouter, Depends
from api.routers.auth import get_current_active_user

router = APIRouter()

@router.get("/")
async def list_data_sources(current_user = Depends(get_current_active_user)):
    """List all configured data sources"""
    return {"data_sources": [], "message": "Data sources endpoint"}

@router.post("/")
async def create_data_source(current_user = Depends(get_current_active_user)):
    """Create new data source connection"""
    return {"message": "Create data source"}
