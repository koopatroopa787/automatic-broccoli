"""Reports Router - Report generation"""
from fastapi import APIRouter, Depends
from api.routers.auth import get_current_active_user

router = APIRouter()

@router.get("/")
async def list_reports(current_user = Depends(get_current_active_user)):
    """List available reports"""
    return {"reports": [], "message": "Reports endpoint"}
