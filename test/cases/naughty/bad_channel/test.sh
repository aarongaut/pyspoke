set -e
rm -rf artifacts
mkdir -p artifacts

port=$(../../../common/find-free-port)

printf "Starting server on port $port\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port spoke >& artifacts/output_server.txt &
SERVER_PID=$!
sleep 0.2

printf "Starting bad client\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port python bad_client.py |& tee artifacts/output_client.txt
sleep 0.2

printf "Sending SIGTERM to server\n"
kill -15 $SERVER_PID

printf "Waiting for everything to shutdown\n"
wait

printf "Diffing output - <exp >got\n"
diff expected_server.txt artifacts/output_server.txt &&
diff expected_client.txt artifacts/output_client.txt
exitcode=$?

exit $exitcode
