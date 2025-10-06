FROM python:3.11-slim
WORKDIR /app
RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync

COPY . .

CMD ["streamlit", "run", "src/taxipred/frontend/dashboard.py", "--server.port", "8501", "--server.address", "0.0.0.0"]