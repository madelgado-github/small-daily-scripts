#!/usr/bin/env bash
# Update every bare mirror (*.git) in the script's own directory.
# Usage: ./update-mirrors.sh [-q] [-r]   (-q quiet, -r force refetch of refs)
#
# Mirrors cloned over HTTPS authenticate via git's credential helper
# (no tokens in this script). To avoid storing credentials on disk,
# use SSH URLs (git@github.com:...) or an in-memory helper instead.
set -uo pipefail

BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$BASE/update.log"
QUIET=0
EXTRA=""
for arg in "$@"; do
  case "$arg" in
    -q) QUIET=1 ;;
    -r) EXTRA="--force" ;;
    *) echo "Unknown option: $arg"; exit 1 ;;
  esac
done

log() { printf '[%s] %s\n' "$(date '+%F %T')" "$1" | tee -a "$LOG"; }

ok=0; fail=0; failed=()
cd "$BASE" || exit 1

shopt -s nullglob
dirs=( *.git )
if (( ${#dirs[@]} == 0 )); then
  log "No mirrors (*.git) found in $BASE"
  exit 1
fi

log "=== Updating ${#dirs[@]} mirrors ==="
for d in "${dirs[@]}"; do
  name="${d%.git}"
  if git -C "$d" fetch --prune $EXTRA origin >/dev/null 2>&1; then
    ok=$((ok+1))
    (( QUIET )) || log "OK   $name"
  else
    fail=$((fail+1))
    failed+=("$name")
    log "FAIL $name"
  fi
done

log "=== Summary: $ok ok, $fail failed ==="
if (( fail > 0 )); then
  log "Repos with errors: ${failed[*]}"
fi

exit "$fail"
