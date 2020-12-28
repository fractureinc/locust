#!/bin/bash

#bail on fail
set -eo pipefail

LOCUST=( "/usr/local/bin/locust" )

LOCUST+=( -f ${LOCUST_SCRIPT:-/locust-tasks/locust-tasks.py} )
LOCUST+=( --host=$TARGET_HOST )
LOCUST_MODE=${LOCUST_MODE:-standalone}

if [[ "$LOCUST_MODE" = "master" ]]; then
    if [[ -z "${SLACK_HOOK}" ]]; then
        echo "Missing SLACK_HOOK env. It's required to send the results."
        exit 1
    fi
    TIME=${LOCUST_TIME:-'1m'}
    USERS=${LOCUST_USERS:-100}
    SPAWN=${LOCUST_SPAWN:-2}
    WORKERS=${LOCUST_WORKERS:-2}
    LOCUST+=( --master --expect-workers $WORKERS --headless --csv=report -u $USERS -r $SPAWN -t $TIME)
    REPORTER=( "python /reporter.py" )
    echo "${LOCUST[@]}"
    ${LOCUST[@]}
    echo "Running reporter.sh"
    exec ${REPORTER[@]}

elif [[ "$LOCUST_MODE" = "worker" ]]; then
    LOCUST+=( --worker --master-host=$LOCUST_MASTER)
    # wait for master
    #while ! wget --spider -qT5 $LOCUST_MASTER:$LOCUST_MASTER_WEB >/dev/null 2>&1; do
    #    echo "Waiting for master"
    sleep 10
    #done
    echo "${LOCUST[@]}"
    exec ${LOCUST[@]}
fi

#replace bash, let locust handle signals