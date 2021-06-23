set -e
rm -rf artifacts
mkdir -p artifacts

port=$(../../common/find-free-port)

printf "Starting server on port $port\n"
SPOKEPORT=$port spoke &
PID=$!
sleep 0.2

printf "Starting echo client\n"
SPOKEPORT=$port spoke-echo | tee artifacts/output.txt &
sleep 0.2

printf "Starting square provider\n"
SPOKEPORT=$port python square.py &
sleep 0.2

printf "Publishing message\n"
SPOKEPORT=$port spoke-publish square/-rpc/call 5 &
sleep 0.2

printf "Sending SIGTERM to server\n"
kill -15 $PID

printf "Waiting for everything to shutdown\n"
wait

printf "Diffing output - <exp >got\n"
diff expected.txt artifacts/output.txt
exitcode=$?

exit $exitcode
