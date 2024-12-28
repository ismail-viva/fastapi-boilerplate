.PHONY: up down migrate downgrade logs test init clean clean_all check

DOCKER_CMD := $(if $(shell command -v docker-compose 2> /dev/null),docker-compose,docker compose)

up:
	echo "=== ===>> Starting server..." \
	&& $(DOCKER_CMD) up -d --build --remove-orphans;

down:
	echo "=== ===>> Stopping server..." \
	&& $(DOCKER_CMD) down;

migrate:
	@read -p "Enter the migration message: " message; \
	echo "=== === ===>> Migrating database..." && \
	$(DOCKER_CMD) run --rm fastapi_app alembic revision --autogenerate -m "$$message" && \
	$(DOCKER_CMD) run --rm fastapi_app alembic upgrade head && \
	echo "=== === ===>> Database migration completed === ===" && \
	echo "=== === ===>> Database migration history === ===" && \
	$(DOCKER_CMD) run --rm fastapi_app alembic history;

downgrade:
	@read -p "Enter downgrade step: " step; \
	echo "=== === ===>> Downgrading database..." && \
	$(DOCKER_CMD) run --rm fastapi_app alembic downgrade -$$step && \
	echo "=== === ===>> Database downgrade completed === ===" && \
	echo "=== === ===>> Database migration history === ===" && \
	$(DOCKER_CMD) run --rm fastapi_app alembic history;

logs:
	echo "=== ===>> Server logs:" \
	&& $(DOCKER_CMD) logs -f -t;

test:
	echo "=== ===>> Running tests:" \
	&& $(DOCKER_CMD) lup db -d --build \
	&& poetry run pytest -v --durations=10 --durations-min=0.5;

init:
	make down && make up && make migrate && make logs

clean:
	docker image prune -f \
		&& docker container prune -f

clean_all:
	docker volume prune -f \
		&& docker system prune -a -f

check:
	pre-commit install && pre-commit run --all-files --verbose --show-diff-on-failure
