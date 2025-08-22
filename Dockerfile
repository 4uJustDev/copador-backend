FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# системные зависимости для psycopg2 и Pillow (если используешь превью картинок)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev gcc \
 && rm -rf /var/lib/apt/lists/*

# зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# код
COPY . .

# непривилегированный пользователь
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# entrypoint прогонит миграции и стартанёт uvicorn
CMD ["bash", "-lc", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
