#!/usr/bin/env bash
set -euo pipefail

input_text="${TOOL_INPUT:-} ${COMMAND:-}"

if [[ -z "${input_text// }" ]]; then
  echo "No TOOL_INPUT or COMMAND provided; pre-tool-use check passed."
  exit 0
fi

blocked_patterns=(
  'rm[[:space:]]+-rf[[:space:]]+/'
  'sudo[[:space:]].*(rm|dd|mkfs|shutdown|reboot)'
  '(cat|less|more|sed|awk)[[:space:]].*(\.env|id_rsa|credentials|secrets)'
  '(curl|wget)[^|;&]*[|][[:space:]]*(sh|bash)'
  '(env|printenv)[[:space:]]*\|'
)

for pattern in "${blocked_patterns[@]}"; do
  if grep -Eiq "${pattern}" <<<"${input_text}"; then
    echo "Blocked obvious unsafe command intent. Pattern category: ${pattern}" >&2
    echo "This example guardrail is conservative and not a complete security system." >&2
    exit 1
  fi
done

echo "Claude Code pre-tool-use example check passed."
