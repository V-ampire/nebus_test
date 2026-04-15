up:
	@docker compose up --remove-orphans

build:
	@docker compose build

down:
	@docker compose down

makemigrations:
ifdef MSG
	@docker compose exec api python -m alembic revision --autogenerate -m "$(MSG)"
else
	@echo "Please provide a migration description: make makemigration MSG='your description'"
endif

db_check:
	@docker compose exec api python -m alembic check

db_head:
	@docker compose exec api python -m alembic upgrade head

dev_psql:
	@docker compose exec postgres psql -U postgres -d postgres