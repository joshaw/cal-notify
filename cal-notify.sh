#!/bin/sh
set -eu

MATCH="$(date -d '15 minutes' '+%Y-%m-%d %H:%M')"

< "events.json" jq \
	--raw-output \
	--arg match "$MATCH" \
	'map(select(.start == $match)) | .[] | [.start, .summary, .location] | @tsv' |
	while IFS=$'\t' read -r start summary location; do
		notify-send "$summary" "$start\\n$location"
	done
