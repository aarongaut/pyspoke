set -e
rm -rf artifacts
mkdir -p artifacts

port=$(../../../../../common/find-free-port)

printf "Starting server on port $port\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port spoke-server &
SERVER_PID=$!
sleep 0.2

printf "Starting invert provider\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port python invert.py &
INVERT_PID=$!
sleep 0.2

printf "Starting invert caller\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port python div_by_zero.py |& tee artifacts/output.txt
sleep 0.2

printf "Sending SIGTERM to server\n"
kill -15 $SERVER_PID

printf "Sending SIGTERM to invert\n"
kill -15 $INVERT_PID

printf "Waiting for everything to shutdown\n"
wait

printf "Diffing output - <got >exp\n"
diff -r artifacts expected
exitcode=$?

exit $exitcode
