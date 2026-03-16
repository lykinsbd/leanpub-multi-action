FROM python:3.9-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY leanpub_multi_action/ leanpub_multi_action/

RUN uv sync --frozen --no-dev

ENTRYPOINT [ "/app/.venv/bin/lma" ]
