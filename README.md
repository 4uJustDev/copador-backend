## Установка

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd tt-oak-company-backend
```

2. **Создайте виртуальное окружение:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

4. **Настройте переменные окружения:**

# === Database ===
DB_USER=
DB_PASSWORD=
DB_NAME=
DB_PORT=
# === JWT Auth ===
JWT_SECRET=
JWT_ALGORITHM=
JWT_EXPIRE_MINUTES=
# === For scripts ===
ADMIN_PASSWORD=


5. **Создайте базу данных:**
Название БД в .env DB_NAME задается.


6. **Запустите приложение:**
```bash
docker compose up -d --build
```

## Полезные команды

# venv
.\venv\Scripts\Activate.ps1

# Running app
run : uvicorn app.main:app --reload

# Alembic
alembic revision --autogenerate -m "comment" 
alembic upgrade head

# Docker 
docker compose down      
docker compose up -d --build  

..
## Стэк
- **FastAPI** - современный веб-фреймворк для Python
- **SQLAlchemy 2.0** - ORM для работы с базой данных
- **PostgreSQL** - реляционная база данных
- **Alembic** - миграции базы данных
- **JWT** - аутентификация
- **Pydantic** - валидация данных
- **bcrypt** - хеширование паролей