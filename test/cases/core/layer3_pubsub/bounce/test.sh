set -e
rm -rf artifacts
mkdir -p artifacts

port=$(../../../../common/find-free-port)

printf "Starting server on port $port\n"
SPOKEPORT=$port spoke &
SERVER_PID=$!
sleep 0.2

printf "Starting echo client\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port spoke-echo > artifacts/client_echo.txt &
ECHO_PID=$!
sleep 0.2

printf "Running client\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port python client.py > artifacts/client.txt &
sleep 0.2

printf "Sending SIGTERM to server and echo client\n"
kill -15 $SERVER_PID $ECHO_PID

printf "Waiting for everything to shutdown\n"
wait

printf "Diffing output - <exp >got\n"
diff expected/client_echo.txt artifacts/client_echo.txt &&
diff expected/client.txt artifacts/client.txt
exitcode=$?

exit $exitcode
