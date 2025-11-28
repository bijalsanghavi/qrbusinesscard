.PHONY: dev-up dev-down dev-reset-db dev-seed backend-run frontend-run \
        prod-build prod-up prod-down prod-logs

ENV ?= development
BACKEND := backend
FRONTEND := frontend

dev-up:
	ENV=$(ENV) docker compose up --build

dev-down:
	docker compose down

dev-reset-db:
	docker compose down -v
	rm -rf $(BACKEND)/media || true
	ENV=$(ENV) docker compose up --build

dev-seed:
	curl -s -X POST http://localhost:3001/dev/login >/dev/null
	curl -s -X POST http://localhost:3001/dev/seed-profile >/dev/null
	@echo "Seeded dev user + profile (slug=devcard)"

backend-run:
	cd $(BACKEND) && ENV=$(ENV) uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend-run:
	cd $(FRONTEND) && npm install && npm run dev

# Production (run on your server)
prod-build:
	docker compose -f docker-compose.prod.yml build

prod-up:
	docker compose -f docker-compose.prod.yml up -d

prod-down:
	docker compose -f docker-compose.prod.yml down

prod-logs:
	docker compose -f docker-compose.prod.yml logs -f
