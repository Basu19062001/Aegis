from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

class AgentBase(BaseModel):
    hostname: str = Field(..., min_length=1, max_length=255)
    ip_address: str = Field(..., description="Agent IP address")
    os_info: Optional[str] = Field(None, description="Operating system info")

class AgentRegisterRequest(AgentBase):
    pass

class AgentResponse(BaseModel):
    id: UUID
    hostname: str
    ip_address: str
    os_info: str | None
    is_active: bool
    created_at: datetime
    last_heartbeat: datetime

    model_config = {
        "from_attributes": True
    }
