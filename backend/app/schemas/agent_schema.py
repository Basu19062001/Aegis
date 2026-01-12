from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field

class AgentBase(BaseModel):
    agent_id: str = Field(..., description="Unique agent identifier (UUID)")
    hostname: str = Field(..., min_length=1, max_length=255)
    ip_address: str = Field(..., description="Agent IP address")
    os_info: Optional[str] = Field(None, description="Operating system info")

class AgentRegisterRequest(AgentBase):
    pass

class AgentResponse(BaseModel):
    agent_id: str
    hostname: str
    ip_address: str
    os_info: Optional[str]
    is_active: bool
    created_at: datetime
    last_heartbeat: Optional[datetime]

    class Config:
        from_attributes = True
