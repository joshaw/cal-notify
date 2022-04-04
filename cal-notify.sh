#!/bin/sh
set -eu

MATCH_15="$(date -d '15 minutes' '+%Y-%m-%d %H:%M')"
MATCH_1="$(date -d '1 minute' '+%Y-%m-%d %H:%M')"

LEVEL=low
for MATCH in "$MATCH_15" "$MATCH_1"; do
	< "events.json" jq \
		--raw-output \
		--arg match "$MATCH" \
		'map(select(.start == $match)) | .[] | [.start, .summary, .location] | @tsv' |
		while IFS=$'\t' read -r start summary location; do
			notify-send \
				--urgency "$LEVEL" \
				--icon "x-office-calendar-symbolic" \
				"$summary" \
				"$start\\n$location"
		done

	LEVEL=normal
done
