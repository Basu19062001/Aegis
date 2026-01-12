from fastapi import APIRouter

from app.api.v1 import *

api_router = APIRouter()

api_router.include_router(agent_router, prefix="/agents", tags=["Agent Management API's"])
