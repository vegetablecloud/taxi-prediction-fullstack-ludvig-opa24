FROM python:3.11-slim
WORKDIR /app
RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --system

COPY . .

CMD ["uvicorn", "taxipred.backend.api:app", "--host", "0.0.0.0", "--port", "8000"]