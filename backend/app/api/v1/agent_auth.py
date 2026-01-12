from fastapi import APIRouter, status, Body, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.agent_schema import AgentRegisterRequest, AgentResponse
from app.api.utils.agent_utils import get_agent_service
from app.services.agent_service import AgentService
from app.db.postgres import get_db

route = APIRouter()

@route.post(
    "/register",
    response_model=AgentResponse,
    summary="Register or update agent",
)
async def agent_register(
    agent_payload: AgentRegisterRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    service: AgentService = Depends(get_agent_service),
):
    agent = await service.register_or_update(db, agent_payload)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=AgentResponse.model_validate(agent).model_dump(),
    )

@route.post(
    "/heartbeat/{agent_id}",
    summary="Agent heartbeat",
)
async def heartbeat(
    agent_id: str,
    service: AgentService = Depends(get_agent_service),
):
    await service.process_heartbeat(agent_id)

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"status": "received"},
    )