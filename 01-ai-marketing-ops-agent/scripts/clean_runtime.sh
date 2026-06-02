#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "Removing generated runtime files from $PROJECT_DIR"

removed=0
for path in \
  reports/*.md \
  reports/*.html \
  reports/*.json \
  run-history/*.jsonl \
  run-history/*.json \
  approval-requests/*.jsonl \
  approval-requests/*.json
do
  if [[ -e "$path" ]]; then
    rm "$path"
    echo "Removed $path"
    removed=1
  fi
done

if [[ "$removed" -eq 0 ]]; then
  echo "No generated runtime files found."
else
  echo "Runtime files cleaned. .gitkeep placeholders were left intact."
fi
