#!/usr/bin/env bash
set -euo pipefail

# Copy of skill script for compose-manager (canonical location under .github/skills)
COMPOSE_FILES="-f compose.yml -f compose.dev-override.yml"
ENV_FILE=".env.example"

print_logs() {
	echo "[canonledger] Showing first 20 log lines from each container:"
	containers=$(docker compose --env-file "$ENV_FILE" $COMPOSE_FILES ps --services)
	for c in $containers; do
		echo "--- [$c] ---"
			docker compose --env-file "$ENV_FILE" $COMPOSE_FILES logs --tail=20 $c || true
	done
}

print_config() {
	echo "[canonledger] Docker Compose config:"
	docker compose --env-file "$ENV_FILE" $COMPOSE_FILES config
}

export_env_file_vars() {
	if [ -f "$ENV_FILE" ]; then
		echo "[canonledger] Exporting environment variables from $ENV_FILE..."
		set -a
		# shellcheck disable=SC1090
		. "$ENV_FILE"
		set +a
	else
		echo "[canonledger] ENV file $ENV_FILE not found. Skipping export."
	fi
}

export_env_file_vars
case "$1" in
	--rebuild)
		echo "[canonledger] Rebuilding images..."
		# Build frontend first (image: canonledger-frontend:local) so web can copy assets
		docker compose --env-file "$ENV_FILE" $COMPOSE_FILES build frontend || true
		docker compose --env-file "$ENV_FILE" $COMPOSE_FILES build web
		;;
	--restart)
		echo "[canonledger] Restarting containers (no volume removal)..."
			docker compose --env-file "$ENV_FILE" $COMPOSE_FILES down
		;;
	"")
		echo "[canonledger] Starting containers..."
		echo "Usage: $0 [--rebuild|--restart]"
		exit 1
		;;
esac

print_config
docker compose --env-file "$ENV_FILE" $COMPOSE_FILES up -d

wait_for_db() {
	echo "[pyledger] Waiting for DB to accept connections..."
	tries=0
	max=30
	until docker compose --env-file "$ENV_FILE" $COMPOSE_FILES exec -T db pg_isready -U "${DB_USER:-postgres}" >/dev/null 2>&1 || [ "$tries" -ge "$max" ]; do
		tries=$((tries+1))
		echo "[canonledger] DB not ready yet, retrying ($tries/$max)..."
		sleep 1
	done
	if [ "$tries" -ge "$max" ]; then
		echo "[canonledger] Warning: DB did not become ready after $max seconds"
	else
		echo "[canonledger] DB is ready."
		echo "[canonledger] Restarting web to pick up DB readiness..."
		docker compose --env-file "$ENV_FILE" $COMPOSE_FILES restart web || true
	fi
}

wait_for_db
print_logs
