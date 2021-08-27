set -e
rm -rf artifacts
mkdir -p artifacts

port=$(../../../../common/find-free-port)

printf "Starting server on port $port\n"
SPOKEPORT=$port spoke-server &
SERVER_PID=$!
sleep 0.2

printf "Starting echo client\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port spoke-echo > artifacts/output.txt &
ECHO_PID=$!
sleep 0.2

printf "Publishing message\n"
SPOKEPORT=$port spoke-publish foo 5 &
sleep 0.2

printf "Sending SIGTERM to server\n"
kill -15 $SERVER_PID

printf "Sending SIGTERM to echo client\n"
kill -15 $ECHO_PID

printf "Waiting for everything to shutdown\n"
wait

printf "Diffing output - <got >exp\n"
diff artifacts/output.txt expected/output.txt
exitcode=$?

exit $exitcode
