
#!/bin/bash
set -e


COMPOSE_FILES="-f compose.yml -f compose.dev-override.yml"
ENV_FILE=".env.example"



print_logs() {
	echo "[pyledger] Showing first 20 log lines from each container:"
	containers=$(docker compose $COMPOSE_FILES ps --services)
	for c in $containers; do
		echo "--- [$c] ---"
		docker compose $COMPOSE_FILES logs --tail=20 $c || true
	done
}

print_config() {
	echo "[pyledger] Docker Compose config:"
	docker compose $COMPOSE_FILES config
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
		docker compose $COMPOSE_FILES build
		;;
	--restart)
		echo "[pyledger] Restarting containers (no volume removal)..."
		docker compose $COMPOSE_FILES down
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
docker compose $COMPOSE_FILES up -d
print_logs
