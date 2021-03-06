set -e
rm -rf artifacts
mkdir -p artifacts

port=$(../../../../../common/find-free-port)

printf "Starting server on port $port\n"
SPOKEPORT=$port spoke-server &
SERVER_PID=$!
sleep 0.2

printf "Starting bad caller\n"
SPOKEPORT=$port python bad_call.py |& tee artifacts/output.txt
sleep 0.2

printf "Sending SIGTERM to server\n"
kill -15 $SERVER_PID

printf "Waiting for everything to shutdown\n"
wait

printf "Diffing output - <got >exp\n"
diff -r artifacts expected
exitcode=$?

exit $exitcode
