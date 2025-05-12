#!/bin/bash

# Direct command based on alias logic
case "$1" in
  import)
    shift
    exec poetry run python bases/terec/import_cli/main.py "$@"
    ;;
  status)
    shift
    exec poetry run python bases/terec/status_cli/main.py "$@"
    ;;
  jenkins)
    shift
    exec poetry run python bases/terec/jenkins_cli/main.py "$@"
    ;;
  *)
    echo "Unknown command: $1"
    exit 1
    ;;
esac
