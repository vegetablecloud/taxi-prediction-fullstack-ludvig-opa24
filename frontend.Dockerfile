FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY . .

RUN uv pip install --system -e .

CMD ["streamlit", "run", "src/taxipred/frontend/dashboard.py", "--server.port", "8501", "--server.address", "0.0.0.0"]