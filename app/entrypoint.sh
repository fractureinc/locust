#!/bin/bash
# dont set -e. we want to report failed tests from locust process.
LOCUST=( "/usr/local/bin/locust" )
LOCUST+=( -f ${LOCUST_SCRIPT:-/locust-tasks/locust-tasks.py} )
LOCUST+=( --host=$TARGET_HOST )
LOCUST_MODE=${LOCUST_MODE:-master}

if [[ "$LOCUST_MODE" = "master" ]]; then
    export TIME=${LOCUST_TIME:-'1m'}
    export USERS=${LOCUST_USERS:-100}
    export SPAWN=${LOCUST_SPAWN:-2}
    export WORKERS=${LOCUST_WORKERS:-5}
    USEREPORTER=${USE_REPORTER:-'yes'}
    LOCUST+=( --master --expect-workers $WORKERS --headless --csv=report -u $USERS -r $SPAWN -t $TIME --stop-timeout 60 )
    echo "${LOCUST[@]}"
    ${LOCUST[@]}
    if [[ "$USEREPORTER" = "yes" ]]; then
        echo "Sending report ..."
        REPORTER=( "python /reporter.py" )
        exec ${REPORTER[@]}
    fi
elif [[ "$LOCUST_MODE" = "worker" ]]; then
    LOCUST+=( --worker --master-host=$LOCUST_MASTER)
    echo "${LOCUST[@]}"
    exec ${LOCUST[@]}
fi