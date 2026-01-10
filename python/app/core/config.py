import os
from pathlib import Path
from typing import Dict, Optional

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator


class OpenAIModelConfig(BaseModel):
    model: str
    temperature: float = 0.3
    max_tokens: int = 512


class OpenAISettings(BaseModel):
    api_key: str = Field(..., description="OpenAI API key (from .env)")
    base_url: Optional[str] = Field(default=None, description="Override base URL")
    organization: Optional[str] = Field(default=None, description="Optional organization id")
    default: OpenAIModelConfig
    models: Dict[str, OpenAIModelConfig] = Field(default_factory=dict)

    @validator("api_key")
    def require_api_key(cls, value: str) -> str:
        if not value:
            raise ValueError("OPENAI_API_KEY is required. Set it in your .env file.")
        return value


class Settings(BaseModel):
    openai: OpenAISettings


def load_settings(config_path: Optional[str] = None) -> Settings:
    """
    Load .env for secrets, then merge with YAML for model parameters.
    Env vars:
      - OPENAI_API_KEY (required)
      - OPENAI_BASE_URL (optional)
      - OPENAI_ORG (optional)
      - OPENAI_CONFIG_PATH (optional path to YAML)
    """
    load_dotenv()
    cfg_path = Path(config_path or os.getenv("OPENAI_CONFIG_PATH", "config/openai.yaml"))
    if not cfg_path.exists():
        raise FileNotFoundError(f"OpenAI config not found at {cfg_path}")

    with cfg_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    openai_data = data.get("openai", {})
    default_cfg = OpenAIModelConfig(**(openai_data.get("default") or {}))
    models_cfg = {
        name: OpenAIModelConfig(**cfg)
        for name, cfg in (openai_data.get("models") or {}).items()
    }

    openai_settings = OpenAISettings(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        base_url=os.getenv("OPENAI_BASE_URL"),
        organization=os.getenv("OPENAI_ORG"),
        default=default_cfg,
        models=models_cfg,
    )

    return Settings(openai=openai_settings)


def resolve_model(task: str, settings: Settings) -> OpenAIModelConfig:
    """Pick a model config by task, falling back to the default."""
    normalized = (task or "").lower()
    return settings.openai.models.get(normalized, settings.openai.default)
