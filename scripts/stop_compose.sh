#!/bin/bash
set -e

usage() {
  echo "Usage: $0 [--volumes|-v] [--prune]"
  echo "  --volumes, -v   Remove named and anonymous volumes (docker compose down -v)"
  echo "  --prune         Prune all stopped containers, unused networks, and dangling images"
  exit 1
}

VOLUMES=""
PRUNE=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --volumes|-v)
      VOLUMES="-v"
      shift
      ;;
    --prune)
      PRUNE=1
      shift
      ;;
    -h|--help)
      usage
      ;;
    *)
      usage
      ;;
  esac
done

docker compose -f compose.yml -f compose.dev-override.yml down $VOLUMES

if [[ -n "$PRUNE" ]]; then
  echo "Pruning stopped containers, unused networks, and dangling images..."
  docker system prune -f
fi
