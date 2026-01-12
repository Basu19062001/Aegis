from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import status, HTTPException

from app.models.agent import Agent
from app.schemas.agent_schema import AgentRegisterRequest
from app.db.redis import get_redis

# Only postgres, one responsibilty
class AgentRepository:
    async def get_by_id(self, db: AsyncSession, agent_id: str):
        result = await db.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        return result.scalars().first()

    async def create(self, db: AsyncSession, payload: AgentRegisterRequest):
        agent = Agent(
            id=payload.agent_id,
            hostname=payload.hostname,
            ip_address=payload.ip_address,
            os_info=payload.os_info,
        )
        db.add(agent)
        await db.commit()
        await db.refresh(agent)
        return agent

    async def update(
        self,
        db: AsyncSession,
        agent: Agent,
        payload: AgentRegisterRequest,
    ):
        agent.hostname = payload.hostname
        agent.ip_address = payload.ip_address
        agent.os_info = payload.os_info

        await db.commit()
        await db.refresh(agent)
        return agent


class AgentStatusStore:
    TTL = 60

    async def set_online(self, agent_id: str):
        redis = get_redis()
        await redis.set(
            f"agent:{agent_id}:status",
            "online",
            ex=self.TTL,
        )

class AgentService:
    def __init__(
        self,
        repo: AgentRepository,
        status_store: AgentStatusStore,
    ):
        self.repo = repo
        self.status_store = status_store

    async def register_or_update(
        self,
        db: AsyncSession,
        payload: AgentRegisterRequest,
    ) -> Agent:
        try:
            agent = await self.repo.get_by_id(db, payload.agent_id)

            if not agent:
                agent = await self.repo.create(db, payload)
            else:
                agent = await self.repo.update(db, agent, payload)

            # Set online status in Redis (60s TTL)
            await self.status_store.set_online(payload.agent_id)

            return agent

        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register agent",
            ) from exc

    async def process_heartbeat(self, agent_id: str):
        await self.status_store.set_online(agent_id)
