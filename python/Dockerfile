FROM python:3.11-slim

WORKDIR /app

# Install Poetry and project dependencies
RUN pip install --no-cache-dir "poetry==1.8.4"
COPY pyproject.toml .
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

COPY app ./app
COPY config ./config

ENV PORT=8000
ENV OPENAI_CONFIG_PATH=/app/config/openai.yaml
ENV AGENT_PUBLIC_URL=http://python-agents:8000
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
