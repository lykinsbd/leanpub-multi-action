FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY leanpub_multi_action/ leanpub_multi_action/

RUN uv sync --frozen --no-dev

ENTRYPOINT [ "/app/.venv/bin/lma" ]
