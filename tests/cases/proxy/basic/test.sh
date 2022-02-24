set -e
rm -rf artifacts
mkdir -p artifacts

public_port=$(../../../common/find-free-port)
private_port=$(../../../common/find-free-port)

printf "Starting server on port $private_port\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$private_port spoke-server &
SERVER_PID=$!

printf "Sending persistent messages to server\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$private_port spoke-publish -p foo 5
PYTHONUNBUFFERED=1 SPOKEPORT=$private_port spoke-publish -p bar 5
PYTHONUNBUFFERED=1 SPOKEPORT=$private_port spoke-publish -p qux 5


sleep 0.2

printf "Starting proxy on port $public_port\n"
PYTHONUNBUFFERED=1 spoke-proxy --private-port $private_port --public-port $public_port foo bar &
PROXY_PID=$!

sleep 0.2

printf "Sending delayed persistent messages to server\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$private_port spoke-publish -p foo 10

sleep 0.2

printf "Starting echo1 client on proxy\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$public_port spoke-echo -l1 -o artifacts/echo1.txt foo &
ECHO1_PID=$!

printf "Starting echo2 client on proxy\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$public_port spoke-echo -l2 -o artifacts/echo2.txt bar &
ECHO2_PID=$!

printf "Starting echo3 client on proxy\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$public_port spoke-echo -l3 -o artifacts/echo3.txt qux &
ECHO3_PID=$!

printf "Starting echo4 client on server\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$private_port spoke-echo -l4 -o artifacts/echo4.txt &
ECHO4_PID=$!

printf "Giving echo clients time to start up\n"
sleep 0.2

printf "Publishing to not-proxied channel (only visible to private echo client)\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$private_port spoke-publish qux 404

sleep 0.2

printf "Publishing to proxied channel on proxy server (should be ignored)\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$public_port spoke-publish bar 405

sleep 0.2

printf "Publishing to proxied channel on private server (should be visible)\n"
PYTHONUNBUFFERED=1 SPOKEPORT=$private_port spoke-publish bar 200

sleep 0.2

printf "Sending SIGTERM to everything\n"
kill -15 $SERVER_PID $PROXY_PID $ECHO1_PID $ECHO2_PID $ECHO3_PID $ECHO4_PID

printf "Waiting for everything to shutdown\n"
wait

printf "Diffing output - <got >exp\n"
diff -r artifacts expected
exitcode=$?

exit $exitcode
