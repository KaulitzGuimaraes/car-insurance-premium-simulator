FROM python:3.11-slim AS builder

ENV POETRY_NO_INTERACTION=1 POETRY_VIRTUALENVS_IN_PROJECT=true PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN pip install poetry==2.2.1
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root

FROM python:3.11-slim AS runtime

ENV PATH="/app/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN groupadd --system app && useradd --system --gid app app
COPY --from=builder /app/.venv /app/.venv
COPY app ./app
COPY config.yml ./config.yml
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health', timeout=2)"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
