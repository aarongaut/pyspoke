set -e
rm -rf artifacts
mkdir -p artifacts

port=$(../../../../common/find-free-port)

printf "Starting server on port $port\n"
SPOKEPORT=$port spoke &
SERVER_PID=$!

printf "Publishing a persistent foo message\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port spoke-publish --persist foo &

printf "Publishing a non-persistent bar message\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port spoke-publish bar &

printf "Waiting a while for messages to be published\n"
sleep 0.2

printf "Starting echo client\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port spoke-echo > artifacts/output.txt &
ECHO_PID=$!
sleep 0.2

printf "Sending SIGTERM to server and echo client\n"
kill -15 $SERVER_PID $ECHO_PID

printf "Waiting for everything to shutdown\n"
wait

printf "Diffing output - <exp >got\n"
diff expected/output.txt artifacts/output.txt
exitcode=$?

exit $exitcode
