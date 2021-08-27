set -e
rm -rf artifacts
mkdir -p artifacts

port1=$(../../../../../common/find-free-port)
port2=$(../../../../../common/find-free-port)

printf "Starting server1 on port $port1\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port1 spoke-server &
SERVER1_PID=$!

printf "Starting server2 on port $port2\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port2 spoke-server &
SERVER2_PID=$!

printf "Sending persistent messages to both servers\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port1 spoke-publish -p foo 5
PYTHONUNBUFFERED=1 SPOKEPORT=$port1 spoke-publish -p bar 5
PYTHONUNBUFFERED=1 SPOKEPORT=$port2 spoke-publish -p foo 5
PYTHONUNBUFFERED=1 SPOKEPORT=$port2 spoke-publish -p bar 5

sleep 0.2

printf "Sending delayed persistent messages to both servers\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port1 spoke-publish -p foo 10
PYTHONUNBUFFERED=1 SPOKEPORT=$port2 spoke-publish -p bar 10

sleep 0.2

printf "Starting echo client1\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port1 spoke-echo -l1 -o artifacts/echo1.txt &
ECHO1_PID=$!

printf "Starting echo client2\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port2 spoke-echo -l2 -o artifacts/echo2.txt &
ECHO2_PID=$!

printf "Giving echo clients time to start up\n"
sleep 0.2

printf "Starting bridge\n"
PYTHONUNBUFFERED=1 spoke-bridge --port1 $port1 --port2 $port2 &
BRIDGE_PID=$!

printf "Giving bridge time to start up\n"
sleep 0.2

printf "Sending SIGTERM to everything\n"
kill -15 $SERVER1_PID $SERVER2_PID $ECHO1_PID $ECHO2_PID $BRIDGE_PID

printf "Waiting for everything to shutdown\n"
wait

printf "Diffing output - <got >exp\n"
diff -r artifacts expected
exitcode=$?

exit $exitcode
