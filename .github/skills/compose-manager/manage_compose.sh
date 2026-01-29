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

wait_for_db() {
	echo "[canonledger] Waiting for DB to accept connections..."
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

print_help() {
  echo "Usage: $0 [--start|--rebuild|--restart|--logs [service]|--health|--doctor|--exec <service> <cmd>]"
  exit 1
}

case "$1" in
  --start|"")
    echo "[canonledger] Starting containers..."
    print_config
    docker compose --env-file "$ENV_FILE" $COMPOSE_FILES up -d
    ;;
  --rebuild)
    echo "[canonledger] Rebuilding images..."
    # Build frontend first (image: canonledger-frontend:local) so web can copy assets
    docker compose --env-file "$ENV_FILE" $COMPOSE_FILES build frontend || true
    docker compose --env-file "$ENV_FILE" $COMPOSE_FILES build web
    print_config
    docker compose --env-file "$ENV_FILE" $COMPOSE_FILES up -d
    ;;
  --restart)
    echo "[canonledger] Restarting containers (no volume removal)..."
    docker compose --env-file "$ENV_FILE" $COMPOSE_FILES down
    docker compose --env-file "$ENV_FILE" $COMPOSE_FILES up -d
    ;;
  --logs)
    svc="$2"
    if [ -n "$svc" ]; then
      echo "[canonledger] Showing last 200 log lines for $svc"
      docker compose --env-file "$ENV_FILE" $COMPOSE_FILES logs --no-color --tail=200 "$svc" || true
    else
      print_logs
    fi
    exit 0
    ;;
  --health)
    port="${APP_EXT_PORT:-8888}"
    echo "[canonledger] Checking health endpoint on http://localhost:$port/api/health"
    if curl -fsS "http://localhost:$port/api/health" >/dev/null 2>&1; then
      echo "[canonledger] OK"
      exit 0
    else
      echo "[canonledger] Unhealthy or unreachable"
      exit 2
    fi
    ;;
  --doctor)
    echo "[canonledger] Running basic diagnostics..."
    print_config
    docker compose --env-file "$ENV_FILE" $COMPOSE_FILES ps
    wait_for_db
    $0 --health || true
    echo "[canonledger] Showing recent web logs:"
    docker compose --env-file "$ENV_FILE" $COMPOSE_FILES logs --no-color --tail=200 web || true
    exit 0
    ;;
  --exec)
    svc="$2"
    shift 2
    if [ -z "$svc" ]; then
      echo "Usage: $0 --exec <service> <cmd...>"
      exit 1
    fi
    if [ $# -eq 0 ]; then
      echo "Usage: $0 --exec <service> <cmd...>"
      exit 1
    fi
    echo "[canonledger] Exec into $svc: $*"
    docker compose --env-file "$ENV_FILE" $COMPOSE_FILES exec -T "$svc" sh -c "$*"
    exit 0
    ;;
  -h|--help)
    print_help
    ;;
  *)
    echo "Unknown argument: $1"
    print_help
    ;;
esac

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
