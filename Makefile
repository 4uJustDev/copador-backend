# имя контейнера с API (см. docker ps)
API_CONTAINER=copador-backend-api-1

# создание новой миграции
revision:
	docker exec -it $(API_CONTAINER) alembic revision --autogenerate -m "$(msg)"

# применение всех миграций
migrate:
	docker exec -it $(API_CONTAINER) alembic upgrade head

# показать состояние (какая ревизия стоит в БД)
current:
	docker exec -it $(API_CONTAINER) alembic current

# откат на шаг назад
downgrade:
	docker exec -it $(API_CONTAINER) alembic downgrade -1
