set -e
rm -rf artifacts
mkdir -p artifacts

port=$(../../../common/find-free-port)

printf "Starting server on port $port\n"
SPOKEPORT=$port spoke &
SERVER_PID=$!
sleep 0.2

printf "Starting square provider\n"
SPOKEPORT=$port python ../../../common/square.py &
SQUARE_PID=$!
sleep 0.2

printf "Starting square caller\n"
SPOKEPORT=$port python square_call.py |& tee artifacts/output.txt
sleep 0.2

printf "Sending SIGTERM to server\n"
kill -15 $SERVER_PID

printf "Sending SIGTERM to square\n"
kill -15 $SQUARE_PID

printf "Waiting for everything to shutdown\n"
wait

printf "Diffing output - <exp >got\n"
diff expected.txt artifacts/output.txt
exitcode=$?

exit $exitcode
