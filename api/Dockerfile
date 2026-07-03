# Container for the FastAPI service (deploys to Fly.io). Build context is the
# repo root (see fly.toml: dockerfile = api/Dockerfile).
FROM python:3.12-slim

WORKDIR /app

# Install the engine + API deps (fastapi, uvicorn). The package lives in src/.
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir ".[api]"

# App code + reference data (regions, appliances, NI carbon profile).
COPY api ./api
COPY data ./data

EXPOSE 8080
# community_energy_api isn't a pip package; --app-dir puts api/ on the path.
CMD ["uvicorn", "community_energy_api.main:app", "--host", "0.0.0.0", "--port", "8080", "--app-dir", "api"]
