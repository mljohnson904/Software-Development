#!/usr/bin/env bash
input=$(cat 2>/dev/null)
if command -v jq >/dev/null 2>&1; then
  get() { printf '%s' "$input" | jq -r "$1 // empty" 2>/dev/null; }
else
  get() { printf '%s' "$input" | python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
    for k in sys.argv[1].lstrip(".").split("."):
        d = d[k]
    print("" if d is None else d)
except Exception:
    pass' "$1" 2>/dev/null; }
fi

R=$'\033[31m'; G=$'\033[32m'; Y=$'\033[33m'; M=$'\033[35m'; C=$'\033[36m'; D=$'\033[2m'; N=$'\033[0m'
SEP="${D} · ${N}"

color() { # pct int
  if [ "$1" -ge 90 ]; then printf '%s' "$R"; elif [ "$1" -ge 70 ]; then printf '%s' "$Y"; else printf '%s' "$G"; fi
}
toint() { # numeric string -> clamped int, empty if invalid
  case "$1" in ''|*[!0-9.]*) return 1;; esac
  local v; v=$(printf '%.0f' "$1" 2>/dev/null) || return 1
  [ "$v" -gt 100 ] && v=100
  printf '%s' "$v"
}

parts=()

ctx=$(toint "$(get .context_window.used_percentage)")
if [ -n "$ctx" ]; then
  filled=$(( ctx * 16 / 100 )); bar=""
  for ((i=0;i<16;i++)); do [ $i -lt $filled ] && bar+="█" || bar+="░"; done
  parts+=("$(color "$ctx")${bar} ${ctx}%${N}")
fi

for w in five_hour:5h seven_day:7d; do
  v=$(toint "$(get ".rate_limits.${w%%:*}.used_percentage")")
  [ -n "$v" ] && parts+=("${D}${w##*:}${N} $(color "$v")${v}%${N}")
done

cost=$(get .cost.total_cost_usd)
if [ -n "$cost" ]; then
  c=$(printf '%.2f' "$cost" 2>/dev/null) && parts+=("${C}\$${c}${N}")
fi

model=$(get .model.display_name)
[ -n "$model" ] && parts+=("${M}${model}${N}")

out=""
for p in "${parts[@]}"; do
  [ -n "$out" ] && out+="$SEP"
  out+="$p"
done
printf '%s\n' "$out"
exit 0
