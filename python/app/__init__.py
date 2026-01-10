from app.api import create_app
from app.core.config import load_settings

# Load configuration on startup so the app has OpenAI settings available.
settings = load_settings()
app = create_app(settings)

__all__ = ["app", "settings"]
