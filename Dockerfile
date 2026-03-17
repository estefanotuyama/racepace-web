FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY ./static/favicon.ico /app/static/favicon.ico

RUN apt-get update && apt-get install -y libpq-dev && \
    rm -rf /var/lib/apt/lists/*

RUN uv sync --frozen --no-dev --no-install-project

COPY ./backend /app/backend

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
