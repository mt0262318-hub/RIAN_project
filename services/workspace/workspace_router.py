import logging
from fastapi import APIRouter
from pydantic import BaseModel
from services.workspace.os_driver import WorkspaceAgentEngine

logger = logging.getLogger("workspace_router")
workspace_router = APIRouter(prefix="/workspace", tags=["Workspace & OS Agent"])
driver = WorkspaceAgentEngine()

class CodeExecutionPayload(BaseModel):
    code: str

@workspace_router.get("/status")
async def get_workspace_status():
    status = driver.inspect_workspace_environment()
    return {"status": "success", "environment": status}

@workspace_router.post("/execute-code")
async def execute_code_sandboxed(payload: CodeExecutionPayload):
    result = driver.execute_dynamic_code(payload.code)
    return {"status": "success", "execution": result}
