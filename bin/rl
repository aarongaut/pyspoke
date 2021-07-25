#!/usr/bin/env sh

CURR_PATH="$PWD"
until [ -z "$CURR_PATH" ]
do
    if [ -e "$CURR_PATH/rl.sh" ]
    then
        RL_PATH="$CURR_PATH/rl.sh"
        export RL_ROOT="$CURR_PATH"
        source "$RL_PATH"
        if [ $# -eq 0 ]
        then
            exit 0
        else
            exec -- "$@"
        fi
    fi
    CURR_PATH=${CURR_PATH%/*}
done
echo rl.sh not found
exit 1
