set -e
rm -rf artifacts
mkdir -p artifacts

port=$(../../../../../common/find-free-port)

printf "Starting server on port $port\n"
SPOKEPORT=$port spoke-server &
SERVER_PID=$!
sleep 0.2

printf "Starting echo client\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port spoke-echo > artifacts/output.txt &
ECHO_PID=$!
sleep 0.2

printf "Starting square provider\n"
SPOKEPORT=$port python ../../../../../common/square.py &
SQUARE_PID=$!
sleep 0.2

printf "Publishing message\n"
SPOKEPORT=$port spoke-publish square/-rpc/call 5 &
sleep 0.2

printf "Sending SIGTERM to server\n"
kill -15 $SERVER_PID

printf "Sending SIGTERM to echo\n"
kill -15 $ECHO_PID

printf "Sending SIGTERM to square\n"
kill -15 $SQUARE_PID

printf "Waiting for everything to shutdown\n"
wait

printf "Diffing output - <exp >got\n"
diff expected.txt artifacts/output.txt
exitcode=$?

exit $exitcode
