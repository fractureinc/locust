#!/bin/bash
set -e 
echo "Building report to send to Slack ..."
file_stats='/report_stats.csv'
file_fail='/report_failures.csv'
file_hist='/report_history.csv'

stats=$( csv2md $file_stats )
fail=$( csv2md $file_fail )
hist=$( csv2md $file_hist )

message="{\"blocks\":[{\"type\":\"mrkdwn\",\"text\":\"$stats\"},{\"type\":\"mrkdwn\",\"text\":\"$fail\"},{\"type\":\"mrkdwn\",\"text\":\"$hist\"}]}"
echo "Sending the following results to Slack:"
echo "$message"
curl -X POST -H 'Content-type: application/json' --data $message https://hooks.slack.com/services/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