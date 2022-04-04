#!/bin/sh
set -eu

echo "Running in '$(pwd)'"

mkdir -p "calendars/"
cat calendars.txt |
	grep -v '^$' |
	grep -v '^#' |
	while read -r name url; do
		fname="calendars/$name.ics"
		echo "Downloading '$url' to '$fname'"
		curl -s "$url" > "$fname"
	done

cat calendars/*.ics | python3 get-next-events.py 3 > events.json
