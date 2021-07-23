set -e
rm -rf artifacts
mkdir -p artifacts

port=$(../../../common/find-free-port)

printf "Starting server on port $port\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port spoke >& artifacts/output_server.txt &
SERVER_PID=$!
sleep 0.2

printf "Starting echo client\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port spoke-echo >& artifacts/output_echo.txt &
ECHO_PID=$!
sleep 0.2

printf "Starting bad client\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port python bad_client.py >& artifacts/output_client.txt
sleep 0.2

printf "Sending SIGTERM to server\n"
kill -15 $SERVER_PID

printf "Sending SIGTERM to echo client\n"
kill -15 $ECHO_PID

printf "Waiting for everything to shutdown\n"
wait

printf "Diffing output - <exp >got\n"
diff expected_server.txt artifacts/output_server.txt &&
diff expected_echo.txt artifacts/output_echo.txt &&
diff expected_client.txt artifacts/output_client.txt
exitcode=$?

exit $exitcode
