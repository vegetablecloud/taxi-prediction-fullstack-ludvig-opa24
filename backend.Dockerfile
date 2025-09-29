FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY . .

RUN uv pip install --system .

CMD ["uvicorn", "taxipred.backend.api:app", "--host", "0.0.0.0", "--port", "8000"]