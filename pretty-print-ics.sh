#!/bin/sh
set -eu

tr -d '\r' |
	awk '
		BEGIN { capline = "" }
		/^[^ ]/ {
			print capline
			capline = $0
		}
		/^ / { capline = capline substr($0, 2) }
	' |
	awk '
		BEGIN { indent=0 }
		/^END/ { indent -= 1 }
		{
			for (i=1; i<=indent; i++)
				printf(".  ")
			print $0
		}
		/^BEGIN/ { indent += 1 }
	' |
	grep -v '^$'
