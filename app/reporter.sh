#!/bin/bash
set -e 
echo "Building report to send to Slack ..."
file_stats='/report_stats.csv'
file_fail='/report_failures.csv'
file_hist='/report_stats_history.csv'

json_escape () {
    printf '%s' "$1" | python -c 'import json,sys; print(json.dumps(sys.stdin.read()))'
}

stats=json_escape $( csv2md $file_stats )
fail=json_escape $( csv2md $file_fail )
hist=json_escape $( csv2md $file_hist )

message="{\"blocks\":[{\"type\":\"section\",\"text\":{\"type\":\"mrkdwn\",\"text\":\"$stats\"}},{\"type\":\"section\",\"text\":{\"type\":\"mrkdwn\",\"text\":\"$fail\"}},{\"type\":\"section\",\"text\":{\"type\":\"mrkdwn\",\"text\":\"$hist\"}}]}"
echo "Sending the following results to Slack:"
echo "$stats"
#json=$( jq -nc --arg str "$message" '$str' )
curl -X POST $SLACK_HOOK \
-H 'Content-type: application/json' --data-binary @- << EOF
$message
EOF