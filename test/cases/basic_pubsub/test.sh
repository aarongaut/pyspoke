set -e
rm -rf artifacts
mkdir -p artifacts

port=$(../../common/find-free-port)

printf "Starting server on port $port\n"
SPOKEPORT=$port spoke &
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

printf "Diffing output - <exp >got\n"
diff expected.txt artifacts/output.txt
exitcode=$?

exit $exitcode
