from fastapi import APIRouter, status, HTTPException, Body
from fastapi.responses import JSONResponse

from app.schemas.agent_schema import AgentRegisterRequest, AgentResponse

route = APIRouter()

@route.post("/register", response_class=AgentResponse, summary="Agent register api")
async def agent_register(agent_payload: AgentRegisterRequest = Body(..., description="Agent register payload") ):
    pass