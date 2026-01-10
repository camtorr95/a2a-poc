from typing import Optional

from openai import OpenAI

from app.core.config import OpenAIModelConfig, Settings, resolve_model


def get_openai_client(settings: Settings) -> OpenAI:
    """Instantiate an OpenAI client with the provided settings."""
    return OpenAI(
        api_key=settings.openai.api_key,
        base_url=settings.openai.base_url,
        organization=settings.openai.organization,
    )


def model_for_task(task: str, settings: Settings) -> OpenAIModelConfig:
    """Resolve the model configuration for a given task."""
    return resolve_model(task, settings)
