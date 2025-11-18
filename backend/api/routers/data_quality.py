"""Data Quality Router - Data quality monitoring"""
from fastapi import APIRouter, Depends
from backend.api.routers.auth import get_current_active_user

router = APIRouter()

@router.get("/rules")
async def list_quality_rules(current_user = Depends(get_current_active_user)):
    """List data quality rules"""
    return {"rules": [], "message": "Data quality rules endpoint"}

@router.get("/checks")
async def list_quality_checks(current_user = Depends(get_current_active_user)):
    """List quality check results"""
    return {"checks": [], "message": "Data quality checks endpoint"}
