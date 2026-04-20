FROM python:3.13-slim AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

RUN uv sync --frozen

CMD ["sh", "-c", "bin/_init.sh && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
