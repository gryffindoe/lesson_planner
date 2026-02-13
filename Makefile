# Makefile for production docker compose tasks

.PHONY: build up down logs ps

build:
	docker compose -f docker-compose.prod.yml build --pull

up:
	docker compose -f docker-compose.prod.yml up --detach --remove-orphans

down:
	docker compose -f docker-compose.prod.yml down --volumes

logs:
	docker compose -f docker-compose.prod.yml logs -f

ps:
	docker compose -f docker-compose.prod.yml ps
