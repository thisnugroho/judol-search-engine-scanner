.PHONY: dev up build down logs

dev:
	docker compose up --build

up:
	docker compose up -d --build

build:
	docker compose build

down:
	docker compose down

logs:
	docker compose logs -f --tail=200
