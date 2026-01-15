.PHONY: up down logs rebuild

up:
	docker compose up -d

rebuild:
	docker compose down -v
	docker compose build --no-cache
	docker compose up -d

down:
	docker compose down -v

logs:
	docker compose logs -f api



