#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/scripts" && pwd)"
COMMAND=$1
shift || true

case "$COMMAND" in
  create)
    bash "$SCRIPT_DIR/create-project.sh" "$@"
    ;;
  add-tool)
    bash "$SCRIPT_DIR/add-tool.sh" "$@"
    ;;
  help|--help|-h|"")
    echo "Usage: ./manage.sh [command]"
    echo ""
    echo "Commands:"
    echo "  create         Scaffold a new modular project"
    echo "  add-tool       Add a new tool module"
    echo ""
    ;;
  *)
    echo "❌ Unknown command: $COMMAND"
    exit 1
    ;;
esac
