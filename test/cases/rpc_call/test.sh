set -e
rm -rf artifacts
mkdir -p artifacts

port=$(../../common/find-free-port)

printf "Starting server on port $port\n"
SPOKEPORT=$port spoke &
PID=$!
sleep 0.2

printf "Starting square provider\n"
SPOKEPORT=$port python square.py &
sleep 0.2

printf "Starting square caller\n"
SPOKEPORT=$port python square_call.py |& tee artifacts/output.txt
sleep 0.2

printf "Sending SIGTERM to server\n"
kill -15 $PID

printf "Waiting for everything to shutdown\n"
wait

printf "Diffing output - <exp >got\n"
diff expected.txt artifacts/output.txt
exitcode=$?

exit $exitcode
