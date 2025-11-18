"""Dashboards Router - Dashboard management"""
from fastapi import APIRouter, Depends
from backend.api.routers.auth import get_current_active_user

router = APIRouter()

@router.get("/")
async def list_dashboards(current_user = Depends(get_current_active_user)):
    """List all dashboards"""
    return {"dashboards": [], "message": "Dashboards endpoint"}
