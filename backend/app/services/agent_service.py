from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import status, HTTPException

from app.models.agent import Agent
from app.schemas.agent_schema import AgentRegisterRequest
from app.db.redis import get_redis
from app.logger import logger

# Only postgres, one responsibilty
class AgentRepository:
    async def get_by_hostname(self, db: AsyncSession, hostname: str):
        result = await db.execute(
            select(Agent).where(Agent.hostname == hostname)
        )
        return result.scalars().first()

    async def create(self, db: AsyncSession, payload: AgentRegisterRequest):
        agent = Agent(
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
            logger.debug("Checking agent by hostname: %s", payload.hostname)

            agent = await self.repo.get_by_hostname(db, payload.hostname)

            if agent is None:
                logger.info("Agent not found, creating new agent")
                agent = await self.repo.create(db, payload)
            else:
                logger.info("Agent found, updating agent id=%s", agent.id)
                agent = await self.repo.update(db, agent, payload)

            logger.info("Agent saved successfully id=%s", agent.id)

            await self.status_store.set_online(str(agent.id))
            logger.debug("Agent marked online in Redis (TTL=60s)")

            return agent

        except Exception as exc:
            logger.exception("Agent registration failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Agent registration failed. Check server logs for details.",
            )


    async def process_heartbeat(self, agent_id: str):
        await self.status_store.set_online(agent_id)
