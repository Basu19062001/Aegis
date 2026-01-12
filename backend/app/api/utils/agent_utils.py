from app.services.agent_service import AgentService, AgentRepository, AgentStatusStore

def get_agent_service() -> AgentService:
    return AgentService(
        repo=AgentRepository(),
        status_store=AgentStatusStore(),
    )