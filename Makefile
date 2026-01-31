# Developer convenience
.PHONY: dev backend frontend stop

dev:
	./scripts/stop_dev.sh || true
	./scripts/dev_local.sh --port 8001 --db sqlite --background-frontend

dev-hmr:
	./scripts/stop_dev.sh || true
	./scripts/dev_local.sh --port 8001 --db sqlite --background-frontend --hmr

backend:
	./scripts/stop_dev.sh || true
	./scripts/dev_local.sh --port 8001 --db sqlite --no-frontend

frontend:
	cd app && npm run dev

stop:
	# Use the comprehensive dev stop helper which kills both backend and frontend
	./scripts/stop_dev.sh || true

migrate-tenants:
	.venv/bin/python scripts/migrate_tenants.py
