from datetime import datetime, timezone
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field

class LogEntry(BaseModel):
    agent_id: str = Field(..., description="Unique identifier of the agent that generated the log")
    timestamp: datetime = Field(default_factory=datetime.now(timezone.utc), description="UTC timestamp when the log was created")
    log_source: str = Field(..., description="Subsystem that generated the log (auth, system, network, etc.)")
    log_level: str = Field(..., description="Severity level of the log (INFO, WARNING, ERROR, CRITICAL)")
    message: str = Field(..., description="Human-readable log message")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional structured data related to the log")
    
    class Config:
        orm_mode = True
