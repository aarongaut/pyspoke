set -e
rm -rf artifacts
mkdir -p artifacts

port1=$(../../../../common/find-free-port)
port2=$(../../../../common/find-free-port)

printf "Starting server1 on port $port1\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port1 spoke &
SERVER1_PID=$!

printf "Starting server2 on port $port2\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port2 spoke &
SERVER2_PID=$!

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

printf "Starting square provider on server2\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port2 python ../../../../common/square.py &
SQUARE_PID=$!

printf "Waiting for everything to start up\n"
sleep 0.2

printf "Calling square from server1\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$port1 python call.py |& tee artifacts/call.txt

printf "Sending SIGTERM to everything\n"
kill -15 $SERVER1_PID $SERVER2_PID $ECHO1_PID $ECHO2_PID $SQUARE_PID $BRIDGE_PID

printf "Waiting for everything to shutdown\n"
wait

printf "Diffing output - <exp >got\n"
diff expected/echo1.txt artifacts/echo1.txt &&
diff expected/echo2.txt artifacts/echo2.txt &&
diff expected/call.txt artifacts/call.txt
exitcode=$?

exit $exitcode
