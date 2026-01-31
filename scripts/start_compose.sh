
#!/usr/bin/env bash
set -euo pipefail

# Backwards-compatible wrapper that forwards to the compose-manager skill
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SCRIPT="$SCRIPT_DIR/.github/skills/compose-manager/manage_compose.sh"

if [ ! -x "$SKILL_SCRIPT" ]; then
  echo "Skill script not found or not executable: $SKILL_SCRIPT"
  exit 1
fi

exec "$SKILL_SCRIPT" "$@"


COMPOSE_FILES="-f compose.yml -f compose.dev-override.yml"
ENV_FILE=".env.example"



print_logs() {
	echo "[pyledger] Showing first 20 log lines from each container:"
	containers=$(docker compose --env-file "$ENV_FILE" $COMPOSE_FILES ps --services)
	for c in $containers; do
		echo "--- [$c] ---"
			docker compose --env-file "$ENV_FILE" $COMPOSE_FILES logs --tail=20 $c || true
	done
}

print_config() {
	echo "[pyledger] Docker Compose config:"
	docker compose --env-file "$ENV_FILE" $COMPOSE_FILES config
}

export_env_file_vars() {
	if [ -f "$ENV_FILE" ]; then
		echo "[pyledger] Exporting environment variables from $ENV_FILE..."
		set -a
		# shellcheck disable=SC1090
		. "$ENV_FILE"
		set +a
	else
		echo "[pyledger] ENV file $ENV_FILE not found. Skipping export."
	fi
}


export_env_file_vars
case "$1" in
	--rebuild)
		echo "[pyledger] Rebuilding images..."
		# Build frontend first (image: canonledger-frontend:local) so web can copy assets
		docker compose --env-file "$ENV_FILE" $COMPOSE_FILES build frontend || true
		docker compose --env-file "$ENV_FILE" $COMPOSE_FILES build web
		;;
	--restart)
		echo "[pyledger] Restarting containers (no volume removal)..."
			docker compose --env-file "$ENV_FILE" $COMPOSE_FILES down
		;;
	"")
		echo "[pyledger] Starting containers..."
		;;
	*)
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
		echo "[pyledger] DB not ready yet, retrying ($tries/$max)..."
		sleep 1
	done
	if [ "$tries" -ge "$max" ]; then
		echo "[pyledger] Warning: DB did not become ready after $max seconds"
	else
		echo "[pyledger] DB is ready."
		echo "[pyledger] Restarting web to pick up DB readiness..."
		docker compose --env-file "$ENV_FILE" $COMPOSE_FILES restart web || true
	fi
}

wait_for_db
print_logs
