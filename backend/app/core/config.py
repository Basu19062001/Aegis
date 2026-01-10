from typing import Optional, Dict, Any

from pydantic_settings import BaseSettings
from starlette.config import Config
from pydantic import field_validator

config = Config("app/.env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "Aegis"
    PROJECT_DESCRIPTION: str = "Linux node Anomaly detection using AI Engine"
    
    VERSION: str = config("VERSION", default="1.0.0")
    ENV: str = config("ENV", default="development")
    
    # PostgreSQL
    POSTGRES_USER: str = config("POSTGRES_USER", cast=str, default="admin")
    POSTGRES_PASSWORD: str = config("POSTGRES_PASSWORD", cast=str, default="pass***123")
    POSTGRES_HOST: str = config("POSTGRES_HOST", cast=str, default="localhost")
    POSTGRES_PORT: int = config("POSTGRES_PORT", cast=int, default=5432)
    POSTGRES_DB: str = config("POSTGRES_DB", cast=str, default="aegis_db")
    POSTGRES_DSN: Optional[str] = config("POSTGRES_DSN", cast=str, default=None)

    @field_validator("POSTGRES_DSN", mode="before")
    @classmethod
    def assemble_postgres_dsn(cls, v: Optional[str], info: Dict[str, Any])->Any:
        if isinstance(v, str) and v:
            return v
        
        values = info.data
        return (
            f"postgresql+psycopg://"
            f"{values['POSTGRES_USER']}:{values['POSTGRES_PASSWORD']}"
            f"@{values['POSTGRES_HOST']}:{values['POSTGRES_PORT']}"
            f"/{values['POSTGRES_DB']}"
        )

    # MongoDB
    MONGO_USERNAME: Optional[str] = config("MONGO_USERNAME", cast=str, default=None)
    MONGO_PASSWORD: Optional[str] = config("MONGO_PASSWORD", cast=str, default=None)
    MONGO_HOST: str = config("MONGO_HOST", cast=str, default="localhost")
    MONGO_PORT: int = config("MONGO_PORT", cast=int, default=27017)
    MONGO_DB: str = config("MONGO_DB", cast=str, default="aegis_logs")
    MONGO_DSN: Optional[str] = config("MONGO_DSN", cast=str, default=None)

    @field_validator("MONGO_DSN", mode="before")
    @classmethod
    def assemble_mongodsn(cls, v: Optional[str], info: Dict[str, Any])->Any:
        if isinstance(v, str) and v:
            return v
        
        values = info.data
        if values.get("MONGO_USERNAME") and values.get("MONGO_PASSWORD"):
            return (
                f"mongodb://{values['MONGO_USERNAME']}:{values['MONGO_PASSWORD']}"
                f"@{values['MONGO_HOST']}:{values['MONGO_PORT']}"
                f"/{values['MONGO_DB']}"
            )

        return f"mongodb://{values['MONGO_HOST']}:{values['MONGO_PORT']}/{values['MONGO_DB']}"

    # Redis
    REDIS_HOST: str = config("REDIS_HOST", cast=str, default="localhost")
    REDIS_PORT: int = config("REDIS_PORT", cast=int, default=6379)
    REDIS_DB: int = config("REDIS_DB", cast=int, default=0)
    REDIS_PASSWORD: Optional[str] = config("REDIS_PASSWORD", cast=str, default=None)
    REDIS_URL: Optional[str] = config("REDIS_URL", cast=str, default=None)

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_url(cls, v: Optional[str], info: Dict[str, Any])->Any:
        if isinstance(v, str) and v:
            return v
        
        values = info.data

        if values.get("REDIS_PASSWORD"):
            return (
                f"redis://:{values['REDIS_PASSWORD']}"
                f"@{values['REDIS_HOST']}:{values['REDIS_PORT']}/{values['REDIS_DB']}"
            )

        return f"redis://{values['REDIS_HOST']}:{values['REDIS_PORT']}/{values['REDIS_DB']}"

    # Redpanda / Kafka
    REDPANDA_HOST: str = config("REDPANDA_HOST", cast=str, default="localhost")
    REDPANDA_PORT: int = config("REDPANDA_PORT", cast=int, default=19092)
    REDPANDA_BOOTSTRAP_SERVERS: Optional[str] = config(
        "REDPANDA_BOOTSTRAP_SERVERS", cast=str, default=None
    )

    @field_validator("REDPANDA_BOOTSTRAP_SERVERS", mode="before")
    @classmethod
    def assemble_REDPANDA_servers(cls, v: Optional[str], info: Dict[str, Any]) -> Any:
        if isinstance(v, str) and v:
            return v

        values = info.data
        return f"{values['REDPANDA_HOST']}:{values['REDPANDA_PORT']}"

settings = Settings()