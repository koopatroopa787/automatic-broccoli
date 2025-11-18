"""ETL Pipeline Router - Manage ETL pipelines and executions"""
from fastapi import APIRouter, Depends
from backend.api.routers.auth import get_current_active_user

router = APIRouter()

@router.get("/pipelines")
async def list_pipelines(current_user = Depends(get_current_active_user)):
    """List all ETL pipelines"""
    return {"pipelines": [], "message": "ETL pipelines endpoint"}

@router.post("/pipelines/{pipeline_id}/execute")
async def execute_pipeline(pipeline_id: int, current_user = Depends(get_current_active_user)):
    """Trigger pipeline execution"""
    return {"message": f"Executing pipeline {pipeline_id}"}
