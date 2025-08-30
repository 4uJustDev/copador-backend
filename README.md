## Установка

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/4uJustDev/copador-backend.git
```

2. **Создайте виртуальное окружение и запустите:**
Инициализируйте виртуальное окружение
```bash
python -m venv venv
```

Запуск Linux/Mac
```bash
source venv/bin/activate  
```

Запуск Windows
```bash  
venv\Scripts\activate  
```

3. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

4. **Настройте переменные окружения:**
Создайте .env файл и заполните переменные

```bash
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
```

5. **Запустите приложение:**
```bash
docker compose up -d --build
```

## Полезные команды

## Alembic
- alembic revision --autogenerate -m "comment" 
- alembic upgrade head
- docker compose exec api alembic history                              | История миграций
- docker compose exec api alembic revision --autogenerate -m "comment" | Создание миграции в контейнере и фиксирование - его на локалке

## Docker 
- docker compose down               | Остановка всех контейнеров
- docker compose up -d --build      | Сборка контейнеров
- docker compose build --no-cache   | Пересборка жесткая 
- docker compose exec api bash      | Подключение к контейнеру с башем

## Scripts
- docker compose exec api bash -lc "python -m app.scripts.seeds" | cat                           

## Logs

- docker compose logs api                  | Логи Докера
- sudo tail -f /var/log/nginx/access.log   | Логи Nginx
- sudo tail -f /var/log/nginx/error.log    | Логи Nginx


..
## Стэк
- **FastAPI** - современный веб-фреймворк для Python
- **SQLAlchemy 2.0** - ORM для работы с базой данных
- **PostgreSQL** - реляционная база данных
- **Alembic** - миграции базы данных
- **JWT** - аутентификация
- **Pydantic** - валидация данных
- **bcrypt** - хеширование паролей