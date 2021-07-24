set -e
rm -rf artifacts
mkdir -p artifacts

port=$(../../../../../common/find-free-port)

printf "Starting server on port $port\n"
SPOKEPORT=$port spoke &
SERVER_PID=$!
sleep 0.2

printf "Starting bad caller\n"
SPOKEPORT=$port python bad_call.py |& tee artifacts/output.txt
sleep 0.2

printf "Sending SIGTERM to server\n"
kill -15 $SERVER_PID

printf "Waiting for everything to shutdown\n"
wait

printf "Diffing output - <exp >got\n"
diff expected.txt artifacts/output.txt
exitcode=$?

exit $exitcode
