set -e
rm -rf artifacts
mkdir -p artifacts

port=$(../../common/find-free-port)

printf "Starting server on port $port\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port python server.py >& artifacts/output_server.txt &
PID=$!

sleep 0.5

printf "Starting client 1\n"
SPOKEPORT=$port name=client1 delay=0.2 count=5 python client.py >& artifacts/output_client1.txt &

sleep 0.5

printf "Starting client 2 (showing output)\n"
SPOKEPORT=$port name=client2 delay=0.2 count=5 python client.py |& tee artifacts/output_client2.txt &

sleep 2

printf "Sending SIGTERM to server\n"
kill -15 $PID

printf "Waiting for everything to shutdown\n"
wait

printf "Diffing output - <exp >got\n"
diff expected_server.txt artifacts/output_server.txt &&
diff expected_client1.txt artifacts/output_client1.txt &&
diff expected_client2.txt artifacts/output_client2.txt
exitcode=$?

exit $exitcode
