"""Queries Router - SQL query management"""
from fastapi import APIRouter, Depends
from backend.api.routers.auth import get_current_active_user

router = APIRouter()

@router.get("/")
async def list_queries(current_user = Depends(get_current_active_user)):
    """List saved queries"""
    return {"queries": [], "message": "Queries endpoint"}
