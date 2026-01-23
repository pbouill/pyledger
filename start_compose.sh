
#!/bin/bash
set -e

COMPOSE_FILES="-f compose.yml -f compose.dev-override.yml"


print_logs() {
	echo "[pyledger] Showing first 20 log lines from each container:"
	containers=$(docker compose $COMPOSE_FILES ps --services)
	for c in $containers; do
		echo "--- [$c] ---"
		docker compose $COMPOSE_FILES logs --tail=20 $c || true
	done
}

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

docker compose $COMPOSE_FILES up -d
print_logs
