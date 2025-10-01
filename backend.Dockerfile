FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY . .

RUN uv pip install --system -e .

CMD ls -R && echo "--- Innehåll i api.py ---" && cat src/taxipred/backend/api.py