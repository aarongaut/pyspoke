set -e
rm -rf artifacts
mkdir -p artifacts

port1=$(../../../../../common/find-free-port)
port2=$(../../../../../common/find-free-port)

printf "Starting server1 on port $port1\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port1 spoke-server -r &
SERVER1_PID=$!

printf "Starting server2 on port $port2\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port2 spoke-server &
SERVER2_PID=$!

printf "Sending persistent message to server2\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port2 spoke-publish -p msg1 10

printf "Waiting a moment\n"
sleep 0.2

printf "Starting bridge\n"
PYTHONUNBUFFERED=1 spoke-bridge --port1 $port1 --port2 $port2 &
BRIDGE_PID=$!

printf "Giving bridge time to start up\n"
sleep 0.2

printf "Sending another persistent message to server2\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port2 spoke-publish -p msg2 20

printf "Sending SIGTERM to server1\n"
kill -15 $SERVER1_PID

printf "Waiting for server1 to shutdown\n"
sleep 0.2

printf "Sending another persistent message to server2\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port2 spoke-publish -p msg3 30

sleep 0.2

printf "Restarting server1\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port1 spoke-server -r &
SERVER1_PID=$!

sleep 0.2

printf "Starting echo client for server1\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port1 spoke-echo -o artifacts/echo_client.txt &
ECHO1_PID=$!

printf "Sending another persistent message to server2\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port2 spoke-publish -p msg4 40

printf "Waiting a moment\n"

sleep 0.2

printf "Sending SIGTERM to everything\n"
kill -15 $SERVER1_PID $SERVER2_PID $ECHO1_PID $ECHO2_PID $BRIDGE_PID

printf "Waiting for everything to shutdown\n"
wait

printf "Diffing output - <got >exp\n"
diff -r artifacts expected
exitcode=$?

exit $exitcode
