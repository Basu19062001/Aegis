from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.agent import Agent
from app.schemas.agent_schema import AgentRegisterRequest

# Only postgres, one responsibilty
class AgentRepository:
    async def get_by_id(self, db: AsyncSession, agent_id: str)-> Agent | None:
        result = await db.execute(
            select(Agent).filter(Agent.id == agent_id)
        )
        return result.scalars().first()
    
    async def save(self, db: AsyncSession, agent: Agent):
        db.add(agent)
        await db.commit()

class AgentStatusStore:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def set_online(self, agent_id: str):
        await self.redis.set(
            f"agent:{agent_id}:status",
            "online",
            ex=60 
        )

class AgentService:
    def __init__(self, repo: AgentRepository, status_store: AgentStatusStore):
        self.repo = repo
        self.status_store = status_store
    
    async def register_or_update(self, db: AsyncSession, agent_data: AgentRegisterRequest):
        agent = await self.repo.get_by_id(db, agent_data.agent_id)

        if not agent:
            agent = Agent(
                id = agent_data.agent_id,
                hostname = agent_data.hostname,
                ip_address = agent_data.ip_address,
                os_info = agent_data.os_info,
            )
        else:
            agent.hostname = agent_data.hostname
            agent.ip_address = agent_data.ip_address
        
        await self.repo.save(db, agent)
        await self.status_store.set_online(agent.id)

        return agent